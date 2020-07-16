import dash_ace
import dash_html_components as html

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

id_editor_panel = 'editor-panel'

panel = html.Div([
    dash_ace.DashAceEditor(
        id=id_editor_panel,
        value='\n\n'
              '# Modeling Incident Root Cause\n'
              'RootCause\n'
              ':: (event: Event) -> (alert: Alert)\n'
              ':= for e in event.past(2hr):\n'
              '      (e.name, e.ip, e.port)\n'
              '         => event\n'
              '         => return alert',
        theme='tomorrow',
        mode='norm',
        syntaxKeywords=syntaxKeywords,
        syntaxFolds=syntaxFolds,
        tabSize=2,
        fontSize=20,
        enableBasicAutocompletion=True,
        enableLiveAutocompletion=True,
        autocompleter='/autocompleter?prefix=',
        prefixLine=True,
        triggerWords=[':', '\\.', '::'],  # consult the completer for types, members and inheritances
        placeholder='Norm code ...',
        height='90vh'
    )
], )
