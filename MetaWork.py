"""A script containing various Metashape workflows."""

import Metashape
from CustomProgress import PBar

from ProjectPrefs import ProjectPrefs
from MetaUtilsClass import MetaUtils

# Import the logging module and get a custom logger for this module
import Logger
logger = None

def ensureLoggerReady():
    global logger
    if logger is None:
        logger = Logger.getLogger('MetaUtils')

"""Alignment Options"""
# Automates Metashape GUI process "Add Photos", "Tool->Detect Markers",
# "Workflow->Align Photos" with settings for quick results.
def quickAlign(chunk, prefsFileName=None, refine=False):
    ensureLoggerReady()
    # From API "Perform image matching for the chunk frame."
    # - First step of the Metashape GUI "Workflow" process "Align Photos",
    #   which generates the Sparse Cloud/Tie Points.
    # - Keypoints and Tiepoints for this script is Agisoft's suggested default.
    # - Accuracy below MediumAccuracy consistently results in failed camera
    #   alignment.
    # - HighAccuracy is used in this script as the results are better for and
    #   the time added is negligible.
    logger.info("Quickly aligning photos")
    elapsed1 = -1
    with PBar("Matching Photos     ") as pbar:
        chunk.matchPhotos(downscale=2, generic_preselection=True, filter_mask=True, reset_matches=(not refine),
                        mask_tiepoints=False, keypoint_limit=(40000), tiepoint_limit=(4000),
                        progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed1 = pbar.getTime()

    # From API "Perform photo alignment for the chunk."
    # - Second step of the Metashape GUI "Workflow" process "Align Photos",
    #   which generates the Sparse Cloud/Tie Points.
    elapsed2 = -1
    with PBar("Aligning Cameras    ") as pbar:
        chunk.alignCameras(progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed2 = pbar.getTime()

    logger.info("Done aligning photos")

    # Write the timing to the project preferences file
    if prefsFileName is not None:
        prefs = ProjectPrefs(prefsFileName)
        prefs.setPref('IMAGE_ALIGN', elapsed1 + elapsed2)
        prefs.setPref('IMAGE_ALIGN_MATCHING', elapsed1)
        prefs.setPref('IMAGE_ALIGN_BUNDLE_ADJUST', elapsed2)
        prefs.saveConfig()

# Automates Metashape GUI process "Add Photos", "Tool->Detect Markers",
# "Workflow->Align Photos" with settings for general results.
def genAlign(chunk, prefsFileName=None, refine=False):
    ensureLoggerReady()
    # From API "Perform image matching for the chunk frame."
    # - First step of the Metashape GUI "Workflow" process "Align Photos",
    #   which generates the Sparse Cloud/Tie Points.
    # - Keypoints and Tiepoints for this script is Agisoft's suggested default.
    # - Accuracy below MediumAccuracy consistently results in failed camera
    #   alignment.
    # - HighAccuracy is used in this script as the results are better for and
    #   the time added is negligible.
    logger.info("Aligning photos for general quality")
    elapsed1 = -1
    with PBar("Matching Photos     ") as pbar:
        chunk.matchPhotos(downscale=1, generic_preselection=True, filter_mask=True, reset_matches=(not refine),
                      mask_tiepoints=False, keypoint_limit=(40000), tiepoint_limit=(20000),
                      progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed1 = pbar.getTime()

    # From API "Perform photo alignment for the chunk."
    # - Second step of the Metashape GUI "Workflow" process "Align Photos",
    #   which generates the Sparse Cloud/Tie Points.
    elapsed2 = -1
    with PBar("Aligning Cameras    ") as pbar:
        chunk.alignCameras(progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed2 = pbar.getTime()

    logger.info("Done aligning photos")

    # Save timing information to project preferences file
    if prefsFileName is not None:
        prefs = ProjectPrefs(prefsFileName)
        prefs.setPref('IMAGE_ALIGN', elapsed1 + elapsed2)
        prefs.setPref('IMAGE_ALIGN_MATCHING', elapsed1)
        prefs.setPref('IMAGE_ALIGN_BUNDLE_ADJUST', elapsed2)
        prefs.saveConfig()


# Automates Metashape GUI process "Add Photos", "Tool->Detect Markers",
# "Workflow->Align Photos" with settings for archival results.
def arcAlign(chunk, prefsFileName=None, refine=False):
    ensureLoggerReady()
    # From API "Perform image matching for the chunk frame."
    # - First step of the Metashape GUI "Workflow" process "Align Photos",
    #   which generates the Sparse Cloud/Tie Points.
    # - Keypoints and Tiepoints for this script is Agisoft's suggested default.
    # - Accuracy below MediumAccuracy consistently results in failed camera
    #   alignment.
    # - HighAccuracy is used in this script as the results are better for and
    #   the time added is negligible.
    logger.info("Aligning photos for archival quality")
    elapsed1 = -1
    with PBar("Matching Photos     ") as pbar:
        chunk.matchPhotos(downscale=0, generic_preselection=True, filter_mask=True, reset_matches=(not refine),
                      mask_tiepoints=False, keypoint_limit=(40000), tiepoint_limit=(40000),
                      progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed1 = pbar.getTime()

    # From API "Perform photo alignment for the chunk."
    # - Second step of the Metashape GUI "Workflow" process "Align Photos",
    #   which generates the Sparse Cloud/Tie Points.
    elapsed2 = -1
    with PBar("Aligning Cameras    ") as pbar:
        chunk.alignCameras(progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed2 = pbar.getTime()

    logger.info("Done aligning photos")

    # Save timing information to project preferences file
    if prefsFileName is not None:
        prefs = ProjectPrefs(prefsFileName)
        prefs.setPref('IMAGE_ALIGN', elapsed1 + elapsed2)
        prefs.setPref('IMAGE_ALIGN_MATCHING', elapsed1)
        prefs.setPref('IMAGE_ALIGN_BUNDLE_ADJUST', elapsed2)
        prefs.saveConfig()


"""Dense Cloud Options"""
# Automates Metashape GUI "Workflow->Dense Cloud" with settings for
# general use.
def genDenseCloud(chunk, prefsFileName=None):
    ensureLoggerReady()
    # From API "Generate depth maps for the chunk."
    # - First step of the Metashape GUI "Workflow" process called
    #   "Dense Cloud".
    # - max_neighbors parameter may save time and help with shadows.
    #   -1 is none.
    elapsed1 = -1
    logger.info("Building general quality Dense Cloud")
    with PBar("Building Depth Maps ") as pbar:
        chunk.buildDepthMaps(downscale=2, filter_mode=Metashape.AggressiveFiltering,
            max_neighbors=100, progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed1 = pbar.getTime()

    # From API "Generate dense cloud for the chunk."
    # - Second step of the Metashape GUI "Workflow" process called
    #   "Dense Cloud".
    elapsed2 = -1
    with PBar("Building Point Cloud") as pbar:
        chunk.buildPointCloud(point_colors=False, keep_depth=True,
            max_neighbors=100, progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed2 = pbar.getTime()

    logger.info("Done building dense cloud")

    # Save timing information to project preferences file
    if prefsFileName is not None:
        prefs = ProjectPrefs(prefsFileName)
        prefs.setPref('DENSE_CLOUD', elapsed1 + elapsed2)
        prefs.setPref('DENSE_CLOUD_DEPTH_MAPS', elapsed1)
        prefs.setPref('DENSE_CLOUD_BUILD', elapsed2)
        prefs.saveConfig()


# Automates Metashape GUI "Workflow->Dense Cloud" with settings for
# archival use.
def arcDenseCloud(chunk, prefsFileName=None):
    ensureLoggerReady()
    # From API "Generate depth maps for the chunk."
    # - First step of the Metashape GUI "Workflow" process called
    #   "Dense Cloud".
    # - max_neighbors parameter may save time and help with shadows.d
    #   -1 is none.
    elapsed1 = -1
    logger.info("Building archival quality Dense Cloud")
    with PBar("Building Depth Maps ") as pbar:
        chunk.buildDepthMaps(downscale=1, filter_mode=Metashape.MildFiltering,
            max_neighbors=100, progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed1 = pbar.getTime()

    # From API "Generate dense cloud for the chunk."
    # - Second step of the Metashape GUI "Workflow" process called
    # "Dense Cloud".
    elapsed2 = -1
    with PBar("Building Point Cloud") as pbar:
        chunk.buildPointCloud(point_colors=False, keep_depth=True,
            max_neighbors=100, progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed2 = pbar.getTime()

    logger.info("Done building dense cloud")

    # Save timing information to project preferences file
    if prefsFileName is not None:
        prefs = ProjectPrefs(prefsFileName)
        prefs.setPref('DENSE_CLOUD', elapsed1 + elapsed2)
        prefs.setPref('DENSE_CLOUD_DEPTH_MAPS', elapsed1)
        prefs.setPref('DENSE_CLOUD_BUILD', elapsed2)
        prefs.saveConfig()


"""Model Options"""
# Automates Metashape GUI "Workflow" process "Build Mesh" and
# "Build Texture" with settings for quick results.
def quickModel(chunk, prefsFileName=None):
    ensureLoggerReady()
    # From API "Generate model for the chunk frame." Builds mesh to be
    # used in the last steps.
    logger.info("Quickly generating textured 3D model")
    elapsed1 = -1
    with PBar("Generating Model    ") as pbar:
        chunk.buildModel(surface_type=Metashape.Arbitrary,
                        interpolation=Metashape.EnabledInterpolation,
                        face_count=Metashape.HighFaceCount,
                        source_data=Metashape.TiePointsData,
                        vertex_colors=True, progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed1 = pbar.getTime()

    # From API "Generate uv mapping for the model."
    elapsed2 = -1
    with PBar("Generating UV Coords") as pbar:
        chunk.buildUV(progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed2 = pbar.getTime()

    # From API "Generate texture for the chunk."
    # - Generates a basic texture for the 3D model.
    elapsed3 = -1
    with PBar("Generating 1k Tex   ") as pbar:
        chunk.buildTexture(blending_mode=Metashape.MosaicBlending,
                        texture_size=(1024), fill_holes=False,
                        progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed3 = pbar.getTime()

    logger.info("Done generating model")

    # Save timing information to project preferences file
    if prefsFileName is not None:
        prefs = ProjectPrefs(prefsFileName)
        prefs.setPref('BUILD_MODEL', elapsed1 + elapsed2 + elapsed3)
        prefs.setPref('BUILD_MODEL_MESH', elapsed1)
        prefs.setPref('BUILD_MODEL_UV', elapsed2)
        prefs.setPref('BUILD_MODEL_TEXTURE', elapsed3)
        prefs.saveConfig()


# Automates Metashape GUI "Workflow" process "Build Mesh" and
# "Build Texture" with settings for general use.
def genModel(chunk, prefsFileName=None):
    ensureLoggerReady()
    # From API "Generate model for the chunk frame." Builds mesh to be
    # used in the last steps.
    logger.info("Building general quality textured 3D model")
    elapsed1 = -1
    with PBar("Generating Model    ") as pbar:
        chunk.buildModel(surface_type=Metashape.Arbitrary,
                        interpolation=Metashape.EnabledInterpolation,
                        face_count=Metashape.HighFaceCount,
                        source_data=Metashape.PointCloudData,
                        vertex_colors=False, keep_depth=True,
                        progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed1 = pbar.getTime()

    # From API "Generate uv mapping for the model."
    elapsed2 = -1
    with PBar("Generating UV Coords") as pbar:
        chunk.buildUV(progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed2 = pbar.getTime()

    # From API "Generate texture for the chunk."
    # - Generates a 4k texture for the 3D model.
    elapsed3 = -1
    with PBar("Generating 4k Tex   ") as pbar:
        chunk.buildTexture(blending_mode=Metashape.MosaicBlending,
                           texture_size=(4096), fill_holes=False,
                           progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed3 = pbar.getTime()

    logger.info("Done building model")

    # Save timing information to project preferences file
    if prefsFileName is not None:
        prefs = ProjectPrefs(prefsFileName)
        prefs.setPref('BUILD_MODEL', elapsed1 + elapsed2 + elapsed3)
        prefs.setPref('BUILD_MODEL_MESH', elapsed1)
        prefs.setPref('BUILD_MODEL_UV', elapsed2)
        prefs.setPref('BUILD_MODEL_TEXTURE', elapsed3)
        prefs.saveConfig()

# Automates Metashape GUI "Workflow" process "Build Mesh" and
# "Build Texture" with settings for archival use.
def arcModel(chunk, prefsFileName=None):
    ensureLoggerReady()
    # From API "Generate model for the chunk frame." Builds accurate mesh
    # without generating extra geometry to be used in the last steps.
    logger.info("Building archival quality textured 3D model")
    elapsed1 = -1
    with PBar("Generating Model    ") as pbar:
        chunk.buildModel(surface_type=Metashape.Arbitrary,
                         interpolation=Metashape.EnabledInterpolation,
                         face_count=Metashape.HighFaceCount,
                         source_data=Metashape.PointCloudData,
                         vertex_colors=False, keep_depth=True,
                         progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed1 = pbar.getTime()

    # From API "Generate uv mapping for the model."
    elapsed2 = -1
    with PBar("Generating UV Coords") as pbar:
        chunk.buildUV(progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed2 = pbar.getTime()

    # From API "Generate texture for the chunk."
    # - Generates a 16k texture for the 3D model.
    elapsed3 = -1
    with PBar("Generating 8k Tex   ") as pbar:
        chunk.buildTexture(blending_mode=Metashape.MosaicBlending,
                           texture_size=(8192), fill_holes=False,
                           progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed3 = pbar.getTime()

    logger.info("Done building model")

    # Save timing information to project preferences file
    if prefsFileName is not None:
        prefs = ProjectPrefs(prefsFileName)
        prefs.setPref('BUILD_MODEL', elapsed1 + elapsed2 + elapsed3)
        prefs.setPref('BUILD_MODEL_MESH', elapsed1)
        prefs.setPref('BUILD_MODEL_UV', elapsed2)
        prefs.setPref('BUILD_MODEL_TEXTURE', elapsed3)
        prefs.saveConfig()


"""Workflow Options"""
# Quick photogrammetry processing.
def metaQuick(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS=None, prefsFileName=None):
    ensureLoggerReady()
    logger.info("Starting quick processing")

    # Creating an instance will initialize the doc, the logger
    # and the paths
    MU = MetaUtils(None, PATH_TO_IMAGES, PROJECT_NAME)

    # Creates an image list and adds them to the current chunk.
    loadElapsed = MU.loadImages()

    # Places markers on coded targets in images.
    markersElapsed = MU.detectMarkers()

    # Creates masks.
    maskElapsed = None
    if PATH_TO_MASKS is not None:
        maskElapsed = MU.autoMask(PATH_TO_MASKS)
    MU.doc.save()

    # Aligns photos.
    quickAlign(MU.chunk, prefsFileName)
    MU.doc.save()

    # Corrects the chunk.
    MU.chunkCorrect()

    # Creates a quick model.
    quickModel(MU.chunk, prefsFileName)
    MU.doc.save()

    if prefsFileName is not None:
        prefs = ProjectPrefs(prefsFileName)
        prefs.setPref('INIT', loadElapsed + markersElapsed +
                      (0 if maskElapsed is None else maskElapsed))
        prefs.setPref('INIT_IMAGE_LOAD', loadElapsed)
        prefs.setPref('INIT_DETECT_MARKERS', markersElapsed)
        if maskElapsed is not None:
            prefs.setPref('INIT_APPLY_MASKS', maskElapsed)
        prefs.saveConfig()

    logger.info("Quick processing done")

# General photogrammetry processing.
def metaGeneral(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS=None, prefsFileName=None):
    ensureLoggerReady()
    logger.info("Starting general quality processing")

    # Creating an instance will initialize the doc, the logger
    # and the paths
    MU = MetaUtils(None, PATH_TO_IMAGES, PROJECT_NAME)

    # Creates an image list and adds them to the current chunk.
    loadElapsed = MU.loadImages()

    # Places markers on coded targets in images.
    markersElapsed = MU.detectMarkers()

    # Creates masks.
    maskElapsed = None
    if PATH_TO_MASKS is not None:
        maskElapsed = MU.autoMask(PATH_TO_MASKS)

    # Aligns photos.
    genAlign(MU.chunk, prefsFileName)
    MU.doc.save()

    # Corrects the chunk.
    MU.chunkCorrect()

    # Generate the dense cloud.
    genDenseCloud(MU.chunk, prefsFileName)
    MU.doc.save()

    # Creates a general model.
    genModel(MU.chunk, prefsFileName)
    MU.doc.save()

    # Write the elapsed times to the project prefs file
    if prefsFileName is not None:
        prefs = ProjectPrefs(prefsFileName)
        prefs.setPref('INIT', loadElapsed + markersElapsed +
                      (0 if maskElapsed is None else maskElapsed))
        prefs.setPref('INIT_IMAGE_LOAD', loadElapsed)
        prefs.setPref('INIT_DETECT_MARKERS', markersElapsed)
        if maskElapsed is not None:
            prefs.setPref('INIT_APPLY_MASKS', maskElapsed)
        prefs.saveConfig()

    logger.info("General quality processing done")

# Archival photogrammetry processing.
def metaArchival(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS=None, prefsFileName=None):
    ensureLoggerReady()
    logger.info("Starting archival quality processing")

    # Creating an instance will initialize the doc, the logger
    # and the paths
    MU = MetaUtils(None, PATH_TO_IMAGES, PROJECT_NAME)

    # Creates an image list and adds them to the current chunk.
    loadElapsed = MU.loadImages()

    # Places markers on coded targets in images.
    markersElapsed = MU.detectMarkers()

    # Creates masks.
    maskElapsed = None
    if PATH_TO_MASKS is not None:
        maskElapsed = MU.autoMask(PATH_TO_MASKS)
    MU.doc.save()

    # Aligns photos.
    arcAlign(MU.chunk, prefsFileName)
    MU.doc.save()

    # Corrects the chunk.
    MU.chunkCorrect()

    # Creates a dense cloud for archival use.
    arcDenseCloud(MU.chunk, prefsFileName)
    MU.doc.save()

    # Creates an archival quality model.
    arcModel(MU.chunk, prefsFileName)
    MU.doc.save()

    # Write the elapsed times to the project prefs file
    if prefsFileName is not None:
        prefs = ProjectPrefs(prefsFileName)
        prefs.setPref('INIT', loadElapsed + markersElapsed +
                      (0 if maskElapsed is None else maskElapsed))
        prefs.setPref('INIT_IMAGE_LOAD', loadElapsed)
        prefs.setPref('INIT_DETECT_MARKERS', markersElapsed)
        if maskElapsed is not None:
            prefs.setPref('INIT_APPLY_MASKS', maskElapsed)
        prefs.saveConfig()

    logger.info("Archival processing done")


# Refinement of quickly processed photogrammetry data.
def metaRefine(PATH_TO_IMAGES, PROJECT_NAME):
    ensureLoggerReady()
    logger.info("Starting refinement.")

    # Creating an instance will initialize the doc, the logger
    # and the paths
    MU = MetaUtils(None, PATH_TO_IMAGES, PROJECT_NAME)

    # Creates a dense cloud for general use.
    genDenseCloud(MU.chunk)

    # Creates a model for general use.
    genModel(MU.chunk)

    MU.doc.save()
    logger.info("Refinement done")

# The beginning steps for any custom full processing workflow.
def metaCustomStart(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS=None, prefsFileName=None):
    ensureLoggerReady()
    logger.info("Starting custom processing")

    # Creating an instance will initialize the doc, the logger,
    # and the paths
    MU = MetaUtils(None, PATH_TO_IMAGES, PROJECT_NAME)

    # Creates an image list and adds them to the current chunk.
    loadElapsed = MU.loadImages()

    # Places markers on coded targets in images.
    markersElapsed = MU.detectMarkers()

    # Creates masks.
    maskElapsed = None
    if PATH_TO_MASKS is not None:
        maskElapsed = MU.autoMask(PATH_TO_MASKS)
    MU.doc.save()

    # Write the elapsed times to the project prefs file
    if prefsFileName is not None:
        prefs = ProjectPrefs(prefsFileName)
        prefs.setPref('INIT', loadElapsed + markersElapsed +
                      (0 if maskElapsed is None else maskElapsed))
        prefs.setPref('INIT_IMAGE_LOAD', loadElapsed)
        prefs.setPref('INIT_DETECT_MARKERS', markersElapsed)
        if maskElapsed is not None:
            prefs.setPref('INIT_APPLY_MASKS', maskElapsed)
        prefs.saveConfig()

    return MU
