# _*_ coding: utf_8 _*_
"""
Created on Fri Sep 11 00:00:03 2020

@author: Michael Ou
"""
import urllib
import uuid
from collections import OrderedDict

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_uploader as du


def uploadlayout():
    upload_style = {
        'width':'400px', 'height':'133px',
        # 'background-image':'url("/assets/upload.png")',
        # 'background-attachment': 'fixed',
        # 'background-size': 'cover',
    }

    upload_id = uuid.uuid1()

    def get_upload_component(id):
        return du.Upload(
            id=id,
            max_file_size=1800,  # 1800 Mb
            filetypes=['csv', 'zip', 'cio'],
            upload_id=upload_id, #uuid.uuid1(),  # Unique session id
            default_style=upload_style,
        )

    return html.Div([
        html.Div(id='msg_uploader'),
        html.Div([
            'Instruction: Compress "file.cio", "output.*" and/or "usgs.csv" (optional) '\
            'into a zip file and upload here',
            get_upload_component(id='uploader')
        ]),

    ])

def subplot(index=0):

    comp_with = 2

    output = dbc.Col(
        dcc.Dropdown(
            id={'type': 'plot-output', 'index': index},
            placeholder='Output Type',
            options=[
            ],
        ),
        id={'type': 'menu', 'index': 10*int(index)+1,},
        md=comp_with,
        xs=comp_with*3,
    )

    var = dbc.Col(
        dcc.Dropdown(
            multi=True,
            id={'type': 'plot-variable', 'index': index},
            placeholder='Variable',
            options=[
            ],
        ),
        id={'type': 'menu', 'index': 10*int(index)+2,},
        md=comp_with,
        xs=comp_with*3,
    )

    location = dbc.Col(
        dcc.Dropdown(
            multi=True,
            id={'type': 'plot-location', 'index': index},
            placeholder='Unit',
            options=[
            ],
        ),
        id={'type': 'menu', 'index': 10*int(index)+3,},
        md=comp_with,
        xs=comp_with*3,
    )

    freq = dbc.Col(
        dcc.Dropdown(
            id={'type': 'plot-freq', 'index': index},
            placeholder='Frequency',
            options=[
            ],
        ),
        id={'type': 'menu', 'index': 10*int(index)+4,},
        md=comp_with,
        xs=comp_with*3,
    )

    agg = dbc.Col(
        dbc.Checklist(
            id={'type': 'plot-sumspace', 'index': index},
            options=[
                {"label": "Areal mean", "value": 1},
            ],
            value=[],
            className='ml-1',
        ),
        id={'type': 'menu', 'index': 10*int(index)+5,},
        md=comp_with,
        xs=comp_with*3,
    )

    export = dbc.Col(
        html.A(
            'Download Data',
            id={'type': 'plot-download', 'index': index},
            download="swatoutput.csv",
            href="",
            target="_blank",
            className='ml-1',
        ),
        id={'type': 'menu', 'index': 10*int(index)+6,},
        md=comp_with,
        xs=comp_with*3
    )

    plot = dcc.Graph(id={'type': 'plot-chart', 'index': index}, figure={'layout':{'margin':{'l':0,'r':0,'t':0,'b':0}}})

    return html.Div(dcc.Loading([
        dbc.Row([output, location, var, freq, agg, export],
            no_gutters=True, align='center', justify='center'), #
        plot
    ]), id={'type': 'subplot', 'index': index}, className='my-2 mx-1')


def chartlayout():
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(dbc.Button('Add Subplot', id='add-sub',   color='primary', outline=True, block=True), md=3),
                    dbc.Col(dbc.Button('Remove Subplot', id='rm-sub', color='primary', outline=True, block=True), md=3),
                    dbc.Col(dbc.Select(
                        id='n-column',
                        options=[
                            {'label': 'One Column', 'value': 1},
                            {'label': 'Two Columns', 'value': 2},
                            {'label': 'Three Columns', 'value': 3},
                            {'label': 'Four Columns', 'value': 4},
                            {'label': 'Six Columns', 'value': 6},

                        ],
                        value=1,
                    ),  md=3),
                    dbc.Col(dbc.Button('Load Data', id='load-data',   color='primary', outline=True, block=True), md=3),
                ],
                no_gutters=False,
                align='center',
                justify='center',
                form=True,
            ),
            html.Div(id='chart-area', className='row mt-2',
                children=[
                    subplot()
                ]
            ),
            html.Div(1, id='nplot', style={'display': 'none'})
        ]
    )

def statlayput():
    return html.H1(
        'This page is under construction. Go to "Upload".'
    )

def homelayout():
    return html.H1(
        'This page is under construction. Go to "Chart".'
    )

pages = OrderedDict(
    Home =          dict(href="/",           page=homelayout()),
    Upload =        dict(href="/upload/",    page=uploadlayout()),
    Chart =         dict(href="/chart/",     page=chartlayout()),
    Statistics =    dict(href="/stat/",      page=statlayput()),
)


def maintabs():
    '''using tabs instead'''


    content = html.Div([
        html.Div([
            html.H3("SWAT Output Viewer", className="display-4"),
            html.Hr(),
            html.P(
                "An efficient app to investigate SWAT model outputs.", className="lead"
            )
            ],
            style={"background-color": "#f8f9fa"}
        ),
        dcc.Tabs(
            # style=SIDEBAR_STYLE,
            className='p-1',
            # style={'height': '44px', 'align-items': 'center'},
            content_className='p-1',
            children=[
                dcc.Tab(label=k, children=v['page'], style={'padding': '10px'}, selected_style={'padding': '10px'}) for k, v in pages.items()
            ]

        )
    ])



    return html.Div([
        # dcc.Store(id='storage_cio', storage_type='session'),
        content,
        dcc.Loading(dcc.Store(id='storage_output', storage_type='session')),
        dcc.Location(id="url"),
    ])
