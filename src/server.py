from flask import Flask, send_from_directory, redirect, url_for, request, abort
from tools import *
from distutils.util import strtobool
from loguru import logger
import base64
import json
import os

# Assumption: It is okay to only allow a single active requestReturn
# I am going to limit active requests witht he UI for performnce.
# This could be reqplaced with a datastore to allow simultanious requests
active_lsc = None
print("FDHJKLFHSDJKFHSDJKFHK", flush=True)

# Singleton
class ActiveRequest:
    __instance = None

    @staticmethod
    def getInstance():
        if ActiveRequest.__instance == None:
            ActiveRequest()
        return ActiveRequest.__instance

    def __init__(self):
        if ActiveRequest.__instance is not None:
            raise("Attempted to create second instance of a singleton")
        else:
            ActiveRequest.__instance = self
            self.active_lsc = None

    def get(self):
        return self.active_lsc

    def set(self, lsc):
        self.active_lsc = lsc

app = Flask(__name__)

@app.route('/ls')
def call_ls():
    # If there has been a previus call, abort it to save on performance
    if ActiveRequest.getInstance().get() is not None:
        ActiveRequest.getInstance().get().setDone()

    logger.debug(request.args)
    b64_encoded_path = request.args.get('b64path')
    str_sort_descending = request.args.get('desc','true')
    sort_by = request.args.get('srt',SIZE)

    # path should be b64 encoded.  This decodes that into a String
    decoded_path = base64.b64decode(b64_encoded_path).decode()
    sort_descending = bool(strtobool(str_sort_descending))
    try:
        active_lsc = LsCompute()
        data_content = active_lsc.ls(decoded_path, sort_by=sort_by, desc=sort_descending)
        ActiveRequest.getInstance().set(active_lsc)
    except PermissionError:
        abort(403, "Access Denied")
    except FileNotFoundError:
        abort(404, "Directory Not Found")
    return json.dumps(data_content)


@app.route('/ping')
def request_update():
    # TODO: better protections here for is ls has not already been called
    if ActiveRequest.getInstance().get() is None:
        msg = "/ls must be called first"
        logger.error(msg)
        return {"ErrorMessage": msg}

    data_content = ActiveRequest.getInstance().get().ping_output()
    logger.debug(data_content)
    return json.dumps(data_content)


@app.route('/ui/<path>')
def show_ui(path):
    """ The UI is stored behind the /ui path.  Doing this, we can protect against path traversal attacks """
    return send_from_directory('../ui', path)

@app.route('/favicon.ico')
def favicon():
    """ The UI icon """
    return redirect(url_for("show_ui",path="dir_icon.ico"),code=302)

@app.route('/')
def root():
    return redirect(url_for("show_ui",path="index.html"),code=302)

if __name__ == "__main__":
    app.run()
