import sys
import os
import vtk
import glob
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QCheckBox, QButtonGroup, QAbstractButton
from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSlot
from PyQt5 import Qt
from PyQt5.QtCore import QTimer
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import Utils
from vtk.util import keys
import networkx as nx
from networkx.algorithms.components.connected import connected_components

class mainWindow(Qt.QMainWindow):
    """Main window class."""

    def __init__(self, *args):
        """Init."""
        super(mainWindow, self).__init__(*args)
        ui = os.path.join(os.path.dirname(__file__), 'mainui.ui')
        uic.loadUi(ui, self)
        vtk.vtkObject.GlobalWarningDisplayOff()  # Supress warnings.
        self.ren1 = vtk.vtkRenderer()
        self.ren2 = vtk.vtkRenderer()
        self.ren3 = vtk.vtkRenderer()
        self.ren4 = vtk.vtkRenderer()
        self.ren5 = vtk.vtkRenderer()
        self.keyType = None
        self.keyID = None
        self.G = None
        self.dataCount = 81
        self.lesionTemporalTileCount = 5

    def setupUI(self):
        print("Starting application")
        # Data Paths
        self.rootPath = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\"
        self.graphPath = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\preProcess\\lesionGraph.gml"
        self.lesionsFolder = self.rootPath + "surfaces\\lesions\\"
        self.ventriclePath = self.rootPath + "surfaces\\ventricleMesh.obj"
        self.lesionActorList = [[] for i in range(81)]
        self.load_data()
        # Renderer for lesions.
        self.vl = Qt.QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frameVTKMain)
        self.vl.addWidget(self.vtkWidget)
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(1.0,1.0,1.0)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.iren.SetRenderWindow(self.vtkWidget.GetRenderWindow())
        self.ren.ResetCamera()
        self.frameVTKMain.setLayout(self.vl)
        self.style = Utils.CustomMouseInteractorLesions(self)
        self.style.SetDefaultRenderer(self.ren)
        self.style.main = self
        self.iren.SetInteractorStyle(self.style)
        #self.show()
        self.iren.Initialize()

        # Renderer for picked lesions.
        self.vlLesions = Qt.QVBoxLayout()
        self.vtkWidgetLesions = QVTKRenderWindowInteractor(self.frameLesions)
        self.vlLesions.addWidget(self.vtkWidgetLesions)
        #self.renLesions = vtk.vtkRenderer()
        #self.renLesions.SetBackground(1.0,1.0,0.0)
        self.renWinLesions = self.vtkWidgetLesions.GetRenderWindow()
        #self.renWinLesions.AddRenderer(self.renLesions)
        self.irenLesions = self.vtkWidgetLesions.GetRenderWindow().GetInteractor()

        self.irenLesions.SetRenderWindow(self.renWinLesions)

        #self.renLesions.ResetCamera()
        self.frameLesions.setLayout(self.vlLesions)

        self.setviewports()
        self.irenLesions.Initialize()
        self.irenLesions.Render()

        # Handlers
        self.pushButtonStart.clicked.connect(self.onStartClick)  # Start button
        self.horizontalSliderTime.valueChanged.connect(self.horizontalSliderTimeChanged)  # Slider

    def readLesionTrackingData(self):
        print("Reading lesion tracking data")
        self.G = nx.read_gml("D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\preProcess\\lesionGraph.gml")

    def updateContourComparisonView(self, pickedLesionID):
        print("picked lesion id is ", pickedLesionID)
        currentTimeIndex = self.horizontalSliderTime.value()
        #if currentTimeIndex + 2 > self.dataCount or currentTimeIndex - 2 < 0:  # Ignore rendering some cells because full data not available for left and right time points.
        #    pass
        #    print("ignore cells")
        #else:  # Full data available for left and right time points.
        linkedLesionIds = self.getLinkedLesionIDFromLeftAndRight(pickedLesionID, currentTimeIndex)

            # for i in range(-2, 3):
            #     lesionID = self.getLinkedLesionIDFromTimeStep(pickedLesionID, currentTimeIndex-i)
            #     lesionIDs.append(lesionID-1)

        #print("New lesion ids are", lesionIDs)

        print("Lesion IDs are", linkedLesionIds)
        # sphereSource = vtk.vtkSphereSource()
        # sphereSource.SetCenter(0.0, 0.0, 0.0)
        # sphereSource.SetRadius(5.0)
        # # Make the surface smooth.
        # sphereSource.SetPhiResolution(5)
        # sphereSource.SetThetaResolution(5)
        #
        # mapper = vtk.vtkPolyDataMapper()
        # mapper.SetInputConnection(sphereSource.GetOutputPort())
        #
        # actor = vtk.vtkActor()
        # actor.SetMapper(mapper)

        lesionSurfaceArray = []
        rendererArray = []

        rendererCollection = self.renWinLesions.GetRenderers()
        currentTimeRenderer = rendererCollection.GetItemAsObject(2) # The middle renderer. the present one.

        print("Renderer count is", rendererCollection.GetNumberOfItems())
        for idIndex in range(rendererCollection.GetNumberOfItems()):
            renderer = rendererCollection.GetItemAsObject(idIndex)
            renderer.RemoveAllViewProps()
            if linkedLesionIds[idIndex] is None:
                renderer.RemoveAllViewProps()
                continue
            else:  # Add valid lesion to renderer.
                for lesion in self.lesionActorList[currentTimeIndex-2+idIndex]:
                    lesionID = int(lesion.GetProperty().GetInformation().Get(self.keyID))
                    if lesionID == linkedLesionIds[idIndex]-1:
                        renderer.AddActor(lesion)
                renderer.ResetCamera()
            #if idIndex > 0:
            renderer.SetActiveCamera(currentTimeRenderer.GetActiveCamera())

        self.irenLesions.Render()

    # Get lesion ID of any timestep provided the current ID and timestep.
    def getLinkedLesionIDFromTimeStep(self, currentLesionID, queryTimeStep=None):
        #print("called me")
        currentTimeStep = self.horizontalSliderTime.value()
        if(queryTimeStep == None):
            queryTimeStep = self.horizontalSlider_TimePoint.value()
        nodeIDList = list(self.G.nodes)
        print("Node list is", nodeIDList)
        for id in nodeIDList:
            timeList = self.G.nodes[id]["time"]
            labelList = self.G.nodes[id]["lesionLabel"]
            print(labelList)
            #print("Entering here", id)
            #print(timeList)
            #print(labelList)
            temporalData = list(zip(timeList, labelList))
            if((currentTimeStep, currentLesionID) in list(temporalData)):
                result = [elem[1] for elem in temporalData if elem[0]==queryTimeStep]
                if(len(result)!=0):
                    return result[0]
        return None


    # Given lesion ID and current time step, extract n number of lesion IDs from left and right
    def getLinkedLesionIDFromLeftAndRight(self, currentLesionID, currentTimeIndex):
        nodeIDList = list(self.G.nodes)
        linkedLesionIds = [None] * 5
        for id in nodeIDList:
            timeList = self.G.nodes[id]["time"]
            labelList = self.G.nodes[id]["lesionLabel"]
            temporalData = list(zip(timeList, labelList))
            temporalDataListLength = len(temporalData)
            if ((currentTimeIndex, currentLesionID) in list(temporalData)):
                itemIndex = temporalData.index((currentTimeIndex, currentLesionID))
                print("printing temporal data", temporalData)
            else:
                continue
            # for i in range(-2, 3):
            #     print("entere here 2")
            #     linkedLesionIds.append(temporalData[itemIndex - i][1]-1) # minus one to adjust lesion number
            if itemIndex == temporalDataListLength-1:
                linkedLesionIds[2] = temporalData[itemIndex][1]
            if (itemIndex + 2) < temporalDataListLength:  # Check overflow towards right
                linkedLesionIds[2] = temporalData[itemIndex][1]
                linkedLesionIds[3] = temporalData[itemIndex+1][1]
                linkedLesionIds[4] = temporalData[itemIndex+2][1]
            if (itemIndex - 2) >= 0:
                linkedLesionIds[0] = temporalData[itemIndex-2][1]
                linkedLesionIds[1] = temporalData[itemIndex-1][1]

            return linkedLesionIds   # Success
        return None  # Failure

    # Initialize lesion viewports
    def setviewports(self):
        # Define viewport ranges
        t1 = [0, 0, 0.2, 1]
        t2 = [0.2, 0, 0.4, 1]
        t3 = [0.4, 0, 0.6, 1]
        t4 = [0.6, 0, 0.8, 1]
        t5 = [0.8, 0, 1.0, 1]
        viewports = [t1, t2, t3, t4, t5]

        #self.lesionRenderers = []

        self.ren1.SetBackground(1.0, 1.0, 1.0)
        self.ren2.SetBackground(0.98, 0.98, 0.98)
        self.ren3.SetBackground(1.0, 1.0, 1.0)
        self.ren4.SetBackground(0.98, 0.98, 0.98)
        self.ren5.SetBackground(1.0, 1.0, 1.0)

        self.ren1.SetViewport(viewports[0][0], viewports[0][1], viewports[0][2], viewports[0][3])
        self.ren2.SetViewport(viewports[1][0], viewports[1][1], viewports[1][2], viewports[1][3])
        self.ren3.SetViewport(viewports[2][0], viewports[2][1], viewports[2][2], viewports[2][3])
        self.ren4.SetViewport(viewports[3][0], viewports[3][1], viewports[3][2], viewports[3][3])
        self.ren5.SetViewport(viewports[4][0], viewports[4][1], viewports[4][2], viewports[4][3])

        self.renWinLesions.AddRenderer(self.ren1)
        self.renWinLesions.AddRenderer(self.ren2)
        self.renWinLesions.AddRenderer(self.ren3)
        self.renWinLesions.AddRenderer(self.ren4)
        self.renWinLesions.AddRenderer(self.ren5)

        # # # Display essentials
        # for i in range(5):
        #     ren = vtk.vtkRenderer()
        #     self.renWinLesions.AddRenderer(ren)
        #     ren.SetViewport(viewports[i][0], viewports[i][1], viewports[i][2], viewports[i][3])
        #     if(i%2==0):
        #         ren.SetBackground(1.0, 0, 0)
        #         print("even")
        #     else:
        #         ren.SetBackground(0.0, 0, 1.0)
        #         print("odd")
        #     ren.ResetCamera()
        #     #iren.Render()
        #     self.lesionRenderers.append(ren)

    @pyqtSlot()
    def onStartClick(self):
        # Load baseline data
        actors = self.lesionActorList[0]
        for actor in actors:
            self.ren.AddActor(actor)
        self.ren.ResetCamera()
        self.iren.Render()

        # Read lesion tracking data
        self.readLesionTrackingData()

    # Handler for time slider changed
    @pyqtSlot()
    def horizontalSliderTimeChanged(self):
        self.ren.RemoveAllViewProps()
        sliderValue = self.horizontalSliderTime.value()
        self.labelTimeIndex.setText(str(sliderValue))
        # Load baseline data
        actors = self.lesionActorList[int(sliderValue)]
        for actor in actors:
            self.ren.AddActor(actor)
        self.iren.Render()

    def load_data(self):
        self.keyType = vtk.vtkInformationStringKey.MakeKey("type", "root")
        self.keyID = vtk.vtkInformationStringKey.MakeKey("ID", "vtkActor")
        file_count = len(glob.glob1(self.lesionsFolder, "*.vtm"))  # number of time points.
        for i in range(file_count):
            print("Loading ", i)
            lesionSurfaceDataFilePath = self.lesionsFolder + "lesions" + str(i) + ".vtm"
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
                    # smoothSurface(actor)
                    actor.GetMapper().ScalarVisibilityOff()
                    mapper.Update()

                    self.lesionActorList[i].append(actor)

app = Qt.QApplication(sys.argv)
window = mainWindow()
window.setupUI()
window.resize(1100,700)
window.show()
#window.showMaximized()
sys.exit(app.exec_())