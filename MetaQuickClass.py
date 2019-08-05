"""A script for quick, "dirty" Metashape results"""

import sys

from ProjectPrefs import ProjectPrefs

#AIW Gets locations for key image files and naming conventions from the user.
prefs = ProjectPrefs(input('Path to the folder to save current project or load previous: ') + 'test.ini')

PATH_TO_IMAGES = prefs.getPref(prefName='ImagePath')
print(PATH_TO_IMAGES)
IMAGE_PREFIX = prefs.getPref(prefName='NamePrefix')
print(IMAGE_PREFIX)
PATH_TO_MASKS = prefs.getPref(prefName='MaskPath',)
print(PATH_TO_MASKS)

prefs.saveConfig()

#SFB Import and initialize the logging system
#SFB This also redirects all MetaScan output
#SFB Reads config from the file 'logging.inf'
import Logger
Logger.init(PATH_TO_IMAGES, IMAGE_PREFIX)
logger = Logger.getLogger()

import Metashape
import MetaWork
from MetaUtilsClass import MetaUtils

#SFB These functions are static and can be called with just the module class name
MetaUtils.CHECK_VER(Metashape.app.version)
MetaUtils.USE_GPU()

logger.info("Starting Quick Processing")

#SFB Creating an instance will initialize the doc, the logger and the paths
MU = MetaUtils(None, PATH_TO_IMAGES, IMAGE_PREFIX)

#AIW Creates an image list and adds them to the current chunk.
MU.loadImages()
"""
#AIW Creates masks.
MU.autoMask(PATH_TO_MASKS)

#AIW Aligns photos.
MetaWork.quickAlign(MU.chunk)

#AIW Corrects the chunk.
MU.chunkCorrect()

#AIW Creats a quick model.
MetaWork.quickModel(MU.chunk)
"""
MU.doc.save()
logger.info("Quick Processing Done")

#AIW Exits script and releases the lock on the current document.
sys.exit()
