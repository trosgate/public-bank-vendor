from general_settings.models import MailingGroup
from future.utilities import get_mailing_group_feature
from account.models import Customer


def get_mailing_group(branch):

    if get_mailing_group_feature():
        mailgroup = MailingGroup.objects.all().distinct()
        cluster = [f'{myname.name}<{mail.email}>' for myname, mail in zip(mailgroup, mailgroup)]
        return cluster
    else:
        mailgroup = MailingGroup.objects.filter(branch=branch).distinct()
        cluster = [f'{myname.name}<{mail.email}>' for myname, mail in zip(mailgroup, mailgroup)]
        return cluster


def get_mailing_group_with_branch(branch):
    customer = Customer.objects.filter(branch=branch).distinct()
    branch_list = [f'{name.get_full_name()}<{mail.email}>' for name, mail in zip(customer, customer)]  

    if get_mailing_group_feature():
        mailgroup = MailingGroup.objects.all().distinct()
        cluster = [f'{myname.name}<{mail.email}>' for myname, mail in zip(mailgroup, mailgroup)]
        cluster.extend(branch_list)
        return cluster
    else:
        mailgroup = MailingGroup.objects.filter(branch=branch).distinct()
        cluster = [f'{myname.name}<{mail.email}>' for myname, mail in zip(mailgroup, mailgroup)]
        cluster.extend(branch_list)
        return cluster
