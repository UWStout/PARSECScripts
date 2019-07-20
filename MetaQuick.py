"""A script for quick, "dirty" Metashape results"""

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

#AIW Check Metashape version compatibility.
MetaUtils.check_ver(Metashape.app.version)

#AIW Enables GPU processing in Metashape.
MetaUtils.use_gpu()

#AIW creates a new document or loads a previous one.
#MetaUtils.doc_mngr(PATH_TO_IMAGES, IMAGE_PREFIX)

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

#AIW Creates an image list and adds them to the current chunk.
MetaUtils.image_list(chunk, PATH_TO_IMAGES, IMAGE_PREFIX)

#AIW Creates masks.
MetaUtils.auto_mask(chunk, PATH_TO_MASKS)

#AIW Aligns photos.
MetaWork.quick_align(chunk)

#AIW Corrects the chunk.
MetaUtils.chunk_correct(doc, chunk)

#AIW Creats a quick model.
MetaWork.quick_model(chunk)

doc.save()

print("Done")

#AIW Exits script and releases the lock on the current document.
sys.exit()