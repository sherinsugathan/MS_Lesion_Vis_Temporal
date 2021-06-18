import pickle
import math
import numpy as np

'''
##########################################################################
    Function for computing y locations(middle) of all the artists in the polyCollection passed in.
##########################################################################
'''
def computeArtistVerticalCenterLocationsForStackPlot(polyCollection):
    numberOfArtists = len(polyCollection)
    stackPlotMiddleLinesY = [None] * numberOfArtists
    for i in range(numberOfArtists):
        vertexList = polyCollection[i].get_paths()[0].vertices
        vertexCount = int(math.ceil(len(vertexList)/2)) # only half (+x direction) is processed.
        firstHalf = vertexList[1:vertexCount-1] # vertices in the forward direction. (first item (starting from 1:) removed)
        #secondHalf = np.flip(vertexList[vertexCount:-1]) # vertices in the reverse direction. (last item (ending at :-2) removed)
        secondHalf = np.flip(vertexList[vertexCount:-1]) # vertices in the reverse direction. (last item (ending at :-2) removed)
        #print(firstHalf)
        #print("Hellow")
        #print(secondHalf)
        firstHalfYValues = [y for x,y in firstHalf]
        secondHalfYValues = [x for x,y in secondHalf]
        #print(firstHalfYValues)
        #print("Done")
        #print(secondHalfYValues)

        #print(firstHalfYValues)
        average = np.true_divide(np.subtract(secondHalfYValues, firstHalfYValues),2)
        # includeInSum = average!=0
        # print(includeInSum)
        firstHalfYValues = np.where(average == 0, 0, firstHalfYValues)
        result = np.add(average, firstHalfYValues) #Doing y1+(y2-y1)/2
        #print(result)
        stackPlotMiddleLinesY[i] = result
        #quit()
        #print(vertexCount)
    return stackPlotMiddleLinesY

with open('D://polyCollection_data.pkl', 'rb') as input:
    polyCollection = pickle.load(input)

yLocs = computeArtistVerticalCenterLocationsForStackPlot(polyCollection)

for item in yLocs:
    print(len(item))
print("Success")