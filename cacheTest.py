import sys
import argparse
import os
import functools
#import pickle
"""
#AIW Based on code by Markus Konrad https://tinyurl.com/yxtrlxxc.
# Creates a decorator which will use "cachefile" for caching the results 
# - of the decorated function "fn".
def userCache(cacheFile):
    def decorator(fn):
        # Defines the wrapper that will call "fn" if cache exists, load it, and return its contents.
        def wrapped(*args, **kwargs):
            if os.path.exists(cacheFile):
                with open(cacheFile, 'r') as cacheHandle:
                    print("Using cached result from {}".format(cacheFile))
                    return pickle.load(cacheHandle)

            #Execute the function with all arguments.
            res = fn(*args, **kwargs)

            #Writes cache.
            with open(cacheFile, 'wb') as cachehandle:
                print("Saving result to cache {}".format(cacheFile))
                pickle.dump(res, cachehandle)
            
            return res

        return wrapped

    return decorator
"""
"""
def userCache(cacheFile):
    #AIW Wraps decorator so its identity isn't lost.
    @functools.wraps(chacheFile)
    def wrapper(*args, **kwargs):
        if os.path.exists(cacheFile):
            with open(cacheFile, 'r') as CacheHandle:
                print("Using previous project {cacheFile}")
                return CacheHandle
"""


"""
#AIW Creates a var from user input
userInput = (('-I') + ('\n') + input("Path to images: ") + ('\n-M') + ('\n') + input("Path and format for background images: ")
                    + ('\n-N') + ('\n') + input("\nPrefix to apply to log and MetaShape file names: "))

#AIW A function that gets user input as binary and writes to cache file via decorator.
@userCache('userInput.pickle')
def IMN(userData):
    map(bin, bytearray(userData, 'utf8'))
    return userData

print(IMN(userInput))
"""
#AIW opens and writes a utf-8 encoded text file with user input.
with open('project.txt', 'w', encoding='utf-8') as f:
    projectPaths = {'imagePath':input('Path to images: '), 
                'imagePrefix':input('Prefix to apply to log and MetaShape file names: '), 
                'maskPath':input('Path and format for background images: ')}
    f.write(str(projectPaths))
