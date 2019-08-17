"""A script containing various Metashape workflows."""

#SFB Import the logging module and get a custom loger for this module
from MetaUtilsClass import MetaUtils
import Logger
logger = Logger.getLogger('Utils')

import Metashape

"""Alignment Options"""
#AIW Automates Metashape GUI processe "Add Photos", "Tool->Detect Markers", "Workflow->Align Photos" with settings for quick results.
def quickAlign(chunk):
    #AIW From API "Perform image matching for the chunk frame." 
    # - First step of the Metashape GUI "Workflow" process "Align Photos", which generates the Sparse Cloud/Tie Points. 
    # - Keypoints and Tiepoints for this script is Agisoft's suggested default. 
    # - Accuracy below MediumAccuracy consistently results in failed camera alignment.
    # - HighAccuracy is used in this script as the results are better for and the time added is negligible.
    logger.info ("Quickly aligning photos")
    chunk.matchPhotos(accuracy=Metashape.HighAccuracy, generic_preselection=True, filter_mask=True, mask_tiepoints=False, keypoint_limit=(40000), tiepoint_limit=(4000))

    #AIW From API "Perform photo alignment for the chunk." 
    # - Second step of the Metashape GUI "Workflow" process "Align Photos", which generates the Sparse Cloud/Tie Points.
    chunk.alignCameras()
    logger.info ("Done aligning photos")

#AIW Automates Metashape GUI processe "Add Photos", "Tool->Detect Markers", "Workflow->Align Photos" with settings for general results.
def genAlign(chunk):
    #AIW From API "Perform image matching for the chunk frame." 
    # - First step of the Metashape GUI "Workflow" process "Align Photos", which generates the Sparse Cloud/Tie Points. 
    # - Keypoints and Tiepoints for this script is Agisoft's suggested default. 
    # - Accuracy below MediumAccuracy consistently results in failed camera alignment.
    # - HighAccuracy is used in this script as the results are better for and the time added is negligible.
    logger.info ("Aligning photos for general quality")
    chunk.matchPhotos(accuracy=Metashape.HighAccuracy, generic_preselection=True, filter_mask=True, mask_tiepoints=False, keypoint_limit=(0), tiepoint_limit=(0))

    #AIW From API "Perform photo alignment for the chunk." 
    # - Second step of the Metashape GUI "Workflow" process "Align Photos", which generates the Sparse Cloud/Tie Points.
    chunk.alignCameras()
    logger.info ("Done aligning photos")

#AIW Automates Metashape GUI processe "Add Photos", "Tool->Detect Markers", "Workflow->Align Photos" with settings for archival results.
def arcAlign(chunk):
    #AIW From API "Perform image matching for the chunk frame." 
    # - First step of the Metashape GUI "Workflow" process "Align Photos", which generates the Sparse Cloud/Tie Points. 
    # - Keypoints and Tiepoints for this script is Agisoft's suggested default. 
    # - Accuracy below MediumAccuracy consistently results in failed camera alignment.
    # - HighAccuracy is used in this script as the results are better for and the time added is negligible.
    logger.info ("Quickly aligning photos")
    chunk.matchPhotos(accuracy=Metashape.HighestAccuracy, generic_preselection=True, filter_mask=True, mask_tiepoints=False, keypoint_limit=(0), tiepoint_limit=(0))

    #AIW From API "Perform photo alignment for the chunk." 
    # - Second step of the Metashape GUI "Workflow" process "Align Photos", which generates the Sparse Cloud/Tie Points.
    chunk.alignCameras()
    logger.info ("Done aligning photos")

"""Dense Cloud Options"""

#AIW Automates Metashape GUI "Workflow->Dense Cloud" with settings for general use.
def genDenseCloud(chunk):
    #AIW From API "Generate depth maps for the chunk."
    # - First step of the Metashape GUI "Workflow" process called "Dense Cloud".
    # - max_neighbors parameter may save time and help with shadows. -1 is none.
    logger.info("Building general quality Dense Cloud")
    chunk.buildDepthMaps(quality=Metashape.HighQuality, filter=Metashape.AggressiveFiltering, max_neighbors=100)

    #AIW From API "Generate dense cloud for the chunk."
    # - Second step of the Metashape GUI "Workflow" process called "Dense Cloud".
    chunk.buildDenseCloud(point_colors=True, keep_depth=True, max_neighbors=100)
    logger.info("Done building dense cloud")

#AIW Automates Metashape GUI "Workflow->Dense Cloud" with settings for archival use.
def arcDenseCloud(chunk):
    #AIW From API "Generate depth maps for the chunk."
    # - First step of the Metashape GUI "Workflow" process called "Dense Cloud".
    # - max_neighbors parameter may save time and help with shadows. -1 is none.
    logger.info("Building archival quality Dense Cloud")
    chunk.buildDepthMaps(quality=Metashape.HighestQuality, filter=Metashape.MildFiltering, max_neighbors=100)

    #AIW From API "Generate dense cloud for the chunk."
    # - Second step of the Metashape GUI "Workflow" process called "Dense Cloud".
    chunk.buildDenseCloud(point_colors=True, keep_depth=True, max_neighbors=100)
    logger.info("Done building dense cloud")

