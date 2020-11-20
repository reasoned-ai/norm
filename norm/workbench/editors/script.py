import json
from typing import List, Dict

import dash_ace
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, State, Output, MATCH
from dash.exceptions import PreventUpdate
from functools import partial
import pandas as pd
from norm import dapp
from norm.workbench.utils import mid, tid, match_id
from norm.models import norma
from norm.engine import execute as norm_execute
from norm.config import MAX_ROWS
from norm.workbench.views.table import id_table_panel
from norm.workbench.views.graph import id_graph_panel, id_graph_tools_search, id_graph_tools_time_range, get_layout

from enum import IntEnum
import datetime
import logging

logger = logging.getLogger('workbench.script')

syntaxKeywords = {
    "variable.language": "this|that|super|self|sub|",
    "support.function": "enumerate|range|pow|sum|abs|max|min|argmax|argmin|len|mean|std|median|all|any|",
    "support.type": "String|Integer|Bool|Float|Image|UUID|Time|DateTime|Type|",
    "storage.modifier": "parameter|atomic|primary|optional|id|time|asc|desc|",
    "constant.language": "true|false|none|na|",
    "keyword.operator": "and|or|not|except|unless|imply|in|",
    "keyword.control": "as|from|to|import|export|return|for|exist|with|"
}

syntaxFolds = '\\:='

id_script = 'script'
id_script_panel = 'script-panel'
id_script_state = 'script-state'
id_script_tools = 'script-tools'
id_script_status = 'script-status'
id_script_module = 'script-module'

id_script_tools_items = 'script-tools-items'
id_script_tools_bigger = 'script-tools-bigger'
id_script_tools_smaller = 'script-tools-smaller'


class EditorState(IntEnum):
    MODULE_LOAD_NEW = 0
    TOTAL = 1


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
                                       className='fa fa-minus',
                                       id=id_script_tools_smaller),
                            dbc.Button('',
                                       color="info",
                                       className="fa fa-plus",
                                       id=_mid(id_script_tools_bigger)),
                        ],
                        id=_mid(id_script_tools_items)
                    )
                ],
                lg=dict(size=6),
            ),
            dbc.Col(
                [
                    dbc.Tooltip("Increase font size",
                                target=_tid(id_script_tools_bigger),
                                placement='right'),
                    dbc.Tooltip("Decrease font size",
                                target=id_script_tools_smaller,
                                placement='right')
                ],
                lg=dict(size=2)
            )
        ],
        className='ml-lg-1',
        justify='between'
    )


def panel(module_name: str, vw: int):
    _mid = partial(mid, module_name)
    return html.Div([
        html.Div([0] * EditorState.TOTAL, id=_mid(id_script_state), hidden=True),
        dbc.Card([
            dbc.CardHeader(
                tools(module_name),
                id=_mid(id_script_tools)
            ),
            dbc.CardBody(
                dash_ace.DashAceEditor(
                    id=_mid(id_script),
                    value='',
                    theme='tomorrow',
                    mode='norm',
                    syntaxKeywords=syntaxKeywords,
                    syntaxFolds=syntaxFolds,
                    tabSize=2,
                    fontSize=20,
                    enableBasicAutocompletion=True,
                    enableLiveAutocompletion=True,
                    enableSnippets=True,
                    autocompleter='/api/v1/completer/suggest?prefix=',
                    prefixLine=True,
                    placeholder='Norm code ...',
                    height='84vh' if vw > 2000 else '69vh',
                    width='23vw' if vw > 2000 else '95vw'
                ),
                style={
                    'margin': '1em'
                }
            ),
            dbc.CardFooter(
                html.H6(
                    '.',
                    id=_mid(id_script_status)
                )
            )
        ], className='m-1')
    ],
        id=_mid(id_script_panel)
    )


@dapp.callback(
    [Output(match_id(id_script_status), 'children'),
     Output(match_id(id_table_panel), "columns"),
     Output(match_id(id_table_panel), "data"),
     Output(match_id(id_table_panel), "tooltip_data"),
     Output(match_id(id_graph_panel), "elements"),
     ],
    [Input(match_id(id_script), 'value'),
     Input(match_id(id_graph_tools_time_range), 'value'),
     Input(match_id(id_graph_tools_search), 'value')],
    [State(match_id(id_table_panel), 'data'),
     State(match_id(id_script), 'id')]
)
def execute(code: str, time_range: List[int], keyword: str, odt: List, script_id: Dict):
    module_name = script_id['index'].replace('-', '.')
    results = norm_execute(code, module_name)
    if results is None:
        raise PreventUpdate

    dt = results.head(MAX_ROWS)
    times = list(dt['src_t'].drop_duplicates().sort_values().values)
    t = len(times) - 1
    tb = times[int(time_range[0] * t / 100)]
    te = times[int(time_range[1] * t / 100)]

    selected_dt = dt[(dt['src_t'] <= te) & (dt['src_t'] >= tb)]
    if keyword is not None:
        selected_dt = selected_dt[selected_dt['src_entity'].str.contains(keyword, case=False)]
    dt['highlighted'] = 0
    dt.loc[selected_dt.index, 'highlighted'] = 1
    nodes, edges = nodes_edges(dt)
    elements = nodes + edges

    dt_cols = [{'name': 'row', 'id': 'row'}] + \
              [{'name': col, 'id': col, 'hideable': True, 'renamable': True, 'selectable': True}
               for col in dt.columns]
    dt['row'] = list(range(len(dt)))
    dt = dt.to_dict(orient='records')
    tooltip_data = [
        {
            column: {'value': str(value), 'type': 'markdown'}
            for column, value in row.items()
        } for row in dt
    ]
    return f'Checkpoint: {datetime.datetime.now().strftime("%H:%M:%S  %Y/%m/%d")}', \
           dt_cols, dt, tooltip_data, \
           elements


def nodes_edges(data):
    src_nodes = data[['src_entity']].rename(columns={'src_entity': 'id'})
    des_nodes = data[['des_entity']].rename(columns={'des_entity': 'id'})
    nodes = pd.concat([src_nodes, des_nodes], ignore_index=True)\
              .drop_duplicates()\
              .to_dict(orient='records')
    edges = data[['src_entity', 'src_e', 'des_entity', 'des_e', 'situation', 'value', 'highlighted']].rename(
        columns={'src_entity': 'source', 'des_entity': 'target'}
    ).to_dict(orient='records')
    layout = get_layout().to_dict(orient='index')
    zero = dict(x=0, y=0)
    nodes = [dict(data=nd, position=layout.get(nd['id'], zero)) for nd in nodes]
    edges = [dict(data=eg) for eg in edges if eg['source'] != eg['target']]
    return nodes, edges

