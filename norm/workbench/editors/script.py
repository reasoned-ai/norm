from typing import List

import dash_ace
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, State, Output
from dash.exceptions import PreventUpdate
import pandas as pd
from norm.root import dapp
from norm.models import norma
from norm import engine
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


tools = dbc.Row(
    [
        dbc.Col([
            dbc.ButtonGroup([
                dbc.Button('',
                           color='info',
                           className='fa fa-minus',
                           id=id_script_tools_smaller),
                dbc.Button('',
                           color="info",
                           className="fa fa-plus",
                           id=id_script_tools_bigger),
            ],
                id=id_script_tools_items
            ),
            dbc.Tooltip("Increase font size", target=id_script_tools_bigger, placement='top'),
            dbc.Tooltip("Decrease font size", target=id_script_tools_smaller, placement='top'),
        ],
            width=dict(size=12),
        ),
        dbc.Col(
            html.Div(''),
            width=dict(size=1)
        )
    ]
)

panel = html.Div([
    html.Div([0] * EditorState.TOTAL, id=id_script_state, hidden=True),
    dbc.Card([
        dbc.CardHeader(tools, id=id_script_tools),
        dbc.CardBody(
            dash_ace.DashAceEditor(
                id=id_script,
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
                height='84vh',
                width='23vw'
            ),
            className='m-0'
        ),
        dbc.CardFooter(
            html.H6('.', id=id_script_status)
        )
    ], className='ml-0')
], id=id_script_panel)


@dapp.callback(
    [Output(id_script_status, 'children'),
     Output(id_table_panel, "columns"),
     Output(id_table_panel, "data"),
     Output(id_table_panel, "tooltip_data"),
     Output(id_graph_panel, "elements"),
     ],
    [Input(id_script, 'value'),
     Input(id_graph_tools_time_range, 'value'),
     Input(id_graph_tools_search, 'value')],
    [State(id_table_panel, 'data')]
)
def execute(code: str, time_range: List[int], keyword: str, odt: List):
    results = engine.execute(code, "") # TODO module_name.lower())
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

