import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

id_display_panel = 'display-panel'
id_display_title = 'display-title'
id_display_state = 'display-state'

init_fig = go.Figure()
init_fig.update_layout(margin={'b': 0, 'l': 0, 'r': 0, 't': 0, 'pad': 0})

panel = html.Div([
    html.Div([], id=id_display_state, hidden=True),
    dbc.Card([
        dbc.CardHeader('Graph', id=id_display_title),
        dbc.CardBody(
            dcc.Graph(
                figure=init_fig,
                config=dict(responsive=True),
                style={
                    'height': '70vh',
                    'width': '100%'
                },
                id=id_display_panel
            )
        )], className='m-0')
])
