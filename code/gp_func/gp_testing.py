from gp_func.gp import Gp

if __name__ == '__main__':
    user = Gp(1)

    user.print_welcome()

print(user.state)

user.main_options()

# user.to_confirm_appts()

print(user.state)