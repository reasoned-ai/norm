from enum import IntEnum

import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table

id_table_panel = 'table-panel'
id_table_title = 'table-title'
id_table_state = 'table-state'
id_table_cols = 'table-cols'
id_table_apply = 'table-apply'

init_columns = [
    {'name': 'time', 'id': 'time', 'hideable': True, 'selectable': True},
    {'name': 'oid',  'id': 'oid',  'hideable': True, 'selectable': True},
    {'name': 'val',  'id': 'val',  'hideable': True, 'selectable': True},
    {'name': 'prb',  'id': 'prb',  'hideable': True, 'selectable': True},
    {'name': 'str',  'id': 'str',  'hideable': True, 'selectable': True},
]

init_tooltips = []
init_dropdown = {}


class TableState(IntEnum):
    ALL = 0


panel = html.Div([
    html.Div([], id=id_table_state, hidden=True),
    dbc.Card([
        dbc.CardHeader([
            html.H5('Data')
        ], id=id_table_title),
        dbc.CardBody(
            dash_table.DataTable(
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
                page_size=10,
                export_format='csv',
                export_headers='display',
                merge_duplicate_headers=True,
                dropdown=init_dropdown,
                style_data_conditional=[{
                    'if': {'row_index': 'even'},
                    'backgroundColor': '#F5F5F5'
                }],
                style_cell={
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': 0,
                },
                tooltip_data=init_tooltips,
                tooltip_duration=None,
                style_header={
                    'backgroundColor': 'rgb(230, 230, 250)',
                    'fontWeight': 'bold',
                    'borderTop': '1px solid black',
                    'borderBottom': '1px solid black'
                },
            )
        )
    ])
])
