# This program reads free surfer parcellation annotation and renders colored surface.
import SimpleITK as sitk
import vtk
import numpy as np
import sys, os
import math
import ctypes
import json
import cv2
from nibabel import freesurfer
from datetime import datetime   




def GetColorForLabel(labelFile, labelID):
    labels, ctab, regions = freesurfer.read_annot(labelFile, orig_ids=False)
    meta = dict(
                (index, {"region": item[0], "color": item[1][:4].tolist()})
                for index, item in enumerate(zip(regions, ctab)))
    annotationDataItem = meta[labelID]
    clr = annotationDataItem["color"]
    return clr

    

def MakeCellData(tableSize, lut, colors):
    '''
    Create the cell data using the colors from the lookup table.
    :param: tableSize - The table size
    :param: lut - The lookup table.
    :param: colors - A reference to a vtkUnsignedCharArray().
    '''
    for i in range(1,tableSize):
        rgb = [0.0, 0.0, 0.0]
        lut.GetColor(float(i) / (tableSize - 1),rgb)
        ucrgb = list(map(int, [x * 255 for x in rgb]))
        #colors.InsertNextTuple3(ucrgb[0], ucrgb[1], ucrgb[2])
        colors.InsertNextTuple3(1.0,0,0)
        s = '['+ ', '.join(['{:0.6f}'.format(x) for x in rgb]) + ']'
        #print(s, ucrgb)

def MakeLUTFromCTF(tableSize):
    """
    Use a color transfer Function to generate the colors in the lookup table.
    See: http://www.vtk.org/doc/nightly/html/classvtkColorTransferFunction.html
    :param: tableSize - The table size
    :return: The lookup table.
    """
    ctf = vtk.vtkColorTransferFunction()
    ctf.SetColorSpaceToDiverging()
    # Green to tan.
    #ctf.AddRGBPoint(0.0, 0.085, 0.532, 0.201)
    #ctf.AddRGBPoint(0.5, 0.865, 0.865, 0.865)
    #ctf.AddRGBPoint(1.0, 0.677, 0.492, 0.093)
    ctf.AddRGBPoint(0.0, 1, 0, 0)
    ctf.AddRGBPoint(0.5, 0.865, 0.865, 0.865)
    ctf.AddRGBPoint(1.0, 0.677, 0.492, 0.093)
    #ctf.AddRGBPoint(0.0, 0, 0, 0)
    #ctf.AddRGBPoint(0.5, 0, 0, 1)
    #ctf.AddRGBPoint(1.0, 1, 1, 1)

    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(tableSize)
    lut.Build()

    for i in range(0, tableSize):
        rgb = list(ctf.GetColor(float(i) / tableSize)) + [1]
        #print("Index is " + str(i))
        #print("RGB is ")
        #print(rgb)
        lut.SetTableValue(i, rgb)

    return lut


def MakeLUT(labelFile, tableSize):
    '''
    Make a lookup table from a set of named colors.
    :param: tableSize - The table size
    :return: The lookup table.
    '''
    labels, ctab, regions = freesurfer.read_annot(labelFile, orig_ids=False)
    meta = dict(
                (index, {"region": item[0], "color": item[1][:4].tolist()})
                for index, item in enumerate(zip(regions, ctab)))

    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(tableSize)
    lut.SetNumberOfColors(tableSize)
    #lut.SetTableRange(0.0, tableSize)
    lut.Build()

    for regionId in range(tableSize):
        annotationDataItem = meta[regionId]
        clr = annotationDataItem["color"]
        clr[3] = 1
        lut.SetTableValue(regionId, clr)
 
    return lut


def processStartInteractionEvent(obj, event):
    pass
    #print("start int")
def processEndInteractionEvent(obj, event):
    pass
    #print("end int")
