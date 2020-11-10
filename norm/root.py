from flask_cors import CORS
import dash_bootstrap_components as dbc
import dash
import flask
from flask_appbuilder import AppBuilder, SQLA
import dash_cytoscape as cyto
from sqlalchemy.engine import Engine
from sqlalchemy import event

import logging
logger = logging.getLogger('norm.root')

external_stylesheets = [
    "https://fonts.googleapis.com/css?family=Kanit&display=swap",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
    dbc.themes.FLATLY
]
external_scripts = ["https://cdn.plot.ly/plotly-latest.js"]

server = flask.Flask(__name__)
CORS(server)

server.config.from_object("norm.config")
db = SQLA(server)
norma_builder = AppBuilder(server, db.session)


# Only include this for SQLLite constraints
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Will force sqllite contraint foreign keys
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


app_path = '/norma/'
cyto.load_extra_layouts()
app = dash.Dash(__name__,
                server=server,
                routes_pathname_prefix=app_path,
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                ],
                external_scripts=external_scripts,
                external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

