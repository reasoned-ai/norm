import os
import pandas as pd
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

# Pandas display options
pd.options.display.width = 400
pd.options.display.max_columns = 100

# Minimal length of a hash string
HASH_MIN_LENGTH = 10

# Caching size:
MAX_MODULE_CACHE_SIZE = 1000
MAX_LAMBDA_CACHE_SIZE = 1000000
