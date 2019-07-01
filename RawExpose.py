# SFB Concurrency methods
import concurrent.futures

# SFB For working with files and directories
import os
from os import path

# SFB Import the rawpy and imageio packages
import rawpy
import imageio

# SFB Common raw file extensions (from wikipedia.org article on 'Raw image format')
RAW_FILE_EXTENSION_LIST = (
  '.3fr', '.ari', '.arw', '.bay', '.crw', '.cr2', '.cr3', '.cap', '.dcs', '.dcr', '.dng', '.drf',
  '.eip', '.erf', '.fff', '.gpr', '.iiq', '.k25', '.kdc', '.mdc', '.mef', '.mos', '.mrw', '.nef',
  '.nrw', '.obm', '.orf', '.pef', '.ptx', '.pxn', '.r3d', '.raf', '.raw', '.rwl', '.rw2', '.rwz',
  '.sr2', '.srf', '.srw', '.x3f'
)

''' Develop a RAW file at half resolution and save to normal image '''
def quick_develop_raw(filename_in, filename_out, overwrite=False):
  # SFB Confirm the input file does exist
  if not path.exists(filename_in):
    raise Exception('RAW Conversion Error - "%s" does not exist' %(filename_in))

  # SFB If overwrite is false, confirm the output file does NOT exist
  if path.exists(filename_out) and not overwrite:
    raise Exception('RAW Conversion Error - "%s" does exist and overwrite is False' %(filename_out))

  # SFB Attept to load and process the RAW file
  with rawpy.imread(filename_in) as rawImg:
    rgbData = rawImg.postprocess(
      half_size = True,
      no_auto_bright = True,
      bright = 1.0,
      use_camera_wb = True,
      use_auto_wb = False,
      user_wb = (0.0, 0.0, 0.0, 0.0))

  # SFB Save the file to the indicated output
  with imageio.get_writer(uri=filename_out, format='TIFF', mode='i') as writer:
    # writer.set_meta_data({ "compress": 1 }) # Enable compression
    writer.append_data(rgbData)

def process_raw_file(fileInfo):
  # SFB Develop the raw file
  quick_develop_raw(fileInfo['inFile'], fileInfo['outFile'], True)
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
  if filename.lower().endswith(RAW_FILE_EXTENSION_LIST):
    # SFB Construct the full filenames for both input and output file
    inputFile = path.join(IN_DIRECTORY, filename)
    outputFile = path.join(OUT_DIRECTORY, filename)
    outputFile = path.splitext(outputFile)[0] + '.tif'
    rawFiles.append({ 'inFile': inputFile, 'outFile': outputFile })

# SFB run process_raw_file() once for each entry in the array concurrently
with concurrent.futures.ProcessPoolExecutor() as executor:
  executor.map(process_raw_file, rawFiles)
print('\ndone')
