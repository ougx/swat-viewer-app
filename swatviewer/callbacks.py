# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 00:06:07 2020

@author: Michael Ou
"""

import base64
import io
import os
from urllib.parse import quote
from zipfile import ZipFile

import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from dash import callback_context, no_update
from dash.dependencies import ALL, MATCH, Input, Output, State

from config import UPLOAD_FOLDER_ROOT
from .layout import subplot
from .swat_output_reader import read_cio, read_output


def load_output(isCompleted, fileNames, upload_id):
    """read the uploaded zipfile

    Args:
        isCompleted (bool): whether the update is completed
        fileNames (str): file name of the zipfile
        upload_id (str): subfolder of the upload which is the session id

    Returns:
        data: a dcc.store
    """

    if not isCompleted:
        return no_update

    acceptable_outputs = ['output.sub', 'output.hru', 'output.rch']

    filename = fileNames[0]

    output_dir = os.path.join(UPLOAD_FOLDER_ROOT, upload_id)
    filename = os.path.join(output_dir, filename)

    if not filename.strip().endswith('.zip'):
        return [no_update,
            dbc.Modal([
                dbc.ModalHeader(dbc.Alert("Error", color="danger")),
                dbc.ModalBody('This must be a zip file with the file extension ".zip".'),
            ], is_open=True)
        ]

    with ZipFile(filename, 'r') as zipfile:

        error = False

        files = zipfile.namelist()

        include_cio = False
        for f in files:
            if f.strip().endswith('file.cio'):
                include_cio = True

        if not include_cio:
            error = True
            results = [no_update,
                dbc.Modal([
                    dbc.ModalHeader(dbc.Alert('Error: "file.cio" must be included in the zipfile.', color="danger")),
                    # dbc.ModalBody('"file.cio" must be included in the zipfile.'),
                ], is_open=True)
            ]

        if not error:
            include_output = False
            for f in files:
                if f.strip() in acceptable_outputs:
                    include_output = True

            if not include_output:
                error = True
                results = [no_update,
                    dbc.Modal([
                        dbc.ModalHeader(dbc.Alert(f"No output.* file is found in the zip file.", color="danger")),
                        dbc.ModalBody(
                            'Acceptable files include: ' + ', '.join(acceptable_outputs)
                        ),
                    ], is_open=True)
                ]

        # no errors read cio and save it
        if not error:
            with io.TextIOWrapper(zipfile.open('file.cio'), encoding='utf-8') as f:
                data = read_cio(f.read())

            data['outputs'] = {}
            for file in files:
                file = file.strip()
                if file in acceptable_outputs:
                    with zipfile.open(file) as f:
                        read_output(
                            f, file[-3:], data['ICALEN'], data['IPRINT'], data['output_start_date']
                        ).to_csv(os.path.join(output_dir, file[-3:] + '.csv'))
                    data['outputs'][file[-3:]] = os.path.join(output_dir, file[-3:] + '.csv')

            results = [
                data,
                dbc.Modal([
                    dbc.ModalHeader(dbc.Alert("Upload completed! See details below.", color="success")),
                    dbc.ModalBody([html.P(f'{k}: {v}') for k,v in data.items()]),
                ], is_open=True)
            ]

    os.remove(filename)
    return results


def add_remove_sub(nadd, nrm, plots):
    """add or remove a subplot

    Args:
        nadd (int): add button
        nrm (int): remove button
        plots (list): current subplots

    Returns:
        list: new subplot list after adding or removeing a subplot
    """
    ctx = callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'add-sub' and nadd:
        if nadd > 0:
            return plots + [subplot(len(plots))], len(plots) + 1

    if button_id == 'rm-sub' and nrm:
        if nrm > 0:
            if len(plots) > 1:
                return plots[:-1], len(plots) - 1

    return no_update


def change_columns(ncol, nplot):
    """change the column number of subplots in one row

    Args:
        ncol (int): column number per row
        nplot (int): subplot number

    Returns:
        list: subplot width
        list: width for subplot menus
    """
    nplot = int(nplot)
    return [[f'col-lg-{12//int(ncol)}'] * nplot, [2*int(ncol)] * nplot * 6]


def load_output_type(data, nplot):
    """load the output type dropdown menu

    Args:
        data (dict): data store
        nplot (str): number of subplots

    Returns:
        dropdown options and value: update the output type dropdown menu
    """
    if data:
        if 'outputs' in data:
            nplot = int(nplot)
            return [
                [[{'label':k, 'value':k} for k in data['outputs'].keys()]] * nplot,
                [list(data['outputs'].keys())[0]] * nplot
            ]
    return no_update

def load_output_variables(output, data):
    """load other subplot menus

    Args:
        output (str): the value of the output type dropdown
        data (dict): dcc.store

    Returns:
        list: options and values for other subplot menu
    """
    try:
        # print(output)
        # print(data)
        if output and data:
            # df = load_outputs_from_local(data, 'output.' + output)
            # if output in session:
            if 'outputs' in data:
                if os.path.exists(data['outputs'][output]):

                    df = pd.read_csv(data['outputs'][output], nrows=1, index_col=0)
                    vars = df.columns[2:]

                    all_locs = pd.read_csv(data['outputs'][output], usecols=[output.upper()], squeeze=True)
                    locs = all_locs.unique()
                    # print([[{'label': output + '-' + str(v), 'value':v} for v in locs]])

                    iprint = int(data['IPRINT'])
                    if iprint == 0:
                        freq_opt = [
                            {'label':'Monthly', 'value':'M.'},
                            {'label':'Annual mean', 'value':'A.mean'},
                            {'label':'Annual sum', 'value':'A.sum'},
                        ]
                        freq_val = 'M.'
                    elif iprint == 1:
                        freq_opt = [
                            {'label':'Daily', 'value':'D.'},
                            {'label':'Monthly mean', 'value':'M.mean'},
                            {'label':'Monthly sum', 'value':'M.sum'},
                            {'label':'Annual mean', 'value':'A.mean'},
                            {'label':'Annual sum', 'value':'A.sum'},
                        ]
                        freq_val = 'D.'
                    else:
                        freq_opt = [{'label':'Yearly', 'value':'A.'}]
                        freq_val = 'A.'

                    # sumspace_option = [
                    #     {'label':'Sum ' + output.upper(), 'value':0}
                    # ]

                    return [
                        [{'label':v, 'value':v} for v in vars],
                        [vars[0]],
                        [{'label': output + '-' + str(v), 'value':v} for v in locs],
                        [locs[0]],
                        freq_opt,
                        freq_val,
                        # sumspace_option
                    ]
    except Exception as e:
        print(e)
        return no_update

    return no_update

def filter_data(output, units, vars, freq, sumspace, data):
    #TODO 1: add USGS observations when it is plotting streamflows
    if output and units and vars and freq and data:

        var_s = ['time', output.upper(), 'AREAkm2'] + vars
        df0 = pd.read_csv(data['outputs'][output], index_col='time', usecols=var_s, parse_dates=True)
        df = df0.loc[ df0[output.upper()].isin(units) ].drop('AREAkm2', axis=1)

        freqs = freq.split('.')
        if freqs[1]:
            df = df.groupby(output.upper()).resample(freqs[0]).agg(freqs[1]).drop(output.upper(), axis=1)
        else:
            df = df.reset_index().set_index([output.upper(), 'time'])

        # calculate the area-weighted mean
        if sumspace:
            df_sum = 0
            area = df0.loc[df0.index[0], [output.upper(), 'AREAkm2']].set_index(output.upper()).squeeze()
            total_area = 0
            print(area)
            for u in units:
                print(df.loc[u] , area.loc[u])
                df_sum += df.loc[u] * area.loc[u]
                total_area += area.loc[u]
            df = df_sum / total_area
            df[output.upper()] = 'all'
            df = df.reset_index().set_index([output.upper(), 'time'])
    else:
        df = None

    return df

def make_plot(output, units, vars, freq, sumspace, data):
    """make plot based on the dropdown menu values

    Args:
        output (str): output type (sub, rch or hru)
        units (list): spatial units for the plot
        vars (list): variable names for the plot
        freq (str): frequqncy and the aggregation method
        data (dict): dcc.store

    Returns:
        subplot's figure
        down link for the csv having the plot data
    """
    #TODO 1: add USGS observations when it is plotting streamflows
    df = filter_data(output, units, vars, freq, sumspace, data)
    if df is not None:
        if sumspace:
            units = ['all']
        fig_data = []
        for u in units:
            for v in vars:
                fig_data.append(
                    go.Scatter(
                        name=v + ', ' + str(u),
                        x=df.loc[u][v].index,
                        y=df.loc[u][v].values,
                        showlegend=True,
                        mode='lines',
                    )
                )

        fig_layout = go.Layout(
            margin=dict(
                l=40, r=0, t=10, b=40
            ),
            xaxis=dict(
                visible=True
            ),
            yaxis=dict(
                visible=True
            ),
            legend=dict(
                x=1.01,
                y=0.5,
            )
        )

        # csv download
        # https://community.plotly.com/t/download-raw-data/4700/8
        csv_string = df.to_csv(encoding='utf-8')
        csv_string = "data:text/csv;charset=utf-8," + quote(csv_string)

        return {'data': fig_data, 'layout':fig_layout}, csv_string
    return no_update



def add_callbacks(app):

    # read uploaded output
    app.callback(
        [Output('storage_output', 'data'), Output('msg_uploader', "children")],
        [Input('uploader', 'isCompleted')],
        [State('uploader', 'fileNames'),
        State('uploader', 'upload_id')],
    )(load_output)

    # add or remove subplots
    app.callback(
        [Output('chart-area', 'children'), Output('nplot', 'children')],
        [Input('add-sub', 'n_clicks'), Input('rm-sub', 'n_clicks')],
        State('chart-area', 'children')
    )(add_remove_sub)

    # change column number of subplots
    app.callback(
        [Output({'type': 'subplot', 'index': ALL}, 'className'), Output({'type': 'menu', 'index': ALL}, 'md')],
        Input('n-column', 'value'),
        State('nplot', 'children')
    )(change_columns)

    # load output dropdown
    app.callback(
        [Output({'type': 'plot-output', 'index': ALL}, 'options'), Output({'type': 'plot-output', 'index': ALL}, 'value')],
        [Input('storage_output', 'data')],
        State('nplot', 'children')
    )(load_output_type)

    # load variable and location dropdown
    app.callback(
        [Output({'type': 'plot-variable', 'index': MATCH}, 'options'), Output({'type': 'plot-variable', 'index': MATCH}, 'value'),
         Output({'type': 'plot-location', 'index': MATCH}, 'options'), Output({'type': 'plot-location', 'index': MATCH}, 'value'),
         Output({'type': 'plot-freq',     'index': MATCH}, 'options'), Output({'type': 'plot-freq',     'index': MATCH}, 'value'),
        #  Output({'type': 'plot-sumspace', 'index': MATCH}, 'options')
        ],
        Input({'type': 'plot-output', 'index': MATCH}, 'value'),
        State('storage_output', 'data')
    )(load_output_variables)

    # make plot
    app.callback(
        [Output({'type': 'plot-chart',    'index': MATCH}, 'figure'),
         Output({'type': 'plot-download', 'index': MATCH}, 'href')],
        [Input({'type':  'plot-output',   'index': MATCH}, 'value'),
         Input({'type':  'plot-location', 'index': MATCH}, 'value'),
         Input({'type':  'plot-variable', 'index': MATCH}, 'value'),
         Input({'type':  'plot-freq',     'index': MATCH}, 'value'),
         Input({'type':  'plot-sumspace', 'index': MATCH}, 'value'),
         ],
        [State('storage_output', 'data'),
        #  State({'type': 'plot-chart', 'index': MATCH}, 'figure'),
        ]
    )(make_plot)
