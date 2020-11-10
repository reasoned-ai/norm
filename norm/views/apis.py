from flask import request
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelRestApi
from flask_appbuilder.api import BaseApi, expose

from norm.root import norma_builder
from norm.models.norm import Lambda
from norm.completer import complete


class LambdaApi(ModelRestApi):
    datamodel = SQLAInterface(Lambda)


norma_builder.add_api(LambdaApi)


class Completer(BaseApi):
    @expose('/suggest', methods=['GET'])
    def suggest(self):
        prefix = request.args.get('prefix')
        results = complete(prefix)
        return self.response(200, suggestions=results)


norma_builder.add_api(Completer)
