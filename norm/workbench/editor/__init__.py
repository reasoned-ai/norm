import dash_bootstrap_components as dbc
import norm.workbench.editor.script as script
import norm.workbench.editor.style as style

id_tab_script = 'tab-script'
id_tab_style = 'tab-style'
id_tab_version = 'tab-version'

label_style = {
    'fontSize': '1.2em'
}

codes = [
    dbc.Tab(script.panel, label='Script', tab_id=id_tab_script, label_style=label_style),
    dbc.Tab('', label='Style', tab_id=id_tab_style, label_style=label_style),
    dbc.Tab('', label='Version', tab_id=id_tab_version, label_style=label_style),
]
