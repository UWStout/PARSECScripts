PATH_TO_IMAGES = ""
IMAGE_PREFIX = ""
PATH_TO_MASKS = ""

#AIW Gets locations for key image files and naming conventions from the user.
def userInput(PATH_TO_IMAGES, IMAGE_PREFIX, PATH_TO_MASKS):
    PATH_TO_IMAGES = input("Image location: ")
    PATH_TO_IMAGES = PATH_TO_IMAGES + "/"
    IMAGE_PREFIX = input("Image prefix: ")
    PATH_TO_MASKS = input("Mask image location: ")
    PATH_TO_MASKS = PATH_TO_MASKS + "/{filename}_mask.tif"