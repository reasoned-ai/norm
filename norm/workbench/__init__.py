import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from typing import List
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from norm.workbench import (chart, console, editor, table)
from norm.root import app
import numpy as np

editor_height = 100
graph_height = 80
console_height = 20
nsample = 2500

id_ctrl_editor = 'ctrl-editor'
id_ctrl_display = 'ctrl-display'
id_ctrl_table = 'ctrl-table'
id_ctrl_buttons = 'ctrl-buttons'

id_panel_editor_collapse = 'panel-editor-collapse'
id_panel_chart_collapse = 'panel-display-collapse'
id_panel_table_collapse = 'panel-table-collapse'
id_panel_editor_col = 'panel-editor-col'
id_panel_right_col = 'panel-right-col'

id_filter_keyword = 'keyword'
id_filter_keyword_type = 'keyword-type'
id_filter_keyword_submit = 'keyword-submit'

id_tab_table = 'tab-table'
id_tab_list = 'tab-list'
id_tab_chart = 'tab-chart'
id_tab_graph = 'tab-graph'
id_tab_geo = 'tab-geo'
id_tab_views = 'tab-views'

init_editor_active = True
init_chart_active = True
init_table_active = True

controls = dbc.Row([
    dbc.Col(
        dbc.ButtonGroup([
            dbc.Button("Editor",
                       color="info",
                       outline=True,
                       active=init_editor_active,
                       id=id_ctrl_editor),
            dbc.Button("Display",
                       color="info",
                       active=init_chart_active,
                       outline=True,
                       id=id_ctrl_display),
            dbc.Button("Table",
                       color="info",
                       outline=True,
                       active=init_table_active,
                       id=id_ctrl_table),
        ], id=id_ctrl_buttons),
        width=dict(size=2),
    ),
    dbc.Col(
        dbc.InputGroup([
            dbc.InputGroupAddon(dbc.Select(
                id=id_filter_keyword_type,
                value='search',
                options=[{'label': 'Search', 'value': 'search'},
                         {'label': 'Predict', 'value': 'predict'}]
            ), addon_type='prepend'),
            dbc.Input(id=id_filter_keyword, type='search', placeholder='Type in keywords...',
                      debounce=True),
            dbc.InputGroupAddon(
                dbc.Button("Go", color='info', id=id_filter_keyword_submit), addon_type="append",
            ),
        ]),
        width=dict(size=5)
    ),
    dbc.Col(
        html.Div(''),
        width=dict(size=1)
    )
], justify='between')

layout = html.Div([
    html.Br(),
    dbc.Row([
        dbc.Col(editor.panel,
                id=id_panel_editor_col,
                width=dict(size=3)),
        dbc.Col(dbc.Tabs([
            dbc.Tab(table.panel, label='Table', tab_id=id_tab_table),
            dbc.Tab('', label='List', tab_id=id_tab_list),
            dbc.Tab(chart.panel, label='Chart', tab_id=id_tab_chart),
            dbc.Tab('', label='Graph', tab_id=id_tab_graph),
            dbc.Tab('', label='Geo', tab_id=id_tab_geo),
        ],
            active_tab=id_tab_table,
            style={'height': '30hv', 'width': '100%'},
            id=id_tab_views
        ), id=id_panel_right_col, width=dict(size=9))
    ]),
    html.Hr(),
    dbc.Row([console.panel])
], className='mr-2')

