from functools import partial

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from norm.workbench.utils import panel_style, mid

id_display_panel = 'display-panel'
id_display_title = 'display-title'
id_display_state = 'display-state'
id_display_response = 'display-response'

init_fig = go.Figure()
init_fig.update_layout(margin={'b': 0, 'l': 0, 'r': 0, 't': 0, 'pad': 0})


def panel(module_name: str, vw: int):
    _mid = partial(mid, module_name)
    return html.Div([
        html.Div([], id=_mid(id_display_state), hidden=True),
        dbc.Card([
            dbc.CardHeader(html.H5('Graph'), id=_mid(id_display_title)),
            dbc.CardBody(
                dcc.Graph(
                    figure=init_fig,
                    config=dict(responsive=True),
                    style=dict(
                        height='85vh' if vw > 2000 else '72vh',
                        width='100%'
                    ),
                    id=_mid(id_display_panel)
                )
            ),
            dbc.CardFooter(
                html.H6('.', id=_mid(id_display_response))
            )
        ],
            className='m-0',
            style=panel_style(vw)
        )
    ])
