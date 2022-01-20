from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5 import QtCore, QtGui
import vtk
import os
import sys
import glob
import math
import numpy as np
import networkx as nx
from vtkmodules.vtkCommonColor import vtkNamedColors
import itertools
import keyboard as kb
from datetime import datetime
import matplotlib.pyplot as plt

class ReadThread(QObject): 
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    def __init__(self, folder_name, actorList, actorListForLesionView, SurfacesList, keyType, keyID, parent=None):
        super(ReadThread, self).__init__(parent) 
        self.read_folder_name = folder_name + "\\surfaces\\lesions\\"
        self.surfaceList = actorList
        self.surfaceListForLesionView = actorListForLesionView
        self.surfaceActor = SurfacesList
        self.keyType = keyType
        self.keyID = keyID
        
    def run(self):
        self.actorList = []
        file_count = len(glob.glob1(self.read_folder_name,"*.vtm")) # number of time points.
        for i in range(file_count):
            lesionSurfaceDataFilePath = self.read_folder_name + "lesions" + str(i) + ".vtm"
            mbr = vtk.vtkXMLMultiBlockDataReader()
            mbr.SetFileName(lesionSurfaceDataFilePath)
            mbr.Update()

            mb = mbr.GetOutput()
            for blockIndex in range(mb.GetNumberOfBlocks()):
                polyData = vtk.vtkPolyData.SafeDownCast(mb.GetBlock(blockIndex))
                if polyData and polyData.GetNumberOfPoints():
                    mapper = vtk.vtkOpenGLPolyDataMapper()
                    mapper.SetInputData(polyData)
                    mapper.SetScalarModeToUseCellData()
                    mapper.Update()

                    mapper2 = vtk.vtkOpenGLPolyDataMapper()
                    mapper2.SetInputData(polyData)
                    mapper2.SetScalarModeToUseCellData()
                    mapper2.Update()

                    info = vtk.vtkInformation()
                    info.Set(self.keyType, "lesion")
                    info.Set(self.keyID, str(blockIndex))

                    info2 = vtk.vtkInformation()
                    info2.Set(self.keyType, "lesion")
                    info2.Set(self.keyID, str(blockIndex))

                    actor = vtk.vtkActor()
                    actor.SetMapper(mapper)
                    actor.GetProperty().SetColor(0.6196078431372549, 0.7372549019607843, 0.8549019607843137)
                    #actor.GetProperty().SetColor(0.9411764705882353, 0.2313725490196078, 0.1254901960784314)
                    actor.GetProperty().SetInformation(info)
                    smoothSurface(actor)
                    actor.GetMapper().ScalarVisibilityOff()
                    mapper.Update()

                    actor2 = vtk.vtkActor()
                    actor2.SetMapper(mapper2)
                    actor2.GetProperty().SetColor(0.6196078431372549, 0.7372549019607843, 0.8549019607843137)
                    #actor2.GetProperty().SetColor(0.9411764705882353, 0.2313725490196078, 0.1254901960784314)
                    actor2.GetProperty().SetInformation(info2)
                    smoothSurface(actor2)
                    actor2.GetMapper().ScalarVisibilityOff()
                    mapper2.Update()

                    self.surfaceList[i].append(actor)
                    self.surfaceListForLesionView[i].append(actor2)
            self.progress.emit(int((i/80)*100))
        #self.surfaceActor.append(self.loadSurfaces()) # Load ventricle mesh
        self.loadSurfaces()
        self.finished.emit()

    def loadSurfaces(self):
        #surfaceFileNames = ["ventricleMesh", "lh.white", "rh.white", "lh.pial", "rh.pial", "lh.inflated", "rh.inflated"]
        surfaceFileNames = ["ventricleMesh", "lh.white", "rh.white", "lh.pial", "rh.pial"]
        for fileName in surfaceFileNames:
            loadPath = self.read_folder_name + "..\\" + fileName + ".obj"
            reader = vtk.vtkOBJReader()
            reader.SetFileName(loadPath)
            reader.Update()
            mapper = vtk.vtkOpenGLPolyDataMapper()
            mapper.SetInputConnection(reader.GetOutputPort())
            mapper.ScalarVisibilityOn()

            info = vtk.vtkInformation()
            info.Set(self.keyType, "OtherSurfaces")
            info.Set(self.keyID, str(fileName)) # does not matter

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetInterpolationToGouraud()
            if(fileName == "ventricleMesh"):
                actor.GetProperty().SetColor(0.5607843137254902, 0.7058823529411765, 0.5725490196078431) # green
            else:
                actor.GetProperty().SetColor(1.0, 1.0, 1.0)
            actor.GetProperty().SetInformation(info)
            self.surfaceActor.append(actor)
        return
        #self.ren.AddActor(actor)
        #self.ren.ResetCamera()
        #self.iren.Render()

