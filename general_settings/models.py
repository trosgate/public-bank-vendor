from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django_cryptography.fields import encrypt
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.template.defaultfilters import slugify
from mptt.models import MPTTModel, TreeForeignKey
from django.conf import settings


def site_path(instance, filename):
    return "site/%s/%s" % (instance.site_name, filename)


def home_layout_path(instance, filename):
    return "layout/%s/%s" % (instance.title_block, filename)


class WebsiteSetting(models.Model):
    USE_HTTPS = "https://"
    USE_HTTP = "http://"
    PROTOCOL_TYPE = (
        (USE_HTTPS, _("Secure:> https://")),
        (USE_HTTP, _("Insecure:> http://")),
    )
    site_name = models.CharField(
        _("Site Name"), max_length=50, default="Example", null=True, blank=True, unique=True)
    site_Logo = models.ImageField(
        _("Site Logo"),  upload_to=site_path, default='site/logo.png', null=True, blank=True)
    protocol = models.CharField(
        _("Protocol Type"), max_length=20, choices=PROTOCOL_TYPE, default=USE_HTTPS, help_text=_("Warning! Make sure you have SSL Certificate for your site before switing to Secure options"))
    site_domain = models.CharField(_("Website Domain"), max_length=255, default="example.com", help_text=_(
        'E.x: example.com'), null=True, blank=True)
    button_color = models.CharField(
        _("Visitor Buttons"), 
        max_length=100, 
        default="purple", 
        help_text=_("Customize colors for signup, login, any other visitor buttons. Example '3F0F8FF', or 'red' or 'blue' or 'purple' or any css color code. Warning!: Donnot add quotation marks around the color attributes"), 
        null=True, 
        blank=True
    )   
    navbar_color = models.CharField(
        _("NavBar Color"), 
        max_length=100, 
        default="purple", 
        help_text=_("Customize colors for Navbar. Example '3F0F8FF', or 'red' or 'blue' or 'purple' or any css color code. Warning!: Donnot add quotation marks around the color attributes"), 
        null=True, 
        blank=True
    )
    twitter_url = models.URLField(
        _("Twitter Page"), 
        max_length=255, 
        null=True, 
        blank=True, 
        help_text=_("Enter the full secure url path of your Twitter page")
    )
    instagram_url = models.URLField(
        _("Instagram Page"), 
        max_length=255, 
        null=True, 
        blank=True, 
        help_text=_("Enter the full secure url path of your Instagram page")
    )
    youtube_url = models.URLField(
        _("Youtube Page"), 
        max_length=255, 
        null=True, 
        blank=True, 
        help_text=_("Enter the full secure url path of your Youtube page")
    )
    facebook_url = models.URLField(
        _("Facebook Page"), 
        max_length=255, 
        null=True, 
        blank=True, 
        help_text=_("Enter the full secure url path of your Facebook page"),
    )
    site_description = models.CharField(
        _("Site Description"), max_length=150, default="Ivendor Management System for ATM Vendors", null=True, blank=True)
    home_title = models.CharField(
        _("Home Title"), max_length=150, default="Welcome to Ivendor", null=True, blank=True)
    home_preview = models.CharField(
        _("Home Preview"), max_length=150, default="Select your option to get in", null=True, blank=True)
    login_preview = models.CharField(
        _("Home Login Preview"), max_length=150, default="Ivendor Management System for ATM Vendors", null=True, blank=True)
    reset_preview = models.CharField(
        _("Home Reset Preview"), max_length=150, default="Ivendor Management System for ATM Vendors", null=True, blank=True)
    profile_description = models.TextField(
        _("Default User profile description"), max_length=1500, default="Ivendor Management System for ATM Vendors", null=True, blank=True)
    team_banner_title = models.CharField(
        _("Default User profile description"), max_length=100, default="Your Workspace", null=True, blank=True)
    team_banner_preview = models.TextField(
        _("Default User profile description"), max_length=250, default="Working remotely with your team shouldn't be nightmare. Create teams, add your perfect staffs online and supervise them. It's that simple.", null=True, blank=True)
    applicant_instruction = models.TextField(
        _("Application Instruction"), max_length=1500, default="Ivendor Management System for ATM Vendors", null=True, blank=True)    
    invite_message = models.TextField(
        _("Invitation Message"), max_length=1500, default="Ivendor Management System for ATM Vendors", null=True, blank=True)    
    # Auto Logout System
    warning_time_schedule = models.PositiveIntegerField(_("Warning Time"), default=2, help_text=_(
        'By default the system will attempt to logout user every 2hrs with a prompt. You can change it in hours or days'))
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.site_name)

    class Meta:
        verbose_name = 'Website Settings'
        verbose_name_plural = 'Website Settings'

    # image display in Admin
    def site_logo_tag(self):
        if self.site_Logo:
            return mark_safe('<img src="/media/%s" width="160" height="50" style="border-radius:10px;"/>' % (self.site_Logo))
        else:
            return mark_safe('<span style="color:white; font-size:2em;">%s</span>' % (self.site_name))

    site_logo_tag.short_description = 'site_Logo'

    def get_site_logo(self):
        if self.site_Logo:
            return self.site_Logo.url
        else:
            return f'<span style="color:white; font-size:60px;">{self.site_name}</span>'


