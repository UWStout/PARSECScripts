import os

from configparser import ConfigParser

#SFB Class wide defaults
DEFAULT_FILENAME = 'project.ini'
PATH_TO_IMAGES = None
IMAGE_PREFIX = None
PATH_TO_MASKS = None

def readConfig(prefsFileName):
    if prefsFileName:
        prefsFileName = prefsFileName
    INIConfig = ConfigParser