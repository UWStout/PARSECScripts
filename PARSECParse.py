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
PREFS_FILENAME = None
PATH_TO_IMAGES = None
PROJECT_NAME = None
PATH_TO_MASKS = None

# Main parser
parser = argparse.ArgumentParser(
    prog='PARSECParse', description='Command line UI for PARSEC photogrammetry processes.')

# Parser group for project options
project_parser = parser.add_argument_group('File Info', 'Options for specifying filepath configuration.')
project_parser.add_argument('-i', '--images', action='store',
                            help='Path to the folder containing subject images.')
project_parser.add_argument('-p', '--project', action='store',
                            help='Project name applied as a prefix to log and MetaShape file names.')
project_parser.add_argument('-m', '--masks', action='store',
                            help='Path to the images for background subtraction with filename pattern.')

# Allow loading of previously created configuration file
projectConfig_parser = parser.add_argument_group('Load a previous configuration', 'Specify whether to load the path data from a config file.')
projectConfig_parser.add_argument('-l', '--load', action='store',
                                  help='Loads image, project, and mask paths from the specified config file (previously created).')

# Mutually exclusive group for workflows.
# - Only one of the following is allowed.
workflow_group = parser.add_argument_group('Main Workflow Options', 'Specify what work to do on this project.')
workflow_parser = workflow_group.add_mutually_exclusive_group(required=True)
workflow_parser.add_argument('-q', '--quick', action='store_true',
                             help='Quick photogrammetry processing.')
workflow_parser.add_argument('-r', '--refine', action='store_true',
                             help='Refinement of quickly processed photogrammetry data.')
workflow_parser.add_argument('-g', '--general', action='store_true',
                             help='General/normal quality processing.')
workflow_parser.add_argument('-a', '--archival', action='store_true',
                             help='Archival quality processing.')
workflow_parser.add_argument('-c', '--custom', action='store_true',
                             help='Run a custom workflow (use with custom workflow options).')

# Parser group for custom workflow options.
project_parser = parser.add_argument_group('Custom Workflow Options', 'Provide details for a custom workflow.')
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

# TODO: Parser group for utilities.
# project_parser = parser.add_argument_group('Utilities')

# Parse the command line arguments.
args = parser.parse_args()

# If custom workflow was specified, ensure at least one workflow step was also specified.
if args.custom and (
    not args.quickAlign and not args.genAlign and not args.arcAlign and
    not args.genDense and not args.arcDense and
    not args.quickMod and not args.genMod and not args.arcMod
):
    print("Please specify at least one custom workflow step when using the custom workflow option.")
    sys.exit()

# Changes global variables to parsed user input.
if args.images:
    PATH_TO_IMAGES = args.images

if args.project:
    PROJECT_NAME = args.project

if args.masks:
    PATH_TO_MASKS = args.masks

# If load was specified, read the project preferences from the specified file.
if args.load:
    paths = vars(args)
    LOAD_PATH = paths.get('load') or paths.get('l')
    PREFS_FILENAME = LOAD_PATH + '.ini'
    prefs = ProjectPrefs(PREFS_FILENAME)
    PATH_TO_IMAGES = prefs.getPref('PATH_TO_IMAGES')
    PROJECT_NAME = prefs.getPref('PROJECT_NAME')
    PATH_TO_MASKS = prefs.getPref('PATH_TO_MASKS')

# Checks for required path parameters
if PATH_TO_IMAGES is None or PROJECT_NAME is None:
    print("Please specify a path for subject images and a project name or load a previous config.")
    sys.exit()

# Creates a new project based on parsed user input.
if not args.load:
    prefs = ProjectPrefs()
    prefs.setPref('PATH_TO_IMAGES', PATH_TO_IMAGES)
    prefs.setPref('PROJECT_NAME', PROJECT_NAME)
    if PATH_TO_MASKS is not None:
        prefs.setPref('PATH_TO_MASKS', PATH_TO_MASKS)
    PREFS_FILENAME = PROJECT_NAME + '.ini'
    prefs.saveConfig(PREFS_FILENAME, './')
    print('Saving configuration to ./' + PREFS_FILENAME)

# Import and initialize the logging system
# This also redirects all MetaScan output
# Reads config from the file 'logging.ini'
Logger.init('./', PROJECT_NAME)
logger = Logger.getLogger()

# Checks for Metashape version and GPU availability
MetaUtils.CHECK_VER(Metashape.app.version)
MetaUtils.USE_GPU()

# Checks for required project name parameter
if PROJECT_NAME is None:
    print('Unable to continue without project name')
    sys.exit()

# Runs metaQuick from MetaWork using the current project.ini info
if args.quick:
    MetaWork.metaQuick(PATH_TO_IMAGES, PROJECT_NAME,
                       PATH_TO_MASKS, PREFS_FILENAME)

# Runs metaGeneral from MetaWork using the current project.ini info
if args.general:
    MetaWork.metaGeneral(PATH_TO_IMAGES, PROJECT_NAME,
                         PATH_TO_MASKS, PREFS_FILENAME)

# Runs metaArchival from MetaWork using the current project.ini info
if args.archival:
    MetaWork.metaArchival(PATH_TO_IMAGES, PROJECT_NAME,
                          PATH_TO_MASKS, PREFS_FILENAME)

# Runs metaRefine from MetaWork using the current project.ini info
if args.refine:
    MetaWork.metaRefine(PATH_TO_IMAGES, PROJECT_NAME)

# Runs metaCustomStart from MetaWork using the current project.ini info
MU = None
if args.custom:
    MU = MetaWork.metaCustomStart(
        PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS, PREFS_FILENAME)

# Custom workflow options to be run after metaCustomStart
if args.quickAlign:
    MetaWork.quickAlign(MU.chunk, PREFS_FILENAME)
    MU.doc.save()

if args.genAlign:
    MetaWork.genAlign(MU.chunk, PREFS_FILENAME)
    MU.doc.save()

if args.arcAlign:
    MetaWork.archAlign(MU.chunk, PREFS_FILENAME)
    MU.doc.save()

if args.genDense:
    MetaWork.genDenseCloud(MU.chunk, PREFS_FILENAME)
    MU.doc.save()

if args.arcDense:
    MetaWork.archDenseCloud(MU.chunk, PREFS_FILENAME)
    MU.doc.save()

if args.quickMod:
    MetaWork.quickModel(MU.chunk, PREFS_FILENAME)
    MU.doc.save()

if args.genMod:
    MetaWork.genModel(MU.chunk, PREFS_FILENAME)
    MU.doc.save()

if args.arcMod:
    MetaWork.archModel(MU.chunk, PREFS_FILENAME)
    MU.doc.save()