"""
@app.callback([Output(id_panel_editor_collapse, 'is_open'),
               Output(id_ctrl_editor, 'active'),
               Output(id_panel_editor_col, 'width'),
               Output(id_panel_right_col, 'width')],
              [Input(id_ctrl_editor, 'n_clicks')],
              [State(id_panel_editor_collapse, 'is_open')])
def toggle_editor(n, is_open):
    print('test')
    if n:
        is_open = not is_open
    else:
        is_open = init_editor_active
    editor_panel_width = dict(size=0) if not is_open else dict(size=3)
    right_panel_width = dict(size=12) if not is_open else dict(size=9)

    return is_open, is_open, editor_panel_width, right_panel_width


@app.callback([Output(id_panel_chart_collapse, 'is_open'),
               Output(id_ctrl_display, 'active')],
              [Input(id_ctrl_display, 'n_clicks')],
              [State(id_panel_chart_collapse, 'is_open')])
def toggle_display(n, is_open):
    if n:
        is_open = not is_open
        return is_open, is_open
    else:
        return init_chart_active, init_chart_active


@app.callback([Output(id_panel_table_collapse, 'is_open'),
               Output(id_ctrl_table, 'active')],
              [Input(id_ctrl_table, 'n_clicks')],
              [State(id_panel_table_collapse, 'is_open')])
def toggle_table(n, is_open):
    if n:
        is_open = not is_open
        return is_open, is_open
    else:
        return init_table_active, init_table_active



@app.callback(
    [
        Output(match_id(id_filter_keyword_submit), 'n_clicks'),
        Output(match_id(train.id_stats_precision), 'figure'),
        Output(match_id(train.id_stats_recall), 'figure'),
        Output(match_id(train.id_bt_state_adapt), 'children')
    ],
    [
        Input(match_id(train.id_train_target), 'n_clicks')
    ],
    [
        State(match_id(train.id_bt_state_adapt), 'children'),
        State(match_id(id_panel_datatable), "data"),
        State(match_id(id_filter_keyword_submit), 'n_clicks'),
        State(match_id(train.id_train_dwell_time), 'value'),
        State(id_discover_tabs, 'active_tab'),
        State(match_id(train.id_stats_precision), 'figure'),
        State(match_id(train.id_stats_recall), 'figure')
    ]
)
def retrain_model(retrain, bt_state, changed_data, nclicks, dwell_time, fn, precision_fig, recall_fig):
    exams = get_exampler(fn)
    if retrain and retrain > bt_state[0]:
        precision, recall, conflicts = exams.retrain(changed_data, dwell_time)
        precision_fig = train.Train.stats_precision_fig(np.round(precision.mean() * 1000) / 10,
                                                        precision_fig['data'][0]['value'])
        recall_fig = train.Train.stats_recall_fig(np.round(recall.mean() * 1000) / 10,
                                                  recall_fig['data'][0]['value'])
        bt_state[0] = retrain

    return [nclicks or 0], precision_fig, recall_fig, bt_state


@app.callback(
    Output(match_id(train.id_bt_state_save), 'children'),
    [
        Input(match_id(train.id_train_save), 'n_clicks')
    ],
    [
        State(match_id(train.id_bt_state_save), 'children'),
        State(id_discover_tabs, 'active_tab')
    ]
)
def save_model(n_save, bt_state, fn):
    if n_save and n_save > bt_state[0]:
        get_exampler(fn).save()
        bt_state[0] = n_save
    return bt_state
"""

"""
@app.callback(
    [Output(match_id(test.id_stats_precision), 'figure'),
     Output(match_id(test.id_stats_recall), 'figure'),
     Output(match_id(test.id_stats_conflict), 'figure')],
    [Input(match_id(test.id_adjust_dwell_time), 'value')],
    [State(id_discover_tabs, 'active_tab'),
     State(match_id(test.id_stats_conflict), 'figure')]
)
def adjust_model(dwell_time, fn, conflict_fig):
    exams = get_exampler(fn)
    precision, recall, conflicts = exams.retrain(None, dwell_time)
    precision_fig = test.Test.stats_precisions_figure(precision.index.values, precision.values)
    recall_fig = test.Test.stats_recalls_figure(recall.index.values, recall.values)
    conflict_fig = test.Test.stats_conflict_figure(conflicts, conflict_fig['data'][0]['value'])
    return precision_fig, recall_fig, conflict_fig
"""

