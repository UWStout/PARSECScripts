import sys
import argparse

from ProjectPrefs import ProjectPrefs

PATH_TO_IMAGES = "E:/ParsecExp/EricMarkersHQ/"
IMAGE_PREFIX = "EricMarkers"
PATH_TO_MASKS = "E:/ParsecExp/EricMArkersHQ/Masks/{filename}_mask.tif"

#SFB Import and initialize the logging system
#SFB This also redirects all MetaScan output
#SFB Reads config from the file 'logging.inf'
import Logger
Logger.init(PATH_TO_IMAGES, IMAGE_PREFIX)
logger = Logger.getLogger()

import Metashape
import MetaWork
from MetaUtilsClass import MetaUtils

parser = argparse.ArgumentParser()
#AIW Sets project
#AIW parser.add_argument('-P', '--project', help='Specifies project file path and name.')
#AIW Runs MetaQuickClass
parser.add_argument('-Q', '--quick', type=MetaWork.metaQuick, help='Quickly process photogrammetry data')
parser.add_argument('-R', '--refine', help='Refines previously processed photogrammetry data')

MetaUtils.CHECK_VER(Metashape.app.version)
MetaUtils.USE_GPU()

args = parser.parse_args()
#args.quick = MetaWork.metaQuick
#args.quick(PATH_TO_IMAGES, IMAGE_PREFIX, PATH_TO_MASKS)


#args.refine = MetaWork.metaRefine
#args.refine(PATH_TO_IMAGES, IMAGE_PREFIX)

#prefs = ProjectPrefs(args.project)