def processInteractionEvent(obj, event):
    value = int(math.floor(obj.GetRepresentation().GetValue() * 80))
    print("during int", numberOfPointsLh)
    affectedLh = np.asarray(structureInfo[str(value)][0][str(lesionIndex)][0]['AffectedPointIdsLh'])
    lesionMappingLh = np.isin(vertexIndexArrayLh, affectedLh)
    c = np.full(numberOfPointsLh*3,255, dtype='B')
    c =c.astype('B').reshape((numberOfPointsLh,3))
    c[lesionMappingLh==True] = [255,0,0]
    vtk_colorsLh.SetArray(c, c.size, True)

    # for vertexIndex in range(numberOfPointsLh):
    #     if(lesionMappingLh[vertexIndex] == True):
    #         vtk_colorsLh.SetTuple3(vertexIndex, clrRed[0], clrRed[1], clrRed[2])
    #     else:
    #         vtk_colorsLh.SetTuple3(vertexIndex, clrWhite[0], clrWhite[1], clrWhite[2])
    surface_mapper.GetInput().GetPointData().SetActiveScalars("projection")
    surface_mapper.GetInput().GetPointData().SetScalars(vtk_colorsLh)
    iren.Render()

surfaceFile = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\surfaces\\lh.white.obj"
labelFile = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\surfaces\\lh.aparc.annot"
jsonFile = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\preProcess\\lesionStatistics.json"

#Load surface data.
surfaceReader = vtk.vtkOBJReader()
surfaceReader.SetFileName(surfaceFile)
surfaceReader.Update()
surface_mapper = vtk.vtkOpenGLPolyDataMapper()
surface_mapper.SetInputConnection(surfaceReader.GetOutputPort())
numberOfPointsLh = surface_mapper.GetInput().GetNumberOfPoints()

with open(jsonFile) as fp: 
    structureInfo = json.load(fp)
numberOfFollowups = len(structureInfo)

print("NUMBER OF TIMESTEPS", numberOfFollowups)


lesionIndex = 1
# for timeIndex in range(numberOfFollowups):
#     #structureInfo[timeIndex][0][lesionIndex][0]['AffectedPointIdsLh']
#     pass

vertexIndexArrayLh = np.arange(numberOfPointsLh)
affectedLh = np.asarray(structureInfo['0'][0][str(lesionIndex)][0]['AffectedPointIdsLh'])
lesionMappingLh = np.isin(vertexIndexArrayLh, affectedLh)
#print(lesionMappingLh.tolist())

clrRed = [227,74,51]
clrWhite = [255,255,255]
vtk_colorsLh = vtk.vtkUnsignedCharArray()
vtk_colorsLh.SetNumberOfComponents(3)
vtk_colorsLh.SetNumberOfTuples(numberOfPointsLh)
c = np.full(numberOfPointsLh*3,255, dtype='B')
c =c.astype('B').reshape((numberOfPointsLh,3))
c[lesionMappingLh==True] = [255,0,0]

start_time = datetime.now() 


vtk_colorsLh.SetArray(c, c.size, True)

# for vertexIndex in range(numberOfPointsLh):
#     if(lesionMappingLh[vertexIndex] == True):
#         vtk_colorsLh.SetTuple3(vertexIndex, clrRed[0], clrRed[1], clrRed[2])
#     else:
#         vtk_colorsLh.SetTuple3(vertexIndex, clrWhite[0], clrWhite[1], clrWhite[2])
time_elapsed = datetime.now() - start_time
print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))





# Read annotation file.
labels, ctab, regions = freesurfer.read_annot(labelFile, orig_ids=False)
meta = dict(
                (index, {"region": item[0], "color": item[1][:4].tolist()})
                for index, item in enumerate(zip(regions, ctab)))

numberOfColors = len(meta)
# for regionId in range(numberOfColors):
#     annotationDataItem = meta[regionId]
#     print(annotationDataItem["region"])
#     print(annotationDataItem["color"])
# print(numberOfColors)
#print(meta[35])

lut = MakeLUT(labelFile, numberOfColors)

#lut = MakeLUTFromCTF(numberOfColors)

