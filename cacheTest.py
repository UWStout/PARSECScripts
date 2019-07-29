import sys
import argparse
import os
import pickle

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

#AIW Creates a var from user input
userInput = (('-I') + ('\n') + input("Path to images: ") + ('\n-M') + ('\n') + input("Path and format for background images: ")
                    + ('\n-N') + ('\n') + input("\nPrefix to apply to log and MetaShape file names: "))

#AIW A function that gets user input as binary and writes to cache file via decorator.
@userCache('userInput.pickle')
def IMN(userInput):
    map(bin, bytearray(userInput, 'utf8'))
    return userInput

print(IMN(userInput))