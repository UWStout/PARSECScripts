"""A command line UI for PARSEC photogrammetry processing."""
# The current order is important, so, if the argparser functions are
# moved around, stuff might break.

import Logger

from MetaUtilsClass import MetaUtils
import MetaWork
import Metashape
import sys
import argparse

from ProjectPrefs import ProjectPrefs

# Global variables
PATH_TO_IMAGES = None
PROJECT_NAME = None
PATH_TO_MASKS = None

# Main parser
parser = argparse.ArgumentParser(
    prog='PARSECParse', description='Command line UI for PARSEC photogrammetry processes.')

# Parser group for project options
project_parser = parser.add_argument_group('File Info')
project_parser.add_argument('-i', '--images', action='store',
                            help='Path to the folder containing subject images.')
project_parser.add_argument('-p', '--project', action='store',
                            help='Project name applied as a prefix to log and MetaShape file names.')
project_parser.add_argument('-m', '--masks', action='store',
                            help='Path to the images for background subtraction with filename pattern.')

# Mutually exclusive group forcing opening or creating project.ini.
# - Only one of the following is allowed.
projectHandle_parser = parser.add_mutually_exclusive_group(required=True)
projectHandle_parser.add_argument(
    '-l', '--load', action='store', help='Loads project using the specified filepath')
projectHandle_parser.add_argument('-n', '--new', action='store_true',
                                  help='Creates a new project using input specified with "-i", "-p", and "-m"')

# Mutually exclusive group for workflows.
# - Only one of the following is allowed.
workflow_parser = parser.add_mutually_exclusive_group()
workflow_parser.add_argument(
    '-q', '--quick', action='store_true', help='Quick photogrammetry processing.')
workflow_parser.add_argument('-r', '--refine', action='store_true',
                             help='Refinement of quickly processed photogrammetry data.')
workflow_parser.add_argument('-c', '--custom', action='store_true',
                             help='Needed for running a custom photogrammetry data processing workflow.')

# Parser group for custom workflow options.
project_parser = parser.add_argument_group('Custom Workflow Options')
project_parser.add_argument('-qa', '--quickAlign', action='store_true',
                            help='Preforms quick quality image matching.')
project_parser.add_argument('-ga', '--genAlign', action='store_true',
                            help='Preforms general quality image matching.')
project_parser.add_argument('-aa', '--arcAlign', action='store_true',
                            help='Preforms archival quality image matching.')
project_parser.add_argument('-gd', '--genDense', action='store_true',
                            help='Creates general quality dense cloud. Requires image matching to have been run.')
project_parser.add_argument('-ad', '--arcDense', action='store_true',
                            help='Creates archival quality dense cloud. Requires image matching to have been run.')
project_parser.add_argument('-qm', '--quickMod', action='store_true',
                            help='Creates a low-quality model. Requires image matching to have been run.')
project_parser.add_argument('-gm', '--genMod', action='store_true',
                            help='Creates a general-quality model. Requires general quality or better image matching & '
                            'dense cloud creation to have been run.')
project_parser.add_argument('-am', '--arcMod', action='store_true',
                            help='Creates an archival-quality model. Requires general quality or better image matching '
                            '& dense cloud creation to have been run.')

# Parser group for utilities.
project_parser = parser.add_argument_group('Utilities')
args = parser.parse_args()

# Changes global variables to parsed user input.
if args.images:
    PATH_TO_IMAGES = args.images

if args.project:
    PROJECT_NAME = args.project

if args.masks:
    PATH_TO_MASKS = args.masks

# Tries to load the specified project.
if args.load:
    paths = vars(args)
    LOAD_PATH = paths.get('load') or paths.get('l')
    prefs = ProjectPrefs(LOAD_PATH + '.ini')
    PATH_TO_IMAGES = prefs.getPref('PATH_TO_IMAGES')
    PROJECT_NAME = prefs.getPref('PROJECT_NAME')
    PATH_TO_MASKS = prefs.getPref('PATH_TO_MASKS')

# Checks for required path parameters
if PATH_TO_IMAGES is None or PROJECT_NAME is None:
    print("Please specify a path for subject images and a project name.")
    sys.exit()

# Creates a new project based on parsed user input.
if args.new:
    prefs = ProjectPrefs()
    prefs.setPref('PATH_TO_IMAGES', PATH_TO_IMAGES)
    prefs.setPref('PROJECT_NAME', PROJECT_NAME)
    if PATH_TO_MASKS is not None:
        prefs.setPref('PATH_TO_MASKS', PATH_TO_MASKS)
    prefs.saveConfig(PROJECT_NAME, './')
    print('Saved configuration to ./' + PROJECT_NAME + '.ini')

# Import and initialize the logging system
# This also redirects all MetaScan output
# Reads config from the file 'logging.ini'
Logger.init('./', PROJECT_NAME)
logger = Logger.getLogger()

# Checks for Metashape version and GPU availability
MetaUtils.CHECK_VER(Metashape.app.version)
MetaUtils.USE_GPU()

# Runs metaQuick from MetaWork using the current project.ini info
if args.quick:
    if PROJECT_NAME is None:
        print(PATH_TO_IMAGES)
        print('Unable to continue without project')
    else:
        MetaWork.metaQuick(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS)

# Runs metaRefine from MetaWork using the current project.ini info
if args.refine:
    if PROJECT_NAME is None:
        print(PATH_TO_IMAGES)
        print('Unable to continue without project')
    else:
        MetaWork.metaRefine(PATH_TO_IMAGES, PROJECT_NAME)

# Runs metaCustomStart from MetaWork using the current project.ini info
if args.custom:
    if PROJECT_NAME is None:
        print(PATH_TO_IMAGES)
        print('Unable to continue without project')
    else:
        MetaWork.metaCustomStart(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS)

# Custom workflow options to be run after metaCustomStart
if args.quickAlign:
    if PROJECT_NAME is None:
        print(PATH_TO_IMAGES)
        print('Unable to continue without project')
    else:
        MetaWork.metaCustomStart(MU.chunk)
