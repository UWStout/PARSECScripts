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
    prog='PARSECParse.py',
    description='Command line UI for PARSEC photogrammetry processes.'
)

# Options for the main program
parser.add_argument('-i', '--images', action='store', help='Path to the folder containing subject images.')
parser.add_argument('-m', '--masks', action='store', help='Path to the images for background subtraction with filename pattern.')
parser.add_argument('-p', '--project', action='store', help='Project name applied as a prefix to log and MetaShape file names.')
parser.add_argument('-l', '--load', action='store', help='Loads paths from the specified config file (previously created).', metavar="PROJECT")
subparsers = parser.add_subparsers(title='Workflow', dest='workflow', description='Select a workflow to run.', metavar='WORKFLOW', required=True)

# Fixed workflow subcommands
quick_command = subparsers.add_parser('quick', help='Quick photogrammetry processing.')
quick_command.add_argument('-r', '--refine', action='store_true', default=False, help='Refine prior data instead of overwriting.')
quick_command.add_argument('-t', '--tolerance', action='store', default=50, help='Marker detection tolerance.')
quick_command.add_argument('-mt', '--modelTie', action='store_true', default=False, help='Generate model from sparse tie points.')
quick_command.add_argument('-md', '--modelDepth', action='store_true', default=False, help='Generate model from depth maps.')
quick_command.add_argument('-mc', '--modelCloud', action='store_true', default=False, help='Generate model from dense point cloud.')

general_command = subparsers.add_parser('general', help='General/normal quality processing.')
general_command.add_argument('-r', '--refine', action='store_true', help='Refine prior data instead of overwriting.')
general_command.add_argument('-t', '--tolerance', action='store', default=50, help='Marker detection tolerance.')
general_command.add_argument('-mt', '--modelTie', action='store_true', default=False, help='Generate model from sparse tie points.')
general_command.add_argument('-md', '--modelDepth', action='store_true', default=False, help='Generate model from depth maps.')
general_command.add_argument('-mc', '--modelCloud', action='store_true', default=False, help='Generate model from dense point cloud.')

archival_command = subparsers.add_parser('archival', help='Archival quality processing.')
archival_command.add_argument('-r', '--refine', action='store_true', default=False, help='Refine prior data instead of overwriting.')
archival_command.add_argument('-t', '--tolerance', action='store', default=50, help='Marker detection tolerance.')
archival_command.add_argument('-mt', '--modelTie', action='store_true', default=False, help='Generate model from sparse tie points.')
archival_command.add_argument('-md', '--modelDepth', action='store_true', default=False, help='Generate model from depth maps.')
archival_command.add_argument('-mc', '--modelCloud', action='store_true', default=False, help='Generate model from dense point cloud.')

# Custom workflow subcommand
custom_command = subparsers.add_parser('custom', help='Run a custom workflow')
custom_command.add_argument('-qa', '--quickAlign', action='store_true', default=False, help='Preforms quick quality image matching.')
custom_command.add_argument('-ga', '--genAlign', action='store_true', default=False, help='Preforms general quality image matching.')
custom_command.add_argument('-aa', '--arcAlign', action='store_true', default=False, help='Preforms archival quality image matching.')

custom_command.add_argument('-qd', '--quickDense', action='store_true', default=False, help='Creates quick quality dense cloud. Requires image matching to have been run.')
custom_command.add_argument('-gd', '--genDense', action='store_true', default=False, help='Creates general quality dense cloud. Requires image matching to have been run.')
custom_command.add_argument('-ad', '--arcDense', action='store_true', default=False, help='Creates archival quality dense cloud. Requires image matching to have been run.')

custom_command.add_argument('-qm', '--quickMod', action='store_true', default=False, help='Creates a low-quality model. Requires image matching to have been run.')
custom_command.add_argument('-gm', '--genMod', action='store_true', default=False, help='Creates a general-quality model. Requires a dense cloud.')
custom_command.add_argument('-am', '--arcMod', action='store_true', default=False, help='Creates an archival-quality model. Requires a dense cloud.')

custom_command.add_argument('-r', '--refine', action='store_true', default=False, help='Refine prior data instead of overwriting.')
custom_command.add_argument('-t', '--tolerance', action='store', default=50, help='Marker detection tolerance.')
custom_command.add_argument('-mt', '--modelTie', action='store_true', default=False, help='Generate model from sparse tie points.')
custom_command.add_argument('-md', '--modelDepth', action='store_true', default=False, help='Generate model from depth maps.')
custom_command.add_argument('-mc', '--modelCloud', action='store_true', default=False, help='Generate model from dense point cloud.')

# Utility actions subcommand
utility_command = subparsers.add_parser('utility', help='Utility actions to apply to an existing project.')
utility_command.add_argument('-t', '--tolerance', action='store', default=50, help='Marker detection tolerance.')

utility_group = utility_command.add_mutually_exclusive_group()
utility_group.add_argument('-cc', '--chunkClean', action='store_true', help='Levels, orients, and centers the chunk based on markers.')

utility_group.add_argument('-rl', '--regionLarge', action='store_true', help='Sets region to include the entire cage.')
utility_group.add_argument('-rm', '--regionMedium', action='store_true', help='Sets region to include most of the scanning volume.')
utility_group.add_argument('-rs', '--regionSmall', action='store_true', help='Sets region to only include the subject (approximate).')