class WebsiteContent(WebsiteSetting):
    class Meta:
        proxy=True
        verbose_name = _("Website Content")
        verbose_name_plural = _("Website Contents")


class Category(models.Model):
    LESS_THAN_FIVE_YEARS = 1
    FIVE_TO_TEN_YEARS = 2
    ABOVE_10_YEARS = 3
    WORK_EXPERIENCE = (
        (LESS_THAN_FIVE_YEARS, _("Less Than Five Years")),
        (FIVE_TO_TEN_YEARS, _("Five to Ten Years")),
        (ABOVE_10_YEARS, _("Above Ten Years")),
    )
    
    name = models.CharField(_("Service Category"), max_length=100, unique=True)
    ordering = models.PositiveIntegerField(_("Order Priority"), default=0)
    status = models.BooleanField(_("Status"), choices=((False, 'Disable'), (True, 'Active')), default=True)
    meta = models.BooleanField(
        _("Meta"), 
        choices=((False, 'Other Vendor types'), (True, 'Core ATM Vendor')),
        help_text=_("Important:'Core ATM Vendor'- means the category is for ATM vendor explicitly. 'Other Vendor types'- means the category is for other vendor types that only need access to work like power vendor, cctv vendor etc ")
    )
    min_score = models.PositiveIntegerField(_("Minimum Score (%)"), default=70, help_text=_("The Minimum pass mark to qualify an applicant"))
    max_member_per_team = models.PositiveIntegerField(_("Expected Team Size"), default=5, help_text=_("The expected team size that will better manage our products or services."))
    regional_availability = models.BooleanField(_("Regional Availability"), choices=((False, 'Incapable'), (True, 'Capable')), default=True, help_text=_("How available is the vendor to work accross regions within the country and beyond."))
    instation = models.PositiveIntegerField(_("Instation Response (Hours)"), default=2, help_text=_("Goal is to know how long it can take vendor to get to instations in line with SLA)."))
    outstation = models.PositiveIntegerField(_("Outstation Response (Hours)"), default=6, help_text=_("Goal is to know how long it can take vendor to get to outstations in line with SLA)."))    
    working_hours = models.BooleanField(_("Supporting Hours"), choices=((False, 'Available Every 24/7'), (True, 'Every 8am - 5pm')), default=True, help_text=_("How available is the vendor to work around the clock especially when night job is roll-out"))
    other_contractual_services = models.BooleanField(_("Has other services/Products"), choices=((False, 'No'), (True, 'Yes')), default=True, help_text=_("Does vendor offer other contract based services?"))
    work_experience = models.PositiveIntegerField(_("Work Experience"), choices=WORK_EXPERIENCE, default=LESS_THAN_FIVE_YEARS, help_text=_("The minimum number of working experince"))
    value_added_services = models.BooleanField(_("Value Added Services"), choices=((False, 'No'), (True, 'Yes')), default=True, help_text=_("If vendor stands a chance, are they expected to give more added value like training etc?"))
    parts_availability = models.BooleanField(_("Product Parts"), choices=((False, 'No'), (True, 'Yes')), default=True, help_text=_("Does Vendor have parts available or need to buy on ad-hoc basis?"))
    emergency_plans = models.BooleanField(_("Emergency Plans"), choices=((False, 'No'), (True, 'Yes')), default=True, help_text=_("Does Vendor have parts available to handle emergencies"))
    concurrent_offers = models.BooleanField(_("Manage Concurrent offers"), choices=((False, 'No'), (True, 'Yes')), default=True, help_text=_("Does Vendor have Ability to manage concurrent offers from us?"))
    
    class Meta:
        ordering = ['ordering']
        verbose_name = _("Vendor Category")
        verbose_name_plural = _("Vendor Categories")


    def __str__(self):
        return self.name


