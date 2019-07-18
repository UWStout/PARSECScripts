"""Script for Metashape utilities.""" 

import Metashape
import sys
import time
import logging

compatible_major_version = "1.5"

#AIW Check compatibility. Modified from public Agisoft scripts.
def compat(metashapeVersionString):
    found_major_version = ".".join(metashapeVersionString.split('.')[:2])
    if found_major_version != compatible_major_version:
        raise Exception("Incompatible Metashape version: {} != {}".format(found_major_version, compatible_major_version))
        logging.warning("Incompatible Metashape version: {} != {}".format(found_major_version, compatible_major_version))
    else:
        print ((found_major_version)+(" OK"))
        logging.info(("Metashape version: ")+(found_major_version)+(" OK"))

"""PHASE_LABEL = "none"
#SFB Erase the current line by printing spaces
# - Does not advance to the next line
def blank_line(length=80):
    empty = " " * length
    print(empty, end='\r')

#SFB Print the current progress over the current line
# - Does not advance to the next line
def progress_callback(prog):
    blank_line()
    print("%s: Progress %6.2f%%" %(PHASE_LABEL, prog), end='\r')
    sys.stdout.flush()

def print_time_elapsed(startTime):
    print("\nElapsed Time: %.2fsecs" %(time.time() - startTime))

def start_time():
    #SFB Indicate processing is starting
    sys.stdout.flush()
    print("\nStarting processing:")
    start = time.time()"""

#AIW Creates a log text file.
def log(PATH_TO_IMAGES, IMAGE_PREFIX):
    logging.basicConfig(filename="{}{}_log.txt".format(PATH_TO_IMAGES, IMAGE_PREFIX), format='%(asctime)s %(messages)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

#AIW Enables GPU processing in Metashape.
def use_gpu():
    #SFB Get number of GPUs available
    gpuList = Metashape.app.enumGPUDevices()
    gpuCount = len(gpuList)

    #SFB Enable all GPUs
    if gpuCount > 0:
        print("Enabling %d GPUs" %(gpuCount))
        Metashape.app.gpu_mask = 2**gpuCount - 1
        Metashape.app.cpu_enable = False
        print("Done")
        logging.info("Enabled %d GPUs" %(gpuCount))

#AIW Automates correction processes for the chunk.
def chunk_correct(doc, chunk):
    #SFB Changes the dimensions of the chunk's reconstruction volume.
    print("Correcting chunk")
    logging.info("Started correcting chunk")
    NEW_REGION = doc.chunk.region
    NEW_REGION.size = NEW_REGION.size * 2.0
    doc.chunk.region = NEW_REGION
    print("Done")
    logging.info("Done")

#AIW Creates an image list and adds them to the current chunk.
def image_list(chunk, PATH_TO_IMAGES, IMAGE_PREFIX):
    #SFB Build the list of image filenames
    images = []

    print("Creating image list")
    logging.info("Started creating image list")
    for image in range(1, 121):
        filename = ("%s%s%04d.tif" %(PATH_TO_IMAGES, IMAGE_PREFIX, image))
        images.append(filename)
    print(images)

    #AIW From API "Add a list of photos to the chunk." 
    chunk.addPhotos(images)
    print("Done")
    logging.info(images)
    logging.info("Done")

#AIW Automates masking.
def auto_mask(chunk, PATH_TO_MASKS):
    #AIW Getting reference to camera. Index is out of range if not run after chunk.addPhotos.
    camera = chunk.cameras[0]
    print("Creating masks")
    logging.info("Started creating masks")

    #AIW From API "Import masks for multiple cameras." 
    # - Import background images for masking out the background. 
    # - Camera must be referenced for this step to work.
    chunk.importMasks(path=PATH_TO_MASKS, source=Metashape.MaskSourceBackground, operation=Metashape.MaskOperationReplacement, tolerance=10)
    print("Done")
    logging.info("Done")

#AIW Places markers on coded targets in images.
def place_markers(chunk):
        print("Placing markers")
        logging.info("Started placing markers")
        chunk.detectMarkers(tolerance=50, filter_mask=False, inverted=False, noparity=False, maximum_residual=5)
        print("Done")
        logging.info("Done")

#AIW Gets marker info.
def print_markers(chunk):
    for marker in chunk.markers:
        print("Getting marker info")
        #XYZ coords?
        print(marker.position)
        #Key in dictionary
        print(marker.key)
        #These are the label names shown in Metashape GUI
        print(marker.label)
        print("Done")