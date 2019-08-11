import sys
import argparse
import Metashape
from ProjectPrefs import ProjectPrefs
import MetaWork

PATH_TO_IMAGES = None
IMAGE_PREFIX = None
PATH_TO_MASKS = None

parser = argparse.ArgumentParser()
#AIW Sets project
parser.add_argument('-P', '--project', help='Specifies project file path and name.')
#AIW Runs MetaQuickClass
#parser.add_argument('-Q', '--quick', help='Quick ')

args = parser.parse_args()
print(args.project)
print("HERE!")

prefs = ProjectPrefs(args.project)
