from norm.models import Register
from norm.models.license import register_licenses


if __name__ == '__main__':
    print('Registering in-place Lambdas')
    Register.register()
    register_licenses()
