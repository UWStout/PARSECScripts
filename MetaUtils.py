"""Script for Metashape utilities.""" 

import Metashape
import sys
import time
import logging

PHASE_LABEL = "none"

"""#AIW Check compatibility. From public Agisoft scripts.
def compat():
    compatible_major_version = "1.5"
    found_major_version = ".".join(Metashape.app.version.split('.')[:2])
    if found_major_version != compatible_major_version:
        raise Exception("Incompatible Metashape version: {} != {}".format(found_major_version, compatible_major_version))
    else:
        print ((found_major_version)+(" OK"))"""

"""#SFB Erase the current line by printing spaces
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
    logging.basicConfig(filename="{}{}_log.txt" .format(PATH_TO_IMAGES, IMAGE_PREFIX), level=logging.INFO)

#AIW Gets marker info.
def print_markers(chunk):
    for marker in chunk.markers:
        #XYZ coords?
        print(marker.position)
        #Key in dictionary
        print(marker.key)
        #These are the label names shown in Metashape GUI
        print(marker.label)