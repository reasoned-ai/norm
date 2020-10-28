import dash_bootstrap_components as dbc
import norm.workbench.view.table as table
import norm.workbench.view.console as console
import norm.workbench.view.chart as chart
import norm.workbench.view.graph as graph

id_tab_page = 'tab-page'
id_tab_table = 'tab-table'
id_tab_chart = 'tab-chart'
id_tab_graph = 'tab-graph'

label_style = {
    'fontSize': '1.2em'
}
views = [
    dbc.Tab('', label='Page', tab_id=id_tab_page, label_style=label_style),
    dbc.Tab(table.panel, label='Table', tab_id=id_tab_table, label_style=label_style),
    dbc.Tab(chart.panel, label='Chart', tab_id=id_tab_chart, label_style=label_style),
    dbc.Tab(graph.panel, label='Graph', tab_id=id_tab_graph, label_style=label_style),
]
