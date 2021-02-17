import argparse
import webbrowser
from server import app
from tools import *
import base64


parser = argparse.ArgumentParser(prog='Re-ls',
    description="Refresh of the the classic ls command")
parser.add_argument('path',type=str, default='.', nargs='?', help='Path to the directory to list.')
parser.add_argument('--serve', action='store_true', help="Start the UI and serving components")
parser.add_argument('-r','--recurse', action='store_true', help="Calculcate directory sizes recursivly.")


args = parser.parse_args()
if args.serve:
    b64path = base64.b64encode(args.path)
    # TODO: move webbroswer open to after app.run via threading
    webbrowser.open('http://127.0.0.1:5000/ui/index.html?b64path=' + b64path)
    app.run()
else:
    # # call tools otherwise
    # # print(args)
    # # ls(args.path)
    # ls_print(ls(args.path))
    # #print(json.dumps(ls(args.path)))

    lsc = LsCompute()
    lsc.ls(args.path, recursive=args.recurse)
    if args.recurse:
        lsc.print_output()
    else:
        lsc.quick_print_output()
