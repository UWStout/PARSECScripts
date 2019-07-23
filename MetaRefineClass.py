"""MetaScan is a script for automating the processing of photogrametry data with Metashape for archival use."""

import Metashape
import sys
import time
import MetaWork

from MetaUtilsClass import MetaUtils

#AIW Change this path to where user has their scan data stored. Create a folder 
# in this dir named 'masks' and place empty images to use for bg masks.
PATH_TO_IMAGES = "E:/ParsecExp/EricMarkersHQ/"
IMAGE_PREFIX = "EricMarkers"
#AIW Change this path to the masks' folder in the user's scan data directory.
PATH_TO_MASKS = "E:/ParsecExp/EricMarkersHQ/Masks/{filename}_mask.tif"
PHASE_LABEL = "none"

#AIW From MetaQuickClass
#SFB These functions are static and can be called with just the module class name
MetaUtils.CHECK_VER(Metashape.app.version)
MetaUtils.USE_GPU()

#AIW From MetaQuickClass
#SFB Creating an instance will initialize the doc, the logger and the paths
MU = MetaUtils(None, PATH_TO_IMAGES, IMAGE_PREFIX)

#AIW Creates a dense cloud for general use.
MetaWork.gen_dense_cloud(MU.chunk)

#AIW Creates a modelfor general use.
MetaWork.gen_model(MU.chunk)

MU.doc.save()
print("Done")

#AIW Exits script and releases the lock on the current document.
sys.exit()