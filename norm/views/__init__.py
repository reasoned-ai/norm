from flask import render_template, redirect
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView
from flask_appbuilder.actions import action

from norm.root import norma_builder
from norm.models.storage import Storage
from norm.models.norm import Module
from norm.models.core import CoreModule
from norm.models.native import NativeModule
import norm.views.apis


class StorageView(ModelView):
    datamodel = SQLAInterface(Storage)
    list_columns = [
        'name', 'description', 'created_on', 'created_by'
    ]


class ModuleView(ModelView):
    datamodel = SQLAInterface(Module)
    list_columns = [
        'name', 'description', 'storage', 'created_on', 'changed_on', 'created_by', 'changed_by'
    ]

    @action("script", "Script the module", "Start scripting?", "fa-rocket")
    def script(self, item):
        """
            do something with the item record
        """
        return redirect(self.get_redirect())


norma_builder.add_view(
    StorageView,
    "Storage",
    icon='fa-folder-open-o',
    category='Connections',
    category_icon='fa-plug'
)

norma_builder.add_view(
    ModuleView,
    "Module",
    icon="fa-file-text",
)


"""
    Application wide 404 error handler
"""


@norma_builder.app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html",
            base_template=norma_builder.base_template,
            appbuilder=norma_builder
        ),
        404,
    )

