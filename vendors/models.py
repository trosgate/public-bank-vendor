from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils.safestring import mark_safe
from PIL import Image
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse


def profile_image_path(instance, filename):
    return "layout/%s/%s" % (instance.user.short_name, filename)


class ActiveVendor(models.Manager):
    def get_queryset(self):
        return super(ActiveVendor, self).get_queryset().filter(user__is_active=True, user__user_type='vendor')


class Vendor(models.Model):
    MALE = 'male'
    FEMALE = 'female'
    GENDER = (
        (MALE, _('Male')),
        (FEMALE, _('Female'))
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_("User"), related_name="vendor", on_delete=models.CASCADE)
    gender = models.CharField(_("Gender"), max_length=10, choices=GENDER)
    tagline = models.CharField(_("Tagline"), max_length=100, blank=True)
    description = models.TextField(_("Description"), max_length=2000, blank=True, error_messages={"name": {"max_length": _("Ensure a maximum character of 2000 for description field")}},)
    profile_photo = models.ImageField(_("Profile Photo"), upload_to='profile_image_path/', default='profile/user-login.png')
    address = models.CharField(_("Residence Address"), max_length=100, null=True, blank=True)
    active_team_id = models.PositiveIntegerField(_("Active Team ID"), default=0)
    
    objects = models.Manager()
    active = ActiveVendor()

    class Meta:
        verbose_name = 'Vendor Profile'
        verbose_name_plural = 'Vendor Profile'

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    # def save(self, *args, **kwargs):
    #     super(Vendor, self).save(*args, **kwargs)
    #     new_profile_photo = Image.open(self.profile_photo.path)
    #     if new_profile_photo.height > 300 or new_profile_photo.width > 300:
    #         output_size = (300, 300)
    #         new_profile_photo.thumbnail(output_size)
    #         new_profile_photo.save(self.profile_photo.path)

    def vendor_profile_absolute_url(self):
        return reverse('vendors:vendor_profile', args=([(self.user.short_name)]))
    
    def modify_vendor_absolute_url(self):
        return reverse('vendors:update_vendor_profile', args=([(self.user.short_name)]))

    # image display in Admin
    def image_tag(self):
        if self.profile_photo:
            return mark_safe('<img src="/media/%s" width="50" height="50" />' % (self.profile_photo))
        else:
            return f'/static/images/user-login.png'

    image_tag.short_description = 'profile_photo'


class Team(models.Model):
    # Team status
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    STATUS = (
        (ACTIVE, _('Active')),
        (INACTIVE, _('Inactive'))
    )
  
    title = models.CharField(
        _("Title"), 
        max_length=100, 
        unique=True,
        help_text="The Short title that fits your service",
    )
    slug = models.SlugField(_("Slug"), max_length=100, editable=True)
    status = models.CharField(_("Team Status"), max_length=20, choices=STATUS, default=ACTIVE)
    purpose = models.TextField(_("Purpose"), blank=True, null=True)   
    ordering = models.PositiveIntegerField(_("Order Priority"), null=True, blank=True, default=0)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Team Founder"), related_name="teammanager", on_delete=models.CASCADE)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_("Team Members"), related_name="team_member")
    
    class Meta:
        ordering = ["ordering"]
        verbose_name = _("Vendor Team")
        verbose_name_plural = _("Vendors Teams")

    def __str__(self):
        return self.title

    def get_team_detail_absolute_url(self):
        return reverse('vendors:vendor_detail', args=[self.slug])


class TeamChat(models.Model):
    team = models.ForeignKey(Team, verbose_name=_("Chat Team"), related_name='teamchats', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Sender"), related_name='teamsender', on_delete=models.CASCADE)
    content = models.TextField()
    sent_on = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['sent_on']

    def __str__(self):
        return self.content[:50] + '...'