'''
##########################################################################
    Class for implementing custom interactor for main VR with lesions in it.
##########################################################################
'''
class CustomMouseInteractorLesions(vtk.vtkInteractorStyleTrackballCamera):
    
    def __init__(self,lesionvis,parent=None,iren=None):
        self.AddObserver("LeftButtonPressEvent",self.leftButtonPressEvent)
        self.AddObserver("LeftButtonReleaseEvent",self.leftButtonReleaseEvent)
        self.AddObserver("MouseMoveEvent", self.mouseMoveEvent)
        self.lesionvis = lesionvis
        self.LastPickedActor = None
        self.NewPickedActor = None
        self.clickedLesionActor = None
        self.LastPickedProperty = vtk.vtkProperty()
        self.iren = iren
        self.MouseMotion = 0
        self.overlayData = None
        self.informationKeyType = vtk.vtkInformationStringKey.MakeKey("type", "vtkActor")
        self.informationKeyID = vtk.vtkInformationStringKey.MakeKey("ID", "vtkActor")

    # Set lesion data to overlay text and display overlay.
    def mapLesionToText(self, lesionID, NewPickedActor):
        self.clickedLesionActor = self.NewPickedActor
        # if(self.vtkWidget.GetRenderWindow().HasRenderer(self.renMapOutcome) == True):
        #     self.vtkWidget.GetRenderWindow().RemoveRenderer(self.renMapOutcome)
        # Highlight the picked actor by changing its properties
        self.NewPickedActor.GetMapper().ScalarVisibilityOff()
        self.NewPickedActor.GetProperty().SetColor(1.0, 0.9686274509803922, 0.7372549019607843) # yellowish color
        self.NewPickedActor.GetProperty().SetDiffuse(1.0)
        self.NewPickedActor.GetProperty().SetSpecular(0.0)

        # centerOfMassFilter = vtk.vtkCenterOfMass()
        # centerOfMassFilter.SetInputData(self.NewPickedActor.GetMapper().GetInput())
        # #print(self.NewPickedActor.GetMapper().GetInput())
        # centerOfMassFilter.SetUseScalarsAsWeights(False)
        # centerOfMassFilter.Update()

        #self.centerOfMass = centerOfMassFilter.GetCenter()
        #self.centerOfMass = self.lesionCentroids[int(lesionID)-1][0:3]

        # Get slice numbers for setting the MPRs.
        #sliceNumbers = computeSlicePositionFrom3DCoordinates(self.subjectFolder, self.lesionCentroids[int(lesionID)-1][0:3])
    
        # Update sliders based on picked lesion.
        #self.sliderA.setValue(sliceNumbers[0])
        #self.sliderB.setValue(sliceNumbers[1])
        #self.sliderC.setValue(sliceNumbers[2])
        
        #self.lesionvis.userPickedLesion = lesionID
        lesionID = int(lesionID)
        self.overlayData = self.lesionvis.getLesionData(lesionID)

    def leftButtonReleaseEvent(self, obj, event):
        if(self.MouseMotion == 0):
            clickPos = self.GetInteractor().GetEventPosition()
            picker = vtk.vtkPropPicker()
            picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
            # pointPicker = vtk.vtkPointPicker()
            # pointPicker.SetTolerance(0.0005)
            # pointPicker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
            # worldPosition = pointPicker.GetPickPosition()
            # print(pointPicker.GetPointId())
            self.clickedLesionActor = None
            cellPicker = vtk.vtkCellPicker()
            cellPicker.SetTolerance(0.0005)
            cellPicker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
            #worldPosition = cellPicker.GetPickPosition()
            #print(cellPicker.GetPointId())
            
            # get the new
            self.NewPickedActor = picker.GetActor()
            # If something was selected
            if self.NewPickedActor:
                # If we picked something before, reset its property
                if self.LastPickedActor:
                    #self.LastPickedActor.GetMapper().ScalarVisibilityOn()
                    self.LastPickedActor.GetProperty().DeepCopy(self.LastPickedProperty)
                
                # Save the property of the picked actor so that we can
                # restore it next time
                self.LastPickedProperty.DeepCopy(self.NewPickedActor.GetProperty())

                itemType = self.NewPickedActor.GetProperty().GetInformation().Get(self.lesionvis.keyType)
                lesionID = self.NewPickedActor.GetProperty().GetInformation().Get(self.lesionvis.keyID)

                if itemType == 'lesion':  # lesion picked.
                    self.lesionvis.userPickedLesionID = int(lesionID) + 1
                    self.lesionvis.clearLesionHighlights()
                    self.mapLesionToText(lesionID, self.NewPickedActor)

                    nodeID = self.lesionvis.getNodeIDforPickedLesion(self.lesionvis.userPickedLesionID)
                    self.lesionvis.selectedNodeID = nodeID
                    # if(self.lesionvis.buttonGroupIntensityGraphs.checkedId() == -3): # Violin plot
                    #     self.lesionvis.plotViolin()
                    #     self.lesionvis.canvasViolin.draw()
                    if kb.is_pressed("ctrl"):
                        self.lesionvis.updateDefaultGraph(None, [nodeID])
                    #self.lesionvis.on_sliderChangedTimePoint() # DO NOT ENABLE. BUG
                    self.lesionvis.updateLesionOverlayText()
                    self.lesionvis.updateContourComparisonView(self.lesionvis.userPickedLesionID)
                else:
                    self.resetToDefaultViewLesions()
                    self.lesionvis.userPickedLesionID = None

                #self.iren.Render()
                # save the last picked actor
                self.LastPickedActor = self.NewPickedActor
            else: # no actor picked. Clicked on background.
                self.resetToDefaultViewLesions()
                self.lesionvis.userPickedLesionID = None

        self.OnLeftButtonUp()
        return

    def resetToDefaultViewLesions(self):
        if(self.LastPickedActor!=None):
            #self.LastPickedActor.GetProperty().DeepCopy(self.LastPickedProperty)
            self.lesionvis.clearLesionHighlights()
            self.LastPickedActor = None
            self.lesionvis.textActorLesionStatistics.SetInput("")
        #self.lesionvis.ren.RemoveActor(self.textActorLesionStatistics) # Text overlay

    def mouseMoveEvent(self,obj,event):
        self.MouseMotion = 1
        self.OnMouseMove()
        return

    def leftButtonPressEvent(self,obj,event):
        self.MouseMotion = 0
        self.OnLeftButtonDown()


