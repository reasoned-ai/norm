import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Output, Input
from norm.workbench import get_layout
from norm.root import app

navbar = dbc.Navbar(
    [
        dbc.Row(
            [
                dbc.Col(html.I(className="fa fa-flask text-light",
                               style={
                                   'fontSize': '2em',
                                   'marginLeft': '1em',
                                   'marginRight': '1em'
                               })),
                dbc.Col(dbc.NavbarBrand(" Norma ", className="ml-2", style={'fontSize': '2em'})),
            ],
            align="center",
            no_gutters=True,
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
    ],
    color="info",
    dark=True,
)


app.layout = html.Div([
    html.Link(href="./assets/norma.css", rel="stylesheet"),
    dcc.Location(id='url', refresh=False),
    html.Div([
        html.Div([html.H1('')],
                 style={'width': '0%'}),
        html.Div([],
                 id='page-content',
                 className='ml-2',
                 style={'width': '99.2%',
                        'float': 'center',
                        'display': 'block'})
    ])
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    return [navbar, get_layout(pathname)]


app.title = 'Norma'

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8005)
