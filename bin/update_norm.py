from norm.models import Register
from norm.root import db
import logging
logger = logging.getLogger('update norm')

if __name__ == '__main__':
    logger.info('Update Norm store')
    from norm.models import storage, native, core
    Register.register()
