from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Bus, Employee, Allocation


@admin.register(Bus)
class BusAdmin(ModelAdmin):
    list_display = ('bus_location', 'bus_number', 'capacity', 'remaining_capacity', 'is_active')
    search_fields = ('bus_number',)
    list_filter = ('is_active',)
    readonly_fields = ('remaining_capacity',)  # Prevent manual edits from bypassing logic


@admin.register(Employee)
class EmployeeAdmin(ModelAdmin):
    list_display = ('first_name', 'last_name', 'employee_id', 'email')
    search_fields = ('employee_id', 'first_name', 'last_name')
    list_filter = ('employee_id',)


@admin.register(Allocation)
class AllocationAdmin(ModelAdmin):
    list_display = ('employee', 'bus', 'allocation_date', 'status')
    search_fields = ('employee__employee_id', 'bus__bus_location')
    list_filter = ('status', 'allocation_date')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "employee":
            kwargs["queryset"] = Employee.objects.order_by('employee_id')
        elif db_field.name == "bus":
            kwargs["queryset"] = Bus.objects.filter(is_active=True).order_by('bus_location')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)