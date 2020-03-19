# -*- coding: utf-8 -*-
import sqlite3

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dte
import pandas as pd
import plotly
import plotly.graph_objs as go
from dash.dependencies import Output, Input

from Config import RunConfig
from tweetsSideCounter import TweetsSideCounter

gvalue = 1000
gstop = False
old_df_pie = None
old_df_tweets = None
old_df_scatter = None
resampleValue = "300L"
app_colors = {
    'pageBackground': '#272B30',
    'background': '#0C0F0A',
    'text': '#6699ff',
    'sentiment-plot': '#41EAD4',
    'volume-bar': '#6699ff',
    'someothercolor': '#80aaff',
    'papercolor': '#1E2022',
    'plotcolor': '#262626',
    'fillcolor': '#ff6666',
    'gridcolor': '#737373',
    'backgroundTableHeaders': '#001133',
    'backgroundTableRows': '#002266'
}
tweetsCounter = TweetsSideCounter()
PositiveNegativeThreshold = RunConfig.positiveNegativeThreshold

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.config.suppress_callback_exceptions = True

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        dbc.NavbarSimple(
            children=[
                dbc.NavLink("home", href="/", id="page-1-link"),
                dbc.NavLink(" وزارة أبشر", href="/Absher", id="page-2-link"),
                dbc.NavLink("وزارة الصحه", href="/SaudiMOH", id="page-3-link"),
                dbc.NavLink("وزارة الاسكان", href="/SaudiHousingCC", id="page-4-link"),
                dbc.NavLink("وزارة التعليم", href="/moegovsa", id="page-5-link"),
            ],
            brand="Live Twitter Sentiment",
            color="primary",
            dark=True,
        ),
        dbc.Container(id="page-content", className="pt-4"),
    ]
)


def layout(currentKeyWordsString):
    return html.Div(

        ### Inputs initialization
        [html.Div(className='container-fluid', children=[html.H2('Live Twitter Sentiment', style={'color': "#CECECE"}),
                                                         html.H5('Sentiment Term:',
                                                                 style={'color': app_colors['text'], 'margin-top': 0,
                                                                        'margin-bottom': 0}),
                                                         dcc.Input(id='sentiment_term', value=currentKeyWordsString,
                                                                   type='text',
                                                                   style={'width': 300,
                                                                          'color': app_colors['someothercolor'],
                                                                          'margin-top': 0, 'margin-bottom': 0}),
                                                         html.Button('Submit', id='buttonKeyWords'),
                                                         ],
                  style={'width': '98%', 'margin-left': 15, 'margin-right': 15, 'max-width': 50000}
                  ),

         html.Div(className='container-fluid',
                  children=[
                      html.H5('Window:', style={'color': app_colors['text'], 'margin-top': 0, 'margin-bottom': 0}),
                      html.Div(className='row', children=
                      [dcc.Input(id='window', value=str(gvalue), type='text',
                                 style={'width': 300,
                                        'color': app_colors['someothercolor'],
                                        'margin-top': 0, 'margin-bottom': 0}),
                       html.Button('Submit', id='buttonWindow'),
                       html.Div(id='output-container-button', children='Enter a value and press submit')
                       ],
                               ),
                      html.Div(className='row', children=
                      [
                          html.Button('Toggle Live', id='buttonStop'),
                          html.Div(id='output-container-stop-button', children='Enter a value and press submit')
                      ],
                               style={'margin-top': 10}
                               ),
                  ],
                  style={'width': '98%', 'margin-left': 30, 'margin-right': 30, 'max-width': 50000}
                  ),

         ### Historical scatter plot initialization

         html.Div(className='two columns', children=[html.Div(dcc.Graph(id='live-graph', figure={'layout': go.Layout(
             xaxis={'showgrid': False},
             yaxis={'title': 'Volume', 'side': 'right'},
             yaxis2={'side': 'left', 'overlaying': 'y',
                     'title': 'Sentiment', 'gridcolor': app_colors['gridcolor']},
             font={'color': app_colors['text'], 'size': 18},
             plot_bgcolor=app_colors['plotcolor'],
             paper_bgcolor=app_colors['papercolor'],
             showlegend=False,
         )}, animate=False), style={'display': 'inline-block',
                                    'width': '66%', 'margin-right': -15}
                                                              ),
                                                     html.Div(dcc.Graph(id='pie-graph', figure={'layout': go.Layout(
                                                         xaxis={'showgrid': False},
                                                         yaxis={'gridcolor': app_colors['gridcolor']},
                                                         font={'color': app_colors['text'], 'size': 18},
                                                         plot_bgcolor=app_colors['plotcolor'],
                                                         paper_bgcolor=app_colors['papercolor'],
                                                         showlegend=False,
                                                     )}, animate=False),
                                                              style={'display': 'inline-block', 'width': '34%',
                                                                     'margin-left': -40, 'margin-right': 0}
                                                              )
                                                     ],
                  style={'display': 'inline-block', 'height': 400, 'width': '100%', 'margin-left': 10,
                         'margin-right': 10,
                         'max-width': 50000}
                  ),

         ### Table initialization

         html.Div(id="recent-tweets-table", children=[
             html.Thead(html.Tr(children=[], style={'color': app_colors['text']})),
             html.Tbody([html.Tr(children=[], style={'color': app_colors['text'],
                                                     'background-color': app_colors['backgroundTableRows'],
                                                     'border': '0.2px', 'font - size': '0.7rem'}
                                 )])],
                  className='col s12 m6 l6', style={'width': '98%', 'margin-top': 30, 'margin-left': 15,
                                                    'margin-right': 15, 'max-width': 500000}),

         # html.Div(className="row", children=[dte.DataTable(id="dashTable", rows=[{}],
         #                        row_selectable=True,
         #                        filterable=True,
         #                        sortable=True
         #                       )],
         #          style={'width': '98%', 'margin-top': 50, 'margin-left': 15, 'margin-right': 15, 'max-width': 500000},
         #          ),

         ### Updates intervals

         dcc.Interval(
             id='graph-update',
             interval=1 * 1000
         ),

         dcc.Interval(
             id='pie-update',
             interval=5 * 1000
         ),

         dcc.Interval(
             id='recent-table-update',
             interval=2 * 1000
         ),

         dcc.Interval(
             id='dashTableUpdate',
             interval=2 * 1000
         ),

         ], style={'backgroundColor': app_colors['pageBackground'], 'margin-top': '-20px',
                   'margin-left': -10, 'margin-right': -10, 'height': '2000px', },
    )


