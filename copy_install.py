from django.core.management import call_command
from django.core.management.base import BaseCommand
from account.models import  Customer, TwoFactorAuth
from general_settings.models import  VendorCompany, Branch, Terminals
from vendors.models import Team, Vendor
from custodians.models import Custodian
from django.utils.text import slugify
from constants import (BRANCH_PK, TERMINAL_NAMES)



class Command(BaseCommand):
    help = "this creates default values via commands for the entire system"

    def handle(self, *args, **kwargs):
        call_command("makemigrations")
        call_command("migrate")
        
        # INITIAL DATABASE POPULATOR STARTS
        VendorCompany.objects.all().delete()
        Customer.objects.all().delete()
        TwoFactorAuth.objects.all().delete()
        Team.objects.all().delete()
        Vendor.objects.all().delete()
        Terminals.objects.all().delete()
        Branch.objects.all().delete()

        TEAM_PK = [1, 2, 3, 4]
        VENDOR_COMPANY = ['Inlaks Limited', 'Addtech Engineering', 'Ncr Technology', 'Holy Explosives']
        vendor_company = [VendorCompany(pk=pk, name=vendor_name) for pk, vendor_name in zip(TEAM_PK, VENDOR_COMPANY)]
        VendorCompany.objects.bulk_create(vendor_company)
        VENDOR_COMPANY = VendorCompany.objects.all()

        if not Customer.objects.count():
            call_command("loaddata", "db_authuser.json")

        for vendor in Customer.objects.filter(user_type='vendor'):
            team = Team.objects.create(
                title = vendor.vendor_company.name,
                slug = slugify(vendor.vendor_company.name),
                created_by = vendor,
            )
            team.members.add(vendor)
            Vendor.objects.create(
                user = vendor,
                active_team_id = team.id,
            )

        for custodian in Customer.objects.all().exclude(user_type='vendor'):
            Custodian.objects.create(user = custodian)

        branches = [Branch(pk=branch_pk, name=branch_name) for branch_pk, branch_name in zip(BRANCH_PK, TERMINAL_NAMES)]
        Branch.objects.bulk_create(branches)
        #BRANCHES = Branch.objects.all() -- Not needed if we create terminals using fixtures

        if not Terminals.objects.count():
            call_command("loaddata", "db_terminals.json")

 