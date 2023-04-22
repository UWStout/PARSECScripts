"""A command line UI for PARSEC photogrammetry processing."""
#AIW The current order is important, so, if the argparser functions are moved around, stuff might break.

import sys
import argparse

from ProjectPrefs import ProjectPrefs

#AIW Global variables
PATH_TO_IMAGES = None
PROJECT_NAME = None
PATH_TO_MASKS = None

#AIW Main parser
parser = argparse.ArgumentParser(prog='PARSECParse', description='Command line UI for PARSEC photogrammetry processes.')

#AIW Parser group for project options
project_parser = parser.add_argument_group('File Info')
project_parser.add_argument('-i', '--images', action='store', help='Path to the folder containing subject images.')
project_parser.add_argument('-p', '--project', action='store', help='Project name applied as a prefix to log and MetaShape file names.')
project_parser.add_argument('-m', '--masks', action='store', help='Path to the images for background subtraction with filename pattern.')

#AIW Mutually exclusive group forcing opening or creating project.ini.
# - Only one of the following is allowed.
projectHandle_parser = parser.add_mutually_exclusive_group(required=True)
projectHandle_parser.add_argument('-l', '--load', action='store', help='Loads project using the specified filepath')
projectHandle_parser.add_argument('-n', '--new', action='store_true', help='Creates a new project using input specified with "-i", "-p", and "-m"')

#AIW Mutually exclusive group for workflows.
# - Only one of the following is allowed.
workflow_parser = parser.add_mutually_exclusive_group()
workflow_parser.add_argument('-q', '--quick', action='store_true', help='Quick photogrammetry processing.')
workflow_parser.add_argument('-r', '--refine', action='store_true', help='Refinement of quickly processed photogrammetry data.')
workflow_parser.add_argument('-c', '--custom', action='store_true', help='Needed for running a custom photogrammetry data processing workflow.')

#AIW Parser group for custom workflow options.
project_parser = parser.add_argument_group('Custom Workflow Options')
project_parser.add_argument('-qa', '--quickAlign', action='store_true', help='Preforms quick quality image matching.')
project_parser.add_argument('-ga', '--genAlign', action='store_true', help='Preforms general quality image matching.')
project_parser.add_argument('-aa', '--arcAlign', action='store_true', help='Preforms archival quality image matching.')
project_parser.add_argument('-gd', '--genDense', action='store_true', help='Creates general quality dense cloud. Requires image matching to have been run.')
project_parser.add_argument('-ad', '--arcDense', action='store_true', help='Creates archival quality dense cloud. Requires image matching to have been run.')
project_parser.add_argument('-qm', '--quickMod', action='store_true', help='Creates a low-quality model. Requires image matching to have been run.')
project_parser.add_argument('-gm', '--genMod', action='store_true', help='Creates a general-quality model. Requires general quality or better image matching & dense cloud creation to have been run.')
project_parser.add_argument('-am', '--arcMod', action='store_true', help='Creates an archival-quality model. Requires general quality or better image matching & dense cloud creation to have been run.')

#AIW Parser group for utilities.
project_parser = parser.add_argument_group('Utilities')
args = parser.parse_args()

#AIW Changes global variables to parsed user input.
if args.images:
    PATH_TO_IMAGES = args.images

if args.project:
    PROJECT_NAME = args.project

if args.masks:
    PATH_TO_MASKS = args.masks

#AIW Tries to load the specified project.
if args.load:
    try:
        path = vars(args)
        prefs = ProjectPrefs()
        prefs.readConfig(path.get('load'))
        print('Loading '+ path.get('load'))
        PATH_TO_IMAGES = prefs.getPref('PATH_TO_IMAGES')
        PROJECT_NAME = prefs.getPref('PROJECT_NAME')
        PATH_TO_MASKS = prefs.getPref('PATH_TO_MASKS')

    except:
        print(path.get('load') + " doesn't exist!")
        sys.exit()

#AIW Creates a new project based on parsed user input.
if args.new:
    if PATH_TO_IMAGES == None or PATH_TO_MASKS == None or PROJECT_NAME == None:
        print("Please specify a path for subject images, a path to the images for background subtraction and filename pattern, and a name prefix.")
        sys.exit()

    else:
        prefs = ProjectPrefs()
        prefs.setPref('PATH_TO_IMAGES', PATH_TO_IMAGES)
        prefs.setPref('PROJECT_NAME', PROJECT_NAME)
        prefs.setPref('PATH_TO_MASKS', PATH_TO_MASKS)
        prefs.saveConfig(PROJECT_NAME, PATH_TO_IMAGES)
        print('Saved new project to '+ PATH_TO_IMAGES)

#SFB Import and initialize the logging system
#SFB This also redirects all MetaScan output
#SFB Reads config from the file 'logging.inf'
import Logger
Logger.init(PATH_TO_IMAGES, PROJECT_NAME)
logger = Logger.getLogger()

import Metashape
import MetaWork
from MetaUtilsClass import MetaUtils

MetaUtils.CHECK_VER(Metashape.app.version)
MetaUtils.USE_GPU()

#AIW Runs metaQuick from MetaWork using the current project.ini info
if args.quick:
    if PROJECT_NAME == None:
        print(PATH_TO_IMAGES)
        print('Unable to continue without project')
    else:
        MetaWork.metaQuick(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS)

#AIW Runs metaRefine from MetaWork using the current project.ini info
if args.refine:
    if PROJECT_NAME == None:
        print(PATH_TO_IMAGES)
        print('Unable to continue without project')
    else:
        MetaWork.metaRefine(PATH_TO_IMAGES, PROJECT_NAME)

#AIW Runs metaCustomStart from MetaWork using the current project.ini info
if args.custom:
    if PROJECT_NAME == None:
        print(PATH_TO_IMAGES)
        print('Unable to continue without project')
    else:
        MetaWork.metaCustomStart(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS)

#AIW Custom workflow options to be run after metaCustomStart
if args.quickAlign:
    if PROJECT_NAME == None:
        print(PATH_TO_IMAGES)
        print('Unable to continue without project')
    else:
        MetaWork.metaCustomStart(MU.chunk)
