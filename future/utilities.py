from future.models import Authenticator, Notifier

# AUTHENTICATOR FEATURE     
def get_token_feature():
    return Authenticator.objects.get_or_create(pk=1)[0].token_authenticator

def get_vendor_role_feature():
    return Authenticator.objects.get_or_create(pk=1)[0].vendor_role

# NOTIFIER FEATURE
def get_mailing_group_feature():
    return Notifier.objects.get_or_create(pk=1)[0].mailing_group

def get_open_ticket_feature():
    return Notifier.objects.get_or_create(pk=1)[0].open_ticket

def get_assign_ticket_feature():
    return Notifier.objects.get_or_create(pk=1)[0].assign_ticket

def get_started_ticket_feature():
    return Notifier.objects.get_or_create(pk=1)[0].started_ticket

def get_deferred_ticket_feature():
    return Notifier.objects.get_or_create(pk=1)[0].deferred_ticket

def get_reopen_ticket_feature():
    return Notifier.objects.get_or_create(pk=1)[0].reopen_ticket

def get_closed_ticket_feature():
    return Notifier.objects.get_or_create(pk=1)[0].closed_ticket

def get_remarks_feature():
    return Notifier.objects.get_or_create(pk=1)[0].remarks

# COMPLAINT FEATURE
def get_complaint_created_feature():
    return Notifier.objects.get_or_create(pk=1)[0].complaint_created

def get_complaint_routing_feature():
    return Notifier.objects.get_or_create(pk=1)[0].complaint_routing

def get_complaint_reply_feature():
    return Notifier.objects.get_or_create(pk=1)[0].complaint_reply

# REQUISITION FEATURE
def get_requisition_created_feature():
    return Notifier.objects.get_or_create(pk=1)[0].requisition_created

def get_requisition_dispatched_feature():
    return Notifier.objects.get_or_create(pk=1)[0].requisition_dispatched

def get_requisition_confirm_feature():
    return Notifier.objects.get_or_create(pk=1)[0].requisition_confirm






