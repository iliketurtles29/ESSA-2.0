from django.db import models, transaction


# Bus model
class Bus(models.Model):
    bus_location = models.CharField(max_length=100, blank=True, null=True)
    bus_number = models.CharField(max_length=10, unique=True)
    capacity = models.PositiveIntegerField()
    remaining_capacity = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:

        
        indexes = [
            models.Index(fields=['bus_location']),
        ]
        verbose_name = "Bus"
        verbose_name_plural = "Buses"

    def save(self, *args, **kwargs):
        if self.pk is None and self.remaining_capacity is None:
            self.remaining_capacity = self.capacity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Bus {self.bus_location} (Remaining: {self.remaining_capacity}/{self.capacity})"


# Employee model
class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    employee_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['employee_id']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"


# Allocation model
class Allocation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="allocations")
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name="allocations")
    allocation_date = models.DateField()
    incoming_time = models.CharField(max_length=5)
    outgoing_time = models.CharField(max_length=5)

    class AllocationStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        CONFIRMED = 'Confirmed', 'Confirmed'
        CANCELLED = 'Cancelled', 'Cancelled'

    status = models.CharField(
        max_length=10, choices=AllocationStatus.choices, default=AllocationStatus.PENDING
    )

    class Meta:
        indexes = [
            models.Index(fields=['allocation_date', 'incoming_time', 'outgoing_time']),
            models.Index(fields=['employee', 'allocation_date', 'incoming_time', 'outgoing_time']),
        ]
        unique_together = ('employee', 'allocation_date', 'incoming_time', 'outgoing_time')

    def __str__(self):
        return f"{self.employee} -> {self.bus.bus_location} on {self.allocation_date} (IN: {self.incoming_time}, OUT: {self.outgoing_time})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        with transaction.atomic():
            if is_new:
                # New allocation — decrement the new bus
                bus = Bus.objects.select_for_update().get(pk=self.bus.pk)
                if bus.remaining_capacity <= 0:
                    raise ValueError(f"Bus {bus.bus_location} is full. No remaining capacity.")
                bus.remaining_capacity -= 1
                bus.save()

            else:
                # Existing allocation — check if the bus changed
                old_allocation = Allocation.objects.select_for_update().get(pk=self.pk)

                if old_allocation.bus_id != self.bus_id:
                    # Restore capacity on the old bus
                    old_bus = Bus.objects.select_for_update().get(pk=old_allocation.bus_id)
                    if old_bus.remaining_capacity < old_bus.capacity:
                        old_bus.remaining_capacity += 1
                        old_bus.save()

                    # Decrement capacity on the new bus
                    new_bus = Bus.objects.select_for_update().get(pk=self.bus.pk)
                    if new_bus.remaining_capacity <= 0:
                        raise ValueError(f"Bus {new_bus.bus_location} is full. No remaining capacity.")
                    new_bus.remaining_capacity -= 1
                    new_bus.save()

            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            bus = Bus.objects.select_for_update().get(pk=self.bus.pk)
            if bus.remaining_capacity < bus.capacity:
                bus.remaining_capacity += 1
                bus.save()
            super().delete(*args, **kwargs)