utility_group.add_argument('-fa', '--filterAggressive', action='store_true', help='Aggressively filter the sparse cloud/tie points.')
utility_group.add_argument('-fn', '--filterNormal', action='store_true', help='Normally filter the sparse cloud/tie points.')
utility_group.add_argument('-fl', '--filterLight', action='store_true', help='Lightly filter the sparse cloud/tie points.')
utility_group.add_argument('-oc', '--optimizeCameras', action='store_true', help='Optimize the camera fitting (best used after -fa, -fn, or -fl).')

# Parse the command line arguments.
args = parser.parse_args()

# Ensure that load is not used with images, project, or masks.
if args.load and (args.images or args.project or args.masks):
    print("Cannot specify load with 'images', 'project', or 'masks'.")
    sys.exit(-1)

# If load was specified, read the project preferences from the specified file.
if args.load:
    # Initialize prefs filename
    PREFS_FILENAME = args.load + '.ini'

    # Try to read the project preferences from the specified file.
    print('Reading configuration from ./' + PREFS_FILENAME)
    prefs = ProjectPrefs(PREFS_FILENAME)
    PATH_TO_IMAGES = prefs.getPref('PATH_TO_IMAGES')
    PROJECT_NAME = prefs.getPref('PROJECT_NAME')
    PATH_TO_MASKS = prefs.getPref('PATH_TO_MASKS')

else:
    # Initialize global paths
    PATH_TO_IMAGES = args.images
    PROJECT_NAME = args.project
    PATH_TO_MASKS = args.masks
    PREFS_FILENAME = PROJECT_NAME + '.ini'

    # Save project preferences to a file
    prefs = ProjectPrefs()
    prefs.setPref('PATH_TO_IMAGES', PATH_TO_IMAGES)
    prefs.setPref('PROJECT_NAME', PROJECT_NAME)
    if PATH_TO_MASKS is not None:
        prefs.setPref('PATH_TO_MASKS', PATH_TO_MASKS)

    print('Saving configuration to ./' + PREFS_FILENAME)
    prefs.saveConfig(PREFS_FILENAME, './')

# Checks for required project name parameter
if PROJECT_NAME is None:
    print('Unable to continue without project name')
    sys.exit()

# Import and initialize the logging system
# This also redirects all MetaScan output
# Reads config from the file 'logging.ini'
Logger.init('./', PROJECT_NAME)
logger = Logger.getLogger()

# Checks for Metashape version and GPU availability
MetaUtils.CHECK_VER(Metashape.app.version)
MetaUtils.USE_GPU()

# Read global workflow options
REFINE_ONLY = (False if args.refine is None else args.refine)
MODEL_SPARSE = (False if args.modelTie is None else args.modelTie)
MODEL_DEPTH = (False if args.modelDepth is None else args.modelDepth)
MODEL_DENSE = (False if args.modelCloud is None else args.modelCloud)
args.tolerance = (50 if args.tolerance is None else int(args.tolerance))

# Runs metaQuick from MetaWork using the current project.ini info
match args.workflow:
    # Standard Workflows
    case 'quick':
        if not MODEL_SPARSE and not MODEL_DEPTH and not MODEL_DENSE:
            MODEL_SPARSE = True
        MetaWork.metaQuick(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS, PREFS_FILENAME, args.tolerance, REFINE_ONLY, MODEL_SPARSE, MODEL_DEPTH, MODEL_DENSE)
    case 'general':
        if not MODEL_SPARSE and not MODEL_DEPTH and not MODEL_DENSE:
            MODEL_DEPTH = True
        MetaWork.metaGeneral(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS, PREFS_FILENAME, args.tolerance, REFINE_ONLY, MODEL_SPARSE, MODEL_DEPTH, MODEL_DENSE)
    case 'archival':
        if not MODEL_SPARSE and not MODEL_DEPTH and not MODEL_DENSE:
            MODEL_DEPTH = True
        MetaWork.metaArchival(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS, PREFS_FILENAME, args.tolerance, REFINE_ONLY, MODEL_SPARSE, MODEL_DEPTH, MODEL_DENSE)

    # Do a custom workflow
    case 'custom':
        if not MODEL_SPARSE and not MODEL_DEPTH and not MODEL_DENSE:
            MODEL_DEPTH = True
        MetaWork.metaCustom(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS, PREFS_FILENAME, args)

    # Apply simple utility steps to existing project
    case 'utility':
        # Initialize the MetaUtils class
        MU = MetaWork.metaInit(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS, PREFS_FILENAME, args.tolerance)
        MU.doc.save()

        # Apply any enabled utility steps
        if args.chunkClean:
            MU.chunkCorrect()
            MU.doc.save()

        if args.regionLarge:
            MU.setRegion(1.1)
            MU.doc.save()

        if args.regionMedium:
            MU.setRegion(0.66)
            MU.doc.save()

        if args.regionSmall:
            MU.setRegion(0.33)
            MU.doc.save()

        if args.filterAggressive:
            MU.setRegion(1.1)
            MU.filterTiePoints()
            MU.doc.save()

        if args.filterNormal:
            MU.setRegion(2.0)
            MU.filterTiePoints()
            MU.doc.save()

        if args.filterLight:
            MU.setRegion(3.0)
            MU.filterTiePoints()
            MU.doc.save()

        if args.optimizeCameras:
            MU.optimizeCameraFitting()
            MU.doc.save()
