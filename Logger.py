import logging
import logging.config

import os
import sys

def init(logFilePath, logFileName):
  '''
  Config the logger module and redirect C module output
  '''
  # Redirect output from C Modules to a log file (assumed to be output from Metashape)
  metashapeLogFile = os.path.join(logFilePath, "{}_metashape.txt".format(logFileName))
  redirectCStdout(metashapeLogFile)

  # Read base logging config
  logging.config.fileConfig("logging.inf")

  # Create default handlers/formatters for logging to file
  LF_Handler = logging.FileHandler(os.path.join(logFilePath, "{}_log.txt".format(logFileName)), "w")
  LF_Formatter = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="")
  LF_Handler.setFormatter(LF_Formatter)

  # Grab and modify the main logger
  LF_Logger = logging.getLogger("MetaPy")
  LF_Logger.addHandler(LF_Handler)

def redirectCStdout(filename):
  sys.stdout.flush() # <--- important when redirecting to files

  # Duplicate stdout (usually file descriptor 1) to a different file descriptor number
  newstdout = os.dup(sys.stdout.fileno())

  # Create a file and overwrite filedescriptor 1 to be that then close it
  testFile = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
  os.dup2(testFile, 1)
  os.close(testFile)

  # Use the original stdout to still be able to print to stdout within python
  sys.stdout = os.fdopen(newstdout, 'w')

def getLogger(name=None):
  if name is None or name == "":
    return logging.getLogger("MetaPy")

  else:
    # Create a new named logger as a child of the MetaPy logger
    return logging.getLogger("MetaPy." + name)
