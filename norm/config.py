from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Default namespace stubs
CONTEXT_NAMESPACE_STUB = 'norm.tmp'
USER_NAMESPACE_STUB = 'norm.user'

# Resource control
MAX_LIMIT = 1000000

# Unicode encoding
UNICODE = 'utf-8'

# Version minimal length
VERSION_MIN_LENGTH = 6

# Where the data is stored, e.g., s3://datalake, gs://datalake
NORM_HOME = os.environ.get('NORM_HOME', '~/.norm')
DATA_STORAGE_ROOT = os.environ.get('NORM_DATA_STORAGE_ROOT', os.path.join(NORM_HOME, 'data'))
DB_PATH = os.environ.get('NORM_DB_PATH', os.path.join(NORM_HOME, 'db/norm.db'))

# Default user name
PUBLIC_USER = dict(first_name='norm',
                   last_name='ai',
                   username='norm',
                   email='norm@reasoned.ai')

# Create database session
try:
    engine = create_engine('sqlite:///{}'.format(DB_PATH))
    Session = sessionmaker(bind=engine)
    session = Session()
except:
    engine = None
    session = None

# Set the context id
context_id = str(datetime.utcnow().strftime('%m%d%Y.%H%M%S'))



