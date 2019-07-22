"""Reworking of MetaUtils as a Class""" 

import Metashape
import sys
import time
import logging
import os

""" This object contains general functions to help process a MetaShape document object
    It should be passed an existing document when created either already processed or
    a new document ready to be filled with images and processed later """
class MetaUtils:
  """ Minimum compatible version of MetaShape """
  COMPATABLE_VERSION = "1.5"

  # SFB Common image file extensions
  IMAGE_FILE_EXTENSION_LIST = ('.jpg', '.jpeg', '.png', '.tif', '.tiff')

  """ Construct a new MetaUtils object with the given Metashape Document """
  def _init_(self, doc, path = "", prefix = ""):
    # Check that all needed information was supplied
    if path == "" and prefix == "" and doc is None:
      raise Exception('You must supply either an existing Metashape.Document or the path and prefix to make one.')

    # Initialize all properties
    self.doc = doc
    self.imagePath = path
    self.namePrefix = prefix

    # Check that we have a valid Document
    if self.doc is None:
      self.initDoc()
    else:
      self.imagePath, self.namePrefix = os.path.split(self.doc.path)
      self.namePrefix, extension = os.path.splitext(self.namePrefix)

    # Initialize logging
    self.initLog()

    # Get reference to active chunk
    self.chunk = self.doc.chunk
    
  #AIW Check compatibility. Modified from public Agisoft scripts.
  @staticmethod
  def CHECK_VER(metashapeVersionString):
    actualVersion = ".".join(metashapeVersionString.split('.')[:2])
    if actualVersion != MetaUtils.COMPATABLE_VERSION:
      logging.warning("Incompatible Metashape version: {} != {}".format(actualVersion, MetaUtils.COMPATABLE_VERSION))
      raise Exception("Incompatible Metashape version: {} != {}".format(actualVersion, MetaUtils.COMPATABLE_VERSION))
    else:
      print (actualVersion + " OK")
      logging.info ("Metashape version: " + actualVersion + " OK")

  #AIW Enables GPU processing in Metashape.
  @staticmethod
  def USE_GPU():
    #SFB Get number of GPUs available
    gpuList = Metashape.app.enumGPUDevices()
    gpuCount = len(gpuList)

    #SFB Enable all GPUs
    if gpuCount > 0:
      print("Enabling %d GPUs" %(gpuCount))
      Metashape.app.gpu_mask = 2**gpuCount - 1
      Metashape.app.cpu_enable = False
      print("Done")
      logging.info("Enabled %d GPUs" %(gpuCount))

  #AIW Creates a log text file.
  def initLog(self):
    # logging.basicConfig(filename="{}{}_log.txt".format(PATH_TO_IMAGES, IMAGE_PREFIX), format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    PATH = "{}{}_log.txt".format(self.imagePath, self.namePrefix)    
    logging.basicConfig(filename=PATH ,format='%(asctime)s %(message)s',
      datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

  #SFB Import images and create a new doc
  def initDoc(self):
    #SFB Get reference to the currently active DOM
    self.doc = Metashape.Document()

    #AIW Attemtps to open an existing project. 
    # - A new project is created if an existing project is not available.
    # - This must be done immediatly after getting reference to active DOM.
    # - .psx format will not save correctly otherwise.
    try:
      self.doc.open("{}{}.psx" .format(self.imagePath, self.namePrefix), read_only=False, ignore_lock=True)
      print("Found existing PSX document.")
    except:
      print("No existing PSX document, creating new.")
      self.doc.save("{}{}.psx" .format(self.imagePath, self.namePrefix))
      self.doc.addChunk()

  #AIW Automates correction processes for the chunk.
  def chunkCorrect(self):
      #SFB Changes the dimensions of the chunk's reconstruction volume.
      print("Correcting chunk")
      logging.info("Started correcting chunk")
      NEW_REGION = self.chunk.region
      NEW_REGION.size = NEW_REGION.size * 2.0
      self.chunk.region = NEW_REGION
      print("Done")
      logging.info("Done")

  #AIW Creates an image list and adds them to the current chunk.
  def loadImages(self):
    #SFB Build the list of image filenames
    images = []

    print("Creating image list")
    logging.info("Started creating image list")

    #SFB Loop over all files in image path and add if an image type
    for filename in os.listdir(self.imagePath):
      if filename.lower().endswith(MetaUtils.IMAGE_FILE_EXTENSION_LIST):
        images.append(filename)
    print(images)

    #AIW From API "Add a list of photos to the chunk." 
    self.chunk.addPhotos(images)
    print("Done")
    logging.info(images)
    logging.info("Done")

  #AIW Automates masking.
  def autoMask(self, PATH_TO_MASKS):
    #SFB Ensure there are images to mask first
    if len(self.chunk.cameras) <= 0:
      raise Exception("Cannot mask before adding images")

    print("Creating masks")
    logging.info("Started creating masks")

    #AIW From API "Import masks for multiple cameras." 
    # - Import background images for masking out the background. 
    # - Camera must be referenced for this step to work.
    self.chunk.importMasks(path=PATH_TO_MASKS, source=Metashape.MaskSourceBackground,
      operation=Metashape.MaskOperationReplacement, tolerance=10)
    print("Done")
    logging.info("Done")

  #AIW Places markers on coded targets in images.
  def detectMarkers(self):
    print("Placing markers")
    logging.info("Started placing markers")
    self.chunk.detectMarkers(tolerance=50, filter_mask=False, inverted=False, noparity=False, maximum_residual=5)
    print("Done")
    logging.info("Done")

  #AIW Displays marker info.
  def outputMarkers(self):
    for marker in self.chunk.markers:
      print("Getting marker info")
      #XYZ coords?
      print(marker.position)
      #Key in dictionary
      print(marker.key)
      #These are the label names shown in Metashape GUI
      print(marker.label)
      print("Done")