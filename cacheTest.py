import sys
import argparse
import os
import pickle

#AIW Based on code by Markus Konrad https://tinyurl.com/yxtrlxxc.
# Creates a decorator which will use "user" for caching the results 
# - of the decorated function "func".
def userCache(user):
    # Defines the wrapper that will call "func" if "user" exists, load it, and return its contents.
    def decor(func):
        def wrap(*args, **kwargs):
            if os.path.exists(user):
                with open(user, 'rb') as userHandle:
                    print("Using cached result from {}".format(user))
                    return pickle.load(userHandle)

            #Execute the function with all arguments.
            res = func(*args, **kwargs)

            #Writes cache.
            with open(user, 'wb') as cacheHandle:
                print("Saving result to cache {}".format(user))
                pickle.dump(res, cacheHandle)
            
            return res

        return wrap

    return decor

@userCache(usePrev.pickle)
def usePrev():
    userCache = ('user.args')
    with open('user.args', 'w') as f:
        f.write (('-I') + ('\n') + input("Path to images: ") + ('\n-M') + ('\n') + input("Path and format for background images: ")
                    + ('\n-N') + ('\n') + input("\nPrefix to apply to log and MetaShape file names: "));

print(usePrev())