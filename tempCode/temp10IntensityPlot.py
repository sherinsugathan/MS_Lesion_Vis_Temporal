import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.text import Text
from matplotlib.image import AxesImage
import numpy as np
from numpy.random import rand
from matplotlib.sankey import Sankey
import matplotlib.patches as patches
import json
import networkx as nx
import SimpleITK as sitk

# read json file
rootFolder = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\"
jsonPath = rootFolder + "preProcess\\lesionStatistics.json"
structuralDataPath = rootFolder + "structural\\T1_0.nii"

img = sitk.ReadImage(structuralDataPath)
stats = sitk.StatisticsImageFilter()
stats.Execute(img)
#print("Minimum:", stats.GetMinimum())
#print("Maximum:", stats.GetMaximum())
intMin = stats.GetMinimum()
intMax = stats.GetMaximum()

dataCount = 81
# load precomputed lesion properties
structureInfo = None
with open(jsonPath) as fp: # read source json file.
    structureInfo = json.load(fp)

# Read intensity related information from lesion JSON data.
def lesionIntensityReader():

    timeDict = {}
    for timeStep in range(dataCount):
        r = structureInfo[str(timeStep)]
        
        numberOfLesionElements = len(r[0])
        #print("Timestep count", timeStep, numberOfLesionElements)
        lesionDict = {}
        for lesionIndex in (range(1,numberOfLesionElements+1)):
            intensityDataDict= {}
            intensityDataDict['Maximum'] = structureInfo[str(timeStep)][0][str(lesionIndex)][0]['Maximum']
            intensityDataDict['Mean'] = structureInfo[str(timeStep)][0][str(lesionIndex)][0]['Mean']
            intensityDataDict['Median'] = structureInfo[str(timeStep)][0][str(lesionIndex)][0]['Median']
            intensityDataDict['Minimum'] = structureInfo[str(timeStep)][0][str(lesionIndex)][0]['Minimum']
            intensityDataDict['Sigma'] = structureInfo[str(timeStep)][0][str(lesionIndex)][0]['Sigma']
            intensityDataDict['Sum'] = structureInfo[str(timeStep)][0][str(lesionIndex)][0]['Sum']
            if(intensityDataDict['Sum']==0):
                print(timeStep, lesionIndex)
            intensityDataDict['Variance'] = structureInfo[str(timeStep)][0][str(lesionIndex)][0]['Variance']
            lesionDict[lesionIndex] = intensityDataDict
        timeDict[timeStep] = lesionDict
    #print(timeDict)

def hinton(matrix, max_weight=None, ax=None):
    """Draw Hinton diagram for visualizing a weight matrix."""
    ax = ax if ax is not None else plt.gca()
    #if not max_weight:
    #    max_weight = 2 ** np.ceil(np.log(np.abs(matrix).max()) / np.log(2))
    max_weight = 0.5
    ax.patch.set_facecolor('gray') # Background color
    ax.set_aspect('equal', 'box')
    #ax.xaxis.set_major_locator(plt.NullLocator())
    #ax.yaxis.set_major_locator(plt.NullLocator())
    for (x, y), w in np.ndenumerate(matrix):
        color = (w, w, w)#'white' if w > 0 else 'black'
        edgeColor = 'black'
        size = np.sqrt(np.abs(w) / max_weight)
        rect = plt.Rectangle([x - size / 2, y - size / 2], size, size, facecolor=color, edgecolor=edgeColor)
        ax.add_patch(rect)
    ax.autoscale_view()
    ax.invert_yaxis()

def readDiffListFromJSON(timeList, labelList):  
    intensityList = []
    for i in range(len(timeList)):
        intensityList.append((int(structureInfo[str(timeList[i])][0][str(labelList[i])][0]['Mean'])-intMin)/(intMax-intMin))
    return intensityList