'''
##########################################################################
    Class for implementing custom interactor for brain surface renderer
##########################################################################
'''
class CustomMouseInteractorSurface(vtk.vtkInteractorStyleTrackballCamera):
    
    def __init__(self,lesionvis,parent=None,iren=None):
        self.AddObserver("LeftButtonPressEvent",self.leftButtonPressEvent)
        #self.AddObserver("LeftButtonReleaseEvent",self.leftButtonReleaseEvent)
        #self.AddObserver("MouseMoveEvent", self.mouseMoveEvent)
        self.lesionvis = lesionvis
        self.LastPickedActor = None
        self.NewPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()
        self.iren = iren
        self.MouseMotion = 0
        self.overlayData = None
        self.informationKeyType = vtk.vtkInformationStringKey.MakeKey("type", "vtkActor")
        self.informationKeyID = vtk.vtkInformationStringKey.MakeKey("ID", "vtkActor")

    # # Set lesion data to overlay text and display overlay.
    # def mapLesionToText(self, lesionID, NewPickedActor):
    #     # if(self.vtkWidget.GetRenderWindow().HasRenderer(self.renMapOutcome) == True):
    #     #     self.vtkWidget.GetRenderWindow().RemoveRenderer(self.renMapOutcome)
    #     # Highlight the picked actor by changing its properties
    #     self.NewPickedActor.GetMapper().ScalarVisibilityOff()
    #     self.NewPickedActor.GetProperty().SetColor(0.4627, 0.4627, 0.9568) # A blueish color.
    #     self.NewPickedActor.GetProperty().SetDiffuse(1.0)
    #     self.NewPickedActor.GetProperty().SetSpecular(0.0)

    def leftButtonPressEvent(self, obj, event):
        #print("left button press event called")
        clickPos = self.GetInteractor().GetEventPosition()
        #print("SherinL calling picker")
        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
        # pointPicker = vtk.vtkPointPicker()
        # pointPicker.SetTolerance(0.0005)
        # pointPicker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
        # worldPosition = pointPicker.GetPickPosition()
        # print(pointPicker.GetPointId())
        self.clickedLesionActor = None
        cellPicker = vtk.vtkCellPicker()
        cellPicker.SetTolerance(0.0005)
        cellPicker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())
        #worldPosition = cellPicker.GetPickPosition()
        #print(cellPicker.GetPointId())

        # get the new
        self.NewPickedActor = picker.GetActor()
        # If something was selected
        if self.NewPickedActor:
            # If we picked something before, reset its property
            if self.LastPickedActor:
                #self.LastPickedActor.GetMapper().ScalarVisibilityOn()
                self.LastPickedActor.GetProperty().DeepCopy(self.LastPickedProperty)

            # Save the property of the picked actor so that we can
            # restore it next time
            self.LastPickedProperty.DeepCopy(self.NewPickedActor.GetProperty())

            itemType = self.NewPickedActor.GetProperty().GetInformation().Get(self.lesionvis.keyType)
            lesionID = self.NewPickedActor.GetProperty().GetInformation().Get(self.lesionvis.keyID)
            #print(itemType, lesionID)

            if(itemType == 'OtherSurfaces'): # lesion picked.
                print("picked other surfaces")
            else:
                self.resetToDefaultViewSurface()
                self.lesionvis.userPickedLesionID = None

            #self.iren.Render()
            # save the last picked actor
            self.LastPickedActor = self.NewPickedActor
        else: # no actor picked. Clicked on background.
            self.resetToDefaultViewSurface()

        self.OnLeftButtonDown()
        #print("left button up through")
        return

    def resetToDefaultViewSurface(self):
        if(self.LastPickedActor!=None):
            pass

    # def mouseMoveEvent(self,obj,event):
    #     self.MouseMotion = 1
    #     self.OnMouseMove()
    #     return

    # def leftButtonPressEvent(self, obj, event):
    #     self.MouseMotion = 0
    #     print("entering heresssssssssss")
    #     self.OnLeftButtonDown()

