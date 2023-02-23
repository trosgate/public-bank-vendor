from django.core.management import call_command
from django.core.management.base import BaseCommand
from account.models import Customer, TwoFactorAuth
from future.models import Authenticator, Notifier
from general_settings.models import (
    VendorCompany, 
    Branch, 
    Terminals,
    Category,
    SupportProduct,
    Inventory,
    Branch,
    MailingGroup,
    Checklist,
    Terminals,
    Mailer,
    TestMailSetting,
    SLAExceptions,
    WebsiteSetting,
)

class Command(BaseCommand):
    help = "this creates default values via commands for the entire system"

    def handle(self, *args, **kwargs):
        call_command("makemigrations")
        call_command("migrate")

        # INITIAL DATABASE POPULATOR STARTS
        WebsiteSetting.objects.all().delete()
        Category.objects.all().delete()
        SupportProduct.objects.all().delete()
        Branch.objects.all().delete()
        VendorCompany.objects.all().delete()
        Terminals.objects.all().delete()
        Inventory.objects.all().delete()
        MailingGroup.objects.all().delete()
        Checklist.objects.all().delete()
        Mailer.objects.all().delete()
        TestMailSetting.objects.all().delete()
        SLAExceptions.objects.all().delete()
        Notifier.objects.all().delete()
        Authenticator.objects.all().delete()
        Customer.objects.all().delete()
        TwoFactorAuth.objects.all().delete()

        if not WebsiteSetting.objects.count():
            call_command("loaddata", "db_settings.json")
        if not Category.objects.count():
            call_command("loaddata", "db_categories.json")            
        if not SupportProduct.objects.count():
            call_command("loaddata", "db_product_categories.json")            
        if not Branch.objects.count():
            call_command("loaddata", "db_branches.json")
        if not VendorCompany.objects.count():
            call_command("loaddata", "db_vendors.json")
        if not Terminals.objects.count():
            call_command("loaddata", "db_terminals.json")
        if not Inventory.objects.count():
            call_command("loaddata", "db_inventory.json")
        if not MailingGroup.objects.count():
            call_command("loaddata", "db_mailgroup.json")
        if not Checklist.objects.count():
            call_command("loaddata", "db_checklist.json")
        if not Mailer.objects.count():
            call_command("loaddata", "db_mailer.json")
        if not TestMailSetting.objects.count():
            call_command("loaddata", "db_testmail.json")
        if not SLAExceptions.objects.count():
            call_command("loaddata", "db_slaexception.json")
        if not Authenticator.objects.count():
            call_command("loaddata", "db_auth_plugin.json")
        if not Notifier.objects.count():
            call_command("loaddata", "db_notifier_plugin.json")
        if not Customer.objects.count():
            call_command("loaddata", "db_authuser.json")
