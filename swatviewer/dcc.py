# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 20:21:10 2020

@author: Michael Ou
"""

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

class uploadButton(dcc.Upload):
    def __init__(self, label1='Drag and Drop File Here', label2='Browse File', *args, **kwargs):
        
        super().__init__(
            children=html.Div([
                    html.Div(html.Img(src='/assets/upload.png', width=480)),
                    html.Div(label1),
                    html.Div(dbc.Button(label2, color="primary"))
                ]),
            
            *args, **kwargs
        )