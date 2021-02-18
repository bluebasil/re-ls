import argparse
import webbrowser
from server import app
from tools import *
import base64
from loguru import logger


parser = argparse.ArgumentParser(prog='Re-ls',
    description="Refresh of the the classic ls command")
parser.add_argument('path',type=str, default='.', nargs='?', help='Path to the directory to list.')
parser.add_argument('--serve', action='store_true', help="Start the UI and serving components")
parser.add_argument('-r','--recurse', action='store_true', help="Calculcate directory sizes recursivly.")
args = parser.parse_args()

if args.serve:
    # pass the inital path to the ui
    b64path = base64.b64encode(args.path.encode()).decode()

    # TODO: move webbroswer open to after app.run via threading
    webbrowser.open(f"http://127.0.0.1:5000/ui/index.html?b64path={b64path}")
    app.run()
else:
    logger.remove()
    logger.add(sys.stderr, level="ERROR")

    lsc = LsCompute(args.path, recursive=args.recurse)
    if args.recurse:
        lsc.print_output()
    else:
        # When recurse is off, this dives a result very similar to the ls command
        lsc.quick_print_output()
