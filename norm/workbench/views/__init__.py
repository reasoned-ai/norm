import dash_bootstrap_components as dbc
import norm.workbench.views.table as table
import norm.workbench.views.chart as chart
import norm.workbench.views.graph as graph

id_tab_page = 'tab-page'
id_tab_table = 'tab-table'
id_tab_chart = 'tab-chart'
id_tab_graph = 'tab-graph'
id_tab_console = 'tab-console'

label_style = {
    'fontSize': '1.2em'
}
views = [
    dbc.Tab('', label='Page', tab_id=id_tab_page, label_style=label_style),
    dbc.Tab(table.panel, label='Table', tab_id=id_tab_table, label_style=label_style),
    dbc.Tab(chart.panel, label='Chart', tab_id=id_tab_chart, label_style=label_style),
    dbc.Tab(graph.panel, label='Graph', tab_id=id_tab_graph, label_style=label_style),
    dbc.Tab('', label='Console', tab_id=id_tab_console, label_style=label_style),
]
