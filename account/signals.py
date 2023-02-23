from django.db.models.signals import post_save
from django.dispatch import receiver
from . models import Customer, TwoFactorAuth
from custodians.models import Custodian
from vendors.models import Vendor, Team
from django.utils.text import slugify


@receiver(post_save, sender=Customer)
def update_superadmin(sender, instance, created, **kwargs):

    if created and instance.is_superuser == True:
        try:
            admin = Customer.objects.get(pk=instance.id, is_superuser=True)
            admin.user_type='admin'
            admin.save()
        except Exception as e:
            print(str(e))


@receiver(post_save, sender=Customer)
def create_superadmin_as_custodian(sender, instance, created, **kwargs):

    if created and instance.is_staff == True:
        try:
            # This also ensures that only SuperAdmin and its profile can be created from terminal
            Custodian.objects.get_or_create(user=instance)[0]
        except Exception as e:
            print(str(e))

    elif created and instance.vendor_company:
        team = Team.objects.get_or_create(
            title=instance.vendor_company.name,
            purpose=f"This is {instance.vendor_company.name} team", 
            created_by = instance,
            slug = slugify(instance.vendor_company.name)
        )[0]
        team.members.add(instance)
        vendor_profile = Vendor.objects.get_or_create(user=instance)[0]

        new_vendor = vendor_profile
        new_vendor.active_team_id = team.pk
        new_vendor.save()


@receiver(post_save, sender=Customer)
def generate_TwoFactorAuth_code(sender, instance, created, **kwargs):
    if created:
            TwoFactorAuth.objects.get_or_create(user=instance)