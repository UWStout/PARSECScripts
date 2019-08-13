import sys
import argparse

#AIW Global variables
PATH_TO_PROJECT = "Placeholder"
PATH_TO_IMAGES = "Placeholder"
IMAGE_PREFIX = "Placeholder"
PATH_TO_MASKS = "Placeholder"

#AIW Main parser
parser = argparse.ArgumentParser(prog='subparseTest', description='Testing argument groups')

#AIW Parser group for project options
project_parser = parser.add_argument_group('project')
project_parser.add_argument('--path', action='store', help='Specify project path.')
project_parser.add_argument('--images', action='store', help='Path to the folder containing subject images.')
project_parser.add_argument('--name', action='store', help='A prefix to apply to log and MetaShape file names.')
project_parser.add_argument('--masks', action='store', help='Path to the images for background subtraction with filename pattern.')

#AIW Mutually exclusive group forcing opening or creating project.ini.
# - Only one of the following is allowed.
projectHandle_parser = parser.add_mutually_exclusive_group(required=True)
projectHandle_parser.add_argument('--load', action='store_true', help='Loads project from specified filepath.')
projectHandle_parser.add_argument('--new', action='store_true', help='Saves project in location specified by filepath.')

#AIW Mutually exclusive group for workflows.
# - Only one of the following is allowed.
workflow_parser = parser.add_mutually_exclusive_group()
workflow_parser.add_argument('--quick', action='store_true', help='Quick photogrammetry processing.')
workflow_parser.add_argument('--refine', action='store_true', help='Refinement of quickly processed photogrammetry data.')

args = parser.parse_args()

#AIW Changes global variables to parsed user input
if args.path:
    PATH_TO_PROJECT = args.path

if args.images:
    PATH_TO_IMAGES = args.images

if args.name:
    IMAGE_PREFIX = args.name

if args.masks:
    PATH_TO_MASKS = args.masks

#AIW gets or creates project.ini through ProjectPrefs class/func
if args.load:
    print('Loading existing project')

if args.new:
    print('saving new project')

"""#SFB Import and initialize the logging system
#SFB This also redirects all MetaScan output
#SFB Reads config from the file 'logging.inf'
import Logger
Logger.init(PATH_TO_IMAGES, IMAGE_PREFIX)
logger = Logger.getLogger()

import Metashape
import MetaWork
from MetaUtilsClass import MetaUtils

MetaUtils.CHECK_VER(Metashape.app.version)
MetaUtils.USE_GPU()"""

#AIW Runs metaQuick from MEtaWork using the current project.ini
if args.quick:
    print('Calling metaQuick works')
    #MetaWork.metaQuick(PATH_TO_IMAGES, IMAGE_PREFIX, PATH_TO_MASKS)

#AIW Runs metaRefine from MetaWork using the current project.ini
if args.refine:
    print('Running metaRefine on works')
    #MetaWork.metaRefine(PATH_TO_IMAGES, IMAGE_PREFIX, PATH_TO_MASKS)