"""Model Options"""

#AIW Automates Metashape GUI "Workflow" processes "Build Mesh" and "Build Texture" with settings for quick results.
def quickModel(chunk):
    #AIW From API "Generate model for the chunk frame." Builds mesh to be used in the last steps.
    logger.info("Quickly generating textured 3D model")
    chunk.buildModel(surface=Metashape.Arbitrary, interpolation=Metashape.EnabledInterpolation, face_count=Metashape.HighFaceCount, source=Metashape.PointCloudData, vertex_colors=True)

    #AIW From API "Generate uv mapping for the model."
    chunk.buildUV(adaptive_resolution=True)

    #AIW From API "Generate texture for the chunk." 
    # - Generates a basic texture for the 3D model.
    chunk.buildTexture(blending=Metashape.MosaicBlending, size=(1024), fill_holes=False)
    logger.info ("Done generating model")

#AIW Automates Metashape GUI "Workflow" processes "Build Mesh" and "Build Texture" with settings for general use.
def genModel(chunk):
    #AIW From API "Generate model for the chunk frame." Builds mesh to be used in the last steps.
    logger.info("Building general quality textured 3D model")
    chunk.buildModel(surface=Metashape.Arbitrary, interpolation=Metashape.EnabledInterpolation, face_count=Metashape.HighFaceCount, source=Metashape.DenseCloudData, vertex_colors=True, keep_depth=True)

    #AIW From API "Generate uv mapping for the model."
    chunk.buildUV(adaptive_resolution=True)

    #AIW From API "Generate texture for the chunk." 
    # - Generates a 4k texture for the 3D model.
    chunk.buildTexture(blending=Metashape.MosaicBlending, size=(4096), fill_holes=False)
    logger.info ("Done building model")

#AIW Automates Metashape GUI "Workflow" processes "Build Mesh" and "Build Texture" with settings for archival use.
def arcModel(chunk):
    #AIW From API "Generate model for the chunk frame." Builds accurate mesh without generating extra geometry to be used in the last steps.
    logger.info("Building archival quality textured 3D model")
    chunk.buildModel(surface=Metashape.Arbitrary, interpolation=Metashape.DisabledInterpolation, face_count=Metashape.HighFaceCount, source=Metashape.DenseCloudData, vertex_colors=True, keep_depth=True)

    #AIW From API "Generate uv mapping for the model."
    chunk.buildUV(adaptive_resolution=True)

    #AIW From API "Generate texture for the chunk." 
    # - Generates a 16k texture for the 3D model.
    chunk.buildTexture(blending=Metashape.MosaicBlending, size=(16384), fill_holes=False)
    logger.info ("Done building model")

"""Workflow Options"""

#AIW Quick photogrammetry processing.
def metaQuick(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS):
    logger.info("Starting quick processing")

    #SFB Creating an instance will initialize the doc, the logger and the paths
    MU = MetaUtils(None, PATH_TO_IMAGES, PROJECT_NAME)

    #AIW Creates an image list and adds them to the current chunk.
    MU.loadImages()

    #AIW Creates masks.
    MU.autoMask(PATH_TO_MASKS)

    #AIW Aligns photos.
    quickAlign(MU.chunk)

    #AIW Corrects the chunk.
    MU.chunkCorrect()

    #AIW Creats a quick model.
    quickModel(MU.chunk)

    MU.doc.save()
    logger.info("Quick processing done")

#AIW Refinement of quickly processed photogrammetry data.
def metaRefine(PATH_TO_IMAGES, PROJECT_NAME):
    logger.info("Starting refinement.")
    
    #SFB Creating an instance will initialize the doc, the logger and the paths
    MU = MetaUtils(None, PATH_TO_IMAGES, PROJECT_NAME)

    #AIW Creates a dense cloud for general use.
    genDenseCloud(MU.chunk)

    #AIW Creates a modelfor general use.
    genModel(MU.chunk)

    MU.doc.save()
    logger.info("Refinement done")

#AIW The begining steps ofor any custom full processing workflow.
def metaCustomStart(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS):
    logger.info("Starting custom processing")

    #SFB Creating an instance will initialize the doc, the logger and the paths
    MU = MetaUtils(None, PATH_TO_IMAGES, PROJECT_NAME)

    #AIW Creates an image list and adds them to the current chunk.
    MU.loadImages()

    #AIW Creates masks.
    MU.autoMask(PATH_TO_MASKS)