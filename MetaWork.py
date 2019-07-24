"""A script containing various Metashape workflows."""

import Metashape
import logging

"""Alignment Options"""
#AIW Automates Metashape GUI processe "Add Photos", "Tool->Detect Markers", "Workflow->Align Photos" with settings for quick results.
def quick_align(chunk):
    #AIW From API "Perform image matching for the chunk frame." 
    # - First step of the Metashape GUI "Workflow" process "Align Photos", which generates the Sparse Cloud/Tie Points. 
    # - Keypoints and Tiepoints for this script is Agisoft's suggested default. 
    # - Accuracy below MediumAccuracy consistently results in failed camera alignment.
    # - HighAccuracy is used in this script as the results are better for and the time added is negligible.
    print ("Quickly aligning photos")
    logging.info("Started photo alignment")
    chunk.matchPhotos(accuracy=Metashape.HighAccuracy, generic_preselection=True, filter_mask=True, mask_tiepoints=False, keypoint_limit=(40000), tiepoint_limit=(4000))

    #AIW From API "Perform photo alignment for the chunk." 
    # - Second step of the Metashape GUI "Workflow" process "Align Photos", which generates the Sparse Cloud/Tie Points.
    chunk.alignCameras()
    print ("Done")
    logging.info("Done")

#AIW Automates Metashape GUI processe "Add Photos", "Tool->Detect Markers", "Workflow->Align Photos" with settings for general results.
def gen_align(chunk):
    #AIW From API "Perform image matching for the chunk frame." 
    # - First step of the Metashape GUI "Workflow" process "Align Photos", which generates the Sparse Cloud/Tie Points. 
    # - Keypoints and Tiepoints for this script is Agisoft's suggested default. 
    # - Accuracy below MediumAccuracy consistently results in failed camera alignment.
    # - HighAccuracy is used in this script as the results are better for and the time added is negligible.
    print ("Aligning photos for general quality")
    logging.info("Started general quality photo alignment")
    chunk.matchPhotos(accuracy=Metashape.HighAccuracy, generic_preselection=True, filter_mask=True, mask_tiepoints=False, keypoint_limit=(0), tiepoint_limit=(0))

    #AIW From API "Perform photo alignment for the chunk." 
    # - Second step of the Metashape GUI "Workflow" process "Align Photos", which generates the Sparse Cloud/Tie Points.
    chunk.alignCameras()
    print ("Done")
    logging.info("Done")

#AIW Automates Metashape GUI processe "Add Photos", "Tool->Detect Markers", "Workflow->Align Photos" with settings for archival results.
def arc_align(chunk):
    #AIW From API "Perform image matching for the chunk frame." 
    # - First step of the Metashape GUI "Workflow" process "Align Photos", which generates the Sparse Cloud/Tie Points. 
    # - Keypoints and Tiepoints for this script is Agisoft's suggested default. 
    # - Accuracy below MediumAccuracy consistently results in failed camera alignment.
    # - HighAccuracy is used in this script as the results are better for and the time added is negligible.
    print ("Quickly aligning photos")
    logging.info("Started photo alignment")
    chunk.matchPhotos(accuracy=Metashape.HighestAccuracy, generic_preselection=True, filter_mask=True, mask_tiepoints=False, keypoint_limit=(0), tiepoint_limit=(0))

    #AIW From API "Perform photo alignment for the chunk." 
    # - Second step of the Metashape GUI "Workflow" process "Align Photos", which generates the Sparse Cloud/Tie Points.
    chunk.alignCameras()
    print ("Done")
    logging.info("Done")

"""Dense Cloud Options"""

#AIW Automates Metashape GUI "Workflow->Dense Cloud" with settings for general use.
def gen_dense_cloud(chunk):
    #AIW From API "Generate depth maps for the chunk."
    # - First step of the Metashape GUI "Workflow" process called "Dense Cloud".
    # - max_neighbors parameter may save time and help with shadows. -1 is none.
    print("Building general quality Dense Cloud")
    logging.info("Started building general quality Dense Cloud")
    chunk.buildDepthMaps(quality=Metashape.HighQuality, filter=Metashape.AggressiveFiltering, max_neighbors=100)

    #AIW From API "Generate dense cloud for the chunk."
    # - Second step of the Metashape GUI "Workflow" process called "Dense Cloud".
    chunk.buildDenseCloud(point_colors=True, keep_depth=True, max_neighbors=100)
    print("Done")
    logging.info("Done")

