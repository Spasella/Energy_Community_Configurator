import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
import pandas as pd
import pandasql as ps
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, html, dcc
from plotly.offline import plot
from dash import Dash, dcc, html, Input, Output
from plotly.subplots import make_subplots
from datetime import date
import json
import requests
import random
import numpy as np

#app = dash.Dash(__name__,external_stylesheets = [dbc.themes.CYBORG])
app = dash.Dash(__name__, external_stylesheets = [dbc.themes.CYBORG])
server = app.server


#---CONSUMI QUARTORARI
consumi = pd.read_csv('hourly_consumption - 2022.csv', low_memory=False)
#print(consumi.columns)
lista_consumatori = list(consumi['ID_POD'].unique())


#---CONSUMI MENSILI

monthly_cons_query = '''
SELECT mese, ID_POD, ID_Utente, CAST(anno AS int) as anno, stabilimento, ROUND(SUM(consumi_kw_h), 2) as consumi_kw_h, date
FROM consumi
GROUP BY mese, anno, ID_POD, ID_Utente
ORDER BY date
'''
monthly_cons_df =  ps.sqldf(monthly_cons_query, locals())



#---PRODUZIONE ORARIA
produzione = pd.read_csv('hourly_prod - 2022.csv', low_memory=False)
#print(produzione.columns)
lista_moduli = list(produzione['config_name'].unique())


#---PRODUZIONE MENSILE
monthly_production_query = '''
SELECT mese, CAST(anno AS int) as anno, config_name, ROUND(SUM(prod), 2) as production_kwh, full_date_time
FROM produzione
GROUP BY mese, anno, config_name
ORDER BY full_date_time
'''
monthly_prod_df = ps.sqldf(monthly_production_query, locals())






PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
button = dbc.Row([
        dbc.Col(
            dbc.Button(
                "Search", color="primary", className="ms-2", n_clicks=0,
                href='https://dashcheatsheet.pythonanywhere.com/',
            ),
            width="auto",
        ),
    ], className="g-0 ms-auto flex-nowrap mt-3 mt-md-0", align="center",)
navbar = dbc.Navbar(dbc.Container([
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=PLOTLY_LOGO, height="40px")),
                        dbc.Col(dbc.NavbarBrand("CER - CONFIGURAZIONE PROFILI", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="https://plotly.com",
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                button,
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),]), color="#111111", dark=True,)



#               !!!LAYOUT SPACE!!!
app.layout = dbc.Container([
    html.Div(id = 'parent', children = [navbar]),
    html.Nav(id='nav', className='menu'),
    html.Br(),
    dbc.Col([
        dbc.Row([
            dbc.Col([
                html.Br(),
                dcc.Dropdown(
                        id='_dropdown_prod_',
                        multi=True,
                        options=[{'label': modulo, 'value': modulo} for modulo in lista_moduli],
                        value=['Modulo VE472PV ppw 160'],
                        placeholder='Select Modulo',
                        style={'color':'blue',
                               'background-color':'#111111',
                               'background':'#111111'}),

                html.Br(),
                dcc.Dropdown(
                    id='_dropdown_consumo_',
                    multi=True,
                    options=[{'label': consumatore, 'value': consumatore} for consumatore in lista_consumatori],
                    value=['IT001E04538845'],
                    placeholder='Select Profilo di consumo',
                    style={'color': 'blue',
                           'background-color': '#111111',
                           'background': '#111111'}),

                html.Br(),
                dcc.Dropdown(
                    id='_dropdown_anno_',
                    multi=True,
                    options=[2022],
                    value=[2022],
                    placeholder='Select Year',
                    style={'color': 'blue',
                           'background-color': '#111111',
                           'background': '#111111'}),


            ],xl=3, lg=3, md=3, sm=3, xs=3, style={'background-color':'#111111'}),

            dbc.Col([
                dbc.Row([
                    dbc.Col([dcc.Graph(id='linebar_chart')])
                    ])
        ],),
    ]),])


], fluid=True)


#                                    !!!CALLBACK SPACE!!!
#_____________________________________________________________________________________________


