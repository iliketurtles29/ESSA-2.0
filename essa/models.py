from django.db import models

class Bus(models.Model):
    bus_location = models.CharField(max_length=100, blank=True, null=True) 
    bus_number = models.CharField(max_length=10, unique=True)  # identifier
    capacity = models.PositiveIntegerField() 
    is_active = models.BooleanField(default=True)  # Whether bus is operational

    class Meta:
        indexes = [
            models.Index(fields=['bus_location']), 
        ]
        verbose_name_plural = "Buses"
        verbose_name = "Bus"

    def __str__(self):
        return f"Bus {self.bus_number} (Capacity: {self.capacity})"


class Employee(models.Model):
    # Employee model optimized for shuttle service
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    employee_id = models.CharField(max_length=20, unique=True)  # Unique ID for each employee
    email = models.EmailField(unique=True, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['employee_id']),  # Index for fast lookup by employee_id
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"


class Allocation(models.Model):
    """
    Represents the allocation of an employee to a specific bus on a given date and time.
    This is different from just tracking rides, as it involves assigning employees to buses in advance.
    """
    # Foreign Key Relationships:
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="allocations")
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name="allocations")

    # Allocation Details:
    allocation_date = models.DateField()  # The date of allocation (the employee is assigned to a bus on this date)
    allocation_time = models.TimeField()  # The time of allocation (departure time for the shuttle)

    # Allocation Status - track whether the allocation is confirmed, pending, or cancelled
    class AllocationStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        CONFIRMED = 'Confirmed', 'Confirmed'
        CANCELLED = 'Cancelled', 'Cancelled'

    status = models.CharField(
        max_length=10, choices=AllocationStatus.choices, default=AllocationStatus.PENDING
    )

    # Ensure no overbooking: an employee can only be allocated to one bus per date and time.
    class Meta:
        indexes = [
            models.Index(fields=['allocation_date', 'allocation_time']),  # Index for fast lookup by date/time
            models.Index(fields=['employee', 'allocation_date', 'allocation_time']),  # Index for fast lookup by employee & time
        ]
        unique_together = ('employee', 'allocation_date', 'allocation_time')  # No double allocation

    def __str__(self):
        return f"Employee {self.employee} allocated to Bus {self.bus.bus_location} on {self.allocation_date} at {self.allocation_time}"

    def save(self, *args, **kwargs):
        # Ensure capacity is not exceeded before saving the allocation
        allocation_count = Allocation.objects.filter(
            bus=self.bus, allocation_date=self.allocation_date, allocation_time=self.allocation_time
        ).count()

        if allocation_count >= self.bus.capacity:
            raise ValueError(f"Bus {self.bus.bus_location} is at full capacity for the selected time slot.")

        super().save(*args, **kwargs)