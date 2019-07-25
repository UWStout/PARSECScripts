import logging
import logging.config

import os, sys, platform
from os import path

# Has the logger been initialized
_LOGGER_INITIALIZED_ = False

def init(logFilePath, logFileName):
  global _LOGGER_INITIALIZED_
  '''
  Config the logger module and redirect C module output
  '''
  # Make sure we never initialize more than once
  if _LOGGER_INITIALIZED_:
    return

  # Redirect output from C Modules to a log file (assumed to be output from Metashape)
  metashapeLogFile = os.path.join(logFilePath, "{}_metashape.txt".format(logFileName))
  redirectCStdout(metashapeLogFile)

  # Read base logging config
  configFilePath = path.join(path.dirname(path.abspath(__file__)), "logging.inf")
  logging.config.fileConfig(str(configFilePath))

  # Create default handlers/formatters for logging to file
  LF_Handler = logging.FileHandler(os.path.join(logFilePath, "{}_log.txt".format(logFileName)), "w")
  LF_Formatter = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="")
  LF_Handler.setFormatter(LF_Formatter)

  # Grab and modify the main logger
  LF_Logger = logging.getLogger("MetaPy")
  LF_Logger.addHandler(LF_Handler)

  _LOGGER_INITIALIZED_ = True

def redirectCStdout(filename):
  # We guard against exceptions in here and if something goes wrong
  # just print a warning and give up.
  try:
    sys.stdout.flush() # <--- important when redirecting to files

    # Duplicate stdout (usually file descriptor 1) to a different file descriptor number
    stdoutFD = 1
    if platform.system() != 'Windows':
      stdoutFD = sys.stdout.fileno()
    newstdout = os.dup(stdoutFD)

    # Create a file and overwrite filedescriptor 1 to be that then close it
    stdoutFile = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
    os.dup2(stdoutFile, 1)
    os.close(stdoutFile)

    # Use the original stdout to still be able to print to stdout within python
    sys.stdout = os.fdopen(newstdout, 'w')

  except Exception as e:
    print("Error: something went wrong while redirecting MetaShape output.", file=sys.stderr)
    print("Error: {}".format(e), file=sys.stderr)

def getLogger(name=None):
  global _LOGGER_INITIALIZED_
  if not _LOGGER_INITIALIZED_:
    return None
    
  if name is None or name == "":  
    return logging.getLogger("MetaPy")

  else:
    # Create a new named logger as a child of the MetaPy logger
    return logging.getLogger("MetaPy." + name)
