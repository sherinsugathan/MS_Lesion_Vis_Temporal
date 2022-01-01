from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5 import QtCore, QtGui
import vtk
import os
import glob
import math
import numpy as np
import networkx as nx
from vtkmodules.vtkCommonColor import vtkNamedColors

class ReadThread(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, folder_name, actorList, SurfacesList, keyType, keyID, parent=None):
        super(ReadThread, self).__init__(parent)
        self.read_folder_name = folder_name + "\\surfaces\\lesions\\"
        self.surfaceList = actorList
        self.surfaceActor = SurfacesList
        self.keyType = keyType
        self.keyID = keyID

    def run(self):
        self.actorList = []
        file_count = len(glob.glob1(self.read_folder_name, "*.vtm"))  # number of time points.
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

                    info = vtk.vtkInformation()
                    info.Set(self.keyType, "lesion")
                    info.Set(self.keyID, str(blockIndex))

                    actor = vtk.vtkActor()
                    actor.SetMapper(mapper)
                    actor.GetProperty().SetColor(0.6196078431372549, 0.7372549019607843, 0.8549019607843137)
                    # actor.GetProperty().SetColor(0.9411764705882353, 0.2313725490196078, 0.1254901960784314)
                    actor.GetProperty().SetInformation(info)
                    smoothSurface(actor)
                    actor.GetMapper().ScalarVisibilityOff()
                    mapper.Update()

                    self.surfaceList[i].append(actor)
            self.progress.emit(int((i / 80) * 100))
        # self.surfaceActor.append(self.loadSurfaces()) # Load ventricle mesh
        self.loadSurfaces()
        self.finished.emit()

    def loadSurfaces(self):
        # surfaceFileNames = ["ventricleMesh", "lh.white", "rh.white", "lh.pial", "rh.pial", "lh.inflated", "rh.inflated"]
        surfaceFileNames = ["ventricleMesh", "lh.white", "rh.white", "lh.inflated", "rh.inflated"]
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
            info.Set(self.keyID, str(fileName))  # does not matter

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            if (fileName == "ventricleMesh"):
                actor.GetProperty().SetColor(0.5607843137254902, 0.7058823529411765, 0.5725490196078431)  # green
            else:
                actor.GetProperty().SetColor(1.0, 1.0, 1.0)
            actor.GetProperty().SetInformation(info)
            self.surfaceActor.append(actor)
        return
        # self.ren.AddActor(actor)
        # self.ren.ResetCamera()
        # self.iren.Render()


'''
##########################################################################
    Class for implementing custom interactor for main VR with lesions in it.
##########################################################################
'''


class CustomMouseInteractorLesions(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, lesionvis, parent=None, iren=None):
        self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)
        self.AddObserver("LeftButtonReleaseEvent", self.leftButtonReleaseEvent)
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


    def leftButtonReleaseEvent(self, obj, event):
        if (self.MouseMotion == 0):
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
            # worldPosition = cellPicker.GetPickPosition()
            # print(cellPicker.GetPointId())

            # get the new
            self.NewPickedActor = picker.GetActor()
            #print("enter here 1")
            # If something was selected
            if self.NewPickedActor:
                #print("enter here 2")
                # If we picked something before, reset its property
                if self.LastPickedActor:
                    # self.LastPickedActor.GetMapper().ScalarVisibilityOn()
                    self.LastPickedActor.GetProperty().DeepCopy(self.LastPickedProperty)

                # Save the property of the picked actor so that we can
                # restore it next time
                self.LastPickedProperty.DeepCopy(self.NewPickedActor.GetProperty())

                itemType = self.NewPickedActor.GetProperty().GetInformation().Get(self.lesionvis.keyType)
                lesionID = self.NewPickedActor.GetProperty().GetInformation().Get(self.lesionvis.keyID)
                userPickedLesionID = int(lesionID) + 1
                self.lesionvis.updateContourComparisonView(userPickedLesionID)

                print(itemType, lesionID)


        self.OnLeftButtonUp()
        return

    def resetToDefaultViewLesions(self):
        if (self.LastPickedActor != None):
            # self.LastPickedActor.GetProperty().DeepCopy(self.LastPickedProperty)
            self.lesionvis.clearLesionHighlights()
            self.LastPickedActor = None
            self.lesionvis.textActorLesionStatistics.SetInput("")
        # self.lesionvis.ren.RemoveActor(self.textActorLesionStatistics) # Text overlay

    def mouseMoveEvent(self, obj, event):
        self.MouseMotion = 1
        self.OnMouseMove()
        return

    def leftButtonPressEvent(self, obj, event):
        self.MouseMotion = 0
        self.OnLeftButtonDown()


'''
##########################################################################
    Smooth polydata.
    Returns: Smoeethened surface.
##########################################################################
'''


def smoothPolyData(polyData):
    smoother = vtk.vtkWindowedSincPolyDataFilter()
    # smoother.SetInputConnection(sphereSource->GetOutputPort())
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
    # smoother.SetInputConnection(sphereSource->GetOutputPort())
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
    # lesionActor = vtk.vtkActor()
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
        vertexCount = int(math.ceil(len(vertexList) / 2))  # only half (+x direction) is processed.
        firstHalf = vertexList[
                    1:vertexCount - 1]  # vertices in the forward direction. (first item (starting from 1:) removed)
        # secondHalf = np.flip(vertexList[vertexCount:-1]) # vertices in the reverse direction. (last item (ending at :-2) removed)
        secondHalf = np.flip(
            vertexList[vertexCount:-1])  # vertices in the reverse direction. (last item (ending at :-2) removed)
        # print(firstHalf)
        # print("Hellow")
        # print(secondHalf)
        firstHalfYValues = [y for x, y in firstHalf]
        secondHalfYValues = [x for x, y in secondHalf]
        # print(firstHalfYValues)
        # print("Done")
        # print(secondHalfYValues)

        # print(firstHalfYValues)
        average = np.true_divide(np.subtract(secondHalfYValues, firstHalfYValues), 2)
        # includeInSum = average!=0
        # print(includeInSum)
        firstHalfYValues = np.where(average == 0, float('nan'), firstHalfYValues)
        result = np.add(average, firstHalfYValues)  # Doing y1+(y2-y1)/2
        # print(result)
        stackPlotMiddleLinesY[i] = result
        # quit()
        # print(vertexCount)
    return stackPlotMiddleLinesY




