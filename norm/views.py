from typing import List, Union

from flask import redirect, url_for, render_template
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView
from flask_appbuilder.actions import action

from norm.models.storage import Storage
from norm.models.norm import Module
from norm.models.core import CoreModule
from norm.models.native import NativeModule
import logging

logger = logging.getLogger('norm.views')


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

    @action("explore", "Explore", icon="fa-flask")
    def explore(self, item: Union[Module, List[Module]]):
        if isinstance(item, list):
            item = item[0]
        return redirect(f'/norma/{item.name}')

