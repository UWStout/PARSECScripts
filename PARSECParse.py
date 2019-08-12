import sys
import argparse

from ProjectPrefs import ProjectPrefs

PATH_TO_IMAGES = ""
IMAGE_PREFIX = ""
PATH_TO_MASKS = ""

parser = argparse.ArgumentParser(prog='PARSECParse.py', description='Program for processing photogrammetry data with Metashape')

parser.add_argument('-P', '--project', choices=['load', 'new'], required=True, help='Load a previous project or process a new one')
parser.add_argument('-Q', '--quick', action="store_true", help='Quickly process photogrammetry data')
parser.add_argument('-R', '--refine', action="store_true", help='Refines previously processed photogrammetry data')

args = parser.parse_args()

#AIW Loads a previous project.ini.
if args.project == 'load':
    prefs = input("Where would you like to load project from? ") + input("\nPlease enter project name: ") + (".ini")

    prefs = ProjectPrefs()

    PATH_TO_IMAGES = prefs.getPref(prefName='ImagePath')
    print(PATH_TO_IMAGES)
    IMAGE_PREFIX = prefs.getPref(prefName='NamePrefix')
    print(IMAGE_PREFIX)
    PATH_TO_MASKS = prefs.getPref(prefName='MaskPath',)
    print(PATH_TO_MASKS)

#AIW Creates a new project.ini
elif args.project == 'new':
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

#AIW Runs metaQuick from MEtaWork using the current project.ini
if args.quick:
    MetaWork.metaQuick(PATH_TO_IMAGES, IMAGE_PREFIX, PATH_TO_MASKS)

#AIW Runs metaRefine from MetaWork using the current project.ini
if args.refine:
    MetaWork.metaRefine(PATH_TO_IMAGES, IMAGE_PREFIX, PATH_TO_MASKS)
