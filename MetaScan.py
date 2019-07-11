"""MetaScan is a script for automating the processing of photogrametry data with Metashape for archival use."""

#AIW Change this path to where user has their scan data stored. Create a folder 
# in this dir named 'masks' and place empty images to use for bg masks.
PATH_TO_IMAGES = "D:/OneDrive/Career/jobs/artDesign/2019/Parsec/Data/Sim/Eric/EricMarkersHQ/"
IMAGE_PREFIX = "EricMarkers"
#AIW Change this path to the masks' folder in the user's scan data directory.
PATH_TO_MASKS = "D:/OneDrive/Career/jobs/artDesign/2019/Parsec/Data/Sim/Eric/EricMarkersHQ/Masks/{filename}_mask.tif"
PHASE_LABEL = "none"

import Metashape
import sys
import time

#AIW Creates a console log.
# - Currently unable to specify a path or filename.
# - Will save outside image folder. 
Metashape.Application.Settings(log_enable=True)

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
except:
    print("No document exists!\nCreating a new document.")
    doc.save("{}{}.psx" .format(PATH_TO_IMAGES, IMAGE_PREFIX))

#AIW Reference chunk in the current document.
chunk = doc.chunk

#SFB Indicate processing is starting
sys.stdout.flush()
print("\nStarting processing:")
start = time.time()

#AIW The masking step is currently handled by MetaQuickScript. 
"""#AIW From API "Import masks for multiple cameras." 
# - Import background images for masking out the background. 
# - Camera must be referenced for this step to work.
phaseTime = time.time()
PHASE_LABEL = "Masking Photos"
chunk.importMasks(path=PATH_TO_MASKS, source=Metashape.MaskSourceBackground, operation=Metashape.MaskOperationReplacement, tolerance=10, progress=progress_callback)
print_time_elapsed(phaseTime)
doc.save()"""

#AIW The HighAccuracy parameter for the matchPhotos function from MetaQuickScan works well.
# - HighestAccuracy will be tested to see if it is valuable.
"""#AIW From API "Perform image matching for the chunk frame." 
# - First step of the Metashape GUI "Workflow" process called "Align Photos", which generates the Sparse Cloud/Tie Points. 
# - Keypoints and Tiepoints are set to unlimited. 
# - Accuracy below MediumAccuracy consistently results in failed camera alignment.
phaseTime = time.time()
PHASE_LABEL = "Matching Photos"
chunk.matchPhotos(accuracy=Metashape.HighestAccuracy, generic_preselection=True, filter_mask=True, mask_tiepoints=False, keypoint_limit=(0), tiepoint_limit=(0), progress=progress_callback)
print_time_elapsed(phaseTime)
doc.save()

#AIW From API "Perform photo alignment for the chunk." 
# - Second step of the Metashape GUI "Workflow" process called "Align Photos", which generates the Sparse Cloud/Tie Points.
phaseTime = time.time()
PHASE_LABEL = "Aligning Cameras"
chunk.alignCameras(progress=progress_callback)
print_time_elapsed(phaseTime)
doc.save()

#SFB Changes the dimensions of the chunk's reconstruction volume.
phaseTime = time.time()
PHASE_LABEL = "Changing Reconstruction Volume dimensions"
NEW_REGION = doc.chunk.region
NEW_REGION.size = NEW_REGION.size * 2.0
doc.chunk.region = NEW_REGION
print_time_elapsed(phaseTime)
doc.save()"""

#AIW From API "Generate depth maps for the chunk."
# - First step of the Metashape GUI "Workflow" process called "Dense Cloud".
# - max_neighbors parameter may save time and help with shadows. -1 is none.
phaseTime = time.time()
PHASE_LABEL = "Building Depth Maps"
chunk.buildDepthMaps(quality=Metashape.HighQuality, filter=Metashape.AggressiveFiltering, progress=progress_callback)
#AIW No image scaling (highly detailed geometry) and will filter fine details.
#chunk.buildDepthMaps(quality=Metashape.UltraQuality, filter=Metashape.AggressiveFiltering, progress=progress_callback)
#AIW No image scaling (highly detailed geometry) and will pull all details possible from images.
#chunk.buildDepthMaps(quality=Metashape.UltraQuality, filter=Metashape.MildFiltering, progress=progress_callback)
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
#AIW volumetric_masks=True will use masks to supress noise. Increases processing time.
#chunk.buildModel(surface=Metashape.Arbitrary, interpolation=Metashape.EnabledInterpolation, face_count=Metashape.HighFaceCount, source=Metashape.DenseCloudData, vertex_colors=True, volumetric_masks=True, keep_depth=True, progress=progress_callback)
#AIW interpolation=Metashape.DisabledInterpolation will not try to fill holes in geometry. More accurate to source but requires manual post-processing.
#chunk.buildModel(surface=Metashape.Arbitrary, interpolation=Metashape.DisabledInterpolation, face_count=Metashape.HighFaceCount, source=Metashape.DenseCloudData, vertex_colors=True, keep_depth=True, progress=progress_callback)
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

#AIW Exits Metashape releasing the lock on the current document.
Metashape.app.quit()