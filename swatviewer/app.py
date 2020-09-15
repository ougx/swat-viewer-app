# _*_ coding: utf_8 _*_
"""
swat reader app to read and plot swat output.* file

Created on Thu Sep 10 19:14:05 2020

@author: Michael Ou, michael.ou@longspring.com
"""


import dash
import dash_bootstrap_components as dbc
import dash_uploader as du

import flask

from .callbacks import add_callbacks
from .layout import maintabs
from .utils import remove_upload, printtest

from .extensions import scheduler, cache

def add_scheduler(scheduler):
    # https://apscheduler.readthedocs.io/en/stable/modules/triggers/interval.html#module-apscheduler.triggers.interval

    # remove uploaded files older than 72 hours every day
    scheduler.task(
        'interval',
        id='printtest',
        days=1,
        misfire_grace_time=900
    )(remove_upload)



def init_app():

    server = flask.Flask(__name__, instance_relative_config=True)
    server.config.from_object('config')
    server.config.from_pyfile('config.py')

    cache.init_app(server)
    scheduler.init_app(server)

    app = dash.Dash(
        __name__,
        server=server,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        title='SWAT Viewer',
        requests_pathname_prefix=f'{server.config["APP_ROOT"]}'
    )


    du.configure_upload(
        app, server.config['UPLOAD_FOLDER_ROOT'],
    )

    app.layout = maintabs

    # add call backs
    add_callbacks(app)

    # add scheduler
    add_scheduler(scheduler)

    scheduler.start()
    return app