'''
##########################################################################
    Smooth polydata.
    Returns: Smoeethened surface.
##########################################################################
'''
def smoothPolyData(polyData):
    smoother = vtk.vtkWindowedSincPolyDataFilter()
    #smoother.SetInputConnection(sphereSource->GetOutputPort())
    smoother.SetInputData(polyData)
    smoother.SetNumberOfIterations(9)
    smoother.BoundarySmoothingOff()
    smoother.FeatureEdgeSmoothingOff()
    smoother.SetFeatureAngle(120.0)
    smoother.SetPassBand(.001)
    smoother.NonManifoldSmoothingOn()
    smoother.NormalizeCoordinatesOn()
    smoother.Update()

    normalGenerator = vtk.vtkPolyDataNormals()
    normalGenerator.SetInputData(smoother.GetOutput())
    normalGenerator.ComputePointNormalsOn()
    normalGenerator.ComputeCellNormalsOff()
    normalGenerator.AutoOrientNormalsOn()
    normalGenerator.ConsistencyOn()
    normalGenerator.SplittingOff()
    normalGenerator.Update()
    
    return normalGenerator.GetOutput()


'''
##########################################################################
    Read a surface and smoothens it.
    Returns: Smoeethened surface.
##########################################################################
'''
def smoothSurface(surfaceActor):
    smoother = vtk.vtkWindowedSincPolyDataFilter()
    #smoother.SetInputConnection(sphereSource->GetOutputPort())
    smoother.SetInputData(surfaceActor.GetMapper().GetInput())
    smoother.SetNumberOfIterations(10)
    smoother.BoundarySmoothingOff()
    smoother.FeatureEdgeSmoothingOff()
    smoother.SetFeatureAngle(120.0)
    smoother.SetPassBand(.001)
    smoother.NonManifoldSmoothingOn()
    smoother.NormalizeCoordinatesOn()
    smoother.Update()

    normalGenerator = vtk.vtkPolyDataNormals()
    normalGenerator.SetInputData(smoother.GetOutput())
    normalGenerator.ComputePointNormalsOn()
    normalGenerator.ComputeCellNormalsOff()
    normalGenerator.AutoOrientNormalsOn()
    normalGenerator.ConsistencyOn()
    normalGenerator.SplittingOff()
    normalGenerator.Update()

    mapper = vtk.vtkOpenGLPolyDataMapper()
    mapper.SetInputData(normalGenerator.GetOutput())
    #lesionActor = vtk.vtkActor()
    surfaceActor.SetMapper(mapper)


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
        firstHalfYValues = np.where(average == 0, float('nan'), firstHalfYValues)
        result = np.add(average, firstHalfYValues) #Doing y1+(y2-y1)/2
        #print(result)
        stackPlotMiddleLinesY[i] = result
        #quit()
        #print(vertexCount)
    return stackPlotMiddleLinesY