# 1- LINE CALLBACK
@app.callback(
    Output('linebar_chart', 'figure'),
    [Input('_dropdown_prod_', 'value'),
     Input('_dropdown_consumo_', 'value'),
     Input('_dropdown_anno_', 'value')]
)
def update_linebar_chart(filtro_prod, filtro_cons, filtro_anno):
    global filtro_anno_1
    fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": True}]])


    # LINEA DI PRODUZIONE
    filtro_anno_prod = monthly_prod_df[monthly_prod_df['anno'].isin(filtro_anno)]
    filtro_modulo_produzione = filtro_anno_prod[filtro_anno_prod['config_name'].isin(filtro_prod)]


    fig.add_trace(go.Scatter(x=filtro_modulo_produzione['mese'],
                             y=filtro_modulo_produzione['production_kwh'],
                             customdata=[filtro_modulo_produzione['anno']],
                             text=filtro_modulo_produzione['production_kwh']), secondary_y= False)

    #fig.update_yaxes(tickvals= random.sample(range(14000, 27000), 8))

    fig.update_yaxes(range=[0, 27000])



    # LINEA DI CONSUMI MODULO 1

    filtro_anno_1 = monthly_cons_df[monthly_cons_df['anno'].isin(filtro_anno)]
    if len(filtro_cons) == 1:
        df_1 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[0:1])]

        fig.add_trace(go.Scatter(x=df_1['mese'], y=df_1['consumi_kw_h'],
                                 text=df_1['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)




    # LINEA DI CONSUMI MODULO 2

    if len(filtro_cons) == 2:#Plotto il primo scatter
        df_1 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[0:1])]

        fig.add_trace(go.Scatter(x=df_1['mese'], y=df_1['consumi_kw_h'],
                                 text=df_1['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)


        # Plotto il secondo scatter sommandolo con i precedenti selezionati
        df_2 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[1:2])]


        fig.add_trace(go.Scatter(x=df_2['mese'], y=df_2['consumi_kw_h'],
                                 text=df_2['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)


    # LINEA DI CONSUMI MODULO 3

    if len(filtro_cons) == 3:  # Plotto il primo scatter
        df_1 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[0:1])]

        fig.add_trace(go.Scatter(x=df_1['mese'], y=df_1['consumi_kw_h'],
                                 text=df_1['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)


        # Plotto il secondo scatter sommandolo con i precedenti selezionati
        df_2 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[1:2])]

        fig.add_trace(go.Scatter(x=df_2['mese'], y=df_2['consumi_kw_h'],
                                 text=df_2['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)


        # Plotto il terzo scatter sommandolo con i precedenti plottati
        df_3 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[2:3])]


        fig.add_trace(go.Scatter(x=df_3['mese'], y=df_3['consumi_kw_h'],
                                 text=df_3['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)


    # LINEA DI CONSUMI MODULO 4

    if len(filtro_cons) == 4:  # Plotto il primo scatter
        df_1 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[0:1])]

        fig.add_trace(go.Scatter(x=df_1['mese'], y=df_1['consumi_kw_h'],
                                 text=df_1['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= False)

        # Plotto il secondo scatter sommandolo con i precedenti selezionati
        df_2 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[1:2])]


        fig.add_trace(go.Scatter(x=df_2['mese'], y=df_2['consumi_kw_h'],
                                 text=df_2['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= False)


        # Plotto il terzo scatter sommandolo con i precedenti plottati
        df_3 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[2:3])]

        fig.add_trace(go.Scatter(x=df_3['mese'], y=df_3['consumi_kw_h'],
                                 text=df_3['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= False)

        # Plotto il quarto scatter sommandolo con i precedenti plottati
        df_4 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[3:4])]

        fig.add_trace(go.Scatter(x=df_4['mese'], y=df_4['consumi_kw_h'],
                                 text=df_4['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= False)



    # LINEA DI CONSUMI MODULO 5

    if len(filtro_cons) == 5:  # Plotto il primo scatter
        df_1 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[0:1])]

        fig.add_trace(go.Scatter(x=df_1['mese'], y=df_1['consumi_kw_h'],
                                 text=df_1['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)

        # Plotto il secondo scatter sommandolo con i precedenti selezionati
        df_2 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[1:2])]

        fig.add_trace(go.Scatter(x=df_2['mese'], y=df_2['consumi_kw_h'],
                                 text=df_2['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)

        # Plotto il terzo scatter sommandolo con i precedenti plottati
        df_3 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[2:3])]

        fig.add_trace(go.Scatter(x=df_3['mese'], y=df_3['consumi_kw_h'],
                                 text=df_3['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)

        # Plotto il quarto scatter sommandolo con i precedenti plottati
        df_4 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[3:4])]

        fig.add_trace(go.Scatter(x=df_4['mese'], y=df_4['consumi_kw_h'],
                                 text=df_4['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)

        # Plotto il quinto scatter sommandolo con i precedenti plottati
        df_5 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[4:5])]

        fig.add_trace(go.Scatter(x=df_5['mese'], y=df_5['consumi_kw_h'],
                                 text=df_5['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)


    # LINEA DI CONSUMI MODULO 6

    if len(filtro_cons) == 6:  # Plotto il primo scatter
        df_1 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[0:1])]

        fig.add_trace(go.Scatter(x=df_1['mese'], y=df_1['consumi_kw_h'],
                                 text=df_1['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)

        # Plotto il secondo scatter sommandolo con i precedenti selezionati
        df_2 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[1:2])]

        fig.add_trace(go.Scatter(x=df_2['mese'], y=df_2['consumi_kw_h'],
                                 text=df_2['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)

        # Plotto il terzo scatter sommandolo con i precedenti plottati
        df_3 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[2:3])]

        fig.add_trace(go.Scatter(x=df_3['mese'], y=df_3['consumi_kw_h'],
                                 text=df_3['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)

        # Plotto il quarto scatter sommandolo con i precedenti plottati
        df_4 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[3:4])]

        fig.add_trace(go.Scatter(x=df_4['mese'], y=df_4['consumi_kw_h'],
                                 text=df_4['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)

        # Plotto il quinto scatter sommandolo con i precedenti plottati
        df_5 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[4:5])]

        fig.add_trace(go.Scatter(x=df_5['mese'], y=df_5['consumi_kw_h'],
                                 text=df_5['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)

        # Plotto il sesto scatter sommandolo con i precedenti plottati
        df_6 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[5:6])]

        fig.add_trace(go.Scatter(x=df_6['mese'], y=df_6['consumi_kw_h'],
                                 text=df_6['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)


    # LINEA DI CONSUMI MODULO 7

    if len(filtro_cons) == 7:  # Plotto il primo scatter
        df_1 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[0:1])]

        fig.add_trace(go.Scatter(x=df_1['mese'], y=df_1['consumi_kw_h'],
                                 text=df_1['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)

        # Plotto il secondo scatter sommandolo con i precedenti selezionati
        df_2 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[1:2])]

        fig.add_trace(go.Scatter(x=df_2['mese'], y=df_2['consumi_kw_h'],
                                 text=df_2['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)

        # Plotto il terzo scatter sommandolo con i precedenti plottati
        df_3 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[2:3])]
        frames = [df_1, df_2, df_3]

        fig.add_trace(go.Scatter(x=df_3['mese'], y=df_3['consumi_kw_h'],
                                 text=df_3['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)

        # Plotto il quarto scatter sommandolo con i precedenti plottati
        df_4 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[3:4])]

        fig.add_trace(go.Scatter(x=df_4['mese'], y=df_4['consumi_kw_h'],
                                 text=df_4['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)

        # Plotto il quinto scatter sommandolo con i precedenti plottati
        df_5 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[4:5])]

        fig.add_trace(go.Scatter(x=df_5['mese'], y=df_5['consumi_kw_h'],
                                 text=df_5['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode = 'lines',

                                 stackgroup='one'), secondary_y= True)

        # Plotto il sesto scatter sommandolo con i precedenti plottati
        df_6 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[5:6])]

        fig.add_trace(go.Scatter(x=df_6['mese'], y=df_6['consumi_kw_h'],
                                 text=df_6['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode='lines',

                                 stackgroup='one'), secondary_y= True)

        # Plotto il settimo scatter sommandolo con i precedenti plottati
        df_7 = filtro_anno_1[filtro_anno_1['ID_POD'].isin(filtro_cons[6:7])]

        fig.add_trace(go.Scatter(x=df_7['mese'], y=df_7['consumi_kw_h'],
                                 text=df_7['consumi_kw_h'],
                                 hoverinfo='x+y',
                                 mode='lines',

                                 stackgroup='one'), secondary_y= True)




    fig.update_layout(hovermode="x unified")
    fig.update_layout(template='plotly_dark')
    return fig



if __name__ == '__main__':
    app.run_server(debug = False)
