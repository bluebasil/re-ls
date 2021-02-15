from flask import Flask, send_from_directory, redirect, url_for, request, abort
from tools import *
from distutils.util import strtobool
import base64
import json
import os

app = Flask(__name__)

@app.route('/ls')
def call_ls():
    print(request.args)
    b64_encoded_path = request.args.get('b64path')
    str_sort_descending = request.args.get('desc','true')
    sort_by = request.args.get('srt',SIZE)
    str_raw_format = request.args.get('raw',"false")

    # path should be b64 encoded.  This decodes that into a String
    decoded_path = base64.b64decode(b64_encoded_path).decode()
    sort_descending = bool(strtobool(str_sort_descending))
    human_readable = not bool(strtobool(str_raw_format))
    try:
        data_content = ls(decoded_path, sort_by=sort_by, desc=sort_descending, readable=human_readable)
    except PermissionError:
        abort(403, "Access Denied")
    return json.dumps(data_content)

@app.route('/ui/<path>')
def show_ui(path):
    return send_from_directory('../ui', path)

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for("show_ui",path="dir_icon.ico"),code=302)

@app.route('/')
def root():
    return redirect(url_for("show_ui",path="index.html"),code=302)

if __name__ == "__main__":
    app.run()
