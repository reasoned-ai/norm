# Default namespace stubs
CONTEXT_NAMESPACE_STUB = 'norm.tmp'
USER_NAMESPACE_STUB = 'norm.user'

# Resource control
MAX_LIMIT = 1000000

# Unicode encoding
UNICODE = 'utf-8'

# Where the data is stored, e.g., s3://datalake
DATA_STORAGE_ROOT = 'data'

# Security of the data storage

# SQLAlchemy hooks
db = None      # type: flask_sqlalchmey.db
Model = None   # type: flask_sqlalchemy.Model
user_model = None
cache = None  # type: norm.cache.SimpleCache

