import sys
import argparse
import os
import pickle

from customActions import CurrentProject
from customActions import SetProject

#AIW Based on code by Markus Konrad https://tinyurl.com/yxtrlxxc.
# Creates a decorator which will use "cachefile" for caching the results 
# - of the decorated function "fn".
def userCache(cachefile):
    def decorator(fn):
        # Defines the wrapper that will call "fn" if cache exists, load it, and return its contents.
        def wrapped(*args, **kwargs):
            if os.path.exists(cachefile):
                with open(cachefile, 'rb') as cachehandle:
                    print("Using cached result from {}".format(cachefile))
                    return pickle.load(cachehandle)

            #Execute the function with all arguments.
            res = fn(*args, **kwargs)

            #Writes cache.
            with open(cachefile, 'wb') as cachehandle:
                print("Saving result to cache {}".format(cachefile))
                pickle.dump(res, cachehandle)
            
            return res

        return wrapped

    return decorator

#SFB Create the parser
parser = argparse.ArgumentParser(description='Quickly Process Photogrammetry Images.',
                                 fromfile_prefix_chars='@')

parser.add_argument('CP', '--currentProject', action=CurrentProject, help="Checks current project.")
parser.add_argument('SP', '--setProject', help="Sets project.")

#SFB Parse arguments from the file only
try:
    args = parser.parse_args(['@userInput.pickle'])
    #print(args.N)
    #print(args.I)
    #print(args.M)
except:
    print('No such file.')

    #AIW Creates a var from user input
    userInput = (('-I') + ('\n') + input("Path to images: ") + ('\n-M') + ('\n') + input("Path and format for background images: ")
                    + ('\n-N') + ('\n') + input("\nPrefix to apply to log and MetaShape file names: "))