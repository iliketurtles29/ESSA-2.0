from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Employee


@receiver(post_save, sender=Employee)
def create_user_for_employee(sender, instance, created, **kwargs):
    if created:
        user = User.objects.create_user(
            username=instance.employee_id,
            email=instance.email or '',
            password=instance.employee_id,  # default password = employee_id
            first_name=instance.first_name,
            last_name=instance.last_name,
        )
