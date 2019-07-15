"""MetaScan is a script for automating the processing of photogrametry data with Metashape for archival use."""

#AIW Change this path to where user has their scan data stored. Create a folder 
# in this dir named 'masks' and place empty images to use for bg masks.
PATH_TO_IMAGES = "E:/ParsecExp/EricMarkersHQ/"
IMAGE_PREFIX = "EricMarkers"
#AIW Change this path to the masks' folder in the user's scan data directory.
PATH_TO_MASKS = "E:/ParsecExp/EricMarkersHQ/Masks/{filename}_mask.tif"
PHASE_LABEL = "none"
#AIW Creates a log and saves to same location as images.
LOG = open("{}{}_log.txt".format(PATH_TO_IMAGES,IMAGE_PREFIX), 'w')

import Metashape
import sys
import time

#AIW Saves system output into the LOG.
sys.stdout = LOG
# - this portion only applys to scripts run in Metashape GUI
Metashape.app.settings.log_enable = True
Metashape.app.settings.log_path = "{}/log.txt" .format(PATH_TO_IMAGES)

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

#AIW Attemtps to open an existing project. 
# - A new project is created if an existing project is not available.
# - This must be done immediatly after getting reference to active DOM.
# - .psx format will not save correctly otherwise.
try:
    doc.open("{}{}.psx" .format(PATH_TO_IMAGES, IMAGE_PREFIX), read_only=False, ignore_lock=True)
    print("Using existing document.")
except:
    print("No document exists!\nCreating a new document.")
    doc.save("{}{}.psx" .format(PATH_TO_IMAGES, IMAGE_PREFIX))

#AIW Reference chunk in the current document.
chunk = doc.chunk

#SFB Indicate processing is starting
sys.stdout.flush()
print("\nStarting processing:")
start = time.time()

#AIW From API "Generate depth maps for the chunk."
# - First step of the Metashape GUI "Workflow" process called "Dense Cloud".
# - max_neighbors parameter may save time and help with shadows. -1 is none.
phaseTime = time.time()
PHASE_LABEL = "Building Depth Maps"
chunk.buildDepthMaps(quality=Metashape.HighQuality, filter=Metashape.AggressiveFiltering, max_neighbors=100, progress=progress_callback)
print_time_elapsed(phaseTime)
doc.save

#AIW From API "Generate dense cloud for the chunk."
# - Second step of the Metashape GUI "Workflow" process called "Dense Cloud".
phaseTime = time.time()
PHASE_LABEL = "Building Dense Cloud"
chunk.buildDenseCloud(point_colors=True, keep_depth=True, max_neighbors=100, progress=progress_callback)
print_time_elapsed(phaseTime)
doc.save()

#AIW From API "Generate model for the chunk frame." 
# - Builds mesh to be used for next steps.
phaseTime = time.time()
PHASE_LABEL = "3D Model"
chunk.buildModel(surface=Metashape.Arbitrary, interpolation=Metashape.EnabledInterpolation, face_count=Metashape.HighFaceCount, source=Metashape.DenseCloudData, vertex_colors=True, keep_depth=True, progress=progress_callback)
print_time_elapsed(phaseTime)
doc.save()

#AIW From API "Generate uv mapping for the model."
phaseTime = time.time()
PHASE_LABEL = "UV 3D Model"
chunk.buildUV(progress=progress_callback)
print_time_elapsed(phaseTime)
doc.save()

#AIW From API "Generate texture for the chunk." 
# - Generates a 4k texture for the 3D model.
phaseTime = time.time()
PHASE_LABEL = "Generate Texture"
chunk.buildTexture(blending=Metashape.MosaicBlending, size=(4096), fill_holes=False, progress=progress_callback)
print_time_elapsed(phaseTime)
doc.save()

print("Done")
print_time_elapsed(start)

#AIW Exits script and releases the lock on the current document.
sys.exit()