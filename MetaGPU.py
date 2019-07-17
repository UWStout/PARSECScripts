"""Enables GPU processing with Metashape"""

import Metashape

def use_gpu():
    #SFB Get number of GPUs available
    gpuList = Metashape.app.enumGPUDevices()
    gpuCount = len(gpuList)

    #SFB Enable all GPUs
    if gpuCount > 0:
        print("Enabling %d GPUs" %(gpuCount))
        Metashape.app.gpu_mask = 2**gpuCount - 1
        Metashape.app.cpu_enable = False
