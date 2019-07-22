"""A script for quick, "dirty" Metashape results"""

import Metashape
import sys
import time
import MetaWork

from MetaUtilsClass import MetaUtils

#AIW Change this path to where user has their scan data stored. Create a folder 
# in this dir named 'masks' and place empty images to use for bg masks.
PATH_TO_IMAGES = "/Volumes/Samsung_T5/SimulatedScans/Reconstruct/Images/"
IMAGE_PREFIX = "EricMarkersHQ"
#AIW Change this path to the masks' folder in the user's scan data directory.
PATH_TO_MASKS = "/Volumes/Samsung_T5/SimulatedScans/Reconstruct/Background/Background{filename}.tif"

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
MetaWork.quick_align(MU.chunk)

#AIW Corrects the chunk.
MU.chunkCorrect()

#AIW Creats a quick model.
MetaWork.quick_model(MU.chunk)

MU.doc.save()
print("Done")

#AIW Exits script and releases the lock on the current document.
sys.exit()
