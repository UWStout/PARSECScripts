import Metashape

def print_markers(chunk):
    for marker in chunk.markers:
        #XYZ coords?
        print(marker.position)
        #Key in dictionary
        print(marker.key)
        #These are the label names shown in Metashape GUI
        print(marker.label)
