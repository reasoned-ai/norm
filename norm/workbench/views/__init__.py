import dash_bootstrap_components as dbc
import norm.workbench.views.table as table
import norm.workbench.views.chart as chart
import norm.workbench.views.graph as graph
from norm.workbench.utils import label_style

id_tab_page = 'tab-page'
id_tab_table = 'tab-table'
id_tab_chart = 'tab-chart'
id_tab_graph = 'tab-graph'
id_tab_console = 'tab-console'
id_tabs_views = 'tabs-views'


def layout(module_name: str, vw: int):
    return dbc.Tabs([
        dbc.Tab('', label='Page', tab_id=id_tab_page, label_style=label_style),
        dbc.Tab(table.panel(module_name, vw), label='Table', tab_id=id_tab_table, label_style=label_style),
        dbc.Tab(chart.panel(module_name, vw), label='Chart', tab_id=id_tab_chart, label_style=label_style),
        dbc.Tab(graph.panel(module_name, vw), label='Graph', tab_id=id_tab_graph, label_style=label_style),
        dbc.Tab('', label='Console', tab_id=id_tab_console, label_style=label_style),
    ],
        active_tab=id_tab_table,
        style={'width': '100%'},
        id=dict(
            type=id_tabs_views,
            index=module_name
        )
    )
