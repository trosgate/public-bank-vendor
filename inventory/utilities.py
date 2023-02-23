
def l1_variance(inventory):
    line_one_var = 0
    if inventory.line_one_order > inventory.line_one_issue:
        line_one_var = inventory.line_one_order - inventory.line_one_issue
    return line_one_var

def l2_variance(inventory):
    line_two_var = 0
    if inventory.line_two_order > inventory.line_two_issue:
        line_two_var = inventory.line_two_order - inventory.line_two_issue
    return line_two_var

def l3_variance(inventory):
    line_three_var = 0
    if inventory.line_three_order > inventory.line_three_issue:
        line_three_var = inventory.line_three_order - inventory.line_three_issue
    return line_three_var

def l4_variance(inventory):
    line_four_var = 0
    if inventory.line_four_order > inventory.line_four_issue:
        line_four_var = inventory.line_four_order - inventory.line_four_issue
    return line_four_var

