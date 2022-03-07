import os

root_path = os.path.dirname(os.path.abspath(__file__))
o = os.listdir(root_path)


def get_path():
    return o


def get_root_path():
    return root_path
