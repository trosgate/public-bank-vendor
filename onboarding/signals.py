from django.db.models.signals import post_save
from django.dispatch import receiver
from . models import Invitation


# @receiver(post_save, sender=Invitation)
# def update_generated_link(sender, instance, created, **kwargs):
#     try:
#         invitation = Invitation.objects.get(pk=instance.pk)
#         invitation.counter += 1
#         invitation.save()
#     except Exception as e:
#         print(str(e))
#     pass