'''
##########################################################################
    Class for supporting zoom pan events in matplotlib graph
######
'''
class ZoomPan:
    def __init__(self):
        self.press = None
        self.cur_xlim = None
        self.cur_ylim = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xpress = None
        self.ypress = None


    def zoom_factory(self, ax, base_scale = 2.):
        def zoom(event):
            if event.button == 3: return  # Do not scroll if user is using right mouse button.
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()


            xdata = event.xdata # get event x location
            ydata = event.ydata # get event y location

            if event.button == 'down':
                # deal with zoom in
                scale_factor = 1 / base_scale
            elif event.button == 'up':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1
                #print(event.button)

            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

            relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])

            # Check if zoom out allowed.
            #newxlim = [xdata - new_width * (1-relx), xdata + new_width * (relx)]
            #newylim = [ydata - new_height * (1-rely), ydata + new_height * (rely)]
            #print(newxlim[0], newxlim[1])
            #skipXScale = False
            #skipYScale = False
            #if newxlim[0] < 0 or newxlim[0] > 80:  # If user is trying to zoom out too much. X values starts at 0. Anything less than that can be hidden.
            #    skipXScale = True
            #if newylim[0] < 0:
            #    skipYScale = True

            # if(skipXScale == False):
            #     ax.set_xlim([xdata - new_width * (1-relx), xdata + new_width * (relx)])
            #     ax.figure.canvas.draw()
            # if (skipYScale == False):
            #     ax.set_ylim([ydata - new_height * (1-rely), ydata + new_height * (rely)])
            #     ax.figure.canvas.draw()

            ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * (relx)])
            ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * (rely)])
            ax.figure.canvas.draw()

        fig = ax.get_figure() # get the figure of interest
        fig.canvas.mpl_connect('scroll_event', zoom)

        return zoom

    def pan_factory(self, ax):
        def onPress(event):
            if event.button == 3: return # Do not pan if user is using right mouse button.
            if event.inaxes != ax: return
            self.cur_xlim = ax.get_xlim()
            self.cur_ylim = ax.get_ylim()
            self.press = self.x0, self.y0, event.xdata, event.ydata
            self.x0, self.y0, self.xpress, self.ypress = self.press

        def onRelease(event):
            self.press = None
            ax.figure.canvas.draw()

        def onMotion(event):
            if self.press is None: return
            if event.inaxes != ax: return
            dx = event.xdata - self.xpress
            dy = event.ydata - self.ypress
            self.cur_xlim -= dx
            self.cur_ylim -= dy

            # Check if panning is going off limits
            if self.cur_xlim[0] < 0 or self.cur_xlim[1] > 80:
                return
            ax.set_xlim(self.cur_xlim)
            ax.set_ylim(self.cur_ylim)

            ax.figure.canvas.draw()

        fig = ax.get_figure() # get the figure of interest

        # attach the call back
        fig.canvas.mpl_connect('button_press_event',onPress)
        fig.canvas.mpl_connect('button_release_event',onRelease)
        fig.canvas.mpl_connect('motion_notify_event',onMotion)

        #return the function
        return onMotion



