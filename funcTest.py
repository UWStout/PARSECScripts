import Metashape

doc = Metashape.app.document
chunk = doc.chunk

def print_markers():
    for marker in chunk.markers:
        #XYZ coords?
        print(marker.position)
        #Key in dictionary?
        print(marker.key)
        #These are the label names shown in Metashape GUI
        print(marker.label)
