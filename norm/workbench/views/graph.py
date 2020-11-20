from enum import IntEnum
from functools import partial
from typing import List, Dict, Optional
import pandas as pd
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import dash_cytoscape as cyto
from dash.dependencies import Input, State, Output, MATCH
from dash.exceptions import PreventUpdate

from norm import dapp
from norm.workbench.utils import panel_style, mid, tid, match_id

import logging

logger = logging.getLogger('workbench.graph')

id_graph_panel = 'graph-panel'
id_graph_response = 'graph-response'
id_graph_tools = 'graph-tools'
id_graph_tools_items = 'graph-tools-items'
id_graph_tools_search = 'graph-tools-search'
id_graph_tools_reset_bt = 'graph-tools-reset-bt'
id_graph_tools_undo_bt = 'graph-tools-undo-bt'
id_graph_tools_redo_bt = 'graph-tools-redo-bt'
id_graph_tools_search_bt = 'graph-tools-search-bt'
id_graph_tools_search_popover = 'graph-tools-search-popover'
id_graph_tools_save_bt = 'graph-tools-save-bt'
id_graph_tools_time_bt = 'graph-tools-time-bt'
id_graph_tools_time_popover = 'graph-tools-time-popover'
id_graph_tools_delete_bt = 'graph-tools-delete-bt'
id_graph_tools_group_bt = 'graph-tools-group-bt'
id_graph_tools_time_range = 'graph-tools-time-range'
id_graph_state = 'graph-state'


class GraphState(IntEnum):
    BT_RESET = 0
    BT_SEARCH = 1
    BT_TIME = 2
    BT_UNDO = 3
    BT_REDO = 4
    BT_GROUP = 5
    BT_DELETE = 6
    BT_SAVE = 7
    ALL = 8


init_stylesheet = [
    {
        'selector': 'edge',
        'style': {
            'curve-style': 'bezier'
        }
    },
    {
        'selector': 'node',
        'style': {
            'background-color': '#1aa1c9',
            'content': 'data(id)',
            'text-valign': 'center',
            'text-outline-width': 2,
            'text-outline-color': '#1aa1c9',
            'font-size': 16,
            'color': '#fff'
        }
    },
    {
        'selector': '[highlighted < 1]',
        'style': {
            'width': 0
        }
    },
    {
        'selector': '[highlighted > 0]',
        'style': {
            'opacity': 0.7,
            'source-arrow-color': '#f92411',
            'source-arrow-shape': 'triangle',
            'target-arrow-color': '#f92411',
            'target-arrow-shape': 'circle',
            'arrow-scale': 1,
            'line-color': '#f92411',
            'content': 'data(situation)',
        }
    }
]

init_layout = {'name': 'preset'}


def tools(module_name: str):
    _mid = partial(mid, module_name)
    _tid = partial(tid, module_name)
    return dbc.Row(
        [
            dbc.Col(
                [
                    dbc.ButtonGroup(
                        [
                            dbc.Button('',
                                       color='info',
                                       className='fa fa-home',
                                       id=_mid(id_graph_tools_reset_bt)),
                            dbc.Button('',
                                       color='info',
                                       className='fa fa-search',
                                       id=_mid(id_graph_tools_search_bt)),
                            dbc.Button('',
                                       color='info',
                                       className='fa fa-clock-o',
                                       id=_mid(id_graph_tools_time_bt)),
                            dbc.Button('',
                                       color='info',
                                       className='fa fa-undo',
                                       id=_mid(id_graph_tools_undo_bt)),
                            dbc.Button('',
                                       color='info',
                                       className='fa fa-repeat',
                                       id=_mid(id_graph_tools_redo_bt)),
                            dbc.Button('',
                                       color='info',
                                       className='fa fa-object-group',
                                       id=_mid(id_graph_tools_group_bt)),
                            dbc.Button('',
                                       color='info',
                                       className='fa fa-trash',
                                       id=_mid(id_graph_tools_delete_bt)),
                            dbc.Button('',
                                       color='info',
                                       className='fa fa-save',
                                       id=_mid(id_graph_tools_save_bt)),
                        ],
                        id=_mid(id_graph_tools_items)
                    ),
                    dbc.Tooltip("Keyword search on the graph",
                                target=_tid(id_graph_tools_search_bt),
                                placement='top'),
                    dbc.Tooltip("Save current graph",
                                target=_tid(id_graph_tools_save_bt),
                                placement='top'),
                    dbc.Tooltip("Time range filtering",
                                target=_tid(id_graph_tools_time_bt),
                                placement='top'),
                    dbc.Tooltip("Redo the latest action",
                                target=_tid(id_graph_tools_redo_bt),
                                placement='top'),
                    dbc.Tooltip("Undo the latest action",
                                target=_tid(id_graph_tools_undo_bt),
                                placement='top'),
                    dbc.Tooltip("Group selected objects",
                                target=_tid(id_graph_tools_group_bt),
                                placement='top'),
                    dbc.Tooltip("Delete selected objects",
                                target=_tid(id_graph_tools_delete_bt),
                                placement='top'),
                ],
                width=dict(size=6),
            ),
            dbc.Col(
                [
                    dbc.Popover(
                        [
                            dbc.PopoverHeader("Select the time range"),
                            dbc.PopoverBody(
                                dcc.RangeSlider(
                                    min=0,
                                    max=100,
                                    value=[0, 40],
                                    included=False,
                                    updatemode='drag',
                                    id=_mid(id_graph_tools_time_range)
                                )
                            )
                        ],
                        style={'width': '20em'},
                        id=_mid(id_graph_tools_time_popover),
                        is_open=False,
                        target=_tid(id_graph_tools_time_bt)
                    ),
                    dbc.Popover(
                        [
                            dbc.PopoverBody(
                                dbc.Input(placeholder='Type keywords...',
                                          debounce=True,
                                          id=_mid(id_graph_tools_search)),
                            )
                        ],
                        style={'width': '20em'},
                        id=_mid(id_graph_tools_search_popover),
                        is_open=False,
                        target=_tid(id_graph_tools_search_bt)
                    )

                ],
                width=dict(size=5),
            ),
        ],
        justify='between')


