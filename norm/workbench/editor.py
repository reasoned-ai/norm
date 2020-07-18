import dash_ace
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, State, Output
from dash.exceptions import PreventUpdate

from norm.root import server, app
import flask
import datetime

syntaxKeywords = {
    "variable.language": "this|that|super|self|sub|",
    "support.function": "enumerate|range|pow|sum|abs|max|min|argmax|argmin|len|mean|std|median|all|any|",
    "support.type": "String|Integer|Bool|Float|Image|UUID|Time|DateTime|Type|",
    "storage.modifier": "parameter|atomic|primary|optional|id|time|asc|desc|",
    "constant.language": "true|false|none|na|",
    "keyword.operator": "and|or|not|except|unless|imply|in|",
    "keyword.control": "as|from|to|import|export|return|for|exist|with|"
}

syntaxFolds = '\\:='

id_editor = 'editor'
id_editor_panel = 'editor-panel'
id_editor_state = 'editor-state'
id_editor_title_text = 'editor-title-text'
id_editor_title_bar = 'editor-title-bar'
id_editor_title_status = 'editor-title-status'


def get_panel(pathname: str) -> html.Div:
    if pathname is None:
        raise PreventUpdate

    module_name = pathname[7:].replace("/", ".").title()

    panel = html.Div([
        html.Div([], id=id_editor_state, hidden=True),
        dbc.Card([
            dbc.CardHeader([
                dbc.Row([
                    dbc.Col([html.P(f'{module_name}',
                                    id=id_editor_title_text,
                                    style={'fontSize': '20px',
                                           'textAlign': 'left'})],
                            width={'size': 6}),
                    dbc.Col([
                        html.P('', id=id_editor_title_status, className='pt-1')
                    ], width={'size': 6})
                ],
                    className='m-0 p-0',
                    justify='between')
            ], id=id_editor_title_bar, style={'height': '60px'}),
            dbc.CardBody(
                dash_ace.DashAceEditor(
                    id=id_editor,
                    value='',
                    theme='tomorrow',
                    mode='norm',
                    syntaxKeywords=syntaxKeywords,
                    syntaxFolds=syntaxFolds,
                    tabSize=2,
                    fontSize=20,
                    width='95%',
                    enableBasicAutocompletion=True,
                    enableLiveAutocompletion=True,
                    autocompleter='/autocompleter?prefix=',
                    prefixLine=True,
                    triggerWords=[':', '\\.', '::'],  # consult the completer for types, members and inheritances
                    placeholder='Norm code ...',
                    debounceChangePeriod=2000,
                    height='85vh'
                )
            )
        ], className='ml-0')
    ], id=id_editor_panel)
    return panel


@app.callback(
    Output(id_editor_title_status, 'children'),
    [Input(id_editor, 'value')]
)
def execute(code: str):
    return f'Checkpoint: {datetime.datetime.now().strftime("%H:%M:%S  %Y/%m/%d")}'


@server.route('/autocompleter', methods=['GET'])
def autocompleter():
    return flask.jsonify([{"name": "Completed", "value": "Completed", "score": 100, "meta": "test"}])


