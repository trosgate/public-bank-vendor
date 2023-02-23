from django.db import models, transaction as db_transaction
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField
from account.exception import TicketException
from datetime import timedelta
from django.utils import timezone
from general_settings.models import SLAExceptions
from .tasks import ticket_assign_alert, ticket_deferred_alert, ticket_opened_alert
from future.utilities import get_assign_ticket_feature, get_deferred_ticket_feature, get_open_ticket_feature    
from .utilities import get_mailing_group, get_mailing_group_with_branch
from general_settings.utilities import get_creation_time, get_assign_time, get_arrival_time
from django.template.defaultfilters import slugify


class Ticket(models.Model):
    # Status
    UNASSIGNED = 'unassigned'
    ASSIGNED = 'assigned'
    STARTED = 'started'
    CLOSED = 'closed'
    DIFFER = 'deffered'
    REOPEN = 'reopen'
    STATUS = (
        (UNASSIGNED, 'Not Assigned'),
        (ASSIGNED, 'Job Assigned'),
        (STARTED, 'Job Started'),
        (CLOSED,'Job closed'),
        (DIFFER, 'Job Deffered'),
        (REOPEN, 'Job Reopen')
    )

    title = models.CharField(_("Title"), max_length=100, help_text=_("title field is Required"))
    slug = models.SlugField(_("Slug"), max_length=100)
    description = RichTextField(verbose_name=_("Description"), max_length=3500, error_messages={"name": {"max_length": _("Description field is required")}},)
    reference = models.CharField(_("Ticket #"), unique=True, blank=True, max_length=100)
    status = models.CharField(_("Status"), max_length=20, choices=STATUS, default=UNASSIGNED)
    category = models.ForeignKey('general_settings.Category', verbose_name=_("Category"), related_name="ticketcategory", on_delete=models.PROTECT)
    branch = models.ForeignKey('general_settings.Branch', verbose_name=_("Branch"), related_name="ticketbranch", on_delete=models.PROTECT)
    terminal = models.ForeignKey('general_settings.Terminals', verbose_name=_("Terminal"), related_name="ticketterminal", on_delete=models.PROTECT)
    team = models.ForeignKey('vendors.Team', verbose_name=_("Team"), related_name="ticketteam", on_delete=models.PROTECT, help_text=_("Team responsible for this task"))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Staff"), related_name="ticketcreator", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(_("Creation Time"), auto_now_add=True)
    created_at = models.DateTimeField(_("Scheduled Time"), auto_now_add=False, auto_now=False, blank=True, null=True, help_text=_("This is the Creation time used for ticket creation, assignment, reporting and insight INTO THE FUTURE based on '8am-5pm' or '24/7' vendor configuration"))
    modified_at = models.DateTimeField(_("Time Modified"), auto_now=True)
    arrival_time = models.DateTimeField(_("First Time Vendor Arrival"), auto_now_add=False, auto_now=False, blank=True, null=True)
    remarks = models.TextField(verbose_name=_("Recommendation"), max_length=3500, blank=True, null=True)
    remarks_date = models.DateTimeField(_("Recommend Time"), auto_now_add=False, auto_now=False, blank=True, null=True)
    sla_exception = models.ManyToManyField(
        "general_settings.SLAExceptions", 
        verbose_name=_("SLA Exception"), 
        related_name="slaexceptions"
    )
    paused_by_system = models.BooleanField(_("System Paused"), default=False)    
    checklist = models.ManyToManyField(
        "general_settings.Checklist", 
        verbose_name=_("Checklist"), 
        related_name="checklists"
    )

    class Meta:
        ordering = ['-id']
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")

    def __str__(self):
        return f'{self.title}'


    @classmethod
    def create(cls, created_by, title, category, branch, terminal, description, team):
        with db_transaction.atomic():
            if created_by is None:
                raise TicketException(_("Unknown user error"))
            if category is None:
                raise TicketException(_("Category not found Error"))
            if branch is None:
                raise TicketException(_("Branch not found error"))
            if terminal is None:
                raise TicketException(_("Terminal not profiled error"))
            if team is None:
                raise TicketException(_("Vendor team error"))
            if not title:
                raise TicketException(_("Error! Title required"))
            if not description:
                raise TicketException(_("Error! Description required"))

            ticket = Ticket.objects.create(
                created_by=created_by,
                title=title, 
                category=category, 
                branch=branch,
                terminal=terminal,
                description=description, 
                team=team
            )
            ticket.created_at = get_creation_time(ticket, ticket.terminal.vendor)
            stan = f'{ticket.pk}'.zfill(4)
            ticket_user = f'{ticket.created_by.pk}'
            ticket.reference = f'TK{ticket_user}{stan}'
            ticket.slug=slugify(ticket.title) 
            ticket.save()

            mailgroup = get_mailing_group_with_branch(ticket.created_by.branch)
            if get_open_ticket_feature():
                try:                
                    db_transaction.on_commit(lambda: ticket_opened_alert.delay(ticket.pk, mailgroup))
                except Exception as e:
                    print(str(e))
        return ticket


    @classmethod
    def assign_and_predict(cls, ticket_pk, assign_pk):
        with db_transaction.atomic():
            if ticket_pk is None:
                raise TicketException(_("Error! Please try again"))
            
            if assign_pk is None:
                raise TicketException(_("Error! Please try again"))

            ticket = cls.objects.select_for_update().get(pk=ticket_pk)
            if ticket.status != 'unassigned':
                raise Exception(_("The ticket is already assigned"))
            
            if ticket.created_at > timezone.now():
                raise TicketException(_("Error! assign time must be ahead of creation time"))
            
            ticket.status = 'assigned'
            ticket.arrival_time = get_assign_time(ticket, ticket.terminal.vendor)
            ticket.save()
            
            assign = AssignMember.objects.select_for_update().filter(pk=assign_pk, ticket=ticket).first()
            assign.created_at = get_assign_time(ticket, ticket.terminal.vendor)
            assign.arrival_time = get_assign_time(ticket, ticket.terminal.vendor) + get_arrival_time(ticket, ticket.terminal.vendor)
            assign.save()
          
            # if ticket.terminal.branch.location == 'instation':
            #     assign.created_at = timezone.now()
            #     assign.arrival_time = timezone.now() + timedelta(hours = assign.vendor.instation_arrival)
            #     assign.save()

            # if ticket.terminal.branch.location == 'outstation':
            #     assign.created_at = timezone.now()
            #     assign.arrival_time = timezone.now() + timedelta(hours = assign.vendor.outstation_arrival)
            #     assign.save()

            mailgroup = get_mailing_group_with_branch(ticket.branch)
            if get_assign_ticket_feature():
                db_transaction.on_commit(lambda: ticket_assign_alert.delay(assign.pk, mailgroup))

        return ticket, assign


    @classmethod
    def defer_ticket(cls, ticket_pk, assign_pk, exception_pk):
        with db_transaction.atomic():
            if ticket_pk is None:
                raise TicketException(_("Error! Please try again"))
            
            if assign_pk is None:
                raise TicketException(_("Error! Please try again"))

            sla_factor = SLAExceptions.objects.select_for_update().get(pk=exception_pk)            
            ticket = cls.objects.select_for_update().get(pk=ticket_pk)            
            ticket.status = 'deffered'
            ticket.save()

            if sla_factor in ticket.sla_exception.all():
                print('already exist')
            else:
                ticket.sla_exception.add(sla_factor)

            assign = AssignMember.objects.select_for_update().get(pk=assign_pk, ticket=ticket)
            time_worked = timezone.now() - assign.arrival_confirm
            minutes = (time_worked.seconds/60)
            assign.completion_time = None            
            assign.total_minutes += minutes
            assign.deffered_count += 1
            assign.save(update_fields=['deffered_count', 'total_minutes', 'completion_time'])
            
            mailgroup = get_mailing_group(ticket.branch)
            if get_deferred_ticket_feature():
                db_transaction.on_commit(lambda: ticket_deferred_alert.delay(ticket.pk, mailgroup))

        return ticket, assign


    @property
    def completion(self):
        for time in self.assignticket.filter(ticket__status='closed'):
            return time.completion_time
        return timezone.now()


    @property
    def recommender(self):
        for engineer in self.assignticket.filter(ticket__status='closed'):
            return engineer.assignee.get_full_name
        return '-'

    @property
    def engineer(self):
        return self.assignticket.all()


