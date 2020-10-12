import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Output, Input
from norm import workbench
from norm.root import app

id_module_search = 'module-search'
id_module_load = 'module-load'

navbar = dbc.Navbar(
    [
        dbc.Row(
            [
                dbc.Col(dbc.NavbarBrand(" Norma ",
                                        className="ml-2 mr-2",
                                        style={'fontSize': '2em', 'fontStyle': 'bolder'}),
                        width=dict(size=2, offset=1)),
                dbc.Col(
                    dcc.Dropdown(id=id_module_search,
                                 searchable=True,
                                 search_value='',
                                 value='',
                                 placeholder='Type module name'),
                    width=dict(size=5)
                ),
                dbc.Col(
                    dbc.Button('Load',
                               id=id_module_load,
                               style={'fontSize': '1.5em'},
                               color='info'),
                    width=dict(size=1)
                ),
                dbc.Col(
                    html.I('', className='fa fa-user text-light', style={'fontSize': '2em'}),
                    width=dict(size=2, offset=1)
                )
            ],
            align="center",
            justify="between",
            no_gutters=True,
            style={
                'width': '100%'
            }
        ),
    ],
    color="info",
    dark=True,
)


app.layout = html.Div([
    html.Link(href="./assets/norma.css", rel="stylesheet"),
    html.Div([
        html.Div([html.H1('')],
                 style={'width': '0%'}),
        html.Div([navbar, workbench.layout],
                 id='page-content',
                 style={'width': '99.6%',
                        'marginLeft': '0.4em',
                        'display': 'block'})
    ])
])


app.title = 'Norma'

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8005)
