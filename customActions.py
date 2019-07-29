import argparse

#AIW For checking the current metashape project via image path, mask path, and optional name prefix.
class CurrentProject(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
    def __call__(self, parser, namespace, values, option_string=None):

#AIW For setting the current metashape project via image path, mask path, and optional name prefix.
class SetProject(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
    def __call__(self, parser, namespace, values, option_string=None):