class AssignMember(models.Model):
    vendor = models.ForeignKey('general_settings.VendorCompany', verbose_name=_("Vendor"), related_name="ticketterminal", on_delete=models.CASCADE)
    team = models.ForeignKey("vendors.Team", verbose_name=_("Team"), related_name='assignteam', on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket,  verbose_name=_("Ticket"), related_name="assignticket", on_delete=models.CASCADE)
    assignor = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Assignor"), related_name="assignors", on_delete=models.CASCADE)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Team Member"), related_name='assignees', on_delete=models.CASCADE)
    created_at = models.DateTimeField(_("Assign On"), auto_now_add=False, auto_now=False, blank=True, null=True)
    arrival_time = models.DateTimeField(_("Journey Starts"), auto_now_add=False, auto_now=False, blank=True, null=True)
    arrival_confirm = models.DateTimeField(_("Confirmed Arrival"), auto_now_add=False, auto_now=False, blank=True, null=True)
    completion_time = models.DateTimeField(_("Closure Time"), auto_now_add=False, auto_now=False, blank=True, null=True)    
    total_minutes = models.PositiveIntegerField(_("Total Minutes worked"), default=0)
    deffered_count = models.PositiveIntegerField(_("Deffered Count"), default=0)

    class Meta:
        ordering = ('-pk',)
        verbose_name = _("Assign Ticket")
        verbose_name_plural = _("Assign Tickets")


    def __str__(self):
        return f'{self.assignor.short_name} assign to {self.assignee.short_name}'

    @property
    def get_time_differences(self):
        arrival_time = self.ticket.arrival_time
        created_time = self.ticket.created_at
        assign_variance = round((((arrival_time - created_time)/60).seconds))
        return assign_variance

    def working_time(self):
        return round(self.total_minutes)

    def tracking_time(self, team):
        assigned = AssignMember.objects.filter(team=team)
        return sum(tracker.total_minutes for tracker in assigned)