def quick_color(s):
    # except return bg as app_colors['background']
    if s >= PositiveNegativeThreshold:
        # positive
        return "#1f7a1f"
    elif s <= -PositiveNegativeThreshold:
        # negative:
        return "#b30000"

    else:
        return app_colors['background']


########

@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 4)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False
    return [pathname == f"/page-{i}" for i in range(1, 4)]


img_style = {"width": "200px",
             "margin": "auto"}
card_style = {"margin": "auto", "height": "200px", "width": "200px"}
card_link = {"margin-bottom": "50px"}
card1 = dcc.Link(
    dbc.Card(
        [
            dbc.CardImg(src="https://proven-sa.com/wp-content/uploads/2016/09/Absher-logo.png", style=img_style)
        ],
        style=card_style,
        id="card1-btn"
    ), href='/Absher',
    style=card_link,
)

card2 = dcc.Link(
    dbc.Card(
        [
            dbc.CardImg(src="https://www.moh.gov.sa/_layouts/15/MOH/Internet/New/images/logo.png",
                        top=True, style=img_style)
        ],
        style=card_style,
        id="card1-btn"
    ), href='/SaudiMOH',
    style=card_link,
)
card3 = dcc.Link(
    dbc.Card(
        [
            dbc.CardImg(src="https://www.housing.gov.sa/sites/all/themes/moh/images/Ministry-Logo.svg",
                        top=True, style=img_style)
        ],
        style=card_style,
        id="card1-btn"
    ), href='/SaudiHousingCC',
    style=card_link,
)
card4 = dcc.Link(
    dbc.Card(
        [
            dbc.CardImg(src="https://www.moe.gov.sa/_layouts/15/MOEResp/ar-SA/Images/MOELogo.png",
                        top=True, style=img_style)
        ],
        style=card_style,
        id="card1-btn"
    ), href='/moegovsa',
    style=card_link,
)

# @app.callback(
#     Output("example-output", "children"), [Input("card1-btn", "n_clicks")]
# )
# def on_button_click(n):
#     if n is None:
#         return "Not clicked."
#     else:
#         return f"Clicked {n} times."

home = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Div(card1), style=card_link),
                dbc.Col(html.Div(card2), style=card_link),
            ],
            align="start",
        ),
        dbc.Row(
            [
                dbc.Col(html.Div(card3), style=card_link),
                dbc.Col(html.Div(card4), style=card_link),
            ],
            align="center",
        ),
        # dbc.Row(
        #     [
        #         dbc.Col(html.Div(card1)),
        #         dbc.Col(html.Div(card1)),
        #     ],
        #     align="end",
        # ),
    ]
)


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    global old_df_pie
    global old_df_tweets
    global old_df_scatter
    if pathname in ["/"]:
        old_df_pie = None
        old_df_tweets = None
        old_df_scatter = None
        return home
    if pathname in ["/", "/Absher"]:
        old_df_pie = None
        old_df_tweets = None
        old_df_scatter = None
        RunConfig.dbName = "Absher.db"
        # RunConfig.dbName = "rump.db"
        return layout("Absher")
    elif pathname == "/SaudiMOH":
        old_df_pie = None
        old_df_tweets = None
        old_df_scatter = None
        RunConfig.dbName = "SaudiMOH.db"
        return layout("SaudiMOH")
    elif pathname == "/SaudiHousingCC":
        old_df_pie = None
        old_df_tweets = None
        old_df_scatter = None
        RunConfig.dbName = "SaudiHousingCC.db"
        return layout("SaudiHousingCC")
    elif pathname == "/moegovsa":
        old_df_pie = None
        old_df_tweets = None
        old_df_scatter = None
        RunConfig.dbName = "moe_gov_sa.db"
        return layout("moegovsa")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


# #########


@app.callback(dash.dependencies.Output('output-container-button', 'children'),
              [dash.dependencies.Input('buttonWindow', 'n_clicks')],
              [dash.dependencies.State('window', 'value')], )
def update_output(n_clicks, value):
    global gvalue
    gvalue = int(value)

    global resampleValue
    resampleValue = "300L"
    if (gvalue > 0) and (gvalue <= 100):
        resampleValue = "300L"
    if (gvalue > 100) and (gvalue <= 200):
        resampleValue = "500L"
    elif (gvalue > 200) and (gvalue <= 1000):
        resampleValue = "1s"
    elif (gvalue > 1000) and (gvalue <= 2000):
        resampleValue = "4s"
    elif (gvalue > 2000) and (gvalue <= 5000):
        resampleValue = "10s"
    elif (gvalue > 5000) and (gvalue <= 10000):
        resampleValue = "15s"
    elif (gvalue > 10000):
        resampleValue = "30s"

    print("Window: " + str(gvalue) + " Resample: " + str(resampleValue))


@app.callback(dash.dependencies.Output('output-container-stop-button', 'children'),
              [dash.dependencies.Input('buttonStop', 'n_clicks')], )
def update_output(n_clicks):
    if n_clicks:
        global gstop
        gstop = not gstop


@app.callback(Output('live-graph', 'figure'),
              [Input(component_id='sentiment_term', component_property='value'),
               Input(component_id='window', component_property='value'),
               Input("graph-update", "n_intervals")
               ],
              # events=[Event('graph-update', 'interval')],
              )
def update_graph_scatter(sentiment_term, window, n):
    global gstop
    global old_df_scatter
    try:
        if gstop:
            df = old_df_scatter
        else:

            conn = sqlite3.connect(RunConfig.dbName)
            df = pd.read_sql("SELECT * FROM %s ORDER BY UnixTime DESC LIMIT %s" % (RunConfig.tableName, gvalue), conn)
            old_df_scatter = df
        if len(df) > 0:
            df.sort_values('UnixTime', inplace=True)
            df['sentiment_smoothed'] = df['Polarity'].rolling(int(len(df) / 5)).mean()
            df['Date'] = pd.to_datetime(df['UnixTime'], unit='ms')

            df.set_index('Date', inplace=True)
            df["Volume"] = 1
            df = df.resample(resampleValue).agg({'Polarity': 'mean', 'sentiment_smoothed': 'mean', 'Volume': 'sum'})
            df.Polarity = df.Polarity.fillna(method="ffill")
            df.sentiment_smoothed = df.sentiment_smoothed.fillna(method="ffill")
            df.Volume = df.Volume.fillna(0)
            df.dropna(inplace=True)

            X = df.index
            Y = df.sentiment_smoothed
            Y2 = df.Volume

            dataScatter = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Scatter',
                mode='lines+markers',
                marker={'size': 4, 'opacity': 0.6},
                yaxis='y2',
                line={'width': 1}
            )

            dataVolume = plotly.graph_objs.Bar(
                x=X,
                y=Y2,
                name='Volume',
                marker=dict(color=app_colors['volume-bar'], opacity=0.5),
            )

            return {'data': [dataScatter, dataVolume], 'layout': go.Layout(
                title='Live sentiment(moving average)',
                xaxis={'range': [min(X), max(X)], 'showgrid': False},
                # yaxis={'range': [min(Y),max(Y)], 'gridcolor': app_colors['gridcolor']},
                yaxis={'range': [min(Y2), max(Y2 * 4)], 'title': 'Volume', 'side': 'right'},
                yaxis2={'range': [min(Y), max(Y)], 'side': 'left', 'overlaying': 'y', 'title': 'Sentiment',
                        'gridcolor': app_colors['gridcolor']},
                font={'color': app_colors['text']},
                plot_bgcolor=app_colors['plotcolor'],
                paper_bgcolor=app_colors['papercolor'],
                showlegend=False,
            )}

    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write("update_graph_scatter: " + str(e))
            f.write('\n')


