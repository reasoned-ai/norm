import dash_bootstrap_components as dbc
import norm.workbench.editors.script as script
import norm.workbench.editors.style as style
from norm.workbench.utils import label_style

id_tab_script = 'tab-script'
id_tab_style = 'tab-style'
id_tab_version = 'tab-version'
id_editor = 'tabs-editor'


def layout(module_name: str, vw: int):
    return dbc.Tabs([
        dbc.Tab(script.panel(module_name, vw), label='Script', tab_id=id_tab_script, label_style=label_style),
        dbc.Tab('', label='Style', tab_id=id_tab_style, label_style=label_style),
        dbc.Tab('', label='Version', tab_id=id_tab_version, label_style=label_style),
    ],
        active_tab=id_tab_script,
        style={'width': '100%'},
        id=dict(
            type=id_editor,
            index=module_name
        )
    )
