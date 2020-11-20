from dash import Dash
import functools
from flask import current_app, flash, jsonify, make_response, redirect, request, url_for, render_template
from flask_jwt_extended import current_user as current_user_jwt
from flask_login import current_user
from flask_appbuilder._compat import as_unicode
from flask_appbuilder.const import (
    FLAMSG_ERR_SEC_ACCESS_DENIED,
    LOGMSG_ERR_SEC_ACCESS_DENIED,
    PERMISSION_PREFIX,
)
import logging
logger = logging.getLogger('norm.secured.dash')


def has_authenticated(f):
    def wraps(self, *args, **kwargs):
        if current_user.is_authenticated or current_user_jwt:
            return f(self, *args, **kwargs)
        else:
            flash(as_unicode(FLAMSG_ERR_SEC_ACCESS_DENIED), "danger")
        return redirect(
            url_for(
                current_app.appbuilder.sm.auth_view.__class__.__name__ + ".login",
                next=request.url,
            )
        )

    return functools.update_wrapper(wraps, f)


class SecuredDash(Dash):

    def interpolate_index(self, **kwargs):
        index_string = render_template(
            "dash.html",
            base_template=current_app.appbuilder.base_template,
            appbuilder=current_app.appbuilder
        )
        return index_string.format(
            dash_css=kwargs['css'],
            dash_app_entry=kwargs['app_entry'],
            dash_config=kwargs['config'],
            dash_scripts=kwargs['scripts'],
            dash_renderer=kwargs['renderer']
        )

    @has_authenticated
    def serve_layout(self):
        return super().serve_layout()

    @has_authenticated
    def serve_component_suites(self, package_name, fingerprinted_path):
        return super().serve_component_suites(package_name, fingerprinted_path)

    @has_authenticated
    def serve_reload_hash(self):
        return super().serve_reload_hash()

    @has_authenticated
    def index(self, *args, **kwargs):
        return super().index(*args, **kwargs)

    @has_authenticated
    def dependencies(self):
        return super().dependencies()

