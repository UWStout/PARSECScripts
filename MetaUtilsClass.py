"""Reworking of MetaUtils as a Class"""

import os
import numpy as np
import re

import Metashape
from CustomProgress import PBar

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

        # Skip if no GPUs found
        if gpuCount == 0:
            logger.info("No GPUs found")
            return

        # Leave out Intel integrated GPUs
        enabledCount = 0
        mask = 0
        for i in range(gpuCount):
            matchRegex = re.search(r"Intel.+UHD", gpuList[i]['name'], re.IGNORECASE)
            if not matchRegex:
                mask = mask | (1 << i)
                enabledCount += 1
            else:
                logger.info("Ignoring GPU: " + gpuList[i]['name'])


        # Enable GPUs and disable the CPU (to optimize performance)
        logger.info("Enabling %d GPUs" % (enabledCount))
        Metashape.app.gpu_mask = mask
        Metashape.app.cpu_enable = False

    @staticmethod
    def fitPlaneToMarkers(markers):
        # Pack markers into matrix subtracting centroid
        points = np.array([
            [marker.position.x, marker.position.y, marker.position.z] for marker in markers
        ])

        # Calculate the centroid of the points
        centroid = np.mean(points, axis=0)

        # Calculate the covariance matrix
        centered_points = points - centroid
        covariance_matrix = np.cov(centered_points.T)

        # Calculate the eigenvectors and eigenvalues
        eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)

        # The best-fit normal vector is the eigenvector corresponding to the smallest eigenvalue
        normal = eigenvectors[:, np.argmin(eigenvalues)]

        # Return normal and centroid
        return Metashape.Vector(normal), Metashape.Vector(centroid)

    # Import images and create a new doc
    def initDoc(self):
        MetaUtils.ensureLoggerReady()

        # Get reference to the currently active DOM
        self.doc = Metashape.Document()

        # Attempts to open an existing project.
        # - A new project is created if an existing project is not available.
        # - This must be done immediately after getting reference to active DOM.
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

    # Helper function to retrieve markes by label
    def findMarkers(self, labels):
        MetaUtils.ensureLoggerReady()

        markers = []
        for label in labels:
            foundMarker = [marker for marker in self.chunk.markers if marker.label == label]
            if len(foundMarker) == 1: markers.append(foundMarker[0])

        # Logs a warning if not all markers were found.
        if len(markers) != len(labels):
            logger.warn("Markers not found:")
            foundLabels = [marker.label for marker in markers]
            for label in labels:
                if label not in foundLabels:
                    logger.warn("\t" + label)

        return markers

    # Automates correction processes for the chunk.
    def chunkCorrect(self):
        MetaUtils.ensureLoggerReady()

        # Changes the dimensions of the chunk's reconstruction volume.
        logger.info("Leveling and orienting chunk")

        # Compute a basis from markers in the scene
        up, view, c = self.computeBasisFromCoplanerMarkers(
            ['target 15', 'target 11', 'target 13', 'target 9']
        )

        # Use markers to find a known "upward" vector
        upMarkers = self.findMarkers(['target 15', 'target 20'])
        upward = (upMarkers[1].position - upMarkers[0].position).normalized()

        # If up vector is opposite to the upward vector, flip it
        if up * upward < 0: up = -up

        # Compute rest of basis and apply to chunk
        t = Metashape.Vector.cross(view, up).normalized()
        v = Metashape.Vector.cross(up, t).normalized()
        self.applyBasis(t, up, v, c)

        # Apply a final fudge rotation to correct for non-planer markers
        fudgeMatrix = Metashape.Matrix([
            [ 0.99895, 0.04575, -0.00006],
            [-0.04570, 0.99791, -0.04557],
            [-0.00202, 0.04552,  0.99896]
        ])
        self.chunk.transform.rotation = fudgeMatrix * self.chunk.transform.rotation

    def setRegion(self, scaler):
        MetaUtils.ensureLoggerReady()

        # Changes the dimensions of the chunk's reconstruction volume.
        logger.info("Limiting and orienting region")

        # Find midpoint of volume
        markers = self.findMarkers(['target 15', 'target 11', 'target 13', 'target 9'])
        points = np.array([[marker.position.x, marker.position.y, marker.position.z] for marker in markers])
        centroid = Metashape.Vector(np.mean(points, axis=0))

        # Compute distance between the width markers
        widthMarkers = self.findMarkers(['target 11', 'target 15'])
        cageWidth = (widthMarkers[0].position - widthMarkers[1].position).norm()

        # Align region with chunk (presumes chunk has already been cleaned)
        self.chunk.region.rot = self.chunk.transform.rotation.t()
        yAxis = Metashape.Matrix.Rotation(self.chunk.region.rot).mulv(Metashape.Vector((0, 1, 0)))
        if scaler > 0.75:
            self.chunk.region.center = centroid
        else:
            # Slightly lower than centroid
            adjust = cageWidth * 0.05
            self.chunk.region.center = Metashape.Vector((
                centroid.x - yAxis.x * adjust,
                centroid.y - yAxis.y * adjust,
                centroid.z - yAxis.z * adjust
            ))

        # Set size according to parameter
        if scaler > 0.75:
            self.chunk.region.size = Metashape.Vector((
                cageWidth * scaler, cageWidth * scaler, cageWidth * scaler
            ))
        else:
            # Don't let height be below 75%
            self.chunk.region.size = Metashape.Vector((
                cageWidth * scaler, cageWidth * 0.75, cageWidth * scaler
            ))

    def computeBasisFromCoplanerMarkers(self, markerLabels):
        MetaUtils.ensureLoggerReady()

        # Find the relevant targets
        targets = self.findMarkers(markerLabels)

        # Check that all targets were found
        if len(targets) < len(markerLabels):
            return None, None, None

        # Compute best-fit plane
        up, centroid = MetaUtils.fitPlaneToMarkers(targets)

        # Compute view direction from first two targets
        v = (targets[0].position - targets[1].position).normalized()

        # Return normal, view direction, and center of mass
        return up, v, centroid

    def applyBasis(self, t, u, v, c):
        self.chunk.transform.matrix = Metashape.Matrix([
            [ t.x,  t.y,  t.z, -c.x],
            [ u.x,  u.y,  u.z, -c.y],
            [-v.x, -v.y, -v.z, -c.z],
            [0, 0, 0, 1]
        ])

    def filterTiePoints(self):
        # Compute distance between the width markers
        widthMarkers = self.findMarkers(['target 11', 'target 15'])
        cageWidth = (widthMarkers[0].position - widthMarkers[1].position).norm()

        # Find midpoint of volume
        markers = self.findMarkers(['target 15', 'target 11', 'target 13', 'target 9'])
        points = np.array([[marker.position.x, marker.position.y, marker.position.z] for marker in markers])
        centroid = Metashape.Vector(np.mean(points, axis=0))

        # General size to limit
        horizSize = 2.138 * cageWidth
        vertSize = 1.145 * cageWidth

        # Build bounding box region
        BBRegion = self.chunk.region.copy()
        BBRegion.size = Metashape.Vector([horizSize, vertSize, horizSize])
        BBRegion.center = centroid

        # Select tie points outside bounding box
        for tiePoint in self.chunk.tie_points.points:
            MetaUtils.checkPoint(tiePoint, BBRegion)

        # Remove selected tie points
        self.chunk.tie_points.removeSelectedPoints()

    def checkPoint(point, region):
        R = region.rot		# Bounding box rotation matrix
        C = region.center	# Bounding box center vector
        size = region.size

        v = point.coord
        v.size = 3
        v_c = v - C
        v_r = R.t() * v_c

        if abs(v_r.x) > abs(size.x / 2.):
            point.selected = True
        elif abs(v_r.y) > abs(size.y / 2.):
            point.selected = True
        elif abs(v_r.z) > abs(size.z / 2.):
            point.selected = True
        else:
            point.selected = False

    # Creates an image list and adds them to the current chunk.
    def loadImages(self):
        MetaUtils.ensureLoggerReady()

        # If the chunk already has images, skip loading
        if len(self.chunk.cameras) > 0:
            logger.info("Skipping image loading (chunk already contains images)")
            return 0

        # Build the list of image filenames
        images = []

        logger.info("Loading Images")

        # Loop over all files in image path and add if an image type
        for filename in os.listdir(self.imagePath):
            if filename.lower().endswith(MetaUtils.IMAGE_FILE_EXTENSION_LIST):
                images.append(os.path.join(self.imagePath, filename))

        # From API "Add a list of photos to the chunk."
        elapsed = 0
        with PBar("Loading Images") as pbar:
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
        with PBar("Applying Masks") as pbar:
            self.chunk.importMasks(path=PATH_TO_MASKS,
                                source=Metashape.MaskSourceBackground,
                                operation=Metashape.MaskOperationReplacement,
                                tolerance=10, progress=(lambda x: pbar.update(x)))
            pbar.finish()
            elapsed = pbar.getTime()

        logger.info("Done Masking")
        return elapsed

    # Places markers on coded targets in images.
    def detectMarkers(self, tolerance=50):
        MetaUtils.ensureLoggerReady()

        # If the chunk already has markers, don't redetect
        if len(self.chunk.markers) > 0:
            logger.info("Skipping marker detection (chunk already has markers)")
            return 0

        logger.info("Detecting markers (tolerance = %d)" % tolerance)
        elapsed = 0
        with PBar("Detecting Markers") as pbar:
            self.chunk.detectMarkers(tolerance=tolerance, filter_mask=False, inverted=False,
                noparity=False, maximum_residual=5, progress=(lambda x: pbar.update(x)))
            pbar.finish()
            elapsed = pbar.getTime()

        logger.info("Done Detecting Markers (found %d markers)" % len(self.chunk.markers))
        return elapsed

    # Places markers on coded targets in images.
    def optimizeCameras(self):
        MetaUtils.ensureLoggerReady()

        logger.info("Optimizing Camera Fitting")
        elapsed = 0
        with PBar("Optimizing Cameras") as pbar:
            self.chunk.optimizeCameras(fit_b1=True, fit_b2=True, progress=(lambda x: pbar.update(x)))
            pbar.finish()
            elapsed = pbar.getTime()

        logger.info("Done Optimizing Cameras")
        return elapsed

    # Displays marker info.
    def outputMarkers(self):
        MetaUtils.ensureLoggerReady()

        logger.info("Outputting Marker Info")
        for marker in self.chunk.markers:
            logger.info("{} / {} - {}".format(marker.key,
                        marker.label, marker.position))
        logger.info("Done with Marker Info")
