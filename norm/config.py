import os
from hashids import Hashids
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool

# Default module stubs
TMP_MODULE_STUB = 'norm.tmp'

# Resource control
MAX_LIMIT = 1000000

# Unicode encoding
UNICODE = 'utf-8'

# Where the data is stored
NORM_HOME = os.environ.get('NORM_HOME', os.path.expanduser('~/.norm'))
DATA_STORAGE_ROOT = os.environ.get('NORM_DATA_STORAGE_ROOT', os.path.join(NORM_HOME, 'data'))
DB_PATH = os.environ.get('NORM_DB_PATH', os.path.join(NORM_HOME, 'db/norm.db'))

# Create database session
engine = create_engine('sqlite:///{}'.format(DB_PATH), poolclass=StaticPool)
Session = scoped_session(sessionmaker(bind=engine))

# Minimal length of a hash string
HASH_MIN_LENGTH = 10
HASH_SALT = 'be normal'
hasher = Hashids(salt=HASH_SALT, min_length=HASH_MIN_LENGTH)

# Caching size:
MAX_MODULE_CACHE_SIZE = 1000
MAX_LAMBDA_CACHE_SIZE = 1000000
