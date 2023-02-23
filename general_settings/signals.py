from django.db.models.signals import post_save
from django.dispatch import receiver
from account.tasks import send_test_mail
from . models import Branch, TestMailSetting, Category


@receiver(post_save, sender=Branch)
def enforce_single_inventory_issuing_unit(sender, instance, created, **kwargs):
    if instance.pk and instance.inventory == True:
        Branch.objects.filter(inventory=True).update(inventory=False)
        Branch.objects.filter(id=instance.id).update(inventory=True)


#This is for Test Email sending
@receiver(post_save, sender=TestMailSetting)
def test_mail(sender, instance, created, **kwargs): 
    try:
        send_test_mail.delay(instance.test_email)
    except:
        print('Test email not sent to:', instance.test_email)


