# For working with directories
from os import path

# Import the rawpy and imageio packages
# NOTE: These must be installed with pip
import rawpy
import imageio

# For dealing with arrays of colors (used by imageio)
import numpy

# Common raw file extensions (from wikipedia.org article on 'Raw image format')
RAW_FILE_EXTENSION_LIST = (
  '.3fr', '.ari', '.arw', '.bay', '.crw', '.cr2', '.cr3', '.cap', '.dcs', '.dcr', '.dng', '.drf',
  '.eip', '.erf', '.fff', '.gpr', '.iiq', '.k25', '.kdc', '.mdc', '.mef', '.mos', '.mrw', '.nef',
  '.nrw', '.obm', '.orf', '.pef', '.ptx', '.pxn', '.r3d', '.raf', '.raw', '.rwl', '.rw2', '.rwz',
  '.sr2', '.srf', '.srw', '.x3f', '.tif'
)

def simulate_bayer_filter(filename_in, filename_out, overwrite=False, metadataSource='example.dng',
                          customWhiteBalance=None):
  # Confirm the input file does exist
  if not path.exists(filename_in):
    raise Exception('RAW Conversion Error - "%s" does not exist' %(filename_in))

  # If overwrite is false, confirm the output file does NOT exist
  if path.exists(filename_out) and not overwrite:
    raise Exception('RAW Conversion Error - "%s" does exist and overwrite is False' %(filename_out))

  # Determine white balance settings
  if not type(customWhiteBalance) is tuple or not len(customWhiteBalance) == 4:
    customWhiteBalance = (1.0, 1.0, 1.0, 1.0)

  # Load in original image and allocate array to store bayer image
  rgbData = imageio.imread(filename_in)
  bayerData = numpy.zeros((rgbData.shape[0], rgbData.shape[1]), dtype='uint16')

  # Copy in RGGB bayer pattern
  for x in range(0, rgbData.shape[0]):
    for y in range(0, rgbData.shape[1]):
      if y % 2 == 0:
        if x % 2 == 0:
          bayerData[x, y] = rgbData[x, y, 0]
        else:
          bayerData[x, y] = rgbData[x, y, 1]
      else:
        if x % 2 == 0:
          bayerData[x, y] = rgbData[x, y, 1]
        else:
          bayerData[x, y] = rgbData[x, y, 2]

  # Write out the bayer data
  with imageio.get_writer(uri=filename_out, format='TIFF', mode='i') as writer:
    writer.set_meta_data({ "compress": 9 }) # Enable compression
    writer.append_data(bayerData)

''' Develop a RAW file at half resolution and save to normal image '''
def quick_develop_raw(filename_in, filename_out, overwrite=False, brightnessScale=1.0,
                      autoWhiteBalance=False, customWhiteBalance=None):
  develop_raw(filename_in, filename_out, overwrite, brightnessScale,
              autoWhiteBalance, customWhiteBalance, True)

''' Develop a RAW file at half resolution and save to normal image '''
def high_quality_develop_raw(filename_in, filename_out, overwrite=False, brightnessScale=1.0,
                             autoWhiteBalance=False, customWhiteBalance=None):
  develop_raw(filename_in, filename_out, overwrite, brightnessScale,
              autoWhiteBalance, customWhiteBalance, False)

''' Develop a RAW file at half resolution and save to normal image '''
def develop_raw(filename_in, filename_out, overwrite=False, brightnessScale=1.0,
                autoWhiteBalance=False, customWhiteBalance=None, halfSize=False):
  # Confirm the input file does exist
  if not path.exists(filename_in):
    raise Exception('RAW Conversion Error - "%s" does not exist' %(filename_in))

  # If overwrite is false, confirm the output file does NOT exist
  if path.exists(filename_out) and not overwrite:
    raise Exception('RAW Conversion Error - "%s" does exist and overwrite is False' %(filename_out))

  # Determine white balance settings
  cameraWhiteBalance = not autoWhiteBalance
  if not autoWhiteBalance and type(customWhiteBalance) is tuple and len(customWhiteBalance) == 4:
    cameraWhiteBalance = False
  else:
    customWhiteBalance = (1.0, 1.0, 1.0, 1.0)

  # Attept to load and process the RAW file
  with rawpy.imread(filename_in) as rawImg:
    rgbData = rawImg.postprocess(
      no_auto_bright = True,
      half_size = halfSize,
      bright = brightnessScale,
      use_camera_wb = cameraWhiteBalance,
      use_auto_wb = autoWhiteBalance,
      user_wb = customWhiteBalance)

  # Save the file to the indicated output
  with imageio.get_writer(uri=filename_out, format='TIFF', mode='i') as writer:
    # writer.set_meta_data({ "compress": 1 }) # Enable compression
    writer.append_data(rgbData)
