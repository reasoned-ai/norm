import dash_ace
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, State, Output
from dash.exceptions import PreventUpdate
from flask import request

from norm.root import server, app
from norm.models import norma
from norm import engine
from norm.workbench.autocompleter import complete

import flask
import datetime
import logging

logger = logging.getLogger('workbench.editor')

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

    module = norma.get_module(module_name)
    if module is None:
        module = norma.create_module(module_name, '')
        title = f'[New] {module_name}'
    else:
        title = f'{module_name}'

    if len(module.scripts) > 0:
        script = module.scripts[-1]
    else:
        script = ''

    panel = html.Div([
        html.Div([], id=id_editor_state, hidden=True),
        dbc.Card([
            dbc.CardHeader([
                dbc.Row([
                    dbc.Col([html.P(title,
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
                    value=script,
                    theme='tomorrow',
                    mode='norm',
                    syntaxKeywords=syntaxKeywords,
                    syntaxFolds=syntaxFolds,
                    tabSize=2,
                    fontSize=20,
                    width='95%',
                    enableBasicAutocompletion=True,
                    enableLiveAutocompletion=True,
                    enableSnippets=True,
                    autocompleter='/autocompleter?prefix=',
                    prefixLine=True,
                    placeholder='Norm code ...',
                    height='85vh'
                ),
                className='m-0'
            )
        ], className='ml-0')
    ], id=id_editor_panel)
    return panel


@app.callback(
    Output(id_editor_title_status, 'children'),
    [Input(id_editor, 'value')],
    [State(id_editor_title_text, 'children')]
)
def execute(code: str, module_name: str):
    logger.debug(f'{module_name}: {code}')
    results = engine.execute(code, module_name.lower())
    return f'Checkpoint: {datetime.datetime.now().strftime("%H:%M:%S  %Y/%m/%d")}'


@server.route('/autocompleter', methods=['GET'])
def autocompleter():
    prefix = request.args.get('prefix')
    results = complete(prefix)
    return flask.jsonify(results)


