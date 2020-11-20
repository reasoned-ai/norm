import os
from flask_appbuilder.security.manager import (
    AUTH_OID,
    AUTH_REMOTE_USER,
    AUTH_DB,
    AUTH_LDAP,
    AUTH_OAUTH,
)

import logging

# Logging configuration
logging.basicConfig(
    format='[%(asctime)s][%(levelname)-8s][%(process)d][%(name)32s:%(lineno)4s]: %(message)s',
    datefmt='%m-%d %H:%M:%S',
    level=logging.DEBUG
)

logging.getLogger('sqlalchemy').propagate = False
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
except Exception as e:
    pass

# Enables SWAGGER UI for superset openapi spec
# ex: http://localhost:8080/swagger/v1
FAB_API_SWAGGER_UI = True

ENABLE_CORS = True
CORS_OPTIONS = {}

TALISMAN_ENABLED = False
TALISMAN_CONFIG = {}

DEBUG = os.environ.get("FLASK_ENV") == "development"
FLASK_USE_RELOAD = True

SILENCE_FAB = False

BLUEPRINTS = []

# Unicode encoding
UNICODE = 'utf-8'

# Where the data is stored
NORM_HOME = os.environ.get('NORM_HOME', os.path.expanduser('~/.norm'))
DATA_STORAGE_ROOT = os.environ.get('NORM_DATA_STORAGE_ROOT', os.path.join(NORM_HOME, 'data'))
DB_PATH = os.environ.get('NORM_DB_PATH', os.path.join(NORM_HOME, 'db/norm.db'))


# Caching size:
MAX_MODULE_CACHE_SIZE = 1000
MAX_LAMBDA_CACHE_SIZE = 1000000

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

MAX_ROWS = 1000

# App configuration:
basedir = os.path.dirname(__file__)

# Your App secret key
SECRET_KEY = "\2\1thisisnormal\1\2\e\y\y\h"

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
# SQLALCHEMY_DATABASE_URI = 'mysql://myapp@localhost/myapp'
# SQLALCHEMY_DATABASE_URI = 'postgresql://root:password@localhost/myapp'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

# ------------------------------
# GLOBALS FOR APP Builder
# ------------------------------
# Uncomment to setup Your App name
APP_NAME = "Norma"

# Uncomment to setup Setup an App icon
APP_ICON = "/static/images/favicon.ico"

# ----------------------------------------------------
# AUTHENTICATION CONFIG
# ----------------------------------------------------
# The authentication type
# AUTH_OID : Is for OpenID
# AUTH_DB : Is for database (username/password()
# AUTH_LDAP : Is for LDAP
# AUTH_REMOTE_USER : Is for using REMOTE_USER from web server
AUTH_TYPE = AUTH_DB

# Uncomment to setup Full admin role name
AUTH_ROLE_ADMIN = 'Admin'

# Uncomment to setup Public role name, no authentication needed
AUTH_ROLE_PUBLIC = 'Public'

# Will allow user self registration
AUTH_USER_REGISTRATION = True

# The default user self registration role
AUTH_USER_REGISTRATION_ROLE = "Public"

# When using LDAP Auth, setup the ldap server
# AUTH_LDAP_SERVER = "ldap://ldapserver.new"

# Uncomment to setup OpenID providers example for OpenID authentication
# OPENID_PROVIDERS = [
#    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
#    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
#    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
#    { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]
# ---------------------------------------------------
# Babel config for translations
# ---------------------------------------------------
# Setup default language
BABEL_DEFAULT_LOCALE = "en"
# Your application default translation path
BABEL_DEFAULT_FOLDER = "translations"
# The allowed translation for you app
LANGUAGES = {
    "en": {"flag": "us", "name": "English"},
    "pt": {"flag": "pt", "name": "Portuguese"},
    "pt_BR": {"flag": "br", "name": "Pt Brazil"},
    "es": {"flag": "es", "name": "Spanish"},
    "de": {"flag": "de", "name": "German"},
    "zh": {"flag": "cn", "name": "Chinese"},
    "ru": {"flag": "ru", "name": "Russian"},
    "pl": {"flag": "pl", "name": "Polish"},
}
# ---------------------------------------------------
# Image and file configuration
# ---------------------------------------------------
# The file upload folder, when using models with files
UPLOAD_FOLDER = basedir + "/static/uploads/"

# The image upload folder, when using models with images
IMG_UPLOAD_FOLDER = basedir + "/static/uploads/"

# The image upload url, when using models with images
IMG_UPLOAD_URL = basedir + "/static/uploads/"
# Setup image size default is (300, 200, True)
IMG_SIZE = (300, 200, True)

# Theme configuration
# these are located on static/appbuilder/css/themes
# you can create your own and easily use them placing them on the same dir structure to override
# APP_THEME = "bootstrap-theme.css"  # default bootstrap
# APP_THEME = "cerulean.css"
# APP_THEME = "cosmo.css"
# APP_THEME = "cyborg.css"
# APP_THEME = "flatly.css"
# APP_THEME = "journal.css"
# APP_THEME = "simplex.css"
# APP_THEME = "slate.css"
# APP_THEME = "spacelab.css"
APP_THEME = "united.css"
# APP_THEME = "yeti.css"

