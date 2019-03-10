from flask import g
import logging
logger = logging.getLogger(__name__)

# TODO: this unprotected context is currently for testing purpose
_user = None


def current_user():
    try:
        return _user or g.user
    except Exception:
        return None


def set_current_user(user):
    # TODO: figuring out how to set flask for testing
    global _user
    _user = user