def panel(module_name: str, vw: int):
    _mid = partial(mid, module_name)
    g = cyto.Cytoscape(
        id=_mid(id_graph_panel),
        layout=init_layout,
        style=dict(
            width='100%',
            height='85vh' if vw > 2000 else '72vh'
        ),
        stylesheet=init_stylesheet,
        boxSelectionEnabled=True,
        elements=[]
    )

    return html.Div([
        html.Div([0] * GraphState.ALL, id=_mid(id_graph_state), hidden=True),
        dbc.Card([
            dbc.CardHeader(tools(module_name), id=_mid(id_graph_tools)),
            dbc.CardBody(g),
            dbc.CardFooter(
                html.H6('.', id=_mid(id_graph_response))
            )
        ],
            className='m-0',
            style=panel_style(vw)
        )
    ])


layout = None


def get_layout():
    global layout
    if layout is not None:
        return layout

    try:
        return pd.read_parquet('/tmp/layout.parquet')
    except:
        return pd.DataFrame({})


def save_layout(l):
    global layout
    if layout is not None:
        diff = l.compare(layout)
        if len(diff) == 0:
            return

    layout = l
    layout.to_parquet('/tmp/layout.parquet')


@dapp.callback([Output(match_id(id_graph_response), 'children'),
                Output(match_id(id_graph_state), 'children')],
               [Input(match_id(id_graph_panel), 'tapNode'),
                Input(match_id(id_graph_panel), 'tapEdgeData'),
                Input(match_id(id_graph_tools_save_bt), 'n_clicks')],
               [State(match_id(id_graph_panel), 'elements'),
                State(match_id(id_graph_state), 'children')])
def display_tap_node_data(node, edge, bt_save, elements, states):
    if node is not None:
        return f"Clicked: {node['position']}", states
    elif edge is not None:
        return f"Clicked: {edge['des_e']} --> {edge['src_e']}", states
    elif bt_save is not None and bt_save > states[GraphState.BT_SAVE]:
        states[GraphState.BT_SAVE] = bt_save
        l = []
        for e in elements:
            pos = e.get('position')
            if pos is not None:
                l.append({'x': pos['x'], 'y': pos['y'], 'id': e.get('data').get('id')})
        save_layout(pd.DataFrame(data=l).set_index('id'))
        return f"Saved", states
    else:
        raise PreventUpdate


@dapp.callback(
    Output(match_id(id_graph_tools_time_popover), "is_open"),
    [Input(match_id(id_graph_tools_time_bt), "n_clicks")],
    [State(match_id(id_graph_tools_time_popover), "is_open")],
)
def toggle_time_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@dapp.callback(
    Output(match_id(id_graph_tools_search_popover), "is_open"),
    [Input(match_id(id_graph_tools_search_bt), "n_clicks")],
    [State(match_id(id_graph_tools_search_popover), "is_open")],
)
def toggle_search_popover(n, is_open):
    if n:
        return not is_open
    return is_open