"""
@app.callback(
    [
        Output(match_id(train.id_target_values), 'children'),
        Output(match_id(id_panel_datatable), 'dropdown')
    ],
    [
        Input(match_id(train.id_target_add), 'n_clicks')
    ],
    [
        State(match_id(train.id_target_value), 'value'),
        State(match_id(train.id_target_values), 'children'),
        State(match_id(id_panel_datatable), 'dropdown')
    ]
)
def add_target_value(add_target, new_value, old_values, old_dropdown):
    if add_target and new_value:
        for item in old_values:
            if new_value == item['props']['children']:
                raise PreventUpdate
        old_values.append(dbc.DropdownMenuItem(new_value))
        old_dropdown['pattern']['options'].append({'label': new_value, 'value': new_value})
        return old_values, old_dropdown
    else:
        raise PreventUpdate


@app.callback([Output(match_id(id_panel_graph), "figure"),
               Output(match_id(id_panel_datatable), "data"),
               Output(match_id(id_panel_datatable), "selected_rows"),
               Output(match_id(id_panel_datatable), "page_current"),
               Output(match_id(id_panel_datatable), "style_data_conditional"),
               Output(match_id(id_panel_datatable_title), 'children'),
               Output(match_id(id_state_graph), 'children'),
               Output(match_id(train.id_stats_labels), "figure"),
               Output(match_id(train.id_stats_progress), 'figure'),
               Output(match_id(test.id_stats_precision), 'figure'),
               Output(match_id(test.id_stats_recall), 'figure'),
               Output(match_id(test.id_stats_conflict), 'figure')
               ],
              [Input(match_id(display.id_graph_text), 'value'),
               Input(match_id(display.id_graph_color), 'value'),
               Input(match_id(display.id_graph_y), 'value'),
               Input(match_id(display.id_graph_size), 'value'),
               Input(match_id(display.id_graph_prob), 'value'),
               Input(match_id(display.id_graph_custom_text), 'value'),
               Input(match_id(display.id_graph_custom_color), 'value'),
               Input(match_id(display.id_graph_custom_x), 'value'),
               Input(match_id(display.id_graph_custom_y), 'value'),
               Input(match_id(display.id_graph_custom_size), 'value'),
               Input(match_id(display.id_graph_custom_interval), 'value'),
               Input(match_id_show(display.id_graph_text), 'checked'),
               Input(match_id_show(display.id_graph_color), 'checked'),
               Input(match_id_show(display.id_graph_y), 'checked'),
               Input(match_id_show(display.id_graph_size), 'checked'),
               Input(match_id_show(display.id_graph_prob), 'checked'),
               Input(match_id(display.id_graph_bw_degree), 'value'),
               Input(match_id(display.id_graph_fw_degree), 'value'),
               Input(match_id(display.id_graph_confidence), 'value'),
               Input(match_id(display.id_graph_relation), 'value'),
               Input(match_id(id_panel_graph), 'clickData'),
               Input(match_id(id_filter_keyword_submit), 'n_clicks'),
               Input(match_id(display.id_filter_time_range), 'end_date'),
               Input(match_id(display.id_filter_time_range), 'start_date'),
               Input(match_id(id_filter_keyword), 'value'),
               Input(match_id(train.id_walkby_next), 'n_clicks'),
               Input(match_id(train.id_walkby_prev), 'n_clicks'),
               Input(match_id(test.id_adjust_dwell_time), 'value'),
               Input(match_id(test.id_walkby_next), 'n_clicks'),
               Input(match_id(test.id_walkby_prev), 'n_clicks'),
               ],
              [State(match_id(id_filter_keyword_type), 'value'),
               State(match_id(id_panel_datatable), 'style_data_conditional'),
               State(id_discover_tabs, 'active_tab'),
               State(match_id(id_state_graph), 'children'),
               State(match_id(train.id_walkby_ent), 'value'),
               State(match_id(id_panel_datatable), "data"),
               State(match_id(train.id_stats_labels), "figure"),
               State(match_id(train.id_stats_progress), "figure"),
               State(match_id(display.id_graph_layout), 'active_tab'),
               State(match_id(test.id_stats_conflict), 'figure')
               ])
def generate_graph(ent_text, ent_clr, ent_y, ent_size, ent_prob,
                   ent_c_text, ent_c_clr, ent_c_x, ent_c_y, ent_c_size, ent_c_interval,
                   show_text, show_color, show_y, show_size, show_prob,
                   bw_degree, fw_degree, alpha, relation_annotation, click_data, click_search,
                   end_date, start_date, query, walkby_next, walkby_prev, dwell_time, walkby_next_adjust,
                   walkby_prev_adjust, query_type, style_data_conditional, fn,
                   graph_state, walkby_ent, changed_data, labels_fig, progress_fig, active_layout, conflict_fig):
    exams = get_exampler(fn)
    pos = None
    if click_data is not None:
        points = click_data.get('points')
        pos = points[0]['id'] if points else None

    if graph_state != '':
        try:
            states = graph_state.split(',')
            pos = int(states[0])
            n_wn = int(states[1])
            n_wp = int(states[2])
            n_wna = int(states[3])
            n_wpa = int(states[4])
            if walkby_next and walkby_next > n_wn:
                pos = exams.get_next(pos, walkby_ent)
                if exams.record_change(changed_data):
                    patterns, counts = exams.count_labeled()
                    labels_fig = train.Train.stats_labels_figure(patterns, counts)
                    progress_fig = train.Train.stats_progress_figure(int((exams.num_labeled() / exams.tol_pos) * 100),
                                                                     progress_fig['data'][0]['value'])
            elif walkby_prev and walkby_prev > n_wp:
                pos = exams.get_prev(pos, walkby_ent)
                if exams.record_change(changed_data):
                    patterns, counts = exams.count_labeled()
                    labels_fig = train.Train.stats_labels_figure(patterns, counts)
                    progress_fig = train.Train.stats_progress_figure(int((exams.num_labeled() / exams.tol_pos) * 100),
                                                                     progress_fig['data'][0]['value'])
            elif walkby_next_adjust and walkby_next_adjust > n_wna:
                pos = exams.get_next(pos, walkby_ent)
            elif walkby_prev_adjust and walkby_prev_adjust > n_wpa:
                pos = exams.get_prev(pos, walkby_ent)
        except:
            pass

    start_time = start_date or exams.min_time
    end_time = end_date or exams.max_time
    if end_time == start_time:
        start_time = end_time - pd.to_timedelta('23h', unit='h')
    if active_layout == 'tab-time':
        fig, dt, tn, p, pos = exams.show_example(
            start_time=start_time,
            end_time=end_time,
            pos=pos,
            query=query,
            query_type=query_type,
            nsample=nsample,
            dwell_time=dwell_time or 5,
            alpha=alpha,
            bw_degree=bw_degree,
            fw_degree=fw_degree,
            ent_y=None if ent_y == 'none' else ent_y,
            ent_clr=None if ent_clr == 'none' else ent_clr,
            ent_text=None if ent_text == 'none' else ent_text,
            ent_size=None if ent_size == 'none' else ent_size,
            ent_prob=None if ent_size == 'none' else ent_prob,
            show_text=show_text,
            show_colorbar=show_color,
            show_prob=show_prob,
            relation_annotation=relation_annotation,
            show_y=show_y,
            show_size=show_size,
        )
    elif active_layout == 'tab-custom':
        fig, dt, tn, p, pos = exams.show_examples(
            start_time=start_time,
            end_time=end_time,
            pos=pos,
            query=query,
            query_type=query_type,
            nsample=nsample,
            dwell_time=dwell_time or 5,
            alpha=alpha,
            bw_degree=bw_degree,
            fw_degree=fw_degree,
            ent_x=None if ent_c_x == 'none' else ent_c_x,
            ent_y=None if ent_c_y == 'none' else ent_c_y,
            ent_clr=None if ent_c_clr == 'none' else ent_c_clr,
            ent_text=None if ent_c_text == 'none' else ent_c_text,
            ent_size=None if ent_c_size == 'none' else ent_c_size,
            ent_interval=None if ent_c_interval == 'none' else ent_c_interval,
            show_text=show_text,
            show_colorbar=show_color,
            show_prob=show_prob,
            relation_annotation=relation_annotation,
            show_y=show_y,
            show_size=show_size,
        )
    else:
        raise RuntimeError(f'{active_layout} not supported yet!')

    dt['row'] = list(range(len(dt)))
    if dt is not None:
        dt = dt.to_dict('rows')
    else:
        dt = []

    precision, recall, conflicts = exams.retrain(None, dwell_time)
    precision_fig = test.Test.stats_precisions_figure(precision.index.values, precision.values)
    recall_fig = test.Test.stats_recalls_figure(recall.index.values, recall.values)
    conflict_fig = test.Test.stats_conflict_figure(conflicts, conflict_fig['data'][0]['value'])

    graph_state = f'{pos if pos else 0},{walkby_next if walkby_next else 0},{walkby_prev if walkby_prev else 0},' \
                  f'{walkby_next_adjust if walkby_next_adjust else 0}, {walkby_prev_adjust if walkby_prev_adjust else 0}'
    return fig, dt, p, int(p[0] / 10) if len(p) > 0 else 0, style_data_conditional, f'Data: {len(dt)} ({tn})', \
           graph_state, labels_fig, progress_fig, precision_fig, recall_fig, conflict_fig
"""
