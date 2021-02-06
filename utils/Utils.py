from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5 import QtCore, QtGui
import vtk

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

                    info = vtk.vtkInformation()
                    info.Set(self.keyType, "lesion")
                    info.Set(self.keyID, str(blockIndex))

                    actor = vtk.vtkActor()
                    actor.SetMapper(mapper)
                    actor.GetProperty().SetColor(0.9, 0.3, 0.4)
                    actor.GetProperty().SetInformation(info)
                    smoothSurface(actor)
                    actor.GetMapper().ScalarVisibilityOff()
                    mapper.Update()

                    self.surfaceList[i].append(actor)
            self.progress.emit(int((i/80)*100))
        #self.surfaceActor.append(self.loadSurfaces()) # Load ventricle mesh
        self.loadSurfaces()
        self.finished.emit()

    def loadSurfaces(self):
        surfaceFileNames = ["ventricleMesh", "lh.white", "rh.white", "lh.pial", "rh.pial", "lh.inflated", "rh.inflated"]
        for fileName in surfaceFileNames:
            loadPath = self.read_folder_name + "..\\" + fileName + ".obj"
            reader = vtk.vtkOBJReader()
            reader.SetFileName(loadPath)
            reader.Update()
            mapper = vtk.vtkOpenGLPolyDataMapper()
            mapper.SetInputConnection(reader.GetOutputPort())

            info = vtk.vtkInformation()
            info.Set(self.keyType, fileName)
            info.Set(self.keyID, str(0)) # does not matter

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(0.545,0.7411,0.545)
            actor.GetProperty().SetInformation(info)
            self.surfaceActor.append(actor)
        return
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
        self.lesionvis = lesionvis
        self.LastPickedActor = None
        self.NewPickedActor = None
        self.clickedLesionActor = None
        self.LastPickedProperty = vtk.vtkProperty()
        self.iren = iren
        self.MouseMotion = 0
        self.informationKeyType = vtk.vtkInformationStringKey.MakeKey("type", "vtkActor")
        self.informationKeyID = vtk.vtkInformationStringKey.MakeKey("ID", "vtkActor")

    # Set lesion data to overlay text and display overlay.
    def mapLesionToText(self, lesionID, NewPickedActor):
        self.clickedLesionActor = self.NewPickedActor
        # if(self.vtkWidget.GetRenderWindow().HasRenderer(self.renMapOutcome) == True):
        #     self.vtkWidget.GetRenderWindow().RemoveRenderer(self.renMapOutcome)
        # Highlight the picked actor by changing its properties
        self.NewPickedActor.GetMapper().ScalarVisibilityOff()
        self.NewPickedActor.GetProperty().SetColor(0.4627, 0.4627, 0.9568) # A blueish color.
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
        followUpIndex = self.lesionvis.horizontalSlider_TimePoint.value()

        # SAMPLE structureInfo[str(followUpIndex)][0][str(lesionID+1)][0]['Elongation']
        self.lesionvis.overlayDataMain["Lesion ID"] = str(lesionID)
        self.lesionvis.overlayDataMain["Centroid"] = str("{0:.2f}".format(self.lesionvis.structureInfo[str(followUpIndex)][0][str(lesionID+1)][0]['Centroid'][0])) +", " +  str("{0:.2f}".format(self.lesionvis.structureInfo[str(followUpIndex)][0][str(lesionID+1)][0]['Centroid'][0])) + ", " + str("{0:.2f}".format(self.lesionvis.structureInfo[str(followUpIndex)][0][str(lesionID+1)][0]['Centroid'][0]))
        self.lesionvis.overlayDataMain["Voxel Count"] = self.lesionvis.structureInfo[str(followUpIndex)][0][str(lesionID+1)][0]['NumberOfPixels']
        self.lesionvis.overlayDataMain["Elongation"] = "{0:.2f}".format(self.lesionvis.structureInfo[str(followUpIndex)][0][str(lesionID+1)][0]['Elongation'])
        self.lesionvis.overlayDataMain["Lesion Perimeter"] = "{0:.2f}".format(self.lesionvis.structureInfo[str(followUpIndex)][0][str(lesionID+1)][0]['Perimeter'])
        self.lesionvis.overlayDataMain["Lesion Spherical Radius"] = "{0:.2f}".format(self.lesionvis.structureInfo[str(followUpIndex)][0][str(lesionID+1)][0]['SphericalRadius'])
        self.lesionvis.overlayDataMain["Lesion Spherical Perimeter"] = "{0:.2f}".format(self.lesionvis.structureInfo[str(followUpIndex)][0][str(lesionID+1)][0]['SphericalPerimeter'])
        self.lesionvis.overlayDataMain["Lesion Flatness"] = "{0:.2f}".format(self.lesionvis.structureInfo[str(followUpIndex)][0][str(lesionID+1)][0]['Flatness'])
        self.lesionvis.overlayDataMain["Lesion Roundness"] = "{0:.2f}".format(self.lesionvis.structureInfo[str(followUpIndex)][0][str(lesionID+1)][0]['Roundness'])

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
                    #self.LastPickedActor.GetMapper().ScalarVisibilityOn()
                    self.LastPickedActor.GetProperty().DeepCopy(self.LastPickedProperty)
                
                # Save the property of the picked actor so that we can
                # restore it next time
                self.LastPickedProperty.DeepCopy(self.NewPickedActor.GetProperty())

                itemType = self.NewPickedActor.GetProperty().GetInformation().Get(self.lesionvis.keyType)
                lesionID = self.NewPickedActor.GetProperty().GetInformation().Get(self.lesionvis.keyID)

                if(lesionID != None): # lesion picked.
                    self.mapLesionToText(lesionID, self.NewPickedActor)

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