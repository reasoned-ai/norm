from enum import IntEnum
from functools import partial
from typing import List, Dict, Optional

import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, State, Output
from dash.exceptions import PreventUpdate

from norm import dapp
import logging

from norm.workbench.utils import panel_style, mid, match_id, tid

logger = logging.getLogger('workbench.table')

MAX_HIDEABLE_COLUMNS = 100

id_table_panel = 'table-panel'
id_table_tools = 'table-tools'
id_table_state = 'table-state'
id_table_cols = 'table-cols'
id_table_apply = 'table-apply'
id_table_title = 'table-title'
id_table_tools_items = 'table-tools-items'
id_table_tools_show = 'table-tools-show'
id_table_tools_save = 'table-tools-save'
id_table_tools_reset = 'table-tools-reset'
id_table_tools_undo = 'table-tools-undo'
id_table_tools_redo = 'table-tools-redo'
id_table_tools_upload = 'table-tools-upload'

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
    ALL = MAX_HIDEABLE_COLUMNS


def tools(module_name: str):
    _mid = partial(mid, module_name)
    _tid = partial(tid, module_name)
    return dbc.Row([
        dbc.Col([
            dbc.ButtonGroup([
                dbc.Button('',
                           color='info',
                           className='fa fa-home',
                           id=_mid(id_table_tools_reset)),
                dbc.Button('',
                           color='info',
                           className='fa fa-undo',
                           id=_mid(id_table_tools_undo)),
                dbc.Button('',
                           color='info',
                           className='fa fa-repeat',
                           id=_mid(id_table_tools_redo)),
                dbc.Button('',
                           color='info',
                           className='fa fa-upload',
                           id=_mid(id_table_tools_upload)),
                dbc.Button('',
                           color='info',
                           className='fa fa-save',
                           id=_mid(id_table_tools_save)),
                dbc.DropdownMenu(
                    label='',
                    color="info",
                    toggleClassName="fa fa-eye",
                    style={'display': 'inline-block'},
                    id=_mid(id_table_tools_show)),
            ],
                id=_mid(id_table_tools_items)
            ),
            dbc.Tooltip("Show hidden columns", target=_tid(id_table_tools_show), placement='top'),
            dbc.Tooltip("Reset table", target=_tid(id_table_tools_reset), placement='top'),
            dbc.Tooltip("Undo last modification", target=_tid(id_table_tools_undo), placement='top'),
            dbc.Tooltip("Redo last undo modification", target=_tid(id_table_tools_redo), placement='top'),
            dbc.Tooltip("Upload new records", target=_tid(id_table_tools_upload), placement='top'),
            dbc.Tooltip("Save current modification", target=_tid(id_table_tools_save), placement='top'),
        ],
            lg=dict(size=11),
        ),
        dbc.Col(
            [],
            lg=dict(size=1)
        )
    ], justify='between')


def panel(module_name: str, vw: int):
    _mid = partial(mid, module_name)
    tbl = dash_table.DataTable(
        id=_mid(id_table_panel),
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
        page_size=45 if vw > 2000 else 30,
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
    return html.Div([
        html.Div([0] * TableState.ALL, id=_mid(id_table_state), hidden=True),
        dbc.Card([
            dbc.CardHeader(
                tools(module_name),
                id=_mid(id_table_tools)
            ),
            dbc.CardBody(tbl)
        ],
            className='m-0',
            style=panel_style(vw)
        )
    ])


@dapp.callback(
    Output(match_id(id_table_tools_show), 'children'),
    Input(match_id(id_table_panel), 'hidden_columns'),
    [State(match_id(id_table_panel), 'columns')]
)
def hide_columns(hcols: Optional[List[str]], cols: Optional[List[Dict]]):
    if hcols is None:
        raise PreventUpdate

    items = [
        dbc.DropdownMenuItem(col['name'],
                             id=f"show-column-{i}",
                             style={'display': 'flex' if col['name'] in hcols else 'none'})
        for i, col in enumerate(cols)
    ]
    items.extend([dbc.DropdownMenuItem('', id=f"show-column-{i}", style={'display': 'none'})
                  for i in range(len(cols), MAX_HIDEABLE_COLUMNS)])
    return items


@dapp.callback(
    Output(match_id(id_table_panel), 'hidden_columns'),
    [Input(f'show-column-{i}', 'n_clicks') for i in range(MAX_HIDEABLE_COLUMNS)],
    [State(match_id(id_table_state), 'children'),
     State(match_id(id_table_panel), 'columns'),
     State(match_id(id_table_panel), 'hidden_columns')],
)
def show_columns(*args):
    hcols = args[-1]
    cols = args[-2]
    states = args[-3]
    for i in range(len(args) - 3):
        if args[i] is not None and args[i] > states[i]:
            col = cols[i]['name']
            return [c for c in hcols if c != col]
    raise PreventUpdate
