"""A script for quick, "dirty" Metashape results"""

import Metashape
import sys
import time
import MetaWork

from MetaUtilsClass import MetaUtils

#AIW Gets locations for key image files and naming conventions from the user.
PATH_TO_IMAGES = input("Image location: ")
PATH_TO_IMAGES = PATH_TO_IMAGES + "/"
print(PATH_TO_IMAGES)
IMAGE_PREFIX = input("Image prefix: ")
print(IMAGE_PREFIX)
PATH_TO_MASKS = input("Mask image location: ")
PATH_TO_MASKS = PATH_TO_MASKS + "/{filename}_mask.tif"
print(PATH_TO_MASKS)

#SFB These functions are static and can be called with just the module class name
MetaUtils.CHECK_VER(Metashape.app.version)
MetaUtils.USE_GPU()

#SFB Creating an instance will initialize the doc, the logger and the paths
MU = MetaUtils(None, PATH_TO_IMAGES, IMAGE_PREFIX)

#AIW Creates an image list and adds them to the current chunk.
MU.loadImages()

#AIW Creates masks.
MU.autoMask(PATH_TO_MASKS)

#AIW Aligns photos.
MetaWork.quickAlign(MU.chunk)

#AIW Corrects the chunk.
MU.chunkCorrect()

#AIW Creats a quick model.
MetaWork.quickModel(MU.chunk)

MU.doc.save()
print("Done")

#AIW Exits script and releases the lock on the current document.
sys.exit()
