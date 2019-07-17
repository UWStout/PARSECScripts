"""A script containing various Metashape workflows."""

import Metashape

def quick_align(chunk):
    #AIW From API "Perform image matching for the chunk frame." 
    # - First step of the Metashape GUI "Workflow" process called "Align Photos", which generates the Sparse Cloud/Tie Points. 
    # - Keypoints and Tiepoints for this script is Agisoft's suggested default. 
    # - Accuracy below MediumAccuracy consistently results in failed camera alignment.
    # - HighAccuracy is used in this script as the results are better for and the time added is negligible.
    chunk.matchPhotos(accuracy=Metashape.HighAccuracy, generic_preselection=True, filter_mask=True, mask_tiepoints=False, keypoint_limit=(40000), tiepoint_limit=(4000))
    print ("Photos matched.")

    #AIW From API "Perform photo alignment for the chunk." 
    # - Second step of the Metashape GUI "Workflow" process called "Align Photos", which generates the Sparse Cloud/Tie Points.
    chunk.alignCameras()
    print ("Camera alignment finished.")