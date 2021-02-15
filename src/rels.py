import argparse
import webbrowser
from server import app
from tools import *


parser = argparse.ArgumentParser(prog='Re-ls',
    description="Refresh of the the classic ls command")
parser.add_argument('--serve', action='store_true', help="Start the UI and serving components")
parser.add_argument('path',type=str, default='.', nargs='?', help='Path to the directory to list.')


args = parser.parse_args()
if args.serve:
    # TODO: move webbroswer open to after app.run via threading
    webbrowser.open('http://127.0.0.1:5000/')
    app.run()
else:
    # call tools otherwise
    # print(args)
    # ls(args.path)
    ls_print(ls(args.path))
    #print(json.dumps(ls(args.path)))