def generate_table(df, max_rows=20):
    return html.Table(className="responsive-table",
                      children=[
                          html.Thead(
                              html.Tr(
                                  children=[
                                      html.Th(col.title()) for col in df.columns.values],
                                  style={'color': app_colors['text'],
                                         'background-color': app_colors['backgroundTableHeaders']}
                              )
                          ),
                          html.Tbody(
                              [
                                  html.Tr(
                                      children=[
                                          html.Td(data) for data in d
                                      ], style={'color': app_colors['text'],
                                                'background-color': quick_color(d[2]),
                                                'border': '0.2px', 'font - size': '0.7rem'}
                                  )
                                  for d in df.values.tolist()])
                      ]
                      )


def generateDashDataTable2(df):
    dte.DataTable(
        data=df.to_dict("rows"),
        columns=[
            {"name": i, "id": i} for i in df.columns
        ],
        style_data_conditional=[{
            "if": {"row_index": 4},
            "backgroundColor": "#3D9970",
            'color': 'white'
        }]
    )


def generateDashDataTable(df):
    return df.to_dict("rows")


@app.callback(Output('recent-tweets-table', 'children'),
              [Input(component_id='sentiment_term', component_property='value'),
               Input("recent-table-update", "n_intervals")
               ],
              # events=[Event('recent-table-update', 'interval')]
              )
def update_recent_tweets(sentiment_term, n):
    global gstop
    global old_df_tweets
    genTable = html.Table()
    try:
        if gstop:
            df = old_df_tweets
        else:
            conn = sqlite3.connect(RunConfig.dbName)
            df = pd.read_sql(
                "SELECT UnixTime, Tweet, Polarity FROM %s ORDER BY UnixTime DESC LIMIT 20" % (RunConfig.tableName),
                conn)
            old_df_tweets = df
        if len(df) > 0:
            df['Date'] = pd.to_datetime(df['UnixTime'], unit='ms')

            df = df.drop(['UnixTime'], axis=1)
            df = df[['Date', 'Tweet', 'Polarity']]
            df.Polarity = df.Polarity.round(3)

            genTable = generate_table(df, max_rows=10)

    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write("update_recent_tweets: " + str(e))
            f.write('\n')

    return genTable


@app.callback(Output('pie-graph', 'figure'),
              [Input(component_id='sentiment_term', component_property='value'),
               Input("pie-update", "n_intervals")
               ],
              # events=[Event('pie-update', 'interval')],
              )
def updatePieChart(sentiment_term, n):
    global gstop
    global old_df_pie
    df = pd.DataFrame()
    try:
        if gstop:
            df = old_df_pie
        else:
            conn = sqlite3.connect(RunConfig.dbName)
            # df = pd.read_sql("SELECT count(case when Polarity > 0 then 1 else null end) as Positive, \
            #        count(case when Polarity < 0 then 1 else null end) as Negative from %s"  % (RunConfig.tableName), conn)

            df = pd.read_sql("SELECT count(case when Polarity > 0 then 1 else null end) as Positive, \
                    count(case when Polarity < 0 then 1 else null end) as Negative from \
                    (select Polarity from %s where abs(Polarity)>=%s \
                     ORDER BY UnixTime DESC limit %s) as a" % (RunConfig.tableName, PositiveNegativeThreshold, gvalue),
                             conn)

            old_df_pie = df
        if len(df) > 0:
            values = [round(100 * df.Positive.iloc[0] / (df.Positive.iloc[0] + df.Negative.iloc[0]), 2),
                      round(100 * df.Negative.iloc[0] / (df.Positive.iloc[0] + df.Negative.iloc[0]), 2)]
        else:
            values = [50, 50]
        colors = ['#007F25', '#800000']
        labels = ['Positive', 'Negative']

        trace = go.Pie(labels=labels, values=values,
                       hoverinfo='label+percent', textinfo='value',
                       textfont=dict(size=20, color=app_colors['text']),
                       marker=dict(colors=colors,
                                   line=dict(color=app_colors['background'], width=2)))

        return {"data": [trace], 'layout': go.Layout(
            title='Positive vs Negative (Count)',
            font={'color': app_colors['text']},
            plot_bgcolor=app_colors['plotcolor'],
            paper_bgcolor=app_colors['papercolor'],
            showlegend=True)}

    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write("updatePieChart: " + str(e))
            f.write('\n')

    return df


if __name__ == "__main__":
    app.run_server(port=8888)