class SupportProduct(models.Model):
    category = models.ForeignKey(Category, verbose_name=_('Parent Category'), on_delete=models.CASCADE, related_name='children')
    name = models.CharField(_('Support Product'), max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(_("Status"), choices=((False, 'Disable'), (True, 'Active')), default=True)
    ordering = models.PositiveIntegerField(_("Order Priority"), default=0)
    
    class Meta:
        ordering = ['ordering']
        verbose_name = _("Support Products")
        verbose_name_plural = _("Support Products")

    def __str__(self):
        return self.name


class Inventory(models.Model):
    # Status
    AVAILABLE = 'available'
    DEPLETED = 'depleted'
    STATUS_CHOICES = (
        (AVAILABLE, _('Available')),
        (DEPLETED, _('Depleted')),
    )
    name = models.CharField(_("Inventory Category "), max_length=100, unique=True)
    quantity = models.PositiveIntegerField(_("Qty in Stock"), default=0)
    ordering = models.PositiveIntegerField(_("Order Priority"), default=0)
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default=AVAILABLE)
    
    class Meta:
        ordering = ["ordering"]
        verbose_name = _("ATM Requisition")
        verbose_name_plural = _("ATM Requisition")

    def __str__(self):
        return self.name


class VendorCompany(models.Model):
    category = models.ForeignKey(Category, verbose_name=_("Service Category"), related_name="category", on_delete=models.CASCADE, help_text=_("Category of service provided"))
    name = models.CharField(_("Company Short Name"), max_length=100, unique=True)
    registered_name = models.CharField(_("Company Registered Name"), max_length=150)
    email = models.EmailField(_("Business/Support Email"), max_length=100)
    purpose = models.TextField(_("Purpose"), max_length=255, blank=True)
    ordering = models.PositiveIntegerField(_("Order Priority"), null=True, blank=True, default=0)
    status = models.BooleanField(_("Status"), choices=((False, 'Dissolved'), (True, 'Contracted')), default=True)
    ticket_response = models.PositiveIntegerField(_("New Ticket Response (Minutes)"), default=15, help_text=_("Counting from the time ticket was created, how long should we wait (in minutes) before sending reminder? E.x: 15 means -> 15 minutes. This works on condition that ticket was not assigned within every 15 minutes"))
    instation_arrival = models.PositiveIntegerField(_("In station Arrival (Hours)"), default=2, help_text=_("SLA Tracking will be invoked when ticket is finally assigned (Goal is to know how long it takes vendor to get to instations in line with SLA)."))
    outstation_arrival = models.PositiveIntegerField(_("Out station Arrival (Hours)"), default=2, help_text=_("SLA Tracking will be invoked when ticket is finally assigned (Goal is to know how long it takes vendor to get to outstations in line with SLA)."))
    working_hours = models.BooleanField(_("Supporting Hours"), choices=((False, 'Every 24/7'), (True, 'Every 8am - 5pm')), default=True, help_text=_("The 'Every 24/7' means ticket will be tracked as and when it is opened. The 'Every 8am - 5pm' means tickets will be tracked from 8am-5pm and deffered to another day if ticket was opened beyond working hours"))
    track_working_time = models.BooleanField(_("Total resolution Hours"), choices=((False, 'No'), (True, 'Yes')), default=True, help_text=_("This feature is the default behaviour of the software. 'Yes' means, it is MANDATORY for Staffs to confirm vendor arrival before work starts. The system will take record of time vendor arrived on site to time ticket was successfully closed"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["ordering"]
        verbose_name = _("ATM Vendor")
        verbose_name_plural = _("ATM Vendors")

    def __str__(self):
        return self.name


class Branch(models.Model):
    # location
    INSTATION = 'instation'
    OUTSTATION = 'outstation'
    LOCATION_CHOICES = (
        (INSTATION, _('In Station')),
        (OUTSTATION, _('Out Station')),
    )
    name = models.CharField(_("Branch/Unit Name"), max_length=100, unique=True)
    location = models.CharField(_("location"), max_length=20, choices=LOCATION_CHOICES, default=INSTATION)
    status = models.BooleanField(_("Status"), choices=((False, 'Closed'), (True, 'Active')), default=True)
    inventory = models.BooleanField(_("This is ATM Unit"), choices=((False, 'No'), (True, 'Yes')), default=False, help_text=_('This unit is the substantive ATM UNIT in charge of ATM consumables, request routing etc'))
    slug = models.SlugField(max_length=120)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Branch & Unit")
        verbose_name_plural = _("Branch & Unit")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug= slugify(self.name)    
        super(Branch, self).save(*args, **kwargs)


class MailingGroup(models.Model):
    name = models.CharField(_("Full name"), max_length=100)
    email = models.EmailField(_("User Email"), max_length=100)
    cluster = models.CharField(_("Cluster alias**"), max_length=100)
    created_at = models.DateTimeField(_("Created Time"), auto_now_add=True)
    branch = models.ForeignKey(
        Branch,
        verbose_name=_("Connected Branch"),
        related_name="mailgroup",
        on_delete=models.CASCADE,
    )
    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Mailing Group")
        verbose_name_plural = _("Mailing Group")
        unique_together =['email', 'branch']

    def __str__(self):
        return self.name


class Checklist(models.Model):
    item = models.CharField(_("checklist Item"), max_length=150, help_text=_(
        "This checklist will be displayed when closing tickets"), unique=True)
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordering"]
        verbose_name = _("Ticket Checklist")
        verbose_name_plural = _("Ticket Checklist")

    def __str__(self):
        return str(self.item)


class Terminals(models.Model):
    # location
    BRANCH = 'branch'
    OFFSITE = 'offsite'
    LOCATION_CHOICES = (
        (BRANCH, _('Branch')),
        (OFFSITE, _('Offsite')),
    )

    # Status
    DEPLOYED = 'deployed'
    DECOMMISSION = 'decommission'
    STATUS_CHOICES = (
        (DEPLOYED, _('Deployed')),
        (DECOMMISSION, _('Decommission')),
    )
    name = models.CharField(_("ATM Name"), max_length=100, help_text=_(
        "Name of ATM, e.x Burma Camp ATM"), unique=True, blank=True)
    terminal = models.CharField(_("ATM Terminal ID"), max_length=100, help_text=_(
        "Name of ATM terminal, e.x 10250001"), unique=True, blank=True)
    description = models.CharField(_("ATM Description"), max_length=100, help_text=_(
        "Description of ATM terminal, e.x Sowutuom Goil"), blank=True)
    gps_address = models.CharField(_("ATM GPS Address"), max_length=100, help_text=_(
        "GPS address of ATM terminal, e.x GP-22589-84"), null=True, blank=True)
    region = models.CharField(_("ATM Region"), max_length=100, help_text=_(
        "GPS address of ATM terminal, e.x GP-22589-84"), null=True, blank=True)
    type = models.CharField(_("ATM Type"), max_length=30, help_text=_(
        "Type of ATM terminal, e.x Ncr"), null=True, blank=True)
    category = models.CharField(_("Category Type"), max_length=100, choices=LOCATION_CHOICES, blank=True)
    status = models.CharField(_("Status"), max_length=100, choices=STATUS_CHOICES, default=DEPLOYED)
    branch = models.ForeignKey(
        Branch, 
        verbose_name=_("Tagged Branch"),
        related_name="terminalbranch",
        on_delete=models.CASCADE,
    )
    vendor = models.ForeignKey(
        VendorCompany, 
        verbose_name=_("Tagged Vendor"),
        related_name="terminalvendor", 
        on_delete=models.CASCADE,
    )
    
    class Meta:
        ordering = ["name"]
        verbose_name = 'ATM Terminal'
        verbose_name_plural = 'ATM Terminals'

    def __str__(self):
        return f'{self.name}'


class Mailer(models.Model):
   # Email API
    email_hosting_server = encrypt(models.CharField(
        _("Email Hosting Server"), 
        max_length=255,
        default="smtp.gmail.com", 
        help_text=_("E.x: smtp.gmail.com"), 
        null=True, 
        blank=True))
    email_hosting_server_password = encrypt(models.CharField(
        _("Email Server Password"), 
        max_length=255, 
        default='ngnrfcsozfrxbgfx', null=True, blank=True))
    email_hosting_username = encrypt(models.CharField(
        _("Email Server Username"), 
        max_length=255, 
        help_text=_('This is the email hosting username created'), 
        null=True, 
        blank=True))
    from_email = encrypt(models.CharField(
        _("Site-Wide Support Email"), 
        max_length=255, help_text=_('This email will be the site-wide support email for all email sending'), 
        null=True, 
        blank=True))
    email_use_tls = encrypt(models.BooleanField(
        _("Use TLS"), 
        choices=((False, 'No'), (True, 'Yes')), 
        default=True, 
        help_text=_('If your hosting support both SSL and TLS, we recommend the use of TLS'), 
        null=True, 
        blank=True))
    email_use_ssl = encrypt(models.BooleanField(
        _("Use SSL"), 
        choices=((False, 'No'), (True, 'Yes')), 
        default=False, 
        help_text=_('If SSL is set to "Yes", TLS should be "No", and vise-versa'), 
        null=True, 
        blank=True))
    email_fail_silently = encrypt(models.BooleanField(
        _("Email Fail Silently"), 
        choices=((False, 'Show Error'), (True, 'Hide Error')), 
        default=True, 
        help_text=_('if you want users to see errors with your misconfiguration, set to "Show Error". We recommend that you Hide Error'), 
        null=True, 
        blank=True))
    email_hosting_server_port = models.PositiveSmallIntegerField(
        _("Email Server Port"), 
        default=587, 
        help_text=_('Usually 587 but confirm from your hosting company'), 
        null=True, 
        blank=True)
    email_timeout = models.PositiveSmallIntegerField(
        _("Email Timeout"), 
        default=60, 
        help_text=_('the timeout time for email'), 
        null=True,
        blank=True)

    def __str__(self):
        return f'{self.from_email}'

    class Meta:
        verbose_name = 'Mailer Settings'
        verbose_name_plural = 'Mailer Settings'

    def clean(self):
        if self.email_use_tls and self.email_use_ssl:
            raise ValidationError(
                _("\"Use TLS\" and \"Use SSL\" are mutually exclusive, "
                  "so only set one of those settings to Yes."))


__all__ = ['Mailer']


class TestMailSetting(models.Model):
    title = encrypt(models.CharField(_("Testing Email"), max_length=20, default="My Test Email", null=True, blank=True))
    test_email = encrypt(models.EmailField(_("Receiver Email"), max_length=100, help_text=_(
        "Test the email settings by sending a Test mail"), null=True, blank=True))

    def __str__(self):
        return f'Testing: {self.test_email}'

    class Meta:
        verbose_name = 'Test Email Settings'
        verbose_name_plural = 'Test Email'


class SLAExceptions(models.Model):
    name = models.CharField(
        _("Breaching Exceptions"), 
        max_length=200, 
        default="Heavy rainfall inturrupted work", 
        null=True, 
        blank=True,
        unique=True,
        help_text=_("These are critical factors that could cause delay in SLA arrival time/pause a job temporarily")
    )
    ordering = models.PositiveIntegerField(_("Order Priority"), default=0)

    class Meta:
        ordering = ('ordering',)
        verbose_name = 'SLA Exceptions'
        verbose_name_plural = 'SLA Exceptions'

    def __str__(self):
        return self.name

