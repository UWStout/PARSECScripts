import sys
import argparse

from ProjectPrefs import ProjectPrefs

PATH_TO_IMAGES = ""
IMAGE_PREFIX = ""
PATH_TO_MASKS = ""

parser = argparse.ArgumentParser(description='Program for processing photogrammetry data with Metashape')

#AIW Sets project
#AIW parser.add_argument('-P', '--project', help='Specifies project file path and name.')
#AIW Runs MetaQuickClass
parser.add_argument('-P', '--project', choices=['load', 'new'], required=True, help='')
parser.add_argument('-Q', '--quick', action="store_true", help='Quickly process photogrammetry data')
parser.add_argument('-R', '--refine', action="store_true", help='Refines previously processed photogrammetry data')

args = parser.parse_args()
if args.project[0]:
    prefs = input("Where would you like to load project from? ") + input("\nPlease enter project name: ") + (".ini")

    prefs = ProjectPrefs()

    PATH_TO_IMAGES = prefs.getPref(prefName='ImagePath')
    print(PATH_TO_IMAGES)
    IMAGE_PREFIX = prefs.getPref(prefName='NamePrefix')
    print(IMAGE_PREFIX)
    PATH_TO_MASKS = prefs.getPref(prefName='MaskPath',)
    print(PATH_TO_MASKS)

elif args.project[1]:
    PATH_TO_IMAGES = input("Please enter the path to images: ")
    IMAGE_PREFIX = input("Please enter filename prefix: ")
    PATH_TO_MASKS = input("Please enter file path and format for background images: ")

    prefs = ProjectPrefs()

    PATH_TO_IMAGES = prefs.getPref(prefName='ImagePath')
    print(PATH_TO_IMAGES)
    IMAGE_PREFIX = prefs.getPref(prefName='NamePrefix')
    print(IMAGE_PREFIX)
    PATH_TO_MASKS = prefs.getPref(prefName='MaskPath',)
    print(PATH_TO_MASKS)

    prefs.saveConfig(IMAGE_PREFIX)

#SFB Import and initialize the logging system
#SFB This also redirects all MetaScan output
#SFB Reads config from the file 'logging.inf'
import Logger
Logger.init(PATH_TO_IMAGES, IMAGE_PREFIX)
logger = Logger.getLogger()

import Metashape
import MetaWork
from MetaUtilsClass import MetaUtils

MetaUtils.CHECK_VER(Metashape.app.version)
MetaUtils.USE_GPU()

if args.quick:
    MetaWork.metaQuick(PATH_TO_IMAGES, IMAGE_PREFIX, PATH_TO_MASKS)

if args.refine:
    MetaWork.metaRefine(PATH_TO_IMAGES, IMAGE_PREFIX, PATH_TO_MASKS)

if args.project:
    prefs = ProjectPrefs()
