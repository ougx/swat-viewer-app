from swatviewer import init_app
from flask import Flask

app = init_app()
if app.server.config['APP_ROOT'] != '/':
    app = app.server

if __name__ == '__main__':
    if isinstance(app, Flask):
        app.run(port=8050)
    else:
        app.run_server(debug=True)
