from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils.safestring import mark_safe
from PIL import Image
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.template.defaultfilters import slugify


def complaint_file_path(instance, filename):
    return "complaints/%s/%s" % (instance.file.name, filename)


class ActiveCustodian(models.Manager):
    def get_queryset(self):
        return super(ActiveCustodian, self).get_queryset().filter(user__is_active=True, user__user_type='vendor')


class Custodian(models.Model):
    MALE = 'male'
    FEMALE = 'female'
    GENDER = (
        (MALE, _('Male')),
        (FEMALE, _('Female'))
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_("User"), related_name="custodian", on_delete=models.CASCADE)
    gender = models.CharField(_("Gender"), max_length=10, choices=GENDER)
    tagline = models.CharField(_("Tagline"), max_length=100, blank=True)
    description = models.TextField(_("Description"), max_length=2000, blank=True, error_messages={"name": {"max_length": _("Ensure a maximum character of 2000 for description field")}},)
    profile_photo = models.ImageField(_("Profile Photo"), upload_to='profile_image_path/', default='profile/user-login.png')
    address = models.CharField(_("Residence Address"), max_length=100, null=True, blank=True)
    objects = models.Manager()
    active = ActiveCustodian()

    class Meta:
        verbose_name = 'Staff Profile'
        verbose_name_plural = 'Staffs Profile'

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

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


class HelpDesk(models.Model):
    # Status
    ACTIVE = 'active'
    CLOSED = 'closed'
    STATUS = (
        (ACTIVE, 'Active'),
        (CLOSED, 'Closed'),
    )

    # Condition
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CONDITION = (
        (LOW, _('Low')),
        (MEDIUM, _('Medium')),
        (HIGH, _('High')),
    )

    title = models.CharField(_("Title"), max_length=100, help_text=_("title field is Required"))
    category = models.ForeignKey("general_settings.Category", verbose_name=_("Category"), related_name="requestcategory", on_delete=models.CASCADE)
    slug = models.SlugField(_("Slug"), max_length=100)
    content = models.TextField(_("Message"), max_length=2000)
    reference = models.CharField(_("Reference #"), unique=True, blank=True, max_length=100)
    status = models.CharField(_("Status"), max_length=20, choices=STATUS, default=ACTIVE)
    condition = models.CharField(_("Priority Level"), max_length=100, choices=CONDITION, default=LOW)
    file = models.ImageField(_("Attachment(Optional)"), upload_to='complaint_file_path/', blank=True, null=True)
    created_at = models.DateTimeField(_("Time Created"), auto_now_add=True)
    modified_at = models.DateTimeField(_("Time Modified"), auto_now=True)
    
    request_branch = models.ForeignKey("general_settings.Branch", verbose_name=_("Request Branch"), related_name="requester", blank=True, null=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Request Staff"), related_name="createdstaff", on_delete=models.CASCADE)
    
    support_branch = models.ForeignKey("general_settings.Branch", verbose_name=_("Support Team"), related_name="supporter", blank=True, null=True, on_delete=models.SET_NULL)
    support_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Support Staff"), related_name="supportstaff", blank=True, null=True, on_delete=models.SET_NULL)
    is_routed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Request'
        verbose_name_plural = 'Requests'

    def __str__(self):
        return f'{self.title}' 

    def save(self, *args, **kwargs):
        self.slug= slugify(self.title)    
        super(HelpDesk, self).save(*args, **kwargs)


class HelpDeskMessage(models.Model):
    helpdesk = models.ForeignKey(HelpDesk, verbose_name=_("HelpDesk"), related_name="deskreplies", on_delete=models.CASCADE)
    support = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Support"), related_name="ticketsupport", blank=True, null=True, on_delete=models.SET_NULL)
    content = models.TextField(_("Message"), max_length=2000)
    created_at = models.DateTimeField(_("Time Created"), auto_now_add=True)
    action = models.BooleanField(_("Action"), choices = ((False,'Customer Replied'), (True, 'Admin Replied')), default = True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = ('HelpDesk Reply')
        verbose_name_plural = ('HelpDesk Replies')

    def __str__(self):
        return f'{self.helpdesk.created_by} vs. {self.support}'
