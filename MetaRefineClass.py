"""MetaScan is a script for automating the processing of photogrametry data with Metashape for archival use."""

import Metashape
import sys
import time
import MetaWork

from MetaUtilsClass import MetaUtils

#AIW Gets locations for key image files and naming conventions from the user.
PATH_TO_IMAGES = input("Image location: ")
PATH_TO_IMAGES = PATH_TO_IMAGES + "\\"
print(PATH_TO_IMAGES)
IMAGE_PREFIX = input("Image prefix: ")
print(IMAGE_PREFIX)
PATH_TO_MASKS = input("Mask image location: ")
PATH_TO_MASKS = PATH_TO_MASKS + "\\{filename}_mask.tif"
print(PATH_TO_MASKS)

#AIW From MetaQuickClass
#SFB These functions are static and can be called with just the module class name
MetaUtils.CHECK_VER(Metashape.app.version)
MetaUtils.USE_GPU()

#AIW From MetaQuickClass
#SFB Creating an instance will initialize the doc, the logger and the paths
MU = MetaUtils(None, PATH_TO_IMAGES, IMAGE_PREFIX)

#AIW Creates a dense cloud for general use.
MetaWork.genDenseCloud(MU.chunk)

#AIW Creates a modelfor general use.
MetaWork.genModel(MU.chunk)

MU.doc.save()
print("Done")

#AIW Exits script and releases the lock on the current document.
sys.exit()