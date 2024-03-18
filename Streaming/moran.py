import numpy as np
import cv2
import warnings
# Objects is a 4d array on the shape:
# [objectNo, layerNo, y, x]
def calculateOv(objects):
    nbhd = 3 # The neighbourhood size inside a layer
    ws = 3 # The neighbourhood size across layers
    includeIncomplete = False # Controls whether points with incomplete neighbourhoods should be included or not
    outlierValues = []
    for _, objectLayers in enumerate(objects):
        objectLayers = np.copy(objectLayers)
        avg = np.nanmean(objectLayers)
        stddev = np.nanstd(objectLayers)
        objectLayers = (objectLayers - avg) / stddev
        z, y, x = objectLayers.shape
        # Step 1: calculate neighbourhood
        if(includeIncomplete):
            neighbourkernel = np.ones((nbhd, nbhd))
            zeroAndOnes = np.where(np.isnan(objectLayers), 0, 1).astype(np.uint8)
            nonBackgroundValues = np.array([cv2.filter2D(src=layer, ddepth=-1, kernel=neighbourkernel) for layer in zeroAndOnes])
            nonBackgroundValues = np.where(nonBackgroundValues < 1, np.nan, nonBackgroundValues)
            objectLayers = np.where(np.isnan(objectLayers), 0, objectLayers)
            flatNeighbourhood = np.array([cv2.filter2D(src=layer, ddepth=-1, kernel=neighbourkernel) for layer in objectLayers]) / nonBackgroundValues
        else:
            neighbourkernel = np.ones((nbhd, nbhd)) / nbhd**2
            flatNeighbourhood = np.array([cv2.filter2D(src=layer, ddepth=-1, kernel=neighbourkernel) for layer in objectLayers])
        neighbourhoodValues = np.array([
            np.sum(flatNeighbourhood[layerIndex-ws:layerIndex], axis=0)/ws
            for layerIndex in range(ws, z+1)
        ])
        # Step 2: calculate outlier
        # This is different from batch processing (we're moving the center)
        ys = neighbourhoodValues
        xs = objectLayers[ws-1:z+1]
        filter = np.logical_and(np.isfinite(xs), np.isfinite(ys))
        with warnings.catch_warnings():
            line = np.polyfit(xs[filter].flatten(), ys[filter].flatten(), 1)
            p = np.poly1d(line)
            outlierValues.append(p(xs) - ys)