def getIntensityDataMatrix(nodeID, maxWidthY):
    intensityMatrix = []
    G = nx.read_gml("D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\preProcess\\lesionGraph.gml")
    connectedComponents = nx.strongly_connected_components(G)
    UG = G.to_undirected()
    dataCount = 81
    sub_graphs = list(nx.connected_components(UG))
    selectedCluster = None
    for item in sub_graphs:
        if(str(nodeID) in item):
            selectedCluster = item

    nodeIDList = selectedCluster
    for id in nodeIDList:
        intensityDiffArray = np.zeros(dataCount)
        timeList = G.nodes[id]["time"]
        labelList = G.nodes[id]["lesionLabel"]
        diffList = readDiffListFromJSON(timeList, labelList)
        #print(labelList)
        intensityDiffArray[timeList] = [elem for elem in diffList ]
        intensityMatrix.append(intensityDiffArray)
        #print(intensityDiffArray)

    old = np.random.rand(81, maxWidthY)
    new = np.array(intensityMatrix).transpose()
    print(old.shape)
    print(new.shape)

        #quit()
    #return np.random.rand(80, maxWidthY) -0.5
    return new #-0.5

def pick_simple():
    # simple picking, lines, rectangles and text
    #fig = plt.figure(num=1, frameon=False, clear=True)
    #plt.figure(1)
    #ig.patch.set_facecolor('black')
    #axIntensity = fig.add_subplot(111)
    #axIntensity.set_facecolor("orange")
    #axIntensity.axis("off")
    #axIntensity.set_axis_bgcolor((1.0, 0.47, 0.42))
    np.random.seed(19680801)
    nodeID = 2
    hinton(getIntensityDataMatrix(nodeID, 3))
    #rect = patches.Rectangle((0, 0.5), 0.05, 0.05, linewidth=1, edgecolor='r', facecolor='none')
    #ax.add_patch(rect)
    plt.subplots_adjust(left=0, right=1, top=0.9, bottom=0.1)
    plt.show()
    #ax.set_title('click on points, rectangles or text', picker=True)
    #ax.set_ylabel('ylabel', picker=True, bbox=dict(facecolor='red'))
    #line, = ax.plot(rand(100), 'o', picker=5)  # 5 points tolerance
    #sankey = Sankey(ax=ax, scale=0.1, offset=0.2, head_angle=180, format='%.0f', trunklength=1.0)
    #sankey.add(flows=[1,-1,-1], labels=['', 'split1', 'split2'], orientations=[0, 0, 0], pathlengths=[0.25, 0.25,0.25])#, #patchlabel="Widget\nA")  # Arguments to matplotlib.patches.PathPatch
    #sankey.add(flows=[1,-1,-1], labels=['', 'split1', 'split2'], orientations=[0, 0, 0], pathlengths=[0, 0,0])#, #patchlabel="Widget\nA")  # Arguments to matplotlib.patches.PathPatch
    
    #diagrams = sankey.finish()
    #diagrams[0].texts[-1].set_color('r')
    #diagrams[0].text.set_fontweight('bold')

    def onpick1(event):
        if isinstance(event.artist, Line2D):
            thisline = event.artist
            xdata = thisline.get_xdata()
            ydata = thisline.get_ydata()
            ind = event.ind
            print('onpick1 line:', np.column_stack([xdata[ind], ydata[ind]]))
        elif isinstance(event.artist, Rectangle):
            patch = event.artist
            print('onpick1 patch:', patch.get_path())
        elif isinstance(event.artist, Text):
            text = event.artist
            print('onpick1 text:', text.get_text())

    #fig.canvas.mpl_connect('pick_event', onpick1)



    def onpick4(event):
        artist = event.artist
        if isinstance(artist, AxesImage):
            im = artist
            A = im.get_array()
            print('onpick4 image', A.shape)

    #fig.canvas.mpl_connect('pick_event', onpick4)


if __name__ == '__main__':
    lesionIntensityReader()
    pick_simple()
    