"""Script for Metashape utilities.""" 

import Metashape
import sys
import time
import logging

PHASE_LABEL = "none"

#SFB Erase the current line by printing spaces
# - Does not advance to the next line
def blank_line(length=80):
    empty = " " * length
    print(empty, end='\r')

#SFB Print the current progress over the current line
# - Does not advance to the next line
def progress_callback(prog):
    blank_line()
    print("%s: Progress %6.2f%%" %(PHASE_LABEL, prog), end='\r')
    sys.stdout.flush()

def print_time_elapsed(startTime):
    print("\nElapsed Time: %.2fsecs" %(time.time() - startTime))

def start_time():
    #SFB Indicate processing is starting
    sys.stdout.flush()
    print("\nStarting processing:")
    start = time.time()

def log(PATH_TO_IMAGES):
    logging.basicConfig(filename="{}log.txt", level=logging.INFO)