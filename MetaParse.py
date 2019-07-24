"""command-line interface for processing photogrammetry data with Metashape"""
import sys
import argparse
import Metashape
import MetaWork

from MetaUtilsClass import MetaUtils

parser = argparse.ArgumentParser(description = "Command-line interface for processing photogrammetry data with Metashape")
PATH_TO_IMAGES = ""
IMAGE_PREFIX = ""
PATH_TO_MASKS = ""

#AIW Gets locations for key image files and naming conventions from the user.
def userInput(PATH_TO_IMAGES, IMAGE_PREFIX, PATH_TO_MASKS):
    PATH_TO_IMAGES = input("Image location: ")
    PATH_TO_IMAGES = PATH_TO_IMAGES + "/"
    IMAGE_PREFIX = input("Image prefix: ")
    PATH_TO_MASKS = input("Mask image location: ")
    PATH_TO_MASKS = PATH_TO_MASKS + "/{filename}_mask.tif"

parser.add_argument("-getD", "--getData", action="callback", help="Gets locations for key image files and naming conventions")
parser.add_argument("-MQ", "--MetaQuick", action="callback", help="Run A script for quick but unoptimized Metashape results")

#SFB These functions are static and can be called with just the module class name
MetaUtils.CHECK_VER(Metashape.app.version)
MetaUtils.USE_GPU()

#SFB Creating an instance will initialize the doc, the logger and the paths
MU = MetaUtils(None, PATH_TO_IMAGES, IMAGE_PREFIX)

args = parser.parse_args()