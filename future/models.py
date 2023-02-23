from django.db import models
from django.utils.translation import gettext_lazy as _


class Authenticator(models.Model):
	preview = models.CharField(max_length=100, default='Control access with token and vendor permission', blank=True)
	token_authenticator = models.BooleanField(_("2FA Mailer"), 
    	choices = ((False,'Disabled'), (True, 'Launched')), 
    	default=False,
    	help_text=(_("By default, all users(excluding Staff) will be able to login to dashoard using EMAIL and PASSWORD. This plugin will (1) Present extra Token form after login, (2) Send simple mail alert containingg token, (3) button to resend token if customer has not received, (4) Then a valid token entered will log user to dashboard")), 
    )

	vendor_role = models.BooleanField(_("Vendor Team Upgrade"), 
    	choices = ((False,'Disabled'), (True, 'Activated')),
    	help_text=(_("By default, only administrator can create vendor with full permission. This feature gives moderating vendor the right to upgrade or downgrade other team members")),  
    	default=True, 
    )

	class Meta:
		verbose_name = _("Authenticator Plugin")
		verbose_name_plural = _("Authenticator Plugins")

	def __str__(self):
		return self.preview


class Notifier(models.Model):
	preview = models.CharField(
		max_length=100, 
		default='Allow or disable email alerts by notification centers', 
	)
	mailing_group = models.BooleanField(_("Mailing Group Alert"), 
    	choices = ((False,'Alert Cluster by Branch'), (True, 'Alert all Cluster Group')), 
    	default=True,
    	help_text=(_("This plugin determines whether cluster should be copied in mail for only their 'managed branches' or in 'all branches' alerts")), 
    )
	open_ticket = models.BooleanField(_("Open Ticket Alert"), 
    	choices = ((False,'Disabled'), (True, 'Launched')), 
    	default=True,
    	help_text=(_("This will enable or disable the notifications when ticket is CREATED")), 
    )
	assign_ticket = models.BooleanField(_("Assign Ticket Alert"), 
    	choices = ((False,'Disabled'), (True, 'Launched')), 
    	default=True,
    	help_text=(_("This will enable or disable the notifications when ticket is ASSIGNED")), 
    )
	started_ticket = models.BooleanField(_("Ongoing Ticket Alert"), 
    	choices = ((False,'Disabled'), (True, 'Launched')), 
    	default=False,
    	help_text=(_("This will enable or disable the notifications when ticket is STARTED/ONGOING")), 
    )
	deferred_ticket = models.BooleanField(_("Paused Ticket Alert"), 
    	choices = ((False,'Disabled'), (True, 'Launched')), 
    	default=False,
    	help_text=(_("This will enable or disable the notifications when ticket is PAUSED, excluding actions performed by system")), 
    )
	reopen_ticket = models.BooleanField(_("Reopen Ticket Alert"), 
    	choices = ((False,'Disabled'), (True, 'Launched')), 
    	default=False,
    	help_text=(_("This will enable or disable the notifications when ticket is REOPEN, excluding actions performed by system")), 
    )
	closed_ticket = models.BooleanField(_("Closed Ticket Alert"), 
    	choices = ((False,'Disabled'), (True, 'Launched')), 
    	default=True,
    	help_text=(_("This will enable or disable the notifications when ticket is CLOSED")), 
    )
	remarks = models.BooleanField(_("Ticket Remark Alert"), 
    	choices = ((False,'Disabled'), (True, 'Launched')), 
    	default=True,
    	help_text=(_("This will enable or disable the notifications when ticket REMARK is submitted by vendor")), 
    )
	# COMPLAINTS
	complaint_created = models.BooleanField(_("New Branch Complaint Alert"), 
    	choices = ((False,'Disabled'), (True, 'Launched')), 
    	default=True,
    	help_text=(_("This will enable or disable the notifications when COMPLAINT is submitted")), 
    )
	complaint_routing = models.BooleanField(_("Complaint Re-Routing Alert"), 
    	choices = ((False,'Disabled'), (True, 'Launched')), 
    	default=True,
    	help_text=(_("This will enable or disable the notifications when COMPLAINT is re-routed")), 
    )
	complaint_reply = models.BooleanField(_("Complaint Reply Alert"), 
    	choices = ((False,'Disabled'), (True, 'Launched')), 
    	default=True,
    	help_text=(_("This will enable or disable the notifications when COMPLAINT is replied")), 
    )
	# REQUISITION
	requisition_created = models.BooleanField(_("New Requisition Alert"), 
    	choices = ((False,'Disabled'), (True, 'Launched')), 
    	default=True,
    	help_text=(_("This will enable or disable the notifications when REQUISITION is CREATED")), 
    )

	class Meta:
		verbose_name = _("Notifier Plugin")
		verbose_name_plural = _("Notifier Plugins")

	def __str__(self):
		return self.preview