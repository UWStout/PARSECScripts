"""MetaScan is a script for automating the processing of photogrametry data with Metashape for archival use."""

import Metashape
import sys
import time
import MetaWork
import MetaUtils

#AIW Change this path to where user has their scan data stored. Create a folder 
# in this dir named 'masks' and place empty images to use for bg masks.
PATH_TO_IMAGES = "E:/ParsecExp/EricMarkersHQ/"
IMAGE_PREFIX = "EricMarkers"
#AIW Change this path to the masks' folder in the user's scan data directory.
PATH_TO_MASKS = "E:/ParsecExp/EricMarkersHQ/Masks/{filename}_mask.tif"
PHASE_LABEL = "none"

#AIW Creates a log.
MetaUtils.log(PATH_TO_IMAGES, IMAGE_PREFIX)

#AIW Check compatibility.
MetaUtils.check_ver(Metashape.app.version)

#AIW Enables GPU processing in Metashape.
MetaUtils.use_gpu()

#SFB Get reference to the currently active DOM
doc = Metashape.Document()

#AIW Attemtps to open an existing project. 
# - A new project is created if an existing project is not available.
# - This must be done immediatly after getting reference to active DOM.
# - .psx format will not save correctly otherwise.
try:
    doc.open("{}{}.psx" .format(PATH_TO_IMAGES, IMAGE_PREFIX), read_only=False, ignore_lock=True)
    print("Using existing document.")
    chunk = doc.chunk
except:
    print("No document exists!\nCreating a new document.")
    doc.save("{}{}.psx" .format(PATH_TO_IMAGES, IMAGE_PREFIX))
    chunk = doc.addChunk()

#AIW Creates a dense cloud for general use.
MetaWork.gen_dense_cloud(chunk)

#AIW Creates a modelfor general use.
MetaWork.gen_model(chunk)

print("Done")

#AIW Exits script and releases the lock on the current document.
sys.exit()