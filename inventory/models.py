from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError


class InventoryRequest(models.Model):
    # Status
    REVIEW = 'review'
    ISSUED = 'issued'
    CLOSED = 'closed'
    STATUS_CHOICES = (
        (REVIEW, _('Review')),
        (ISSUED, _('Issued')),
        (CLOSED, _('Closed')),
    )
    # Condition
    GOOD_CONDITION = 'good_condition'
    PARTLY_DAMAGED = 'partly_damaged'
    TOTALLY_DAMAGED = 'damaged'
    CONDITION_CHOICES = (
        (GOOD_CONDITION, _('Good Condition')),
        (PARTLY_DAMAGED, _('Partly Damaged')),
        (TOTALLY_DAMAGED, _('Damaged')),
    )
    request_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Issuer"), related_name="request_by", on_delete=models.CASCADE)
    request_branch = models.ForeignKey('general_settings.Branch', verbose_name=_("Request Branch"), related_name="requestbranch", on_delete=models.CASCADE)    
    category = models.ForeignKey('general_settings.Inventory', verbose_name=_("Category"), related_name="inventories", on_delete=models.CASCADE)
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default=REVIEW)
    condition = models.CharField(_("Condition"), max_length=30, choices=CONDITION_CHOICES, default=GOOD_CONDITION)
    
    line_one = models.CharField(_('Item name'), max_length=120)
    line_one_order = models.PositiveIntegerField(_('Quantity'), default=0)
    line_one_issue = models.PositiveIntegerField(_('Issue Qty'), default=0)
    slug = models.SlugField(max_length=120)

    line_two = models.CharField('Extra Item One', max_length=120, blank=True, null=True)
    line_two_order = models.PositiveIntegerField(_('Req Qty'), default=0)
    line_two_issue = models.PositiveIntegerField(_('Issue Qty 1'), default=0)
    
    line_three = models.CharField('Extra Item Two', max_length=120, blank=True, null=True)
    line_three_order = models.PositiveIntegerField(_('Req Qty'), default=0)
    line_three_issue = models.PositiveIntegerField(_('Issue Qty 2'), default=0)
    
    line_four = models.CharField('Extra Item three', max_length=120, blank=True, null=True)
    line_four_order = models.PositiveIntegerField(_('Req Qty'), default=0)
    line_four_issue = models.PositiveIntegerField(_('Issue Qty 3'), default=0)
    
    issue_branch = models.ForeignKey('general_settings.Branch', verbose_name=_("Issue Branch"), related_name="issuebranch", blank=True, null=True, on_delete=models.SET_NULL)
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Issuer"), related_name="issued_by", blank=True, null=True, on_delete=models.SET_NULL)
    request_message = models.TextField(_("Request Comment"), blank=True, null=True)
    issue_remark = models.TextField(_("Issue Remarks"), blank=True, null=True)
    reference = models.CharField(_("System Trace Audit No."), unique=True, blank=True, max_length=100)
    request_at = models.DateTimeField(_("Request Time"), auto_now_add=True)
    issue_at = models.DateTimeField(_("Issue Time"), blank=True, null=True)
    receive_at = models.DateTimeField(_("Receipt Time"), blank=True, null=True)

    class Meta:
        ordering = ['-request_at']
        verbose_name = _("All requests")
        verbose_name_plural = _("All requests")

    def __str__(self):
        return f'{self.line_one}'

    def save(self, *args, **kwargs):
        self.slug= slugify(self.line_one)    
        super(InventoryRequest, self).save(*args, **kwargs)

    
    def clean(self):
        if self.line_one_issue is not None and self.line_one_issue > self.line_one_order:
            raise ValidationError(
                {'line_one_issue': _('Issue Qty must be less or equal to proposed Qty')})
        
        if self.line_two_issue is not None and self.line_two_issue > self.line_two_order:
            raise ValidationError(
                {'line_two_issue': _('Issue Qty must be less or equal to proposed Qty')})
        
        if self.line_three_issue is not None and self.line_three_issue > self.line_three_order:
            raise ValidationError(
                {'line_two_issue': _('Issue Qty must be less or equal to proposed Qty')})
        
        if self.line_four_issue is not None and self.line_four_issue > self.line_three_order:
            raise ValidationError(
                {'line_two_issue': _('Issue Qty must be less or equal to proposed Qty')})
                
        return super().clean()


class RequisitionReview(InventoryRequest):
    class Meta:
        proxy=True
        verbose_name = _("Pending Requests")
        verbose_name_plural = _("Pending Requests")


class RequisitionIssued(InventoryRequest):
    class Meta:
        proxy=True
        verbose_name = _("Issued Requests")
        verbose_name_plural = _("Issued Requests")  


class RequisitionClosed(InventoryRequest):
    class Meta:
        proxy=True
        verbose_name = _("Closed Requests")
        verbose_name_plural = _("Closed Requests")  

 