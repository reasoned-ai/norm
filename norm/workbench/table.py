from enum import IntEnum
from typing import List, Dict, Optional

import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, State, Output
from dash.exceptions import PreventUpdate

from norm.root import app
import logging

logger = logging.getLogger('workbench.table')

id_table_panel = 'table-panel'
id_table_tools = 'table-tools'
id_table_state = 'table-state'
id_table_cols = 'table-cols'
id_table_apply = 'table-apply'
id_table_title = 'table-title'
id_table_tools_items = 'table-tools-items'
id_table_tools_show = 'table-tools-show'
id_table_tools_save = 'table-tools-save'

init_columns = [
    {'name': 'row', 'id': 'row', 'hideable': True, 'selectable': True},
    {'name': 'time', 'id': 'time', 'hideable': True, 'renamable': True, 'selectable': True},
    {'name': 'oid', 'id': 'oid', 'hideable': True, 'renamable': True, 'selectable': True},
    {'name': 'val', 'id': 'val', 'hideable': True, 'renamable': True, 'selectable': True},
    {'name': 'prb', 'id': 'prb', 'hideable': True, 'renamable': True, 'selectable': True},
    {'name': 'str', 'id': 'str', 'hideable': True, 'renamable': True, 'selectable': True},
]

init_tooltips = []
init_dropdown = {}


class TableState(IntEnum):
    ALL = 0


tbl = dash_table.DataTable(
    id=id_table_panel,
    columns=init_columns,
    data=[],
    editable=True,
    filter_action="native",
    sort_action="native",
    sort_mode="multi",
    column_selectable="multi",
    row_selectable="multi",
    row_deletable=True,
    selected_columns=[],
    selected_rows=[],
    page_action="native",
    page_current=0,
    page_size=45,
    merge_duplicate_headers=True,
    dropdown=init_dropdown,
    style_data_conditional=[{
        'if': {'row_index': 'even'},
        'backgroundColor': '#F5F5F5'
    }],
    style_cell={
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
        'maxWidth': 200,
    },
    style_table={
        'overflowX': 'scroll',
        'padding': '1em',
    },
    style_header={
        'backgroundColor': 'rgb(230, 230, 230)',
        'fontWeight': 'bold',
    },
    tooltip_data=init_tooltips,
    tooltip_duration=None,
)

tools = dbc.Row([
    dbc.Col(
        dbc.InputGroup([
            dbc.DropdownMenu(
                label='',
                color="info",
                toggleClassName="fa fa-eye",
                id=id_table_tools_show),
            dbc.Button('',
                       color='info',
                       className='fa fa-save',
                       id=id_table_tools_save)
        ], id=id_table_tools_items),
        width=dict(size=12),
    ),
    dbc.Col(
        html.Div(''),
        width=dict(size=1)
    )
], justify='between')

panel = html.Div([
    html.Div([], id=id_table_state, hidden=True),
    dbc.Card([
        dbc.CardHeader(tools, id=id_table_tools),
        dbc.CardBody(tbl)],
        className='m-0',
        style={
            'height': '91.4vh'
        }
    )
])


@app.callback(
    [Output(id_table_tools_show, 'children')],
    Input(id_table_panel, 'hidden_columns'),
    [State(id_table_state, 'children')]
)
def update_columns(cols: Optional[List[Dict]], states: List[int]):
    if cols is None:
        raise PreventUpdate

    items = [
        dbc.DropdownMenuItem(col) for col in cols
    ]
    return items,
