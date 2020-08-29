import os
from hashids import Hashids
import logging

formatter = logging.Formatter(
    '[%(asctime)s][%(levelname)-8s][%(process)d][%(name)32s:%(lineno)4s]: %(message)s',
    '%m-%d %H:%M:%S')

console = logging.StreamHandler()
console.setFormatter(formatter)
console.setLevel(logging.DEBUG)

logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
logger.addHandler(console)

logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)
logging.getLogger('numba').setLevel(logging.ERROR)
try:
    # Capirca uses Google's abseil-py library, which uses a Google-specific
    # wrapper for logging. That wrapper will write a warning to sys.stderr if
    # the Google command-line flags library has not been initialized.
    #
    # https://github.com/abseil/abseil-py/blob/pypi-v0.7.1/absl/logging/__init__.py#L819-L825
    #
    # This is not right behavior for Python code that is invoked outside of a
    # Google-authored main program. Use knowledge of abseil-py to disable that
    # warning; ignore and continue if something goes wrong.
    import absl.logging

    # https://github.com/abseil/abseil-py/issues/99
    logging.root.removeHandler(absl.logging._absl_handler)
    # https://github.com/abseil/abseil-py/issues/102
    absl.logging._warn_preinit_stderr = False
except Exception:
    pass

# Default module stubs
TMP_MODULE_STUB = 'tmp'

# Resource control
MAX_LIMIT = 1000000

# Unicode encoding
UNICODE = 'utf-8'

# Where the data is stored
NORM_HOME = os.environ.get('NORM_HOME', os.path.expanduser('~/.norm'))
DATA_STORAGE_ROOT = os.environ.get('NORM_DATA_STORAGE_ROOT', os.path.join(NORM_HOME, 'data'))
DB_PATH = os.environ.get('NORM_DB_PATH', os.path.join(NORM_HOME, 'db/norm.db'))

# Minimal length of a hash string
HASH_MIN_LENGTH = 10
HASH_SALT = 'be normal'
hasher = Hashids(salt=HASH_SALT, min_length=HASH_MIN_LENGTH)

# Caching size:
MAX_MODULE_CACHE_SIZE = 1000
MAX_LAMBDA_CACHE_SIZE = 1000000

# SQLAlchemy configuration
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

# Dask configuration:
USE_DASK = True
if USE_DASK:
    import dask.dataframe as pdd
    from dask.dataframe import DataFrame
    import pandas as pd
    EMPTY_DATA = pdd.from_pandas(pd.DataFrame(), npartitions=1)
else:
    import pandas as pdd
    from pandas import DataFrame
    EMPTY_DATA = pdd.DataFrame()

MAX_ROWS = 200
