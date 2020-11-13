from flask import request, jsonify
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelRestApi
from flask_appbuilder.api import BaseApi, expose

from norm.models.norm import Lambda
from norm.completer import complete


class LambdaApi(ModelRestApi):
    datamodel = SQLAInterface(Lambda)


class Completer(BaseApi):
    @expose('/suggest', methods=['GET', 'POST'])
    def suggest(self):
        prefix = request.args.get('prefix')
        results = complete(prefix)
        return jsonify(results)

