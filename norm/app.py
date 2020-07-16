import dash_html_components as html
import dash_bootstrap_components as dbc
import flask
from norm.workbench import layout
from norm.root import app, server

navbar = dbc.Navbar(
    [
        dbc.Row(
            [
                dbc.Col(html.I(className="fa fa-wrench text-light",
                               style={
                                   'fontSize': '2em',
                                   'marginLeft': '3em',
                                   'marginRight': '1em'
                               })),
                dbc.Col(dbc.NavbarBrand(" Norma ", className="ml-2", style={'fontSize': '2em'})),
            ],
            align="center",
            no_gutters=True,
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
    ],
    color="dark",
    dark=True,
)


content = [navbar, layout]

app.layout = html.Div([
    html.Link(href="./assets/norma.css", rel="stylesheet"),
    html.Div([
        html.Div([html.H1('')],
                 style={'width': '0%', 'float': 'left'}),
        html.Div(content,
                 style={'width': '100%', 'float': 'center'})
    ])
])


@server.route('/autocompleter', methods=['GET'])
def autocompleter():
    return flask.jsonify([{"name": "Completed", "value": "Completed", "score": 100, "meta": "test"}])


app.title = 'Norma'

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0")
