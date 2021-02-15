import os
from datetime import datetime
from tabulate import tabulate
import humanfriendly


NAME = "Name"
SIZE = "Size"
LAST_MODIFIED = "Last Modified"
TYPE = "Type"
PATH = "path"

def _sort_size(item):
    return os.stat(item[PATH]).st_size

def _sort_modified(item):
    return os.stat(item[PATH]).st_mtime

def _sort_name(item):
    return item[NAME]

sort_helpers = {
    SIZE: _sort_size,
    LAST_MODIFIED: _sort_modified,
    NAME: _sort_name
}

def _determine_filetype(path):
    if os.path.isfile(path):
        return "FILE"
    elif os.path.isdir(path):
        return "DIR"
    else:
        return "OTHER"

def ls(path, sort_by=SIZE, desc=True, readable=True):
    """Return a Json compatable objet containing the contents of the given directly

    Positional arguments:
    path -- The directory path of whihc you want to list all_contents

    Keyword arguments:
    sort_by -- a String, representing the desired sort by column (Default: Size)
    desc -- Boolean representing if the list should be sorted in descending order (Default:True)
    readable -- Boolean representing if the dametime and filesizes should be returned in a human readable or raw format (Default: True)

    Returns a dict containing 'size' whihc represents the sum of the size of the direclty direct contents (not recursive),
        'file_count' representing the number of files that are found in the directory (Does not include ohter type: Directory, Symlink, etc.)
        and 'contents', which is a sorted list, each element being a dict with a 'name', 'size' and 'modified' field.
    """
    # Have to get the full path of the files - srtoed in a dict for readability - however a tuple may be more efficient
    all_contents = [{PATH: os.path.join(path, f), NAME: f} for f in os.listdir(path)]
    # Sort the contetns based on recived parameters
    if sort_by not in sort_helpers:
        raise(ValueError(f"provided sort_by does not match any of {SIZE}, {LAST_MODIFIED}, or {NAME}."))
    all_contents.sort(key=sort_helpers[sort_by], reverse=desc)
    output = []
    sum_file_size = 0
    file_count = 0
    for f in all_contents:
        file_stats = os.stat(f[PATH])
        if os.path.isfile(f[PATH]):
            file_count += 1
        output.append({
            NAME: f[NAME],
            SIZE: humanfriendly.format_size(file_stats.st_size) if readable else file_stats.st_size,
            LAST_MODIFIED: datetime.fromtimestamp(file_stats.st_mtime).strftime("%Y-%m-%d %I:%M %p") if readable else file_stats.st_mtime,
            TYPE: _determine_filetype(f[PATH]),
            PATH: f[PATH]
        })
        sum_file_size += file_stats.st_size
    return {"contents":output,
        "path": os.path.abspath(path),
        "size": humanfriendly.format_size(sum_file_size) if readable else sum_file_size,
        "file_count":file_count, "content_count":len(output)}

def ls_print(ls_return):
    print(tabulate(ls_return["contents"], headers={NAME:NAME, SIZE:SIZE, LAST_MODIFIED:LAST_MODIFIED}))
    print(f"Number of files (not including directories or other): {ls_return['file_count']}, with total size: {ls_return['size']}")

if __name__ == "__main__":
    print(ls("."))
