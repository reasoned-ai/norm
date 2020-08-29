from flask_cors import CORS
import dash_bootstrap_components as dbc
import dash
import flask
from norm.config import DB_PATH, SQLALCHEMY_TRACK_MODIFICATIONS, SQLALCHEMY_ECHO
from flask_sqlalchemy import SQLAlchemy
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
server.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
server.config["SQLALCHEMY_ECHO"] = SQLALCHEMY_ECHO
db = SQLAlchemy(server)


app_path = '/norma/'
app = dash.Dash(__name__,
                server=server,
                routes_pathname_prefix=app_path,
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                ],
                external_scripts=external_scripts,
                external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

