import random

#Helper functions for generating 2FA Code
def auth_code():
    number_list = [x for x in range(10)]
    code_list = []

    for i in range(6):
        number = random.choice(number_list)
        code_list.append(number)
    passcode = "".join(str(code) for code in code_list)

    return passcode


#

















