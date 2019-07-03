# SFB Concurrency methods
import concurrent.futures

# SFB For working with files and directories
import os
from os import path

# SFB Utility objects and functions for Raw processing
import RawUtils

def process_raw_file(fileInfo):
  # SFB Develop the raw file
  RawUtils.quick_develop_raw(fileInfo['inFile'], fileInfo['outFile'], True)
  print ('.', end='')

# SFB Hard-coded directories for testing
IN_DIRECTORY = './TestData/001 Daisy-Yoshi/Raw'
OUT_DIRECTORY = './TestData/001 Daisy-Yoshi/Processed'

# SFB Ensure output directory exists
os.makedirs(OUT_DIRECTORY, exist_ok=True)

# SFB Build list of all raw files in directory
rawFiles = []
for filename in os.listdir(IN_DIRECTORY):
  # SFB Determine if this is a raw file (ends with a recognized extension)
  if filename.lower().endswith(RawUtils.RAW_FILE_EXTENSION_LIST):
    # SFB Construct the full filenames for both input and output file
    inputFile = path.join(IN_DIRECTORY, filename)
    outputFile = path.join(OUT_DIRECTORY, filename)
    outputFile = path.splitext(outputFile)[0] + '.tif'
    rawFiles.append({ 'inFile': inputFile, 'outFile': outputFile })

# SFB run process_raw_file() once for each entry in the array concurrently
with concurrent.futures.ProcessPoolExecutor() as executor:
  executor.map(process_raw_file, rawFiles)
print('\ndone')
