from norm.models import Register
from norm.models.license import register_licenses
import logging
logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    print('Registering in-place Lambdas.')
    register_licenses()
    Register.register()
