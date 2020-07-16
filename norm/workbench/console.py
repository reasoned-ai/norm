import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

id_console_panel = 'console-panel'
id_console_history = 'console-history'
id_console_log = 'console-log'
id_console_system = 'console-system'

panel = dbc.Tabs([
        dbc.Tab('', label='History', tab_id=id_console_history),
        dbc.Tab('', label='Log', tab_id=id_console_log),
        dbc.Tab('', label='System', tab_id=id_console_system),
    ],
    active_tab=id_console_history,
    style={'height': '30hv', 'width': '100%'},
    id=id_console_panel
)