#AIW Automates Metashape GUI "Workflow->Dense Cloud" with settings for archival use.
def arc_dense_cloud(chunk):
    #AIW From API "Generate depth maps for the chunk."
    # - First step of the Metashape GUI "Workflow" process called "Dense Cloud".
    # - max_neighbors parameter may save time and help with shadows. -1 is none.
    print("Building archival quality Dense Cloud")
    logging.info("Started building archival quality Dense Cloud")
    chunk.buildDepthMaps(quality=Metashape.HighestQuality, filter=Metashape.MildFiltering, max_neighbors=100)

    #AIW From API "Generate dense cloud for the chunk."
    # - Second step of the Metashape GUI "Workflow" process called "Dense Cloud".
    chunk.buildDenseCloud(point_colors=True, keep_depth=True, max_neighbors=100)
    print("Done")
    logging.info("Done")

"""Model Options"""

#AIW Automates Metashape GUI "Workflow" processes "Build Mesh" and "Build Texture" with settings for quick results.
def quick_model(chunk):
    #AIW From API "Generate model for the chunk frame." Builds mesh to be used in the last steps.
    print("Quickly generating textured 3D model")
    logging.info("Started generating quick model")
    chunk.buildModel(surface=Metashape.Arbitrary, interpolation=Metashape.EnabledInterpolation, face_count=Metashape.HighFaceCount, source=Metashape.PointCloudData, vertex_colors=True)

    #AIW From API "Generate uv mapping for the model."
    chunk.buildUV(adaptive_resolution=True)

    #AIW From API "Generate texture for the chunk." 
    # - Generates a basic texture for the 3D model.
    chunk.buildTexture(blending=Metashape.MosaicBlending, size=(1024), fill_holes=False)
    print ("Done")
    logging.info("Done")

#AIW Automates Metashape GUI "Workflow" processes "Build Mesh" and "Build Texture" with settings for general use.
def gen_model(chunk):
    #AIW From API "Generate model for the chunk frame." Builds mesh to be used in the last steps.
    print("Building general quality textured 3D model")
    logging.info("Building general quality textured 3D model")
    chunk.buildModel(surface=Metashape.Arbitrary, interpolation=Metashape.EnabledInterpolation, face_count=Metashape.HighFaceCount, source=Metashape.DenseCloudData, vertex_colors=True, keep_depth=True)

    #AIW From API "Generate uv mapping for the model."
    chunk.buildUV(adaptive_resolution=True)

    #AIW From API "Generate texture for the chunk." 
    # - Generates a 4k texture for the 3D model.
    chunk.buildTexture(blending=Metashape.MosaicBlending, size=(4096), fill_holes=False)
    print ("Done")
    logging.info("Done")

#AIW Automates Metashape GUI "Workflow" processes "Build Mesh" and "Build Texture" with settings for archival use.
def arc_model(chunk):
    #AIW From API "Generate model for the chunk frame." Builds accurate mesh without generating extra geometry to be used in the last steps.
    print("Building archival quality textured 3D model")
    logging.info("Building archival quality textured 3D model")
    chunk.buildModel(surface=Metashape.Arbitrary, interpolation=Metashape.DisabledInterpolation, face_count=Metashape.HighFaceCount, source=Metashape.DenseCloudData, vertex_colors=True, keep_depth=True)

    #AIW From API "Generate uv mapping for the model."
    chunk.buildUV(adaptive_resolution=True)

    #AIW From API "Generate texture for the chunk." 
    # - Generates a 16k texture for the 3D model.
    chunk.buildTexture(blending=Metashape.MosaicBlending, size=(16384), fill_holes=False)
    print ("Done")
    logging.info("Done")