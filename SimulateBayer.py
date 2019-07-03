# SFB Concurrency methods
import concurrent.futures

# SFB For working with files and directories
import os
from os import path

# SFB Utility objects and functions for Raw processing
import RawUtils

def create_raw_file(fileInfo):
  # SFB Develop the raw file
  RawUtils.simulate_bayer_filter(fileInfo['inFile'], fileInfo['outFile'], True)

# SFB Hard-coded directories for testing
IN_DIRECTORY = '/Volumes/Samsung_T5/SimulatedScans/BackgroundMarkersHQ/raw'
OUT_DIRECTORY = '/Volumes/Samsung_T5/SimulatedScans/BackgroundMarkersHQ/sim'

# SFB Ensure output directory exists
os.makedirs(OUT_DIRECTORY, exist_ok=True)

# SFB Build list of all raw files in directory
rawFiles = []
for filename in os.listdir(IN_DIRECTORY):
  # SFB Determine if this is a raw file (ends with a recognized extension)
  if filename.lower().endswith('.tif'):
    # SFB Construct the full filenames for both input and output file
    inputFile = path.join(IN_DIRECTORY, filename)
    outputFile = path.join(OUT_DIRECTORY, filename)
    outputFile = path.splitext(outputFile)[0] + '.tif'
    rawFiles.append({ 'inFile': inputFile, 'outFile': outputFile })

# SFB run process_raw_file() once for each entry in the array concurrently
for rawFile in rawFiles:
  create_raw_file(rawFile)

RawUtils.quick_develop_raw('/Volumes/Samsung_T5/SimulatedScans/BackgroundMarkersHQ/sim/BackgroundMarkersHQ0009.dng',
  '/Volumes/Samsung_T5/SimulatedScans/BackgroundMarkersHQ/sim/BackgroundMarkersHQ0009.tif', True,
  customWhiteBalance=(1.0, 1.0, 1.0, 1.0))

print('\ndone')