'''
##########################################################################
    Function for plotting VTK based node-graph
##########################################################################
'''
def drawNodeGraph(selfObject, graphPath, graph_layout_view, graphNodeColors):
    colors = vtk.vtkNamedColors()
    # Read data
    G = nx.read_gml(graphPath)
    #print(list(G.edges()))
    #print(G.nodes())
    # For scaling vertices or nodes.
    scales = vtk.vtkFloatArray()
    scales.SetNumberOfComponents(1)
    scales.SetName('Scales')

    vertex_labels = vtk.vtkStringArray()
    vertex_labels.SetName("VertexLabels")

    nodes = G.nodes()
    edges = list(G.edges())
    vtkGraph = vtk.vtkMutableDirectedGraph()
    vertices = [0] * len(nodes)

    # Create the color array for the vertices
    vertexColors = vtk.vtkIntArray()
    vertexColors.SetNumberOfComponents(1)
    vertexColors.SetName('VertexColors')

    # Create the color array for the edges.
    edgeColors = vtk.vtkIntArray()
    edgeColors.SetNumberOfComponents(1)
    edgeColors.SetName('EdgeColors')

    lookupTableVertices = vtk.vtkLookupTable()
    lookupTableVertices.SetNumberOfTableValues(len(nodes))
    for i in range(len(nodes)):
        clr = list(graphNodeColors[i])
        clr.append(1.0)  # A 4 element list is expected. last element is alpha
        lookupTableVertices.SetTableValue(i, clr)
    # lookupTableVertices.SetTableValue(1, colors.GetColor4d('Red'))
    # lookupTableVertices.SetTableValue(2, colors.GetColor4d('Green'))
    # lookupTableVertices.SetTableValue(3, colors.GetColor4d('Green'))
    # lookupTableVertices.SetTableValue(4, colors.GetColor4d('Green'))
    # lookupTableVertices.SetTableValue(5, colors.GetColor4d('Red'))
    # lookupTableVertices.SetTableValue(6, colors.GetColor4d('Green'))
    # lookupTableVertices.SetTableValue(7, colors.GetColor4d('Green'))
    # lookupTableVertices.SetTableValue(8, colors.GetColor4d('Green'))
    # lookupTableVertices.SetTableValue(9, colors.GetColor4d('Green'))
    lookupTableVertices.Build()

    lookupTableEdges = vtk.vtkLookupTable()
    lookupTableEdges.SetNumberOfTableValues(len(edges))

    for i in range(len(nodes)):
        vertices[i] = vtkGraph.AddVertex()  # Add vertex to the graph
        scales.InsertNextValue(3)
        vertex_labels.InsertValue(vertices[i], str(int(vertices[i]) + 1))  # Add label.
        vertexColors.InsertNextValue(i)

    for i in range(len(edges)):
        edgeColors.InsertNextValue(i)
        lookupTableEdges.SetTableValue(i, colors.GetColor4d('Gray'))

    lookupTableEdges.Build()

    # colorsArray = vtk.vtkUnsignedCharArray()
    # colorsArray.SetNumberOfComponents(3)
    # colorsArray.SetNumberOfTuples(len(edges))
    # colorsArray.SetName('EdgeColors')
    # for c in range(len(edges)):
    #     colorsArray.SetTuple(c, [255, 0, 0])

    for item in edges:
        vtkGraph.AddEdge(int(item[0]) - 1, int(item[1]) - 1)

    # Add the scale array to the graph
    vtkGraph.GetVertexData().AddArray(scales)

    # Add vertex labels to the graph
    vtkGraph.GetVertexData().AddArray(vertex_labels)

    # Add color data to vertices
    vtkGraph.GetVertexData().AddArray(vertexColors)

    # Add color array to edges
    vtkGraph.GetEdgeData().AddArray(edgeColors)

    #graph_layout_view = vtk.vtkGraphLayoutView()
    #graph_layout_view.SetRenderWindow(selfObject.vtkWidgetNodeGraph.GetRenderWindow())

    layout = vtk.vtkGraphLayout()
    strategy = vtk.vtkSimple2DLayoutStrategy()
    strategy.SetRestDistance(100.0)
    layout.SetInputData(vtkGraph)
    layout.SetLayoutStrategy(strategy)
    graph_layout_view.SetLayoutStrategyToPassThrough()
    graph_layout_view.SetEdgeLayoutStrategyToPassThrough()
    graph_layout_view.SetVertexLabelArrayName('VertexLabels')
    graph_layout_view.SetVertexColorArrayName("VertexColors")
    graph_layout_view.SetEdgeColorArrayName('EdgeColors')
    graph_layout_view.ColorVerticesOn()
    graph_layout_view.ColorEdgesOn()

    graph_layout_view.SetVertexLabelVisibility(True)
    graphToPoly = vtk.vtkGraphToPolyData()
    graphToPoly.SetInputConnection(layout.GetOutputPort())
    graphToPoly.EdgeGlyphOutputOn()
    graphToPoly.SetEdgeGlyphPosition(0.94)

    arrowSource = vtk.vtkGlyphSource2D()
    arrowSource.SetGlyphTypeToEdgeArrow()
    arrowSource.FilledOn()
    arrowSource.SetColor(255, 255.0, 0)
    arrowSource.SetScale(2)
    arrowSource.Update()

    # vertexCircleSource = vtk.vtkGlyphSource2D()
    # vertexCircleSource.SetGlyphTypeToCircle()
    # vertexCircleSource.FilledOn()
    # vertexCircleSource.SetScale(3)
    # vertexCircleSource.SetResolution(20)
    # vertexCircleSource.Update()

    arrowGlyph = vtk.vtkGlyph3D()
    arrowGlyph.SetColorModeToColorByScalar()
    arrowGlyph.SetScaleFactor(1)
    arrowGlyph.SetInputConnection(0, graphToPoly.GetOutputPort(1))
    arrowGlyph.SetInputConnection(1, arrowSource.GetOutputPort())

    arrowMapper = vtk.vtkPolyDataMapper()
    arrowMapper.SetInputConnection(arrowGlyph.GetOutputPort())
    arrowActor = vtk.vtkActor()
    arrowActor.SetMapper(arrowMapper)
    arrowActor.GetProperty().SetColor(0.5, 0.5, 0.5)

    # vertexGlyph = vtk.vtkGlyph3D()
    # vertexGlyph.SetColorModeToColorByScalar()
    # vertexGlyph.SetScaleFactor(4)
    #
    # vertexGlyph.SetInputConnection(0, graphToPoly.GetOutputPort(0))
    # vertexGlyph.SetInputConnection(1, vertexCircleSource.GetOutputPort())

    #vertexMapper = vtk.vtkPolyDataMapper()
    #vertexMapper.SetInputConnection(vertexGlyph.GetOutputPort())
    #vertexActor = vtk.vtkActor()
    #vertexActor.SetMapper(vertexMapper)
    #vertexActor.GetProperty().SetColor(0.0, 0.0, 0.0)

    graph_layout_view.AddRepresentationFromInputConnection(layout.GetOutputPort())
    #graph_layout_view.ScaledGlyphsOn()
    #graph_layout_view.SetScalingArrayName('Scales')

    textActorTitle = vtk.vtkTextActor()
    textActorTitle.UseBorderAlignOff()
    textActorTitle.SetDisplayPosition(10, 10)
    textActorTitle.GetTextProperty().SetFontFamily(4)
    textActorTitle.GetTextProperty().SetFontFile("asset\\arial.ttf")
    textActorTitle.GetTextProperty().SetFontSize(14)
    textActorTitle.GetTextProperty().SetColor(0.4, 0.4, 0.4)
    textActorTitle.SetInput("Lesion Activity Graph")

    rGraph = vtk.vtkRenderedGraphRepresentation()
    gGlyph = vtk.vtkGraphToGlyphs()
    rGraph.SafeDownCast(graph_layout_view.GetRepresentation()).SetGlyphType(gGlyph.CIRCLE)
    graph_layout_view.GetRenderer().AddActor(arrowActor)
    #graph_layout_view.GetRenderer().AddActor(vertexActor)
    graph_layout_view.GetRenderer().AddActor(textActorTitle)

    viewTheme = vtk.vtkViewTheme()
    viewTheme.SetLineWidth(3.0)
    viewTheme.SetOutlineColor(0.0, 0.0, 0.0)
    viewTheme.SetVertexLabelColor(0.0, 0.0, 0.0)
    viewTheme.SetPointLookupTable(lookupTableVertices)
    viewTheme.SetCellLookupTable(lookupTableEdges)
    viewTheme.SetVertexLabelColor(0, 0, 0)

    labelTextProperty = vtk.vtkTextProperty()
    labelTextProperty.SetColor(0.1, 0.1, 0.1)
    labelTextProperty.SetFontSize(14)
    labelTextProperty.ShadowOn()
    labelTextProperty.BoldOn()

    viewTheme.SetPointTextProperty(labelTextProperty)

    graph_layout_view.GetRepresentation().ApplyViewTheme(viewTheme)
    graph_layout_view.GetRepresentation().ScalingOn()
    graph_layout_view.GetRepresentation().SetScalingArrayName('Scales')

    # graph_layout_view.GetRenderer().AddActor(edgeActor)
    graph_layout_view.GetRenderer().SetBackground(colors.GetColor3d('White'))
    graph_layout_view.GetRenderer().SetBackground2(colors.GetColor3d('White'))
    graph_layout_view.SetEdgeColorArrayName("EdgeColors")

    graph_layout_view.GetRepresentation().GetAnnotationLink().AddObserver("AnnotationChangedEvent", selfObject.graphSelectionCallback)

    graph_layout_view.ResetCamera()
    selfObject.renNodeGraph.ResetCamera()
    #graph_layout_view.Render()
    #graph_layout_view.GetInteractor().Start()


