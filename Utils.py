from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5 import QtCore, QtGui
import vtk

class ReadThread(QObject): 
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    def __init__(self, folder_name, actorList, SurfacesList, parent=None): 
        super(ReadThread, self).__init__(parent) 
        self.read_folder_name = folder_name + "\\surfaces\\lesions\\"
        self.surfaceList = actorList
        self.surfaceActor = SurfacesList
        
    def run(self):
        self.actorList = []
        for i in range(81):
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
                    actor = vtk.vtkActor()
                    actor.SetMapper(mapper)
                    actor.GetProperty().SetColor(0.9, 0.3, 0.4)
                    smoothSurface(actor)
                    actor.GetMapper().ScalarVisibilityOff()
                    mapper.Update()
                    self.surfaceList[i].append(actor)
            self.progress.emit(int((i/80)*100))
        self.surfaceActor.append(self.loadSurfaces()) # Load ventricle mesh
        self.finished.emit()

    def loadSurfaces(self):
        loadPath = self.read_folder_name + "..\\ventricleMesh.obj"
        reader = vtk.vtkOBJReader()
        reader.SetFileName(loadPath)
        reader.Update()
        mapper = vtk.vtkOpenGLPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.545,0.7411,0.545)
        return actor
        #self.ren.AddActor(actor)
        #self.ren.ResetCamera()
        #self.iren.Render()

'''
##########################################################################
    Class for implementing custom interactor for main VR.
##########################################################################
'''
class CustomMouseInteractor(vtk.vtkInteractorStyleTrackballCamera):
    
    def __init__(self,lesionvis,parent=None,iren=None):
        self.AddObserver("LeftButtonPressEvent",self.leftButtonPressEvent)
        self.AddObserver("LeftButtonReleaseEvent",self.leftButtonReleaseEvent)
        self.AddObserver("MouseMoveEvent", self.mouseMoveEvent)
        self.AddObserver("RightButtonPressEvent", self.RightButtonPressEvent)
        self.lesionvis = lesionvis
        self.LastPickedActor = None
        self.NewPickedActor = None
        self.clickedLesionActor = None
        self.LastPickedProperty = vtk.vtkProperty()
        self.iren = iren
        self.MouseMotion = 0

    def leftButtonReleaseEvent(self,obj,event):
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
                    self.LastPickedActor.GetMapper().ScalarVisibilityOn()
                    self.LastPickedActor.GetProperty().DeepCopy(self.LastPickedProperty)
                
                # Save the property of the picked actor so that we can
                # restore it next time
                self.LastPickedProperty.DeepCopy(self.NewPickedActor.GetProperty())

                #itemType = self.NewPickedActor.GetProperty().GetInformation().Get(self.informationKey)
                #lesionID = self.NewPickedActor.GetProperty().GetInformation().Get(self.informationKeyID)

                #self.iren.Render()
                # save the last picked actor
                self.LastPickedActor = self.NewPickedActor
            else: # no actor picked. Clicked on background.
                #self.resetToDefaultViewLesions()
                pass

        self.OnLeftButtonUp()
        return

    def mouseMoveEvent(self,obj,event):
        self.MouseMotion = 1
        self.OnMouseMove()
        return

    def RightButtonPressEvent(self,obj,event):
        print("Hi Sherin")

    def leftButtonPressEvent(self,obj,event):
        self.MouseMotion = 0
        self.OnLeftButtonDown()

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