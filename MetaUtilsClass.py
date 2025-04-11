"""Reworking of MetaUtils as a Class"""

import Metashape
from CustomProgress import PBar
import os
import math

from ProjectPrefs import ProjectPrefs

import Logger
logger = None

""" This object contains general functions to help process a MetaShape
    document object It should be passed an existing document when
    created either already processed or a new document ready to be
    filled with images and processed later """


class MetaUtils:
    """ Minimum compatible version of MetaShape """
    COMPATIBLE_VERSION = "2.2"

    # Common image file extensions
    IMAGE_FILE_EXTENSION_LIST = ('.jpg', '.jpeg', '.png', '.tif', '.tiff')

    """ Construct a new MetaUtils object with the given Metashape Document """

    def __init__(self, doc, path="", prefix=""):
        # Check that all needed information was supplied
        if path == "" and prefix == "" and doc is None:
            raise Exception(
                'You must supply either an existing Metashape.Document or the path and prefix to make one.')

        # Initialize all properties
        self.doc = doc
        self.imagePath = path
        self.projectName = prefix

        # Check that we have a valid Document
        logger.debug("Verifying / loading doc")
        if self.doc is None:
            self.initDoc()
        else:
            self.imagePath, self.projectName = os.path.split(self.doc.path)
            self.projectName, extension = os.path.splitext(self.projectName)

        # Get reference to active chunk
        logger.debug("Referencing chunk")
        self.chunk = self.doc.chunk
        if self.chunk is None:
            if len(self.doc.chunks) > 0:
                self.chunk = self.doc.chunks[0]
            else:
                raise Exception('Could not find or make chunk in document.')

        logger.debug("> doc is " + str(self.doc))
        logger.debug("> chunk is " + str(self.chunk))

    @staticmethod
    def ensureLoggerReady():
        global logger
        if logger is None:
            logger = Logger.getLogger('MetaUtils')

    # Check compatibility. Modified from public Agisoft scripts.
    @staticmethod
    def CHECK_VER(metashapeVersionString):
        MetaUtils.ensureLoggerReady()
        actualVersion = ".".join(metashapeVersionString.split('.')[:2])
        if actualVersion != MetaUtils.COMPATIBLE_VERSION:
            logger.warning("Incompatible Metashape version: {} != {}".format(
                actualVersion, MetaUtils.COMPATIBLE_VERSION))
            raise Exception("Incompatible Metashape version: {} != {}".format(
                actualVersion, MetaUtils.COMPATIBLE_VERSION))
        else:
            logger.info("Metashape version: " + actualVersion + " OK")

    # Enables GPU processing in Metashape.
    @staticmethod
    def USE_GPU():
        MetaUtils.ensureLoggerReady()

        # Get number of GPUs available
        gpuList = Metashape.app.enumGPUDevices()
        gpuCount = len(gpuList)

        # Enable all GPUs
        if gpuCount > 0:
            logger.info("Enabling %d GPUs" % (gpuCount))
            Metashape.app.gpu_mask = 2**gpuCount - 2
            Metashape.app.cpu_enable = False

    # Import images and create a new doc
    def initDoc(self):
        MetaUtils.ensureLoggerReady()

        # Get reference to the currently active DOM
        self.doc = Metashape.Document()

        # Attempts to open an existing project.
        # - A new project is created if an existing project is not available.
        # - This must be done immediately after getting reference to\
        #   active DOM.
        # - .psx format will not save correctly otherwise.
        doc_path = "./" + self.projectName + ".psx"
        try:
            self.doc.open(doc_path, read_only=False, ignore_lock=True)
            logger.info("Found existing PSX document.")
        except:
            logger.info("No existing PSX document, creating new.")
            self.doc.save(doc_path)

        if len(self.doc.chunks) < 1:
            self.doc.chunk = self.doc.addChunk()
            self.doc.save(doc_path)

    # Automates correction processes for the chunk.
    def chunkCorrect(self):
        MetaUtils.ensureLoggerReady()

        # Changes the dimensions of the chunk's reconstruction volume.
        logger.info("Correcting chunk")
        NEW_REGION = self.chunk.region.copy()
        NEW_REGION.size = NEW_REGION.size * 2.0
        self.chunk.region = NEW_REGION
        logger.info("Done Correcting Chunk")

    # Creates an image list and adds them to the current chunk.
    def loadImages(self):
        MetaUtils.ensureLoggerReady()

        # Build the list of image filenames
        images = []

        logger.info("Loading Images")

        # Loop over all files in image path and add if an image type
        for filename in os.listdir(self.imagePath):
            if filename.lower().endswith(MetaUtils.IMAGE_FILE_EXTENSION_LIST):
                images.append(os.path.join(self.imagePath, filename))

        # From API "Add a list of photos to the chunk."
        elapsed = 0
        with PBar("Loading Images      ") as pbar:
            self.chunk.addPhotos(images, progress=(lambda x: pbar.update(x)))
            pbar.finish()
            elapsed = pbar.getTime()

        logger.info("Done Loading Images")
        return elapsed

    # Automates masking.
    def autoMask(self, PATH_TO_MASKS):
        MetaUtils.ensureLoggerReady()

        # Ensure there are images to mask first
        if len(self.chunk.cameras) <= 0:
            raise Exception("Cannot mask before adding images")

        logger.info("Importing Backgrounds for Masking")

        # From API "Import masks for multiple cameras."
        # - Import background images for masking out the background.
        # - Camera must be referenced for this step to work.
        elapsed = 0
        with PBar("Applying Masks      ") as pbar:
            self.chunk.importMasks(path=PATH_TO_MASKS,
                                source=Metashape.MaskSourceBackground,
                                operation=Metashape.MaskOperationReplacement,
                                tolerance=10, progress=(lambda x: pbar.update(x)))
            pbar.finish()
            elapsed = pbar.getTime()

        logger.info("Done Masking")
        return elapsed

    # Places markers on coded targets in images.
    def detectMarkers(self):
        MetaUtils.ensureLoggerReady()

        logger.info("Detecting markers")
        elapsed = 0
        with PBar("Detecting Markers   ") as pbar:
            self.chunk.detectMarkers(tolerance=50, filter_mask=False, inverted=False,
                noparity=False, maximum_residual=5, progress=(lambda x: pbar.update(x)))
            pbar.finish()
            elapsed = pbar.getTime()

        logger.info("Done Detecting Markers")
        return elapsed

    # Displays marker info.
    def outputMarkers(self):
        MetaUtils.ensureLoggerReady()

        logger.info("Outputting Marker Info")
        for marker in self.chunk.markers:
            logger.info("{} / {} - {}".format(marker.key,
                        marker.label, marker.position))
        logger.info("Done with Marker Info")
