from norm.models import Register
import norm.config
import logging
logger = logging.getLogger('update norm')

if __name__ == '__main__':
    logger.info('Update Norm store')
    from norm.models import storage, native, core
    Register.register()