'''
##########################################################################
    Capture a screenshot from renderers. File gets written with timestamp name.
    Returns: Nothing
##########################################################################
'''
def captureScreenshot(renderWindow):
    windowToImageFilter = vtk.vtkWindowToImageFilter()
    windowToImageFilter.SetInput(renderWindow)
    windowToImageFilter.SetScale(1,1)
    # windowToImageFilter.SetMagnification(3) #set the resolution of the output image (3 times the current resolution of vtk render window)
    windowToImageFilter.SetInputBufferTypeToRGBA()  # also record the alpha (transparency) channel
    windowToImageFilter.ReadFrontBufferOff()  # read from the back buffer
    windowToImageFilter.Update()

    if getattr(sys, 'frozen', False):
        dir_path = os.path.dirname(sys.executable)
    elif __file__:
        dir_path = os.path.dirname(__file__)

    # plt.figure(0)
    # curr_time = datetime.now()
    # timestr = curr_time.strftime('%H.%M.%S.%f')
    # fileName = dir_path + "\\captures\\MPR" + timestr + ".jpg"
    # plt.savefig(fileName)

    curr_time = datetime.now()
    timestr = curr_time.strftime('%H.%M.%S.%f')

    # fileName = dir_path + "\\captures\\" + timestr + ".png"
    # writer = vtk.vtkPNGWriter()
    # writer.SetFileName(fileName)
    # writer.SetInputConnection(windowToImageFilter.GetOutputPort())
    # writer.Write()

    timestr = "MS-LONG" + timestr
    fileName = dir_path + "\\captures\\" + timestr + ".jpg"
    print("filepath is", fileName)
    writer = vtk.vtkJPEGWriter()
    writer.SetFileName(fileName)
    writer.SetInputConnection(windowToImageFilter.GetOutputPort())
    writer.Write()