"""Reworking of MetaUtils as a Class"""

import Metashape
import os

import Logger
logger = None

""" This object contains general functions to help process a MetaShape
    document object It should be passed an existing document when
    created either already processed or a new document ready to be
    filled with images and processed later """


class MetaUtils:
    """ Minimum compatible version of MetaShape """
    COMPATIBLE_VERSION = "2.2"

    # SFB Common image file extensions
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

    # AIW Enables GPU processing in Metashape.
    @staticmethod
    def USE_GPU():
        MetaUtils.ensureLoggerReady()

        # Get number of GPUs available
        gpuList = Metashape.app.enumGPUDevices()
        gpuCount = len(gpuList)

        # SFB Enable all GPUs
        if gpuCount > 0:
            logger.info("Enabling %d GPUs" % (gpuCount))
            Metashape.app.gpu_mask = 2**gpuCount - 1
            Metashape.app.cpu_enable = False

    # SFB Import images and create a new doc
    def initDoc(self):
        MetaUtils.ensureLoggerReady()

        # SFB Get reference to the currently active DOM
        self.doc = Metashape.Document()

        # Attempts to open an existing project.
        # - A new project is created if an existing project is not available.
        # - This must be done immediately after getting reference to\
        #   active DOM.
        # - .psx format will not save correctly otherwise.
        doc_path = os.path.join(self.imagePath, self.projectName + ".psx")
        try:
            self.doc.open(doc_path, read_only=False, ignore_lock=True)
            logger.info("Found existing PSX document.")
        except:
            logger.info("No existing PSX document, creating new.")
            self.doc.save(doc_path)

        if len(self.doc.chunks) < 1:
            self.doc.chunk = self.doc.addChunk()
            self.doc.save(doc_path)

    # AIW Automates correction processes for the chunk.
    def chunkCorrect(self):
        MetaUtils.ensureLoggerReady()

        # SFB Changes the dimensions of the chunk's reconstruction volume.
        logger.info("Correcting chunk")
        NEW_REGION = self.chunk.region
        NEW_REGION.size = NEW_REGION.size * 2.0
        self.chunk.region = NEW_REGION
        logger.info("Done Correcting Chunk")

    # AIW Creates an image list and adds them to the current chunk.
    def loadImages(self):
        MetaUtils.ensureLoggerReady()

        # SFB Build the list of image filenames
        images = []

        logger.info("Loading Images")

        # SFB Loop over all files in image path and add if an image type
        for filename in os.listdir(self.imagePath):
            if filename.lower().endswith(MetaUtils.IMAGE_FILE_EXTENSION_LIST):
                images.append(os.path.join(self.imagePath, filename))

        # AIW From API "Add a list of photos to the chunk."
        self.chunk.addPhotos(images)
        logger.info("Done Loading Images")
        logger.debug(images)

    # AIW Automates masking.
    def autoMask(self, PATH_TO_MASKS):
        MetaUtils.ensureLoggerReady()

        # SFB Ensure there are images to mask first
        if len(self.chunk.cameras) <= 0:
            raise Exception("Cannot mask before adding images")

        logger.info("Importing Backgrounds for Masking")

        # AIW From API "Import masks for multiple cameras."
        # - Import background images for masking out the background.
        # - Camera must be referenced for this step to work.
        self.chunk.importMasks(path=PATH_TO_MASKS,
                               source=Metashape.MaskSourceBackground,
                               operation=Metashape.MaskOperationReplacement,
                               tolerance=10)
        logger.info("Done Masking")

    # AIW Places markers on coded targets in images.
    def detectMarkers(self):
        MetaUtils.ensureLoggerReady()

        logger.info("Detecting markers")
        self.chunk.detectMarkers(
            tolerance=50, filter_mask=False, inverted=False,
            noparity=False, maximum_residual=5)
        logger.info("Done Detecting Markers")

    # AIW Displays marker info.
    def outputMarkers(self):
        MetaUtils.ensureLoggerReady()

        logger.info("Outputting Marker Info")
        for marker in self.chunk.markers:
            logger.info("{} / {} - {}".format(marker.key,
                        marker.label, marker.position))
        logger.info("Done with Marker Info")
