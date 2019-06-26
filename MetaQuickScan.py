"""A script for a quick, "dirty" Metashape scan"""

PATH_TO_IMAGES = "D:/OneDrive/Career/jobs/artDesign/2019/parsec/Data/Sim/Eric/EricMarkLowQ/"
IMAGE_PREFIX = "EricMarkers"
PATH_TO_MASKS = "D:/OneDrive/Career/jobs/artDesign/2019/parsec/Data/Sim/Eric/EricMarkLowQ/masks/{filename}_mask.tif"
PHASE_LABEL = "none"

import Metashape
import sys
import time

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

#AIW Check compatibility. From public Agisoft scripts.
compatible_major_version = "1.5"
found_major_version = ".".join(Metashape.app.version.split('.')[:2])
if found_major_version != compatible_major_version:
    raise Exception("Incompatible Metashape version: {} != {}".format(found_major_version, compatible_major_version))
else:
    print ((found_major_version)+(" OK"))

#SFB Get number of GPUs available
gpuList = Metashape.app.enumGPUDevices()
gpuCount = len(gpuList)

#SFB Enable all GPUs
if gpuCount > 0:
    print("Enabling %d GPUs" %(gpuCount))
    Metashape.app.gpu_mask = 2**gpuCount - 1
    Metashape.app.cpu_enable = False

#SFB Get reference to the currently active DOM
doc = Metashape.Document()
chunk = doc.addChunk()

#SFB Saves a new project to a directory.
doc.save("%s%s.psz" %(PATH_TO_IMAGES, IMAGE_PREFIX))

#SFB Build the list of image filenames
images = []
for image in range(1, 121):
    filename = ("%s%s%04d.tif" %(PATH_TO_IMAGES, IMAGE_PREFIX, image))
    images.append(filename)
print(images)

#SFB Indicate processing is starting
sys.stdout.flush()
print("\nStarting processing:")
start = time.time()

#AIW From API "Add a list of photos to the chunk." Must be run before getting a reference to camera.
phaseTime = time.time()
PHASE_LABEL = "Adding Photos"
chunk.addPhotos(images, progress=progress_callback)
print_time_elapsed(phaseTime)
doc.save()

#AIW Getting reference to camera. Index is out of range if not run after chunk.addPhotos.
camera = chunk.cameras[0]

#AIW From API "Import masks for multiple cameras." Import background images for masking out the background. Camera must be referenced for this step to work.
phaseTime = time.time()
PHASE_LABEL = "Masking Photos"
chunk.importMasks(path=PATH_TO_MASKS, source=Metashape.MaskSourceBackground, operation=Metashape.MaskOperationReplacement, tolerance=10, progress=progress_callback)
print_time_elapsed(phaseTime)
doc.save()

#AIW From API "Create markers from coded targets." Detects markers with default settings.
phaseTime = time.time()
PHASE_LABEL = "Detecting Markers"
chunk.detectMarkers(tolerance=50, filter_mask=False, inverted=False, noparity=False, maximum_residual=5, progress=progress_callback)
print_time_elapsed(phaseTime)
doc.save()

"""AIW From API "Perform image matching for the chunk frame." First step of the "Workflow" process called "Align Photos" in Metashape GUI, 
which generates the Sparse Cloud. Keypoint and Tiepoint of 0 is = no restriction. Accuracy below MediumAccuracy consistently results in failed camera alignment"""
phaseTime = time.time()
PHASE_LABEL = "Matching Photos"
chunk.matchPhotos(accuracy=Metashape.MediumAccuracy, reference_preselection=False, filter_mask=True, mask_tiepoints=False, keypoint_limit=(0), tiepoint_limit=(0), progress=progress_callback)
print_time_elapsed(phaseTime)
doc.save()

#AIW From API "Perform photo alignment for the chunk." Second step of the "Workflow" process called "Align Photos" in Metashape GUI, which generates the Sparse Cloud.
phaseTime = time.time()
PHASE_LABEL = "Aligning Cameras"
chunk.alignCameras(progress=progress_callback)
print_time_elapsed(phaseTime)
doc.save()

print("Done")
print_time_elapsed(start)