from flask import render_template

from norm.root import app, dapp, appbuilder
from norm.workbench import layout
import logging
logger = logging.getLogger('norm.app')


dapp.layout = layout
