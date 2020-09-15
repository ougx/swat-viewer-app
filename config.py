import os

ENV = 'development'
DEBUG = True

UPLOAD_FOLDER_ROOT = "./temp"

# APP ROOT
APP_ROOT = '/swatviewer/' if 'home/nebraska' in os.getcwd() else '/'

# cache
CACHE_TYPE = 'simple'

# APScheduler
SCHEDULER_API_ENABLED = True

