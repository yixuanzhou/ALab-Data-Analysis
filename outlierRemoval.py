import numpy as np

def removeOutliers(x, outlierConstant):
    upper_quartile = np.percentile(x, 75)
    lower_quartile = np.percentile(x, 25)
    IQR = (upper_quartile - lower_quartile) * outlierConstant
    quartileSet = (lower_quartile - IQR, upper_quartile + IQR)
    resultList = []
    for y in x.tolist():
        if y >= quartileSet[0] and y <= quartileSet[1]:
            resultList.append(y)
    return resultList