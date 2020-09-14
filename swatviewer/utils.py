from config import UPLOAD_FOLDER_ROOT

import shutil
import os
import time

def remove_upload(max_hour=72):

    now = time.time()
    for f in os.scandir(UPLOAD_FOLDER_ROOT):
        if (now - f.stat().st_mtime) / 3600 >  max_hour:
            if f.is_file():
                os.remove(os.path.join(UPLOAD_FOLDER_ROOT, f.name))
            elif f.is_dir():
                shutil.rmtree(os.path.join(UPLOAD_FOLDER_ROOT, f.name), ignore_errors=True)


def printtest(s='0'):
    print('test 1', s)
