from django.db import models, transaction as db_transaction
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.template.defaultfilters import slugify
from django.urls import reverse
from general_settings.models import Category
from django.db import IntegrityError
from .utilities import create_random_code
from .tasks import send_invitation_link
from uuid import uuid4
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from general_settings.models import WebsiteSetting, VendorCompany
from django.db.models import Avg, F


def applications_path(instance, filename):
    return "%s/%s" % (instance.name, filename)


class Composer(WebsiteSetting):
    class Meta:
        proxy=True
        verbose_name = _("Application Instruction")
        verbose_name_plural = _("Application Instruction")


class Contacts(models.Model):
    name = models.CharField(_("Company or Receiver name"), max_length=150)
    email = models.EmailField(_("Email"), max_length=100)
    phone = models.CharField(_("Phone Number"), max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(_("Date Created"), auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Creator"), related_name="mycontacts", on_delete=models.PROTECT)
    
    def __str__(self):
        return f'{self.name}<{self.email}>'

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Contact List"
        verbose_name_plural = "Contact List"    


class Parameters(models.Model):
    id=models.AutoField(primary_key=True)
    reference = models.UUIDField(unique=True, editable=False, default=uuid4)
    criteria1 = models.CharField(_("Criteria 1"), max_length=100, unique=True, default='Criteria 1')
    note1 = models.CharField(_("Guiding Note 1"), max_length=350, default='Criteria 1 note', help_text=_("What information does this parameter seek to find from vendors. This will guide but not restrict Panelists."))
    criteria2 = models.CharField(_("Criteria 2"), max_length=100, unique=True, default='Criteria 2')
    note2 = models.CharField(_("Guiding Note 2"), max_length=350, default='Criteria 2 note', help_text=_("What information does this parameter seek to find from vendors. This will guide but not restrict Panelists."))
    criteria3 = models.CharField(_("Criteria 3"), max_length=100, unique=True, default='Criteria 3')
    note3 = models.CharField(_("Guiding Note 3"), max_length=350, default='Criteria 3 note', help_text=_("What information does this parameter seek to find from vendors. This will guide but not restrict Panelists."))
    criteria4 = models.CharField(_("Criteria 4"), max_length=100, unique=True, default='Criteria 4')
    note4 = models.CharField(_("Guiding Note 4"), max_length=350, default='Criteria 4 note', help_text=_("What information does this parameter seek to find from vendors. This will guide but not restrict Panelists."))
    criteria5 = models.CharField(_("Criteria 5"), max_length=100, unique=True, default='Criteria 5')
    note5 = models.CharField(_("Guiding Note 5"), max_length=350, default='Criteria 5 note', help_text=_("What information does this parameter seek to find from vendors. This will guide but not restrict Panelists."))
    criteria6 = models.CharField(_("Criteria 6"), max_length=100, unique=True, default='Criteria 6')
    note6 = models.CharField(_("Guiding Note 6"), max_length=350, default='Criteria 6 note', help_text=_("What information does this parameter seek to find from vendors. This will guide but not restrict Panelists."))
    edited_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Last Editor"), related_name="paramcreator", blank=True, null=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField(_("Date Created"), auto_now_add=True)
    modified_at = models.DateTimeField(_("Date Created"), auto_now=True)

    def __str__(self):
        return str(self.reference)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Appraisal Parameter"
        verbose_name_plural = "Appraisal Parameters"    


class Tender(models.Model):
    GENERAL = 'general'
    CATEGORY_BASED = 'category'
    ONBOARDING_MODES = (
        (GENERAL, _("General Onboarding")),
        (CATEGORY_BASED, _("Category-Based Onboarding")),
    )
    title = models.CharField(_("Title"), max_length=150, help_text=_("This title will be the heading on invite mail and application form"))
    slug = models.SlugField(_("Slug"), max_length=150)
    number_of_links = models.PositiveIntegerField(_("Number of Links"), help_text=_("Please specify number of invite links to generate for this Tender"))
    duration = models.DateTimeField(_("Expiration of Link"), help_text=_("Deadline for expiration of application link")) 
    mode = models.CharField(_("Onboarding Mode"), max_length=30, choices=ONBOARDING_MODES, default=GENERAL)
    reference = models.CharField(_("Reference"), max_length=15)
    created_at = models.DateTimeField(_("Date Created"), auto_now_add=True)
    modified_at = models.DateTimeField(_("Last Modified"), auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tendercreator', on_delete=models.PROTECT)        
    category = models.ForeignKey('general_settings.Category', verbose_name='Support Category', blank=True, null=True, on_delete=models.PROTECT)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Onboarding Group"
        verbose_name_plural = "Onboarding Group"

    def save(self, *args, **kwargs):
        if self.slug is None or self.slug == '':
            self.slug = slugify(self.title)
        super(Tender, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.title)

    # absolute url for tender detail page
    def tender_absolute_url(self):
        return reverse('onboarding:tender_detail', kwargs={'tender_pk': self.pk, 'tender_slug':self.slug})


    def clean(self):
        if self.duration is None or self.duration == '':
            raise ValidationError(
                {'duration': _('Expiry time of the invite link is required')})

        if not (self.duration > timezone.now()):
            raise ValidationError(
                {'duration': _('You cannot schedule in the past')})

        if self.mode == 'category' and self.category == '' or self.mode == 'category' and self.category is None:
            raise ValidationError(
                {'category': _('Error! support category is required')})
        

    @classmethod
    def create(cls, title:str, duration, number_of_links:int, mode, created_by, category=None):
        with db_transaction.atomic():

            if title is None or title == '':
                raise Exception(_("Error! Email field is required"))
            if mode == 'category' and category == '' or mode == 'category' and category is None:
                raise Exception(_("Error! Email field is required"))

            if mode == 'category':
                new_category = category
            else:
                new_category = None

            tender = cls.objects.create(
                title=title, 
                duration=duration,
                number_of_links=number_of_links,
                mode=mode, 
                category=new_category, 
                created_by=created_by
            )
            tender.slug = slugify(tender.title)
            code = create_random_code()
            tender.reference=f'{code}{tender.pk}'
            tender.save()

        return tender


    @property
    def invitation_count(self):
        return Invitation.objects.filter(tender=self).count()
        
    @property
    def application_count(self):
        return Application.objects.filter(invitation__tender=self).count()
    

class ActiveVendor(VendorCompany):
    class Meta:
        proxy=True
        verbose_name = _("Active Vendor")
        verbose_name_plural = _("Active Vendor")


class Invitation(models.Model):
    LOCKED = 'locked'
    UNLOCKED = 'unlocked'
    ACCESS_CHOICES = (
        (LOCKED, _("Locked")),
        (UNLOCKED, _("Unlocked")),
    )
    INVITED = 'invited'
    APPLIED = 'applied'
    EXPIRED = 'expired'
    INVITATION_CHOICES = (
        (INVITED, _("Invited")),
        (APPLIED, _("Applied")),
        (EXPIRED, _("Expired")),
    )
    id=models.AutoField(primary_key=True)
    reference = models.UUIDField(unique=True, editable=False, default=uuid4)
    tender = models.ForeignKey(Tender, verbose_name=_("Tender"), related_name='invitations', on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Sender"), related_name="sender", blank=True, on_delete=models.PROTECT)
    receiver = models.ForeignKey(Contacts, verbose_name=_("Receiver"), related_name="receiver", blank=True, on_delete=models.PROTECT)
    access = models.CharField(_("Access Status"), max_length=10, choices=ACCESS_CHOICES, default=LOCKED)
    status = models.CharField(_("Status"),  max_length=20, choices=INVITATION_CHOICES, default=INVITED)
    token = models.CharField(_("Access Token"), max_length=100, unique=True)
    sent_on = models.DateTimeField(_("Date"), auto_now_add=True)
      
    def __str__(self):
        return f'Invitation to {self.receiver}'

    class Meta:
        ordering = ('-id',)


    @classmethod
    def send_invitation(cls, tender, created_by, receiver):
        
        if receiver is None or receiver == '':
            raise Exception(_("Error! Receiver Unknown"))

        if created_by is None or created_by == '':
            raise Exception(_("Error! Unknown request"))

        if tender is None or tender == '':
            raise Exception(_("Error! Please check the invite link and try again"))
        
        if cls.objects.filter(tender=tender, receiver=receiver).exists():
            raise Exception(_("Error! Company already invited"))
        
        while True:
            token=f'tokenize_{create_random_code()}'
            try:
                with db_transaction.atomic():
                    invite = cls.objects.create(
                        tender=tender,
                        created_by=created_by,
                        receiver=receiver,
                        token=token
                    )
                    
            except IntegrityError:
                token=f'tokenize_{create_random_code()}'
                invite = cls.objects.create(
                    tender=tender,
                    created_by=created_by,
                    receiver=receiver,
                    token=token
                )
            
            db_transaction.on_commit(lambda: send_invitation_link.delay(invite.reference))
            return invite

    def invitation_absolute_url(self):
        return reverse('onboarding:application', kwargs={'invite_reference': self.reference, 'tender_slug':self.tender.slug})


class Application(models.Model):
    NOT_GRADED = 'notgraded'
    INCONPLETE = 'incomplete'
    REVIEWED = 'reviewed'
    GRADED = 'graded'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    APPLICATION_CHOICES = (
        (NOT_GRADED, _("Not Graded")),
        (INCONPLETE, _("Incomplete")),
        (REVIEWED, _("Reviewed")),
        (GRADED, _("Graded")),
        (APPROVED, _("Approved")),
        (REJECTED, _("Rejected")),
    )
 
    LOW_SCORE = 'low_score'
    SHORTLIST_SATISFIED = 'shortlist_satisfied'
    MISCONDUCT = 'misconduct'
    MISREPRESENTATION = 'misrepresentation'
    BAD_HISTORY = 'badhistory'
    REJECT_REASON_CHOICES = (
        (LOW_SCORE, _("Low Score or blacklist zone")),
        (SHORTLIST_SATISFIED, _("Cut-off already satisfied")),
        (MISCONDUCT, _("Applicant misconduct prior or after application")),
        (MISREPRESENTATION, _("Applicant misrepresentation of identity")),
        (BAD_HISTORY, _("Recent finding about vendor against our policies")),
    ) 

    LESS_THAN_FIVE_YEARS = 1
    FIVE_TO_TEN_YEARS = 2
    ABOVE_10_YEARS = 3
    WORK_EXPERIENCE = (
        (LESS_THAN_FIVE_YEARS, _("Less Than Five Years")),
        (FIVE_TO_TEN_YEARS, _("Five to Ten Years")),
        (ABOVE_10_YEARS, _("Above Ten Years")),
    )
    ONE_HOUR = 1
    TWO_HOURS = 2
    THREE_HOURS = 3
    FOUR_HOURS = 4
    FIVE_HOURS = 5
    SIX_HOURS = 6
    SEVEN_HOURS = 7
    EIGHT_HOURS = 8
    NINE_HOURS = 9
    TEN_HOURS = 10
    RESPONSE_CHOICES = (
        (ONE_HOUR, _("1 Hour")),
        (TWO_HOURS, _("2 Hours")),
        (THREE_HOURS, _("3 Hours")),
        (FOUR_HOURS, _("4 Hours")),
        (FIVE_HOURS, _("5 Hours")),
        (SIX_HOURS, _("6 Hours")),
        (SEVEN_HOURS, _("7 Hours")),
        (EIGHT_HOURS, _("8 Hours")),
        (NINE_HOURS, _("9 Hours")),
        (TEN_HOURS, _("10 Hours")),
    )
    applicant = models.CharField(_("Applicant Fullname"), max_length=100)
    email = models.EmailField(_("Business/Support Email"), max_length=100, unique=True)
    name = models.CharField(_("Company Short Name"), max_length=100, unique=True)
    reference = models.CharField(_("Reference"), max_length=100, blank=True, null=True)
    registered_name = models.CharField(_("Company Registered Name"), max_length=150)
    max_member_per_team = models.PositiveIntegerField(_("Current Team Size"), default=1, help_text=_("The expected team size that will better manage our products or services."))
    counter = models.PositiveIntegerField(_("Count"), default=0)
    instation = models.PositiveIntegerField(_("Response Within Accra"), choices=RESPONSE_CHOICES, help_text=_("This will consider working hours agreed by both parties"))
    outstation = models.PositiveIntegerField(_("Response Outside Accra"), choices=RESPONSE_CHOICES, help_text=_("This will consider working hours agreed by both parties"))    
    regional_availability = models.BooleanField(_("Regional Availability"), choices=((False, 'Only available in Greater Accra'), (True, 'Available in any Region and/ or country')), help_text=_("How available are your Team to work accross regions/countries."))    
    working_hours = models.BooleanField(_("Working Hours"), choices=((True, 'Available for 8am-5pm or 24/7 support'), (False, 'Available for 8am-5pm support only')), help_text=_("This may depend on the kind of service"))
    proposal_attachment = models.FileField(
        _("1. Attachment (Proposal)"),
        help_text=_("File must be any of these 'doc', 'docx', 'pdf'"), 
        upload_to=applications_path, 
        validators=[FileExtensionValidator(allowed_extensions=['DOC', 'DOCX', 'PDF'])])
    company_attachment_1= models.FileField(
        _("2. Form A Attachment"),
        help_text=_("File must be any of these 'doc', 'docx', 'pdf'"), 
        upload_to=applications_path, 
        validators=[FileExtensionValidator(allowed_extensions=['DOC', 'DOCX', 'PDF'])])
    company_attachment_2= models.FileField(
        _("3. Form C Attachment"),
        help_text=_("File must be any of these 'doc', 'docx', 'pdf'"), 
        upload_to=applications_path, 
        validators=[FileExtensionValidator(allowed_extensions=['DOC', 'DOCX', 'PDF'])])
    company_attachment_3= models.FileField(
        _("3. Other Attachment"),
        help_text=_("File must be any of these 'doc', 'docx', 'pdf'"),
        blank=True, 
        null=True, 
        upload_to=applications_path, 
        validators=[FileExtensionValidator(allowed_extensions=['DOC', 'DOCX', 'PDF'])])

    created_at = models.DateTimeField(_("Date Created"), auto_now_add=True)
    modified_at = models.DateTimeField(_("Date Created"), auto_now=True)
    status = models.CharField(_("Status"), max_length=20, choices=APPLICATION_CHOICES, default=NOT_GRADED)
    reason = models.TextField(_("Reason"), max_length=400, blank=True, null=True)
    reviewed_at = models.DateTimeField(_("Date Reviewed"), blank=True, null=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name=_("Review Officer"), 
        related_name="applicationreviewer",
        blank=True, 
        null=True, 
        on_delete=models.PROTECT
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name=_("Approved Officer"), 
        related_name="applicationapprover",
        blank=True, 
        null=True, 
        on_delete=models.PROTECT
    ) 
    justification = models.CharField(_("Justification (**if Rejected)"), max_length=60, choices=REJECT_REASON_CHOICES)
    is_marked = models.BooleanField(default=False) # Marked for bulk approval
    visibility = models.BooleanField(default=True) # Show or hide panel list
    invitation = models.ForeignKey(Invitation, related_name='tenderapplication', on_delete=models.PROTECT)
    category = models.ForeignKey('general_settings.Category', verbose_name='Support Category', on_delete=models.PROTECT)
    support_product = models.ManyToManyField('general_settings.SupportProduct', verbose_name='Support Products')
    meeting_link = models.URLField(_("Meeting Link"),  max_length=2048, blank=True, null=True)     
          
    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ("id",)
        verbose_name = "Application"
        verbose_name_plural = "Application" 

    def save(self, *args, **kwargs):
        if self.reference is None or self.reference == '':
            self.reference = f'{create_random_code()}'
        super(Application, self).save(*args, **kwargs)

    def grading_absolute_url(self):
        return reverse('onboarding:grading', kwargs={'application_pk': self.pk, 'application_name': self.name})

    def scoresheet_absolute_url(self):
        return reverse('onboarding:master_scoresheet', kwargs={'reference': self.pk, 'vendor_name': self.name})
    
    def review_absolute_url(self):
        return reverse('onboarding:pool_review', kwargs={'reference': self.pk, 'vendor_name': self.name})

    def application_absolute_url(self):
          return reverse('onboarding:panelist_view', args=[self.name])

    def approval_absolute_url(self):
        return reverse('onboarding:approval', kwargs={'application_pk': self.pk, 'vendor_name': self.name})

    def expire_invitation(self):
        invitation = self.invitation
        invitation.status = 'expired'
        invitation.save()

    @property
    def applicant_final_result(self):
        applicant_score = Grading.objects.filter(application=self.pk)    
        return sum(score.total_marks for score in applicant_score)
    
    @property
    def total_panelist(self):
        return Panelist.objects.filter(application=self.pk).count()         
         
    @property
    def average_score(self):
        if self.counter < 1:
            return 0
        total = self.applicant_final_result
        count = self.counter
        return round(total/count)

    @property
    def get_ranking(self):
        grand_total = self.average_score
        
        if grand_total < 20:
            return 'Blacklist'
        if int(20) <= grand_total <= int(22):
            return 'Dissatisfactory'
        if int(23) <= grand_total <= int(24):
            return 'Fairly Satisfactory'
        if int(25) <= grand_total <= int(26):
            return 'Satisfactory'
        if grand_total > int(26):
            return 'Highly Satisfactory'


class Panelist(models.Model):
    LOCKED = 'locked'
    UNLOCKED = 'unlocked'
    ACCESS_CHOICES = (
        (LOCKED, _("Locked")),
        (UNLOCKED, _("Unlocked")),
    )

    INVITED = 'invited'
    ACCEPTED = 'accepted'
    GRADED = 'graded'
    INVITATION_CHOICES = (
        (INVITED, _("Invited")),
        (ACCEPTED, _("Applied")),
        (GRADED, _("Graded")),
    )

    INTERNAL = 'internal'
    EXTERNAL = 'external'
    MODE_CHOICES = (
        (INTERNAL, _("Login Access")),
        (EXTERNAL, _("Token Access")),
    )
    id=models.AutoField(primary_key=True)
    reference = models.UUIDField(unique=True, editable=False, default=uuid4)
    application = models.ForeignKey(
        Application, 
        related_name='applicapanelists',
        on_delete=models.PROTECT
    )
    mode = models.CharField(_("Access Type"), max_length=20, choices=MODE_CHOICES, default=INTERNAL)     
    panelist = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name=_("Panelist A"), 
        related_name="parampanelist",
        blank=True, 
        null=True, 
        on_delete=models.PROTECT
    )
    access = models.CharField(_("Access Status"), max_length=10, choices=ACCESS_CHOICES, default=LOCKED)
    status = models.CharField(_("Status"),  max_length=20, choices=INVITATION_CHOICES, default=INVITED)
    name = models.CharField(_("External Panelist Name"),  max_length=100, blank=True, null=True)     
    email = models.EmailField(_("External Panelist Email"),  max_length=100, blank=True, null=True)     
    token = models.CharField(_("Access Token"), max_length=100)
    created_at = models.DateTimeField(_("Date Created"), auto_now_add=True)
    reminder_count = models.PositiveIntegerField(_("Reminder Count"), default=0)

    def __str__(self):
        return str(self.application.applicant)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Panelist"
        verbose_name_plural = "Panelist"    

    def save(self, *args, **kwargs):
        if self.token is None or self.token == '':
            self.token = f'{create_random_code()}'
        super(Panelist, self).save(*args, **kwargs)

    def panel_absolute_url(self):
        return reverse('onboarding:scoresheet', kwargs={'reference': self.reference, 'vendor_name':self.application.name})
    
    def ext_panel_absolute_url(self):
        return reverse('onboarding:internal_scoresheet', kwargs={'reference': self.reference, 'vendor_name':self.application.name})

    @property
    def fetch_application(self):
        return self.application



class Grading(models.Model):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SCORE_CHOICES = (
        (ONE, _("1 Mark")),
        (TWO, _("2 Marks")),
        (THREE, _("3 Marks")),
        (FOUR, _("4 Marks")),
        (FIVE, _("5 Marks")),
    )
  
    panelist = models.ForeignKey(
        Panelist, 
        related_name='gradingpanelist',
        on_delete=models.PROTECT
    )
    
    application = models.ForeignKey(
        Application, 
        related_name='gradings',
        on_delete=models.PROTECT
    )
    criteria1 = models.CharField(_("Criteria 1"), max_length=100)
    marks1 = models.PositiveIntegerField(
        _("Marks 1"),
        choices=SCORE_CHOICES, 
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    criteria2 = models.CharField(_("Criteria 2"), max_length=100)
    marks2 = models.PositiveIntegerField(
        _("Marks 2"),
        choices=SCORE_CHOICES, 
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    criteria3 = models.CharField(_("Criteria 3"), max_length=100)
    marks3 = models.PositiveIntegerField(
        _("Marks 3"),
        choices=SCORE_CHOICES, 
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    criteria4 = models.CharField(_("Criteria 4"), max_length=100)
    marks4 = models.PositiveIntegerField(
        _("Marks 4"),
        choices=SCORE_CHOICES, 
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    criteria5 = models.CharField(_("Criteria 5"), max_length=100)
    marks5 = models.PositiveIntegerField(
        _("Marks 5"),
        choices=SCORE_CHOICES, 
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    criteria6 = models.CharField(_("Criteria 6"), max_length=100, default="Criteria 6")
    marks6 = models.PositiveIntegerField(
        _("Marks 6"),
        choices=SCORE_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    created_at = models.DateTimeField(_("Date Created"), auto_now_add=True)
    modified_at = models.DateTimeField(_("Date Modified"), auto_now=True)

    def __str__(self):
        return str(self.panelist.panelist.get_full_name() if self.panelist.panelist else self.panelist.name)

    class Meta:
        ordering = ('id',)
        verbose_name = _("Grading")
        verbose_name_plural = _("Gradings")

    def ranking_percentage(self):
        return f'50%'

    @property
    def total_marks(self):
        grand_total = self.marks1 + self.marks2 + self.marks3 + self.marks4 + self.marks5 + self.marks6
        return grand_total
    
    @property
    def get_ranking(self):
        grand_total = self.total_marks
        
        if grand_total < 20:
            return 'Blacklist'
        if int(20) <= grand_total <= int(22):
            return 'Dissatisfactory'
        if int(23) <= grand_total <= int(24):
            return 'Fairly Satisfactory'
        if int(25) <= grand_total <= int(26):
            return 'Satisfactory'
        if grand_total > int(26):
            return 'Highly Satisfactory'

    @property
    def applicant_final_result(self):
        applicant_score = Grading.objects.filter(application=self.application)
        return sum(score.total_marks for score in applicant_score)     


class BlacklistedVendor(models.Model):
    category = models.ForeignKey(Category, verbose_name=_("Service Category"), related_name="blacklistcategory", on_delete=models.PROTECT, help_text=_("Category of service provided"))
    name = models.CharField(_("Company Short Name"), max_length=100, unique=True)
    registered_name = models.CharField(_("Company Registered Name"), max_length=150)
    email = models.EmailField(_("Business/Support Email"), max_length=100)
    reason = models.TextField(_("BlackList Reason"), max_length=255, blank=True)
    ordering = models.PositiveIntegerField(_("Order Priority"), null=True, blank=True, default=0)
    status = models.BooleanField(_("Status"), choices=((False, 'Dissolved'), (True, 'Contracted')), default=False)
    ticket_response = models.PositiveIntegerField(_("New Ticket Response (Minutes)"), default=15, help_text=_("Counting from the time ticket was created, how long should we wait (in minutes) before sending reminder? E.x: 15 means -> 15 minutes. This works on condition that ticket was not assigned within every 15 minutes"))
    instation_arrival = models.PositiveIntegerField(_("In station Arrival (Hours)"), default=2, help_text=_("SLA Tracking will be invoked when ticket is finally assigned (Goal is to know how long it takes vendor to get to instations in line with SLA)."))
    outstation_arrival = models.PositiveIntegerField(_("Out station Arrival (Hours)"), default=2, help_text=_("SLA Tracking will be invoked when ticket is finally assigned (Goal is to know how long it takes vendor to get to outstations in line with SLA)."))
    working_hours = models.BooleanField(_("Supporting Hours"), choices=((False, 'Every 24/7'), (True, 'Every 8am - 5pm')), default=True, help_text=_("The 'Every 24/7' means ticket will be tracked as and when it is opened. The 'Every 8am - 5pm' means tickets will be tracked from 8am-5pm and deffered to another day if ticket was opened beyond working hours"))
    track_working_time = models.BooleanField(_("Total resolution Hours"), choices=((False, 'No'), (True, 'Yes')), default=True, help_text=_("This feature is the default behaviour of the software. 'Yes' means, it is MANDATORY for Staffs to confirm vendor arrival before work starts. The system will take record of time vendor arrived on site to time ticket was successfully closed"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["ordering"]
        verbose_name = _("Blacklisted Vendor")
        verbose_name_plural = _("Blacklisted Vendors")

    def __str__(self):
        return self.name

