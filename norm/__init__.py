from typing import Tuple

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from sqlalchemy.engine import Engine
from sqlalchemy import event
from flask_compress import Compress
from flask_migrate import Migrate
from flask_talisman import Talisman
from dash import Dash
import os
import logging

from norm.secured_dash import SecuredDash

logger = logging.getLogger('norm')


# Only include this for SQLLite constraints
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Will force sqllite contraint foreign keys
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_app() -> Tuple[Flask, Dash]:
    app = Flask(__name__)

    try:
        config_module = os.environ.get("NORM_CONFIG", "norm.config")
        app.config.from_object(config_module)
        return NormaInitializer(app).init_app()
    except Exception as e:
        logger.exception("Failed to create app")
        raise e


class NormaInitializer:
    def __init__(self, app: Flask) -> None:
        super().__init__()

        self.flask_app = app
        self.dapp = None
        self.config = app.config

    def init_views(self):
        from norm.views import StorageView, ModuleView
        appbuilder.add_view(
            StorageView,
            "Storage",
            icon='fa-folder-open-o',
            category='Connection',
            category_icon='fa-plug'
        )

        appbuilder.add_view(
            ModuleView,
            "Module",
            icon="fa-code",
            category='Knowledge',
            category_icon='fa-lightbulb-o'
        )

    def init_apis(self):
        from norm.apis import LambdaApi, Completer
        appbuilder.add_api(LambdaApi)
        appbuilder.add_api(Completer)

    def init_dash(self):
        import dash_cytoscape as cyto

        cyto.load_extra_layouts()
        external_stylesheets = [
            "/static/styles/norma.css"
        ]
        external_scripts = [
            "https://cdn.plot.ly/plotly-latest.js"
        ]

        self.dapp = SecuredDash(
            name='Norma',
            title='Norma',
            server=self.flask_app,
            routes_pathname_prefix='/norma/',
            meta_tags=[
                {
                    "name": "viewport",
                    "content": "width=device-width, initial-scale=1"
                }
            ],
            external_scripts=external_scripts,
            external_stylesheets=external_stylesheets
        )
        self.dapp.config.suppress_callback_exceptions = True

    def init_app_in_ctx(self) -> None:
        """
        Runs init logic in the context of the app
        """
        self.configure_fab()
        self.init_views()
        self.init_apis()
        self.init_dash()

    def init_app(self) -> Tuple[Flask, Dash]:
        """
        Main entry point which will delegate to other methods in
        order to fully init the app
        """
        self.setup_db()
        self.register_blueprints()
        self.configure_middlewares()

        with self.flask_app.app_context():  # type: ignore
            self.init_app_in_ctx()

        return self.flask_app, self.dapp

    def configure_fab(self) -> None:
        if self.config["SILENCE_FAB"]:
            logging.getLogger("flask_appbuilder").setLevel(logging.ERROR)

        appbuilder.base_template = "base.html"
        appbuilder.init_app(self.flask_app, db.session)

    def configure_middlewares(self) -> None:
        if self.config["ENABLE_CORS"]:
            from flask_cors import CORS

            CORS(self.flask_app, **self.config["CORS_OPTIONS"])

        # Flask-Compress
        Compress(self.flask_app)

        if self.config["TALISMAN_ENABLED"]:
            talisman.init_app(self.flask_app, **self.config["TALISMAN_CONFIG"])

    def setup_db(self) -> None:
        db.init_app(self.flask_app)
        # migrate.init_app(self.flask_app, db=db, directory=APP_DIR + "/migrations")

    def register_blueprints(self) -> None:
        for bp in self.config["BLUEPRINTS"]:
            try:
                logger.info("Registering blueprint: %s", bp.name)
                self.flask_app.register_blueprint(bp)
            except Exception:  # pylint: disable=broad-except
                logger.exception("blueprint registration failed")


appbuilder = AppBuilder(update_perms=True)
db = SQLA()
migrate = Migrate()
talisman = Talisman()

app, dapp = create_app()
