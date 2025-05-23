"""A script containing various Metashape workflows."""

from datetime import timedelta

import Metashape
from CustomProgress import PBar

from ProjectPrefs import ProjectPrefs
from MetaUtilsClass import MetaUtils

# Import the logging module and get a custom logger for this module
import Logger
logger = None

def format_td(seconds, digits=2):
    i_sec, f_sec = divmod(round(seconds*10**digits), 10**digits)
    return f'{timedelta(seconds=i_sec)}.{f_sec:0{digits}.0f}'

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
    with PBar("Matching Photos") as pbar:
        chunk.matchPhotos(
            downscale=8, generic_preselection=True, filter_mask=True,
            reset_matches=(not refine), mask_tiepoints=False,
            keypoint_limit=(40000), tiepoint_limit=(20000),
            progress=(lambda x: pbar.update(x))
        )
        pbar.finish()
        elapsed1 = pbar.getTime()

    # From API "Perform photo alignment for the chunk."
    # - Second step of the Metashape GUI "Workflow" process "Align Photos",
    #   which generates the Sparse Cloud/Tie Points.
    elapsed2 = -1
    with PBar("Aligning Cameras") as pbar:
        chunk.alignCameras(reset_alignment=(not refine), progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed2 = pbar.getTime()

    # Print the timing
    logger.info("Quick alignment complete: %s" % format_td(elapsed1 + elapsed2))

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
    with PBar("Matching Photos") as pbar:
        chunk.matchPhotos(
            downscale=2, generic_preselection=True, filter_mask=True,
            reset_matches=(not refine), mask_tiepoints=False,
            keypoint_limit=(40000), tiepoint_limit=(40000),
            progress=(lambda x: pbar.update(x))
        )
        pbar.finish()
        elapsed1 = pbar.getTime()

    # From API "Perform photo alignment for the chunk."
    # - Second step of the Metashape GUI "Workflow" process "Align Photos",
    #   which generates the Sparse Cloud/Tie Points.
    elapsed2 = -1
    with PBar("Aligning Cameras") as pbar:
        chunk.alignCameras(reset_alignment=(not refine), progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed2 = pbar.getTime()

    # Print the timing
    logger.info("General alignment complete: %s" % format_td(elapsed1 + elapsed2))

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
    with PBar("Matching Photos") as pbar:
        chunk.matchPhotos(
            downscale=0, generic_preselection=True, filter_mask=True,
            reset_matches=(not refine), mask_tiepoints=False,
            keypoint_limit=(40000), tiepoint_limit=(10000),
            progress=(lambda x: pbar.update(x))
        )
        pbar.finish()
        elapsed1 = pbar.getTime()

    # From API "Perform photo alignment for the chunk."
    # - Second step of the Metashape GUI "Workflow" process "Align Photos",
    #   which generates the Sparse Cloud/Tie Points.
    elapsed2 = -1
    with PBar("Aligning Cameras") as pbar:
        chunk.alignCameras(progress=(lambda x: pbar.update(x)), reset_alignment=True)
        pbar.finish()
        elapsed2 = pbar.getTime()

    # Print the timing
    logger.info("Archival alignment complete: %s" % format_td(elapsed1 + elapsed))

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
def quickDenseCloud(chunk, prefsFileName=None, refine=False, noCloud=False):
    ensureLoggerReady()

    # From API "Generate depth maps for the chunk."
    # - First step of the Metashape GUI "Workflow" process called "Dense Cloud".
    # - max_neighbors parameter may save time and help with shadows (-1 is none).
    elapsed1 = -1
    logger.info("Building quick quality Dense Cloud")
    with PBar("Building Depth Maps") as pbar:
        chunk.buildDepthMaps(
            downscale=8, filter_mode=Metashape.AggressiveFiltering,
            max_neighbors=50, progress=(lambda x: pbar.update(x))
        )
        pbar.finish()
        elapsed1 = pbar.getTime()

    # From API "Generate dense cloud for the chunk."
    # - Second step of the Metashape GUI "Workflow" process called "Dense Cloud".
    elapsed2 = -1
    if not noCloud:
        with PBar("Building Point Cloud") as pbar:
            chunk.buildPointCloud(
                point_colors=True, keep_depth=True,
                max_neighbors=50, progress=(lambda x: pbar.update(x))
            )
            pbar.finish()
            elapsed2 = pbar.getTime()

        logger.info("Done building dense cloud")
    else:
        elapsed2 = 0
        logger.info("Skipping dense cloud")

    logger.info("Quick Dense Cloud complete: %s" % format_td(elapsed1 + elapsed2))

    # Save timing information to project preferences file
    if prefsFileName is not None:
        prefs = ProjectPrefs(prefsFileName)
        prefs.setPref('DENSE_CLOUD', elapsed1 + elapsed2)
        prefs.setPref('DENSE_CLOUD_DEPTH_MAPS', elapsed1)
        if not noCloud: prefs.setPref('DENSE_CLOUD_BUILD', elapsed2)
        prefs.saveConfig()

# Automates Metashape GUI "Workflow->Dense Cloud" with settings for
# general use.
def genDenseCloud(chunk, prefsFileName=None, refine=False, noCloud=False):
    ensureLoggerReady()

    # From API "Generate depth maps for the chunk."
    # - First step of the Metashape GUI "Workflow" process called "Dense Cloud".
    # - max_neighbors parameter may save time and help with shadows (-1 is none).
    elapsed1 = -1
    logger.info("Building general quality Dense Cloud")
    with PBar("Building Depth Maps") as pbar:
        chunk.buildDepthMaps(
            downscale=4, filter_mode=Metashape.AggressiveFiltering,
            max_neighbors=100, progress=(lambda x: pbar.update(x))
        )
        pbar.finish()
        elapsed1 = pbar.getTime()

    # From API "Generate dense cloud for the chunk."
    # - Second step of the Metashape GUI "Workflow" process called "Dense Cloud".
    elapsed2 = -1
    if not noCloud:
        with PBar("Building Point Cloud") as pbar:
            chunk.buildPointCloud(
                point_colors=True, keep_depth=True,
                max_neighbors=100, progress=(lambda x: pbar.update(x))
            )
            pbar.finish()
            elapsed2 = pbar.getTime()

        logger.info("Done building dense cloud")
    else:
        elapsed2 = 0
        logger.info("Skipping dense cloud")

    logger.info("General Dense Cloud complete: %s" % format_td(elapsed1 + elapsed2))

    # Save timing information to project preferences file
    if prefsFileName is not None:
        prefs = ProjectPrefs(prefsFileName)
        prefs.setPref('DENSE_CLOUD', elapsed1 + elapsed2)
        prefs.setPref('DENSE_CLOUD_DEPTH_MAPS', elapsed1)
        if not noCloud: prefs.setPref('DENSE_CLOUD_BUILD', elapsed2)
        prefs.saveConfig()


# Automates Metashape GUI "Workflow->Dense Cloud" with settings for
# archival use.
def arcDenseCloud(chunk, prefsFileName=None, refine=False, noCloud=False):
    ensureLoggerReady()

    # From API "Generate depth maps for the chunk."
    # - First step of the Metashape GUI "Workflow" process called "Dense Cloud".
    # - max_neighbors parameter may save time and help with shadows (-1 is none).
    elapsed1 = -1
    logger.info("Building archival quality Dense Cloud")
    with PBar("Generating Depth Maps") as pbar:
        chunk.buildDepthMaps(
            downscale=1, filter_mode=Metashape.MildFiltering,
            max_neighbors=100, progress=(lambda x: pbar.update(x))
        )
        pbar.finish()
        elapsed1 = pbar.getTime()

    # From API "Generate dense cloud for the chunk."
    # - Second step of the Metashape GUI "Workflow" process called "Dense Cloud".
    elapsed2 = -1
    if not noCloud:
        with PBar("Generating Point Cloud") as pbar:
            chunk.buildPointCloud(
                point_colors=True, keep_depth=True,
                max_neighbors=100, progress=(lambda x: pbar.update(x))
            )
            pbar.finish()
            elapsed2 = pbar.getTime()

        logger.info("Done building dense cloud")
    else:
        elapsed2 = 0
        logger.info("Skipping dense cloud")

    logger.info("Archival Dense Cloud complete: %s" % format_td(elapsed1 + elapsed2))

    # Save timing information to project preferences file
    if prefsFileName is not None:
        prefs = ProjectPrefs(prefsFileName)
        prefs.setPref('DENSE_CLOUD', elapsed1 + elapsed2)
        prefs.setPref('DENSE_CLOUD_DEPTH_MAPS', elapsed1)
        if not noCloud: prefs.setPref('DENSE_CLOUD_BUILD', elapsed2)
        prefs.saveConfig()


"""Model Options"""
def getSourceNames(sourceData):
    match sourceData:
        case Metashape.TiePointsData:
            return ' (from tie points)', '_TIE_POINTS'
        case Metashape.PointCloudData:
            return ' (from point cloud)', '_DENSE_CLOUD'
        case Metashape.DepthMapsData:
            return ' (from depth maps)', '_DEPTH_MAPS'

    return '', ''

# Automates Metashape GUI "Workflow" process "Build Mesh" and
# "Build Texture" with settings for quick results.
def quickModel(chunk, sourceData=Metashape.TiePointsData, prefsFileName=None, refine=False):
    ensureLoggerReady()

    # Determine source data type
    sourceString, sourceSuffix = getSourceNames(sourceData)

    # From API "Generate model for the chunk frame."
    # - Builds mesh to be used in the last steps.
    logger.info("Quickly generating textured 3D model%s" % sourceString)
    elapsed1 = -1
    with PBar("Generating Model") as pbar:
        chunk.buildModel(surface_type=Metashape.Arbitrary,
                         interpolation=Metashape.EnabledInterpolation,
                         face_count=Metashape.HighFaceCount,
                         source_data=sourceData,
                         vertex_colors=True, keep_depth=True,
                         progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed1 = pbar.getTime()

    # From API "Generate uv mapping for the model."
    elapsed2 = -1
    with PBar("Generating UV Coords") as pbar:
        chunk.buildUV(
            mapping_mode=Metashape.GenericMapping,
            page_count=1, texture_size=1024,
            progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed2 = pbar.getTime()

    # From API "Generate texture for the chunk."
    # - Generates a basic texture for the 3D model.
    elapsed3 = -1
    with PBar("Generating 1k Tex") as pbar:
        chunk.buildTexture(texture_type=Metashape.Model.DiffuseMap,
                           blending_mode=Metashape.MosaicBlending,
                           source_data=Metashape.ImagesData,
                           texture_size=1024, fill_holes=True,
                           progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed3 = pbar.getTime()

    logger.info("Quick 3D model%s complete: %s" % (sourceString,
                format_td(elapsed1 + elapsed2 + elapsed3)))

    # Save timing information to project preferences file
    if prefsFileName is not None:
        prefs = ProjectPrefs(prefsFileName)
        prefs.setPref('BUILD_MODEL%s' % sourceSuffix, elapsed1 + elapsed2 + elapsed3)
        prefs.setPref('BUILD_MODEL_MESH%s' % sourceSuffix, elapsed1)
        prefs.setPref('BUILD_MODEL_UV%s' % sourceSuffix, elapsed2)
        prefs.setPref('BUILD_MODEL_TEXTURE%s' % sourceSuffix, elapsed3)
        prefs.saveConfig()


# Automates Metashape GUI "Workflow" process "Build Mesh" and
# "Build Texture" with settings for general use.
def genModel(chunk, sourceData=Metashape.PointCloudData, prefsFileName=None, refine=False):
    ensureLoggerReady()

    # Determine source data type
    sourceString, sourceSuffix = getSourceNames(sourceData)

    # From API "Generate model for the chunk frame."
    # - Builds mesh to be used in the last steps.
    logger.info("Building general quality textured 3D model%s" % sourceString)
    elapsed1 = -1
    with PBar("Generating Model") as pbar:
        chunk.buildModel(surface_type=Metashape.Arbitrary,
                         interpolation=Metashape.EnabledInterpolation,
                         face_count=Metashape.HighFaceCount,
                         source_data=sourceData,
                         vertex_colors=True, keep_depth=True,
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
    with PBar("Generating 4k Tex") as pbar:
        chunk.buildTexture(texture_type=Metashape.Model.DiffuseMap,
                           blending_mode=Metashape.MosaicBlending,
                           source_data=Metashape.ImagesData,
                           texture_size=(4096), fill_holes=True,
                           progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed3 = pbar.getTime()

    logger.info("General 3D model%s complete: %s" % (sourceString,
               format_td(elapsed1 + elapsed2 + elapsed3)))

    # Save timing information to project preferences file
    if prefsFileName is not None:
        prefs = ProjectPrefs(prefsFileName)
        prefs.setPref('BUILD_MODEL%s' % sourceSuffix, elapsed1 + elapsed2 + elapsed3)
        prefs.setPref('BUILD_MODEL_MESH%s' % sourceSuffix, elapsed1)
        prefs.setPref('BUILD_MODEL_UV%s' % sourceSuffix, elapsed2)
        prefs.setPref('BUILD_MODEL_TEXTURE%s' % sourceSuffix, elapsed3)
        prefs.saveConfig()

# Automates Metashape GUI "Workflow" process "Build Mesh" and
# "Build Texture" with settings for archival use.
def arcModel(chunk, sourceData=Metashape.PointCloudData, prefsFileName=None, refine=False):
    ensureLoggerReady()

    # Determine source data type
    sourceString, sourceSuffix = getSourceNames(sourceData)

    # From API "Generate model for the chunk frame."
    # - Builds accurate mesh to be used in the last steps.
    logger.info("Building archival quality textured 3D model%s" % sourceString)
    elapsed1 = -1
    with PBar("Generating Model") as pbar:
        chunk.buildModel(surface_type=Metashape.Arbitrary,
                         interpolation=Metashape.EnabledInterpolation,
                         face_count=Metashape.HighFaceCount,
                         source_data=sourceData,
                         vertex_colors=True, keep_depth=True,
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
    with PBar("Generating 8k Tex") as pbar:
        chunk.buildTexture(texture_type=Metashape.Model.DiffuseMap,
                           blending_mode=Metashape.MosaicBlending,
                           source_data=Metashape.ImagesData,
                           texture_size=(8192), fill_holes=True,
                           progress=(lambda x: pbar.update(x)))
        pbar.finish()
        elapsed3 = pbar.getTime()

    logger.info("Archival 3D model%s complete: %s" % (sourceString,
               format_td(elapsed1 + elapsed2 + elapsed3)))

    # Save timing information to project preferences file
    if prefsFileName is not None:
        prefs = ProjectPrefs(prefsFileName)
        prefs.setPref('BUILD_MODEL%s' % sourceSuffix, elapsed1 + elapsed2 + elapsed3)
        prefs.setPref('BUILD_MODEL_MESH%s' % sourceSuffix, elapsed1)
        prefs.setPref('BUILD_MODEL_UV%s' % sourceSuffix, elapsed2)
        prefs.setPref('BUILD_MODEL_TEXTURE%s' % sourceSuffix, elapsed3)
        prefs.saveConfig()


"""Workflow Options"""
def metaInit(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS=None, prefsFileName=None, markerTolerance=50):
    # Creating an instance will initialize the doc, the logger and the paths
    MU = MetaUtils(None, PATH_TO_IMAGES, PROJECT_NAME)

    # Creates an image list and adds them to the current chunk.
    loadElapsed = MU.loadImages()

    # Places markers on coded targets in images.
    markersElapsed = MU.detectMarkers(markerTolerance)

    # Creates masks.
    maskElapsed = None
    if PATH_TO_MASKS is not None:
        maskElapsed = MU.autoMask(PATH_TO_MASKS)

    if prefsFileName is not None:
        prefs = ProjectPrefs(prefsFileName)
        prefs.setPref('INIT', loadElapsed + markersElapsed +
                      (0 if maskElapsed is None else maskElapsed))
        prefs.setPref('INIT_IMAGE_LOAD', loadElapsed)
        prefs.setPref('INIT_DETECT_MARKERS', markersElapsed)
        if maskElapsed is not None:
            prefs.setPref('INIT_APPLY_MASKS', maskElapsed)
        prefs.saveConfig()

    # Return the initialized MetaUtils object
    return MU

# Quick photogrammetry processing.
def metaQuick(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS=None, prefsFileName=None, markerTolerance=50, refine=False, modelTie=True, modelDepth=False, modelCloud=False):
    ensureLoggerReady()
    logger.info("Starting quick processing")

    # Initialize the MetaUtils object and project
    MU = metaInit(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS, prefsFileName, markerTolerance)
    MU.doc.save()

    # Aligns photos and corrects the chunk
    quickAlign(MU.chunk, prefsFileName, refine)
    MU.chunkCorrect()
    MU.setRegion(1.1)
    MU.filterTiePoints()
    MU.optimizeCameras()
    MU.doc.save()

    # Generate the dense cloud (if needed)
    if modelDepth or modelCloud:
        quickDenseCloud(MU.chunk, prefsFileName, refine, not modelCloud)
        MU.doc.save()

    # Creates a quick model.
    MU.setRegion(0.33)
    if modelTie:
        quickModel(MU.chunk, Metashape.TiePointsData, prefsFileName, refine)
        MU.doc.save()
    if modelDepth:
        quickModel(MU.chunk, Metashape.DepthMapsData, prefsFileName, refine)
        MU.doc.save()
    if modelCloud:
        quickModel(MU.chunk, Metashape.PointCloudData, prefsFileName, refine)
        MU.doc.save()

    logger.info("Quick processing done")

# General photogrammetry processing.
def metaGeneral(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS=None, prefsFileName=None, markerTolerance=50, refine=False, modelTie=False, modelDepth=True, modelCloud=False):
    ensureLoggerReady()
    logger.info("Starting general quality processing")

    # Initialize the MetaUtils object and project
    MU = metaInit(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS, prefsFileName, markerTolerance)
    MU.doc.save()

    # Aligns photos and corrects the chunk.
    genAlign(MU.chunk, prefsFileName, refine)
    MU.chunkCorrect()
    MU.setRegion(1.1)
    MU.filterTiePoints()
    MU.optimizeCameras()
    MU.doc.save()

    # Generate the dense cloud.
    if modelDepth or modelCloud:
        genDenseCloud(MU.chunk, prefsFileName, refine, not modelCloud)
        MU.doc.save()

    # Creates a general model.
    MU.setRegion(0.5)
    if modelTie:
        genModel(MU.chunk, Metashape.TiePointsData, prefsFileName, refine)
        MU.doc.save()

    if modelDepth:
        genModel(MU.chunk, Metashape.DepthMapsData, prefsFileName, refine)
        MU.doc.save()

    if modelCloud:
        genModel(MU.chunk, Metashape.PointCloudData, prefsFileName, refine)
        MU.doc.save()

    logger.info("General quality processing done")

# Archival photogrammetry processing.
def metaArchival(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS=None, prefsFileName=None, markerTolerance=50, refine=False, modelTie=False, modelDepth=True, modelCloud=False):
    ensureLoggerReady()
    logger.info("Starting archival quality processing")

    # Initialize the MetaUtils object and project
    MU = metaInit(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS, prefsFileName, markerTolerance)
    MU.doc.save()

    # Aligns photos and corrects the chunk.
    arcAlign(MU.chunk, prefsFileName, refine)
    MU.chunkCorrect()
    MU.setRegion(1.1)
    MU.filterTiePoints()
    MU.optimizeCameras()
    MU.doc.save()

    # Creates a dense cloud for archival use.
    if modelDepth or modelCloud:
        arcDenseCloud(MU.chunk, prefsFileName, refine, not modelCloud)
        MU.doc.save()

    # Creates an archival quality model.
    MU.setRegion(0.66)
    if modelTie:
        arcModel(MU.chunk, Metashape.TiePointsData, prefsFileName, refine)
        MU.doc.save()

    if modelDepth:
        arcModel(MU.chunk, Metashape.DepthMapsData, prefsFileName, refine)
        MU.doc.save()

    if modelCloud:
        arcModel(MU.chunk, Metashape.PointCloudData, prefsFileName, refine)
        MU.doc.save()

    logger.info("Archival processing done")


def metaCustom(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS=None, prefsFileName=None, args={}):
    ensureLoggerReady()
    logger.info("Starting custom workflow")

    # Initialize the MetaUtils object and project
    MU = metaInit(PATH_TO_IMAGES, PROJECT_NAME, PATH_TO_MASKS, prefsFileName, (50 if args.tolerance is None else args.tolerance))
    MU.doc.save()

    if args.quickAlign:
        quickAlign(MU.chunk, prefsFileName)
        MU.doc.save()
        MU.chunkCorrect()
        MU.setRegion(1.1)
        MU.filterTiePoints()
        MU.optimizeCameras()
        MU.doc.save()

    if args.genAlign:
        genAlign(MU.chunk, prefsFileName)
        MU.doc.save()
        MU.chunkCorrect()
        MU.setRegion(1.1)
        MU.filterTiePoints()
        MU.optimizeCameras()
        MU.doc.save()

    if args.arcAlign:
        arcAlign(MU.chunk, prefsFileName)
        MU.doc.save()
        MU.chunkCorrect()
        MU.setRegion(1.1)
        MU.filterTiePoints()
        MU.optimizeCameras()
        MU.doc.save()

    if args.quickDense:
        genDenseCloud(MU.chunk, prefsFileName)
        MU.doc.save()

    if args.genDense:
        genDenseCloud(MU.chunk, prefsFileName)
        MU.doc.save()

    if args.arcDense:
        arcDenseCloud(MU.chunk, prefsFileName)
        MU.doc.save()

    if args.quickMod:
        MU.setRegion(0.33)
        if args.modelTie:
            quickModel(MU.chunk, Metashape.TiePointsData, prefsFileName)
            MU.doc.save()
        if args.modelCloud:
            quickModel(MU.chunk, Metashape.PointCloudData, prefsFileName)
            MU.doc.save()
        if args.modelDepth:
            quickModel(MU.chunk, Metashape.DepthMapsData, prefsFileName)
            MU.doc.save()

    if args.genMod:
        MU.setRegion(0.5)
        if args.modelTie:
            genModel(MU.chunk, Metashape.TiePointsData, prefsFileName)
            MU.doc.save()
        if args.modelCloud:
            genModel(MU.chunk, Metashape.PointCloudData, prefsFileName)
            MU.doc.save()
        if args.modelDepth:
            genModel(MU.chunk, Metashape.DepthMapsData, prefsFileName)
            MU.doc.save()

    if args.arcMod:
        MU.setRegion(0.66)
        if args.modelTie:
            arcModel(MU.chunk, Metashape.TiePointsData, prefsFileName)
            MU.doc.save()
        if args.modelCloud:
            arcModel(MU.chunk, Metashape.PointCloudData, prefsFileName)
            MU.doc.save()
        if args.modelDepth:
            arcModel(MU.chunk, Metashape.DepthMapsData, prefsFileName)
            MU.doc.save()

    logger.info("Custom workflow done")
