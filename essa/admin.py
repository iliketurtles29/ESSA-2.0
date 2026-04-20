from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Bus, Employee, Allocation
# Register your models here.

@admin.register(Bus)
class BusAdmin(ModelAdmin):
    list_display = ('bus_number', 'capacity', 'is_active')
    search_fields = ('bus_number',)
    list_filter = ('is_active',)

@admin.register(Employee)
class EmployeeAdmin(ModelAdmin):
    list_display = ('first_name', 'last_name', 'employee_id', 'email')
    search_fields = ('employee_id', 'first_name', 'last_name')
    list_filter = ('employee_id',)

@admin.register(Allocation)
class AllocationAdmin(ModelAdmin):
    list_display = ('employee', 'bus', 'allocation_date', 'allocation_time', 'status')
    search_fields = ('employee__employee_id', 'bus__bus_number')
    list_filter = ('status', 'allocation_date')