# colorData1 = vtk.vtkUnsignedCharArray()
# colorData1.SetName('projection') # Any name will work here.
# colorData1.SetNumberOfComponents(3)
#MakeCellData(numberOfColors, lut, colorData1)

    # labels, ctab, regions = freesurfer.read_annot(labelFile, orig_ids=False)
    # meta = dict(
    #             (index, {"region": item[0], "color": item[1][:4].tolist()})
    #             for index, item in enumerate(zip(regions, ctab)))
    # annotationDataItem = meta[labelID]
    # clr = annotationDataItem["color"]
#print("Label count " + str(len(labels)))
#print("Vertex count " + str(numberOfPoints))
uniqueElements = np.unique(labels)
#print(uniqueElements)
#print(meta)

# for index in range(numberOfPointsLh):
#     if(labels[index] == -1):
#         clr = [25,5,25]
#     else:
#         clr = meta[labels[index]]["color"]
#     vtk_colors.SetTuple3(index, clr[0], clr[1], clr[2])


surface_mapper.GetInput().GetPointData().SetActiveScalars("projection")
surface_mapper.GetInput().GetPointData().SetScalars(vtk_colorsLh)
#surface_mapper.GetInput().GetPointData().AddArray(vtk_colorsLh)
#print(surface_mapper.GetInput().GetPointData().GetScalars())

#surface_mapper.SetScalarRange(0, numberOfColors-1)
#print(surface_mapper.GetScalarRange())
#surface_mapper.SetLookupTable(lut)
surface_mapper.ScalarVisibilityOn()
surface_actor = vtk.vtkActor()
surface_actor.SetMapper(surface_mapper)


    
# Display essentials
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# sliderRep = vtk.vtkSliderRepresentation2D()
# sliderRep.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
# sliderRep.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
# prop = sliderRep.GetSliderProperty()
# prop.SetColor( 1.0, 0.0, 0.0 )
# prop.SetOpacity( 0.5 )
# sprop = sliderRep.GetSelectedProperty()
# sprop.SetOpacity( 0.8 )           
# tprop = sliderRep.GetTubeProperty()
# tprop.SetColor( 0.5, 0.5, 0.5 )
# tprop.SetOpacity( 0.5 )
# cprop = sliderRep.GetCapProperty()
# cprop.SetColor( 0.0, 0.0, 1.0 )
# cprop.SetOpacity( 0.5 )
# sliderRep.PlaceWidget(  bounds   )  
# sliderRep.SetSliderLength(0.05)
# sliderRep.SetSliderWidth(0.02)
# sliderRep.SetTubeWidth(0.01)
# sliderRep.SetEndCapLength(0.02)
# sliderRep.SetEndCapWidth(0.02)
# sliderRep.SetTitleHeight( 0.02 )
#  
# contour slider
slider_rep = vtk.vtkSliderRepresentation2D()
#slider_rep.SetTitleText("contour")
slider_rep.GetPoint1Coordinate().SetCoordinateSystemToNormalizedViewport()
slider_rep.GetPoint1Coordinate().SetValue(0.65, 0.1)
slider_rep.GetPoint2Coordinate().SetCoordinateSystemToNormalizedViewport()
slider_rep.GetPoint2Coordinate().SetValue(0.95, 0.1)

sliderWidget = vtk.vtkSliderWidget()
sliderWidget.SetInteractor(iren)
sliderWidget.SetRepresentation( slider_rep )
sliderWidget.SetAnimationModeToAnimate()
sliderWidget.EnabledOn()
sliderWidget.AddObserver("StartInteractionEvent", processStartInteractionEvent )
sliderWidget.AddObserver("EndInteractionEvent", processEndInteractionEvent )
sliderWidget.AddObserver("InteractionEvent", processInteractionEvent )
sliderWidget.KeyPressActivationOff()

# Add the actors to the renderer, set the background and size
ren.AddActor(surface_actor)
ren.SetBackground(0, 0, 1.0)
renWin.SetSize(800, 800)

# This allows the interactor to initalize itself. It has to be
# called before an event loop.
iren.Initialize()

# We'll zoom in a little by accessing the camera and invoking a "Zoom"
# method on it.
ren.ResetCamera()
#ren.GetActiveCamera().Zoom(2)
renWin.Render()

# Start the event loop.
iren.Start()


print("FINISHED")