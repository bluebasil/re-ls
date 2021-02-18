import pytest
from unittest.mock import patch
from rels.tools import *

""" Just two very simple tests to test the core backend functionality """"

@patch('os.stat')
@patch('os.listdir')
@patch('os.path')
def test_ls_init(path, listdir, stat):
    path.abspath.return_value = "A:/foo/bar"
    listdir.return_value = ["Hello","World"]
    path.join.side_effect = ["A:/foo/bar/Hello","A:/foo/bar/World"]
    path.isfile.return_value = True
    path.basename.side_effect = ["Hello","World"]
    stat.return_value.st_mtime = 1613090877.605168
    stat.return_value.st_size = 2

    lsc = LsCompute(".")

    assert(lsc.payload["count"] == 2)
    assert(lsc.payload["raw_size"] == 4)


@patch('os.walk')
@patch('os.stat')
@patch('os.listdir')
@patch('os.path')
def test_ls_recurse(path, listdir, stat, walk):
    path.abspath.return_value = "A:/foo/bar"
    listdir.return_value = ["Hello","World"]
    path.join.side_effect = ["A:/foo/bar/Hello","A:/foo/bar/World","A:/foo/bar/World/apple"]
    path.isfile.side_effect = [True,False,True]
    path.isdir.return_value = True
    path.basename.side_effect = ["Hello","World"]
    stat.return_value.st_mtime = 1613090877.605168
    stat.return_value.st_size = 2
    walk.return_value = [("A:/foo/bar/World", ["apple"], [])]

    lsc = LsCompute(".")
    payload = lsc.ping_output()

    assert(payload["count"] == 2)
    assert(payload["raw_size"] == 6)
    assert(payload["contents"][0]["raw_size"] == 4)
