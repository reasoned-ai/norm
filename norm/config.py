from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

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
DATA_STORAGE_ROOT = 'data'
DB_PATH = 'norm/db/norm.db'

# Default user name
PUBLIC_USER = dict(first_name='norm',
                   last_name='ai',
                   username='norm',
                   email='norm@reasoned.ai')

# Create database session
engine = create_engine('sqlite:///{}'.format(DB_PATH))
Session = sessionmaker(bind=engine)
session = Session()

# Set the context id
context_id = str(uuid.uuid4())



