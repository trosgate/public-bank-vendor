from constants import (
    BRANCH_PK, TERMINALS, TERMINAL_NAMES, TERMINAL_DESCRIPTION, 
    TERMINAL_REGION, GPS_ADDRESS, TERMINAL_TYPE, CATEGORY
)
from general_settings.models import Branch, Terminals


Branch.objects.all().delete()

branches = [Branch(pk=branch_pk, name=branch_name) for branch_pk, branch_name in zip(BRANCH_PK, TERMINAL_NAMES)]
Branch.objects.bulk_create(branches)
BRANCHES = Branch.objects.all()

terminals = [
    Terminals(
        name=terminal_name, terminal=terminals,description=descriptions,
        gps_address=gps_addresss,region=regions,category=categorys,
        type=atm_types, branch=new_branchs#, vendor=vendors
    ) for (
        terminal_name, terminals, descriptions, gps_addresss, 
        regions, categorys, atm_types, new_branchs#, vendors
        ) in zip(
        TERMINAL_NAMES, TERMINALS, TERMINAL_DESCRIPTION,GPS_ADDRESS, 
        TERMINAL_REGION, CATEGORY, TERMINAL_TYPE, BRANCHES, #VENDOR_COMPANY
    )
]
Terminals.objects.bulk_create(terminals)