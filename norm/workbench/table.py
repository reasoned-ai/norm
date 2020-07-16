import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table

id_table_panel = 'table-panel'
id_table_title = 'table-title'
id_table_state = 'table-state'

init_columns = [
    {'name': 'time', 'id': 'time', 'deletable': True, 'selectable': True},
    {'name': 'oid',  'id': 'oid',  'deletable': True, 'selectable': True},
    {'name': 'val',  'id': 'val',  'deletable': True, 'selectable': True},
    {'name': 'prb',  'id': 'prb',  'deletable': True, 'selectable': True},
    {'name': 'str',  'id': 'str',  'deletable': True, 'selectable': True},
]

init_dropdown = {}

panel = html.Div([
    html.Div([], id=id_table_state, hidden=True),
    dbc.Card([
        dbc.CardHeader('Data', id=id_table_title),
        dbc.CardBody(
            dash_table.DataTable(
                id=id_table_panel,
                columns=init_columns,
                data=[],
                editable=True,
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                column_selectable="single",
                row_selectable="multi",
                row_deletable=True,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=10,
                dropdown=init_dropdown,
                style_data_conditional=[{
                    'if': {'row_index': 'even'},
                    'backgroundColor': '#F5F5F5'
                }],
                style_header={
                    'backgroundColor': 'rgb(230, 230, 250)',
                    'fontWeight': 'bold',
                    'borderBottom': '1px solid black'
                },
            )
        )
    ])
])

