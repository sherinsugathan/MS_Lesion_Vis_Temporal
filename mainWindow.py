###################################
# MUSCLEVIS LONGITUDINAL 
# Author: Sherin Sugathan
# Last Modified Date: 6th Jan 2021
###################################
# from PyQt5 import QtWidgets, uic
# from PyQt5.QtWidgets import QFileDialog, QCheckBox, QButtonGroup, QAbstractButton, QMessageBox, QDialog
# from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal, QUrl, QObject
# from PyQt5.QtWebEngineWidgets import  QWebEngineView,QWebEnginePage
# from PyQt5.QtWebEngineWidgets import QWebEngineSettings
# from PyQt5.QtWebChannel import QWebChannel
# from PyQt5 import QtCore, QtGui
# from PyQt5 import Qt
# from PyQt5.QtCore import QTimer

import vtk
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QCheckBox, QButtonGroup, QAbstractButton
from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5 import QtCore, QtGui
from PyQt5 import Qt
from PyQt5.QtCore import QTimer
#from OpenGL import GL

# Pyinstaller exe requirements
#import pkg_resources.py2_warn
import vtkmodules
import vtkmodules.all
import vtkmodules.qt.QVTKRenderWindowInteractor
import vtkmodules.util
import vtkmodules.util.numpy_support

import sys
import os
from utils import Utils
import numpy as np
import numpy.ma as ma
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import networkx as nx
from networkx.algorithms.components.connected import connected_components
from matplotlib import colors
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.patches as mpatches
import matplotlib.cm as cm
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import nibabel as nib
import json
import random
import pickle
from scipy.ndimage.filters import gaussian_filter1d
import seaborn as sns
import SimpleITK as sitk
from qt_range_slider import QtRangeSlider
import matplotlib.colors as mc
import colorsys
from matplotlib import font_manager # Add custom font without installing it.
from matplotlib.ticker import AutoMinorLocator
from numpy import diff
import math
import keyboard as kb
import itertools
import msvcrt

# Main window class.
class mainWindow(Qt.QMainWindow):
    # Initialization
    def __init__(self):
        super(mainWindow, self).__init__()
        self.intensityImage = None
        # font_dirs = [os.path.dirname(os.path.realpath(__file__))+"\\asset\\fonts"]
        # font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
        # for font_file in font_files:
        #     #print(font_file)
        #     #font_manager.fontManager.addfont(font_file)
        #     QtGui.QFontDatabase.addApplicationFont(font_file)

        #self.setFont(QtGui.QFont("Roboto Black", 20))
        #self.fontFamily = 'Roboto Black'
        #self.fontColor = 'black'
        #self.fontSize = '12'
        self.ren1 = vtk.vtkRenderer()
        self.ren2 = vtk.vtkRenderer()
        self.ren3 = vtk.vtkRenderer()
        self.ren4 = vtk.vtkRenderer()
        self.ren5 = vtk.vtkRenderer()

        # Load UI file.
        uic.loadUi("asset\\mstemporal_uifile.ui", self)

        self.initUI()
        self.initVTK()
        self.showMaximized()

        # self.slider = QtRangeSlider(self, 0, 80, 0, 80)
        # self.slider3DCompare = QtRangeSlider(self, 0, 80, 0, 80)
        # self.gridLayout_14.addWidget(self.slider, 0,9)
        #self.gridLayout_16.addWidget(self.slider3DCompare,0,0)
        # self.slider.left_thumb_value_changed.connect(self.graphRangeSliderChanged)
        # self.slider3DCompare.left_thumb_value_changed.connect(self.compare3DRangeSliderChangedLeft)
        # self.slider3DCompare.right_thumb_value_changed.connect(self.compare3DRangeSliderChangedRight)
        # self.slider3DCompare.setEnabled(False)

        # font_dirs = [os.path.dirname(os.path.realpath(__file__))+"\\asset\\GoogleSans"]
        # font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
        # for font_file in font_files:
        #     print(font_file)
        #     font_manager.fontManager.addfont(font_file)



    def showDialog(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Loading Data...Please wait...")
        msgBox.setStyleSheet("background-color: rgb(46,46,46); color:rgb(200,200,200); font: 10pt 'Open Sans';")
        msgBox.setEscapeButton(None)
        msgBox.exec()
        dlg = QDialog(self)
        dlg.setWindowTitle("HELLO!")
        dlg.exec_()

    # UI setup.
    def initUI(self):
        #self.setStyleSheet('font-family: %s; color: %s; background-color: rgb(28,33,39);' % (self.fontFamily, self.fontColor))
        vtk.vtkObject.GlobalWarningDisplayOff() # Supress warnings.
        #print("\033[1;101m STARTING APPLICATION... \033[0m")
        #pmMain = Qt.QPixmap("icons\\AppLogo.png")
        #self.logoLabel.setPixmap(pmMain.scaled(self.logoLabel.size().width(), self.logoLabel.size().height(), 1,1))
        #self.showDialog()
        self.comboBox_LesionAttributes.addItem("Physical Size")
        self.comboBox_LesionAttributes.addItem("Elongation")
        self.comboBox_LesionAttributes.addItem("Perimeter")
        self.comboBox_LesionAttributes.addItem("Spherical Radius")
        self.comboBox_LesionAttributes.addItem("Spherical Perimeter")
        self.comboBox_LesionAttributes.addItem("Flatness")
        self.comboBox_LesionAttributes.addItem("Roundness")

        self.comboBox_ProjectionMethods.addItem("DTI")
        self.comboBox_ProjectionMethods.addItem("Heat Equation")
        self.comboBox_ProjectionMethods.addItem("Danielsson")

        # Constants
        self.NAWM_INTENSITY_T1 = 215
        self.NAWM_INTENSITY_T2 = 58
        self.R_ISO = 0.1

        # Handlers
        #self.pushButton_LoadFolder.clicked.connect(self.on_click_browseFolder) # Attaching button click handler.
        self.pushButton_LoadFolder.clicked.connect(self.autoLoadData) # Attaching button click handler.
        self.pushButton_Compare.clicked.connect(self.compareDataAndUpdateSurface) # Attaching button click handler.
        #self.pushButton_IntensityAnalysis.clicked.connect(self.loadIntensityAnalysisPage) # Attaching button click handler for intensity analysis page.
        self.horizontalSlider_TimePoint.valueChanged.connect(self.on_sliderChangedTimePoint) # Attaching slider value changed handler.
        self.horizontalSlider_Riso.valueChanged.connect(self.on_sliderChangedRiso) # Attaching slider value (Riso) changed handler.
        self.comboBox_LesionAttributes.currentTextChanged.connect(self.on_combobox_changed_LesionAttributes) # Attaching handler for lesion filter combobox selection change.
        self.comboBox_ProjectionMethods.currentTextChanged.connect(self.on_combobox_changed_ProjectionMethods) # Attaching handler for projection methods combobox selection change.
        self.checkBox_ShowClasses.stateChanged.connect(self.checkBox_ShowClasses_changed) # Display lesion classes in the intensity graph.
        self.checkBox_RangeCompare.stateChanged.connect(self.checkBox_RangeCompare_changed) # Enables comparison view for lesions.
        self.pushButton_Capture.clicked.connect(self.on_click_CaptureScreeshot)  # Attaching button click Handlers
        self.spinBox_RangeMin.valueChanged.connect(self.spinBoxMinChanged)
        self.spinBox_RangeMax.valueChanged.connect(self.spinBoxMaxChanged)

    # Initialize vtk
    def initVTK(self):
        self.dataFolderInitialized = False
        # Renderer for lesions.
        self.vl = Qt.QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(1.0,1.0,1.0)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.iren.SetRenderWindow(self.vtkWidget.GetRenderWindow())
        self.ren.ResetCamera()
        self.frame.setLayout(self.vl)
        self.style = Utils.CustomMouseInteractorLesions(self)
        self.style.SetDefaultRenderer(self.ren)
        self.style.main = self
        self.iren.SetInteractorStyle(self.style)
        self.readThread = None
        self.show()
        self.iren.Initialize()

        # Brain surface 3D
        # Viewport definition
        xmins = [0, 0, 0.2, 0.4, 0.6, 0.8]
        xmaxs = [1, 0.2, 0.4, 0.6, 0.8, 1]
        ymins = [0.3, 0, 0, 0, 0, 0]
        ymaxs = [1, 0.3, 0.3, 0.3, 0.3, 0.3]

        colorsLesionRenderers = vtk.vtkNamedColors()
        # colors for renderers
        ren_bkg = ['WhiteSmoke', 'WhiteSmoke', 'GhostWhite', 'Seashell', 'GhostWhite', 'WhiteSmoke']

        self.vlDual = Qt.QVBoxLayout()
        self.vtkWidgetDual = QVTKRenderWindowInteractor(self.frameDual)
        self.vlDual.addWidget(self.vtkWidgetDual)
        self.renDual = vtk.vtkRenderer()
        self.renDual.SetBackground(1.0, 1.0, 1.0)
        self.ren1.SetBackground(colorsLesionRenderers.GetColor3d(ren_bkg[1]))
        self.ren2.SetBackground(colorsLesionRenderers.GetColor3d(ren_bkg[2]))
        self.ren3.SetBackground(colorsLesionRenderers.GetColor3d(ren_bkg[3]))
        self.ren4.SetBackground(colorsLesionRenderers.GetColor3d(ren_bkg[4]))
        self.ren5.SetBackground(colorsLesionRenderers.GetColor3d(ren_bkg[5]))

        self.vtkWidgetDual.GetRenderWindow().AddRenderer(self.renDual)
        self.vtkWidgetDual.GetRenderWindow().AddRenderer(self.ren1)
        self.vtkWidgetDual.GetRenderWindow().AddRenderer(self.ren2)
        self.vtkWidgetDual.GetRenderWindow().AddRenderer(self.ren3)
        self.vtkWidgetDual.GetRenderWindow().AddRenderer(self.ren4)
        self.vtkWidgetDual.GetRenderWindow().AddRenderer(self.ren5)

        self.renDual.SetViewport(xmins[0], ymins[0], xmaxs[0], ymaxs[0])
        self.ren1.SetViewport(xmins[1], ymins[1], xmaxs[1], ymaxs[1])
        self.ren2.SetViewport(xmins[2], ymins[2], xmaxs[2], ymaxs[2])
        self.ren3.SetViewport(xmins[3], ymins[3], xmaxs[3], ymaxs[3])
        self.ren4.SetViewport(xmins[4], ymins[4], xmaxs[4], ymaxs[4])
        self.ren5.SetViewport(xmins[5], ymins[5], xmaxs[5], ymaxs[5])

        self.irenDual = self.vtkWidgetDual.GetRenderWindow().GetInteractor()
        self.irenDual.SetRenderWindow(self.vtkWidgetDual.GetRenderWindow())
        self.renDual.ResetCamera()
        self.frameDual.setLayout(self.vlDual)
        #self.styleSurface = Utils.CustomMouseInteractorSurface(self)
        self.actor_style = vtk.vtkInteractorStyleTrackballCamera()
        #self.styleSurface.SetDefaultRenderer(self.renDual)
        #self.styleSurface.main = self
        #self.irenDual.SetInteractorStyle(self.styleSurface)
        self.irenDual.SetInteractorStyle(self.actor_style)
        self.irenDual.Initialize()

        self.vl_MPRA = Qt.QVBoxLayout()
        self.vl_MPRB = Qt.QVBoxLayout()
        self.vl_MPRC = Qt.QVBoxLayout()
        self.figureMPRA = plt.figure(num = 0, frameon=False, clear=True)
        self.figureMPRA.subplots_adjust(bottom=0, top=1, left=0, right=1)
        self.figureMPRB = plt.figure(num = 1, frameon=False, clear=True)
        self.figureMPRB.subplots_adjust(bottom=0, top=1, left=0, right=1)
        self.figureMPRC = plt.figure(num = 2, frameon=False, clear=True)
        self.figureMPRC.subplots_adjust(bottom=0, top=1, left=0, right=1)
        self.canvasMPRA = FigureCanvas(self.figureMPRA)
        self.canvasMPRB = FigureCanvas(self.figureMPRB)
        self.canvasMPRC = FigureCanvas(self.figureMPRC)
        self.vl_MPRA.addWidget(self.canvasMPRA)
        self.vl_MPRB.addWidget(self.canvasMPRB)
        self.vl_MPRC.addWidget(self.canvasMPRC)
        self.dtiDataActive = True
        self.MPROverlayColorMap = colors.ListedColormap(['blue', 'blue'])
        self.frame_MPRA.setLayout(self.vl_MPRA)
        self.frame_MPRB.setLayout(self.vl_MPRB)
        self.frame_MPRC.setLayout(self.vl_MPRC)
        self.figureMPRA.canvas.mpl_connect('scroll_event', self.onScrollMPRA)
        self.figureMPRB.canvas.mpl_connect('scroll_event', self.onScrollMPRB)
        self.figureMPRC.canvas.mpl_connect('scroll_event', self.onScrollMPRC)
        self.figureMPRA.canvas.mpl_connect('button_press_event', self.onClickMPRA)
        self.figureMPRB.canvas.mpl_connect('button_press_event', self.onClickMPRB)
        self.figureMPRC.canvas.mpl_connect('button_press_event', self.onClickMPRC)

        self.keyType = vtk.vtkInformationStringKey.MakeKey("type", "vtkActor")
        self.keyID = vtk.vtkInformationStringKey.MakeKey("ID", "vtkActor")
        self.overlayDataMain = {"Lesion ID":"--", "Voxel Count":"--", "Physical Size":"--", "Centroid":"--", "Elongation":"--", "Lesion Perimeter":"--", "Lesion Spherical Radius":"--", "Lesion Spherical Perimeter":"--", "Lesion Flatness":"--", "Lesion Roundness":"--"}
        self.structureInfo = None
        self.userPickedLesionID = None
        self.isBasePlottingNeeded = False
        self.overlayLesionStripActivated = False
        self.dataCount = 0
        self.vtk_colorsLh = vtk.vtkUnsignedCharArray()
        self.vtk_colorsRh = vtk.vtkUnsignedCharArray()
        self.vtk_colorsLh.SetNumberOfComponents(3)
        self.vtk_colorsRh.SetNumberOfComponents(3)

        self.textActorLesionStatistics = vtk.vtkTextActor()
        self.textActorLesionStatistics.UseBorderAlignOff()
        self.textActorLesionStatistics.SetPosition(1, 0)
        self.textActorLesionStatistics.GetTextProperty().SetFontFamily(4)
        self.textActorLesionStatistics.GetTextProperty().SetFontFile("asset\\arial.ttf")
        self.textActorLesionStatistics.GetTextProperty().SetFontSize(12)
        self.textActorLesionStatistics.GetTextProperty().ShadowOn()
        self.textActorLesionStatistics.GetTextProperty().SetLineSpacing(1.6)
        self.textActorLesionStatistics.GetTextProperty().SetColor(0.1,0.1,0.1)

        self.buttonGroupSurfaces = QButtonGroup()
        self.buttonGroupSurfaces.addButton(self.radioButton_White)
        self.buttonGroupSurfaces.addButton(self.radioButton_Inflated)
        self.buttonGroupSurfaces.setExclusive(True)
        self.buttonGroupSurfaces.buttonClicked.connect(self.on_buttonGroupSurfaceChanged)

        self.buttonGroupModalities = QButtonGroup()
        self.buttonGroupModalities.addButton(self.radioButton_T1)
        self.buttonGroupModalities.addButton(self.radioButton_T2)
        self.buttonGroupModalities.addButton(self.radioButton_FLAIR)
        self.buttonGroupModalities.setExclusive(True)
        self.buttonGroupModalities.buttonClicked.connect(self.on_buttonGroupModalityChanged)

        # Hide some buttons (things here soon going to get removed/replaced.)
        self.horizontalSlider_Riso.hide()
        self.radioButton_T1.hide()
        self.radioButton_T2.hide()
        self.radioButton_FLAIR.hide()
        self.checkBox_ShowClasses.hide()
        self.label_Riso.hide()
        self.label_6.hide()

    def updateContourComparisonView(self, pickedLesionID):
        vert = """
            //VTK::System::Dec
            attribute vec4 vertexMC;
            attribute vec3 normalMC;
            uniform mat3 normalMatrix;
            uniform mat4 MCDCMatrix;
            uniform mat4 MCVCMatrix;  // Combined model to view transform.
            varying vec3 normalVCVSOutput2;
            varying vec4 vertexVCVSOutput2;
            attribute vec2 tcoordMC;
            out vec3 color;
            varying vec2 tcoordVCVSOutput;
            void main () {
              normalVCVSOutput2 = normalMatrix * normalMC;
              tcoordVCVSOutput = tcoordMC;
              vertexVCVSOutput2 = MCVCMatrix * vertexMC;
              gl_Position = MCDCMatrix * vertexMC;
            }
        """
        frag = """
           //VTK::System::Dec
           varying vec4 vColor;
           in vec3 color;
           void main()
           {
               gl_FragColor = vec4(1.0,0.0,0.0,0.5);
               //gl_FragColor = vColor;
            }
        """

        #print("i am called", pickedLesionID)
        currentTimeIndex = self.horizontalSlider_TimePoint.value()
        linkedLesionIds = self.getLinkedLesionIDFromLeftAndRight(pickedLesionID, currentTimeIndex)

        lesionSurfaceArray = []
        rendererArray = []

        rendererCollection = self.irenDual.GetRenderWindow().GetRenderers()
        currentTimeRenderer = rendererCollection.GetItemAsObject(2)
        #print(rendererCollection.GetNumberOfItems())  # TODO: Check why this is giving 7!!

        for i in range(rendererCollection.GetNumberOfItems()-1):
            if i == 0:  # ignore brain surface renderer
                continue
            renderer = rendererCollection.GetItemAsObject(i)
            renderer.RemoveAllViewProps()
            if linkedLesionIds[i-1] is None:
                renderer.RemoveAllViewProps()
                continue
            else:  # Add valid lesion to renderer.
                for lesion in self.LesionActorList[currentTimeIndex - 2 + (i-1)]:
                    lesionID = int(lesion.GetProperty().GetInformation().Get(self.keyID))
                    #lesion.GetMapper().SetVertexShaderCode(vert)
                    #lesion.GetMapper().SetFragmentShaderCode(frag)

                    silhouette = vtk.vtkPolyDataSilhouette()
                    silhouette.SetInputData(lesion.GetMapper().GetInput())
                    silhouette.SetCamera(renderer.GetActiveCamera())
                    silhouette.SetEnableFeatureAngle(0)

                    silhouetteMapper = vtk.vtkPolyDataMapper()
                    silhouetteMapper.SetInputConnection(silhouette.GetOutputPort())
                    silhouetteActor = vtk.vtkActor()
                    silhouetteActor.SetMapper(silhouetteMapper)
                    silhouetteActor.GetProperty().SetColor(0.1, 0.1, 0.1)
                    silhouetteActor.GetProperty().SetLineWidth(2)

                    if lesionID == linkedLesionIds[i-1] - 1:
                        #renderer.AddActor(lesion)
                        renderer.AddActor(silhouetteActor)
                        #print("adding actor")
                renderer.ResetCamera()
                renderer.Render()

        self.irenDual.Render()


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
            else:
                continue

            if itemIndex == temporalDataListLength-1:
                linkedLesionIds[2] = temporalData[itemIndex][1]
            if (itemIndex + 2) < temporalDataListLength:  # Check overflow towards right
                linkedLesionIds[2] = temporalData[itemIndex][1]
                linkedLesionIds[3] = temporalData[itemIndex+1][1]
                linkedLesionIds[4] = temporalData[itemIndex+2][1]
            if (itemIndex - 2) >= 0:
                linkedLesionIds[0] = temporalData[itemIndex-1][1]
                linkedLesionIds[1] = temporalData[itemIndex-2][1]


            return linkedLesionIds   # Success
        return None  # Failure

    def spinBoxMinChanged(self, val):
        if(val>=self.spinBox_RangeMax.value()):
            self.spinBox_RangeMin.setValue(self.spinBox_RangeMax.value()-1)
        else:
            #self.slider3DCompare.set_left_thumb_value(val)
            pass

    def spinBoxMaxChanged(self, val):
        if(val<=self.spinBox_RangeMin.value()):
            self.spinBox_RangeMax.setValue(self.spinBox_RangeMin.value()+1)
        else:
            #self.slider3DCompare.set_right_thumb_value(val)
            pass

    def reportProgress(self, n):
        self.progressBar.setValue(n)

    # Handler for lesion attribute selection changed.
    @pyqtSlot()
    def on_combobox_changed_LesionAttributes(self): 
        if (str(self.comboBox_LesionAttributes.currentText())=="Physical Size"):
            self.plotDefaultGraph("PhysicalSize")
        if (str(self.comboBox_LesionAttributes.currentText())=="Elongation"):
            self.plotDefaultGraph("Elongation")
        if (str(self.comboBox_LesionAttributes.currentText())=="Perimeter"):
            self.plotDefaultGraph("Perimeter")
        if (str(self.comboBox_LesionAttributes.currentText())=="Spherical Radius"):
            self.plotDefaultGraph("SphericalRadius")
        if (str(self.comboBox_LesionAttributes.currentText())=="Spherical Perimeter"):
            self.plotDefaultGraph("SphericalPerimeter")
        if (str(self.comboBox_LesionAttributes.currentText())=="Flatness"):
            self.plotDefaultGraph("Flatness")
        if (str(self.comboBox_LesionAttributes.currentText())=="Roundness"):
            self.plotDefaultGraph("Roundness") 

    # Handler for projection method selection changed.
    @pyqtSlot()
    def on_combobox_changed_ProjectionMethods(self): 
        self.on_sliderChangedTimePoint()

    def enableControls(self):
        self.checkBox_RangeCompare.setEnabled(True)

    # Handler for mode change inside button group (surfaces)
    @pyqtSlot(QAbstractButton)
    def on_buttonGroupSurfaceChanged(self, btn):
        if(self.dataFolderInitialized == True):
            if(self.buttonGroupSurfaces.checkedButton().text() == "White"):
                self.renDual.RemoveActor(self.surfaceActors[3])
                self.renDual.RemoveActor(self.surfaceActors[4])
                self.renDual.AddActor(self.surfaceActors[1])
                self.renDual.AddActor(self.surfaceActors[2])
                self.surfaceActors[1].GetMapper().GetInput().GetPointData().SetActiveScalars("projection")
                self.surfaceActors[2].GetMapper().GetInput().GetPointData().SetActiveScalars("projection")
            else:
                self.renDual.RemoveActor(self.surfaceActors[1])
                self.renDual.RemoveActor(self.surfaceActors[2])
                self.renDual.AddActor(self.surfaceActors[3])
                self.renDual.AddActor(self.surfaceActors[4])
                self.surfaceActors[3].GetMapper().GetInput().GetPointData().SetActiveScalars("projection")
                self.surfaceActors[4].GetMapper().GetInput().GetPointData().SetActiveScalars("projection")
            self.irenDual.Render()

    # Handler for mode change inside button group (modality)
    @pyqtSlot(QAbstractButton)
    def on_buttonGroupModalityChanged(self, btn):
        self.plotIntensityGraph()
        self.canvasIntensity.draw()

    def updateLesionOverlayText(self):
        overlayText = ""
        for key in self.overlayDataMain.keys():
            overlayText = overlayText + "\n" + str(key) + ": " + str(self.overlayDataMain[key])
        self.textActorLesionStatistics.SetInput(overlayText)
        
    def renderData(self):
        Utils.smoothSurface(self.surfaceActors[0])
        self.dataCount = len(self.LesionActorList)
        self.spinBox_RangeMin.setMinimum(0)
        self.spinBox_RangeMin.setMaximum(int(self.dataCount-1))
        self.spinBox_RangeMin.setValue(0)
        self.spinBox_RangeMax.setMinimum(0)
        self.spinBox_RangeMax.setMaximum(int(self.dataCount-1))
        self.spinBox_RangeMax.setValue(5)
        self.horizontalSlider_TimePoint.setMaximum(self.dataCount-1)
        for lesion in self.LesionActorList[0]:
            self.ren.AddActor(lesion)
        self.ren.AddActor(self.surfaceActors[0]) # ventricle
        self.ren.ResetCamera()
        self.ren.GetActiveCamera().Zoom(1.3)
        self.iren.Render()
        openglRendererInUse = self.ren.GetRenderWindow().ReportCapabilities().splitlines()[1].split(":")[1].strip()
        self.textEdit_Information.append("GPU: " + str(openglRendererInUse))

        self.renDual.AddActor(self.surfaceActors[1])
        self.renDual.AddActor(self.surfaceActors[2])
        self.renDual.ResetCamera()
        self.renDual.GetActiveCamera().Zoom(1.3)
        self.irenDual.Render()

        self.readInitializeLesionJSONData() # Read lesion data from JSON file.
        self.displayOrientationCube()  # Display orientation cube
        self.LoadStructuralSlices(self.folder, "T1", 0, True) # load slices
        self.initializeDefaultGraph()  # Load graph data
        self.initializeGraphVis()  # Load graph visualization.
        self.readInitializestructuralData()
        self.activateControls()  # Activate controls.
        self.ren.AddActor2D(self.textActorLesionStatistics)  # Add lesion statistics overlay.
        self.dataFolderInitialized = True
        self.enableControls()
        self.currentTimeStep = self.horizontalSlider_TimePoint.value()
        self.numberOfPointsLh = self.surfaceActors[3].GetMapper().GetInput().GetNumberOfPoints()
        self.numberOfPointsRh = self.surfaceActors[4].GetMapper().GetInput().GetNumberOfPoints()
        self.vtk_colorsLh.SetNumberOfTuples(self.numberOfPointsLh)
        self.vtk_colorsRh.SetNumberOfTuples(self.numberOfPointsRh)
        self.vertexIndexArrayLh = np.arange(self.numberOfPointsLh)
        self.vertexIndexArrayRh = np.arange(self.numberOfPointsRh)

        self.iren.Render()
        self.irenDual.Render()

    # Read structural data information.
    def readInitializestructuralData(self):
        self.intMin = 0
        self.intMax = 255
        return
        #structuralDataPath = self.folder + "structural\\T1_0.nii"
        structuralDataPath = "asset\\dataset\\Subject1\\structural\\T1.nii"
        img = sitk.ReadImage(structuralDataPath)
        stats = sitk.StatisticsImageFilter()
        stats.Execute(img)
        #print("Minimum:", stats.GetMinimum())
        #print("Maximum:", stats.GetMaximum())
        self.intMin = stats.GetMinimum()
        self.intMax = stats.GetMaximum()

    # Read lesion data from json file.
    # How to access data 
    # FORMAT - structureInfo[StringFollowUpIndex][0][StringLesionIndex][0]['Elongation']
    # Example print(structureInfo[str(0)][0][str(1)][0]['Elongation']) # First timestep, First Lesion, Elongation property.
    def readInitializeLesionJSONData(self):
        # load precomputed lesion properties
        with open(self.folder + "\\preProcess\\lesionStatistics.json") as fp: 
            self.structureInfo = json.load(fp)
        self.numberOfFollowups = len(self.structureInfo)

    # action called by thte push button 
    def plotMPRs(self, maskAlpha = 0.5, refreshData=True): 
        # clearing old figures
        self.figureMPRA.clear()
        plt.figure(0)
        # create an axis
        self.axMPRA = self.figureMPRA.add_subplot(111)
        plt.axis('off')
        plt.subplots_adjust(wspace=None, hspace=None)
        if(refreshData == True):
            self.slice_MPRA = np.fliplr(np.rot90(self.slice_MPRA))
            self.sliceMask_MPRA = np.fliplr(np.rot90(self.sliceMask_MPRA))
        if(self.radioButton_FLAIR.isChecked() == True):
            aspectCoronalData = self.spacingData[2]/self.spacingData[1]
            aspectCoronalMask = self.spacingMask[2]/self.spacingMask[1]
        else:
            aspectCoronalData = self.spacingData[2]/self.spacingData[0]
            aspectCoronalMask = self.spacingMask[2]/self.spacingMask[0]

        my_cmap = self.MPROverlayColorMap
        my_cmap.set_under('k', alpha=0) # For setting background to alpha 0

        #self.slice_MPRA = np.ma.masked_where(self.slice_MPRA <1, self.slice_MPRA)
        self.MPRA = plt.imshow(self.slice_MPRA, cmap='Greys_r', aspect=aspectCoronalData)
        self.MPRAMask = plt.imshow(self.sliceMask_MPRA, cmap=my_cmap, aspect=aspectCoronalMask,  alpha=maskAlpha, interpolation='none', clim=[0.9, 1])
        self.sliceNumberHandleMPRA = self.axMPRA.text(5, 5, str(self.midSliceX), verticalalignment='top', horizontalalignment='left', color='green', fontsize=12)
        
        self.figureMPRB.clear()
        plt.figure(1)
        self.axMPRB = self.figureMPRB.add_subplot(111)
        plt.axis('off')
        plt.subplots_adjust(wspace=None, hspace=None)
        if(refreshData == True):
            self.slice_MPRB = np.rot90(self.slice_MPRB)
            self.sliceMask_MPRB = np.rot90(self.sliceMask_MPRB)
        if(self.radioButton_FLAIR.isChecked() == True):
            aspectAxialData = self.spacingData[1]/self.spacingData[0]
            aspectAxialMask = self.spacingMask[1]/self.spacingMask[0]
        else:
            aspectAxialData = self.spacingData[2]/self.spacingData[1]
            aspectAxialMask = self.spacingMask[2]/self.spacingMask[1]
        self.MPRB = plt.imshow(self.slice_MPRB, cmap='Greys_r', aspect=aspectAxialData)
        self.MPRBMask = plt.imshow(self.sliceMask_MPRB, cmap=my_cmap, aspect=aspectCoronalMask,  alpha=maskAlpha, interpolation='none', clim=[0.9, 1])
        self.sliceNumberHandleMPRB = self.axMPRB.text(5, 5, str(self.midSliceY), verticalalignment='top', horizontalalignment='left', color='green', fontsize=12)

        self.figureMPRC.clear()
        plt.figure(2)
        self.axMPRC = self.figureMPRC.add_subplot(111) 
        plt.axis('off')
        plt.subplots_adjust(wspace=None, hspace=None)
        if(refreshData == True):
            if(self.dtiDataActive == True):
                self.slice_MPRC = np.rot90(self.slice_MPRC)
                self.sliceMask_MPRC = np.rot90(self.sliceMask_MPRC)
            else:
                self.slice_MPRC = np.rot90(self.slice_MPRC, 3)
                self.sliceMask_MPRC = np.rot90(self.sliceMask_MPRC, 3)

        if(self.radioButton_FLAIR.isChecked() == True):
            aspectSagittalData = self.spacingData[1]/self.spacingData[0]
            aspectSagittalMask = self.spacingMask[1]/self.spacingMask[0]
        else:
            aspectSagittalData = self.spacingData[1]/self.spacingData[0]
            aspectSagittalMask = self.spacingMask[1]/self.spacingMask[0]
        self.MPRC = plt.imshow(self.slice_MPRC, cmap='Greys_r', aspect=aspectSagittalData)
        self.MPRCMask = plt.imshow(self.sliceMask_MPRC, cmap=my_cmap, aspect=aspectCoronalMask,  alpha=maskAlpha, interpolation='none', clim=[0.9, 1])
        self.sliceNumberHandleMPRC = self.axMPRC.text(5, 5, str(self.midSliceZ), verticalalignment='top', horizontalalignment='left', color='green', fontsize=12)

        # scale = 1.1
        # zpMPRA = Utils.ZoomPan()
        # figZoomMPRA = zpMPRA.zoom_factory(self.axMPRA, base_scale = scale)
        # figPanMPRA = zpMPRA.pan_factory(self.axMPRA)

        self.canvasMPRA.draw()
        self.canvasMPRB.draw()
        self.canvasMPRC.draw()

    # Load and Render Structural data as image slices.
    def LoadStructuralSlices(self, subjectFolder, modality, dataIndex, IsOverlayEnabled = False):
        fileName = subjectFolder + "\\structural\\"+modality+".nii"
        fileNameOverlay = subjectFolder + "\\lesionMask\\Consensus"+modality+"VoxelSpaceCorrected" + str(dataIndex) + ".nii"
        
        self.epi_img = nib.load(fileName)
        self.mask_img = nib.load(fileNameOverlay)
        self.epi_img_data = self.epi_img.get_fdata() # Read structural
        
        self.mask_data = self.mask_img.get_fdata() # Read mask data
        

        self.spacingData = self.epi_img.header.get_zooms()
        self.spacingMask = self.mask_img.header.get_zooms()
        # Creating mask
        #self.alpha_mask = ma.masked_where(self.mask_data <= 0, self.mask_data)
        #self.alpha_mask = ma.masked_where(self.mask_data == 0, self.mask_data)
        self.alpha_mask = self.mask_data
        #print(np.unique(self.alpha_mask))
        #self.alpha_mask[self.alpha_mask>0] = 255

        self.data_dims = self.epi_img_data.shape
        self.midSliceX = int(self.data_dims[0]/2)
        self.midSliceY = int(self.data_dims[1]/2)
        self.midSliceZ = int(self.data_dims[2]/2)

        ################################
        # MPR SLICES    ################
        ################################
        self.slice_MPRA = self.epi_img_data[self.midSliceX, :, :]
        self.slice_MPRB = self.epi_img_data[:, self.midSliceY, :]
        self.slice_MPRC = self.epi_img_data[:, :, self.midSliceZ]
        #self.slice_MPRA = np.ma.masked_where(self.slice_MPRA==0, self.slice_MPRA) # Make MRI data background transparent
        #self.slice_MPRB = np.ma.masked_where(self.slice_MPRB==0, self.slice_MPRB) # Make MRI data background transparent
        #self.slice_MPRC = np.ma.masked_where(self.slice_MPRC==0, self.slice_MPRC) # Make MRI data background transparent
        self.sliceMask_MPRA = self.alpha_mask[self.midSliceX, :, :]
        self.sliceMask_MPRB = self.alpha_mask[:, self.midSliceY, :]
        self.sliceMask_MPRC = self.alpha_mask[:, :, self.midSliceZ]

        # Plot the MPRs
        self.plotMPRs()

        self.mprA_Slice_Slider.setMaximum(self.data_dims[0]-1)
        self.mprB_Slice_Slider.setMaximum(self.data_dims[1]-1)
        self.mprC_Slice_Slider.setMaximum(self.data_dims[2]-1)

        self.mprA_Slice_Slider.setValue(self.midSliceX)
        self.mprB_Slice_Slider.setValue(self.midSliceY)
        self.mprC_Slice_Slider.setValue(self.midSliceZ)

        self.mprA_Slice_Slider.valueChanged.connect(self.on_sliderChangedMPRA)
        self.mprB_Slice_Slider.valueChanged.connect(self.on_sliderChangedMPRB)
        self.mprC_Slice_Slider.valueChanged.connect(self.on_sliderChangedMPRC)

    # Display orientation cube.
    def displayOrientationCube(self):
        self.axesActor = vtk.vtkAnnotatedCubeActor()
        self.axesActor.SetXPlusFaceText('R')
        self.axesActor.SetXMinusFaceText('L')
        self.axesActor.SetYMinusFaceText('P')
        self.axesActor.SetYPlusFaceText('A')
        self.axesActor.SetZMinusFaceText('I')
        self.axesActor.SetZPlusFaceText('S')
        self.axesActor.GetTextEdgesProperty().SetColor(1.0,1.0,1.0)
        self.axesActor.GetTextEdgesProperty().SetLineWidth(1)
        #self.axesActor.GetCubeProperty().SetColor(0.7255, 0.8470, 0.7725)
        self.axesActor.GetCubeProperty().SetColor(0.4, 0.4, 0.4)
        self.axes = vtk.vtkOrientationMarkerWidget()
        self.axes.SetOrientationMarker(self.axesActor)
        self.axes.SetViewport( 0.93, 0.9, 1.0, 1.0 )
        self.axes.SetCurrentRenderer(self.ren)
        self.axes.SetInteractor(self.iren)
        self.axes.EnabledOn()

        self.axesActorDual = vtk.vtkAnnotatedCubeActor()
        self.axesActorDual.SetXPlusFaceText('R')
        self.axesActorDual.SetXMinusFaceText('L')
        self.axesActorDual.SetYMinusFaceText('P')
        self.axesActorDual.SetYPlusFaceText('A')
        self.axesActorDual.SetZMinusFaceText('I')
        self.axesActorDual.SetZPlusFaceText('S')
        self.axesActorDual.GetTextEdgesProperty().SetColor(1,1,1)
        self.axesActorDual.GetTextEdgesProperty().SetLineWidth(1)
        #self.axesActorDual.GetCubeProperty().SetColor(0.7255, 0.8470, 0.7725)
        self.axesActorDual.GetCubeProperty().SetColor(0.4, 0.4, 0.4)
        self.axesDual = vtk.vtkOrientationMarkerWidget()
        self.axesDual.SetOrientationMarker(self.axesActorDual)
        self.axesDual.SetViewport( 0.93, 0.9, 1.0, 1.0 )
        self.axesDual.SetCurrentRenderer(self.renDual)
        self.axesDual.SetInteractor(self.irenDual)
        self.axesDual.EnabledOn()

    def initializeDefaultGraph(self):
        self.vl_default = Qt.QVBoxLayout()
        #self.figureDefault = plt.figure(num = 3, frameon=False, clear=True)
        self.figureDefault, (self.axDefaultIntensity, self.axDefault) = plt.subplots(2, 1, num=3, sharex = True, gridspec_kw={'height_ratios': [1, 4]})

        self.canvasDefault = FigureCanvas(self.figureDefault)
        self.vl_default.addWidget(self.canvasDefault)
        self.frameDefaultGraph.setLayout(self.vl_default)
        self.plotDefaultGraph("PhysicalSize")
        self.overlayGlyphActive = False

    def initializeGraphVis(self):
        print("initializing node graph...")

        # Colors for actors
        graphNodeColors = []
        for i in range(1, 10 + 1):
            graphNodeColors.append(self.plotColors[self.graphLegendLabelList.index(str(i))])

        self.vlNodeGraph = Qt.QVBoxLayout()
        self.vtkWidgetNodeGraph = QVTKRenderWindowInteractor(self.frame_NodeGraph)
        self.vlNodeGraph.addWidget(self.vtkWidgetNodeGraph)

        self.graph_layout_view = vtk.vtkGraphLayoutView()
        self.graph_layout_view.SetRenderWindow(self.vtkWidgetNodeGraph.GetRenderWindow())
        #self.renNodeGraph = vtk.vtkRenderer()
        self.renNodeGraph = self.graph_layout_view.GetRenderer()
        self.renNodeGraph.SetBackground(255.0, 0.0, 0.0)
        self.vtkWidgetNodeGraph.GetRenderWindow().AddRenderer(self.renNodeGraph)

        self.irenNodeGraph = self.vtkWidgetNodeGraph.GetRenderWindow().GetInteractor()
        self.irenNodeGraph.SetRenderWindow(self.vtkWidgetNodeGraph.GetRenderWindow())
        self.irenNodeGraph.SetInteractorStyle(self.graph_layout_view.GetInteractorStyle())

        #self.irenNodeGraph = self.graph_layout_view.GetInteractor()
        #self.irenNodeGraph.SetRenderWindow(self.vtkWidgetNodeGraph.GetRenderWindow())

        self.renNodeGraph.ResetCamera()
        self.frame_NodeGraph.setLayout(self.vlNodeGraph)
        self.irenNodeGraph.Initialize()
        Utils.drawNodeGraph(self, "asset\\dataset\\Subject1\\preProcess\\lesionGraph.gml", self.graph_layout_view, graphNodeColors)

        #self.vl_graph = Qt.QVBoxLayout()
        #self.figureGraph = plt.figure(num = 4, frameon=False, clear=True)
        #self.canvasGraph = FigureCanvas(self.figureGraph)
        #self.vl_graph.addWidget(self.canvasGraph)
        #self.frame_NodeGraph.setLayout(self.vl_graph)
        #self.canvasGraph.mpl_connect('pick_event', self.nodeGraphPickEventHandler)

    def nodeGraphPickEventHandler(self):
        print("pick evenet trigerred")

    def on_press_intensityGlyph(self, event):
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #     ('double' if event.dblclick else 'single', event.button,
        #     event.x, event.y, event.xdata, event.ydata))
        if(event.button == 2): # middle mouse button pressed
            self.plotIntensityGlyphGraph()

    def onScrollMPRA(self, event):
        currentSlide = self.midSliceX
        if(event.button == 'up'):
            if(currentSlide + 1 <= self.data_dims[0]):
                self.midSliceX = self.midSliceX + 1
        if(event.button == 'down'):
            if(currentSlide - 1 > 0):
                self.midSliceX = self.midSliceX - 1
        self.mprA_Slice_Slider.setValue(self.midSliceX)

    def onScrollMPRB(self, event):
        currentSlide = self.midSliceY
        if(event.button == 'up'):
            if(currentSlide + 1 <= self.data_dims[1]):
                self.midSliceY = self.midSliceY + 1
        if(event.button == 'down'):
            if(currentSlide - 1 > 0):
                self.midSliceY = self.midSliceY - 1
        self.mprB_Slice_Slider.setValue(self.midSliceY)

    def onScrollMPRC(self, event):
        currentSlide = self.midSliceZ
        if(event.button == 'up'):
            if(currentSlide + 1 <= self.data_dims[2]):
                self.midSliceZ = self.midSliceZ + 1
        if(event.button == 'down'):
            if(currentSlide - 1 > 0):
                self.midSliceZ = self.midSliceZ - 1
        self.mprC_Slice_Slider.setValue(self.midSliceZ)

    def onClickMPRA(self, event):
        pass
        # location = event.x, event.y
        # transform = self.axMPRA.transData.inverted().transform(location)
        # pickID = self.sliceMask_MPRA[int(transform[1]), int(transform[0])]
        # if(isinstance(pickID, np.float64)):
        #     sliceLesionID = [int(pickID)]
        #     LesionUtils.highlightActors(self.lesionActors, sliceLesionID, self.informationUniqueKey)
        #     LesionUtils.refreshActiveRenderer(self)

    def onClickMPRB(self, event):
        pass
        # location = event.x, event.y
        # transform = self.axMPRB.transData.inverted().transform(location)
        # pickID = self.sliceMask_MPRB[int(transform[1]), int(transform[0])]
        # if(isinstance(pickID, np.float64)):
        #     sliceLesionID = [int(pickID)]
        #     LesionUtils.highlightActors(self.lesionActors, sliceLesionID, self.informationUniqueKey)
        #     LesionUtils.refreshActiveRenderer(self)

    def onClickMPRC(self, event):
        pass
        # location = event.x, event.y
        # transform = self.axMPRC.transData.inverted().transform(location)
        # pickID = self.sliceMask_MPRC[int(transform[1]), int(transform[0])]
        # if(isinstance(pickID, np.float64)):
        #     sliceLesionID = [int(pickID)]
        #     LesionUtils.highlightActors(self.lesionActors, sliceLesionID, self.informationUniqueKey)
        #     LesionUtils.refreshActiveRenderer(self)

    # Handler for MPRA Slider change.
    @pyqtSlot()
    def on_sliderChangedMPRA(self):
        plt.figure(0)
        self.midSliceX = self.mprA_Slice_Slider.value()
        self.slice_MPRA = np.fliplr(np.rot90(self.epi_img_data[self.midSliceX, :, :]))
        #self.slice_MPRA = np.ma.masked_where(self.slice_MPRA==0, self.slice_MPRA) # Make MRI data background transparent.
        self.sliceMask_MPRA = np.fliplr(np.rot90(self.alpha_mask[self.midSliceX, :, :]))
        self.MPRA.set_data(self.slice_MPRA)
        self.sliceNumberHandleMPRA.set_text(self.midSliceX)
        self.MPRAMask.set_data(self.sliceMask_MPRA)
        self.canvasMPRA.draw()

    # Handler for MPRB Slider change.
    @pyqtSlot()
    def on_sliderChangedMPRB(self):
        plt.figure(1)
        self.midSliceY = self.mprB_Slice_Slider.value()
        self.slice_MPRB = np.rot90(self.epi_img_data[:, self.midSliceY, :])
        #self.slice_MPRB = np.ma.masked_where(self.slice_MPRB==0, self.slice_MPRB) # Make MRI data background transparent.
        self.sliceMask_MPRB = np.rot90(self.alpha_mask[:, self.midSliceY, :])
        self.MPRB.set_data(self.slice_MPRB)
        self.sliceNumberHandleMPRB.set_text(self.midSliceY)
        self.MPRBMask.set_data(self.sliceMask_MPRB)
        self.canvasMPRB.draw()

    # Handler for MPRC Slider change.
    @pyqtSlot()
    def on_sliderChangedMPRC(self):
        plt.figure(2)
        self.midSliceZ = self.mprC_Slice_Slider.value()
        if(self.dtiDataActive == True):
            self.slice_MPRC = np.rot90(self.epi_img_data[:, :, self.midSliceZ])
            self.sliceMask_MPRC = np.rot90(self.alpha_mask[:, :, self.midSliceZ])
        else:
            self.slice_MPRC = np.rot90(self.epi_img_data[:, :, self.midSliceZ], 3)
            self.sliceMask_MPRC = np.rot90(self.alpha_mask[:, :, self.midSliceZ], 3)    
        # self.slice_MPRC = np.ma.masked_where(self.slice_MPRC==0, self.slice_MPRC)  # Make MRI data background transparent.
        self.MPRC.set_data(self.slice_MPRC)
        self.sliceNumberHandleMPRC.set_text(self.midSliceZ)
        self.MPRCMask.set_data(self.sliceMask_MPRC)
        self.canvasMPRC.draw()

    # Actvate controls after dataset is loaded.
    def activateControls(self):
        self.mprA_Slice_Slider.setEnabled(True)
        self.mprB_Slice_Slider.setEnabled(True)
        self.mprC_Slice_Slider.setEnabled(True)

    # Plot node graph visual
    def plotGraphVis(self):
        print("sfsdfsdf")
        # self.figureGraph.clear()
        # plt.figure(4)
        # plt.rcParams['font.family'] = 'Open Sans'
        # self.axGraph = self.figureGraph.add_subplot(111)
        # self.axGraph.set_title('Lesion Activity Graph', fontsize=12, fontweight='normal', color="#666666", loc='left')
        # plt.subplots_adjust(left=0.09, bottom=0.09, right=0.95, top=0.95)
        # G = nx.read_gml("asset\\dataset\\Subject1\\preProcess\\lesionGraph.gml")
        # edges = G.edges()
        # weights = [3 for u, v in edges]
        #
        # graphNodeColors = []
        # for i in range(1, 10+1):
        #     graphNodeColors.append(self.plotColors[self.graphLegendLabelList.index(str(i))])
        #
        # nx.draw_planar(G, with_labels=True, node_size=700, node_color=graphNodeColors, node_shape="h", edge_color="#4c80b3", font_color="#112840", font_weight="normal", alpha=0.5, linewidths=2, width=weights, arrowsize=20)
        # self.canvasGraph.draw()

    def computeNodeOrderForGraph(self, G): #TODO NEED TO UPDATE CODE to support multilevel activity (eg split and merge in one sequence)
        # color palette
        numberOfConnectedComponents = len(list(nx.strongly_connected_components(G))) # gets the number of disconnected components in the graph
        #print("Number of connected components", numberOfConnectedComponents)
        #print(list(nx.strongly_connected_components(G)))
        #print(list(nx.connected_components(G.to_undirected())))
        #print(nx.number_connected_components(G))
         
        nodeIDList = list(G.nodes)
        streamPlotDataColors = sns.color_palette("Set2", len(nodeIDList)) # visually pleasing colors from color brewer.
        #streamPlotDataColors = sns.color_palette()
        nodesAndDegreesUndirected =  list(G.degree(nodeIDList))
        nodesAndDegreesDirectedOut =  list(G.out_degree(nodeIDList))
        nodesAndDegreesDirectedIn =  list(G.in_degree(nodeIDList))
        #print(nodesAndDegreesDirectedIn)
        #connectedComponents = nx.strongly_connected_components(G)
        connectedComponents = nx.connected_components(G.to_undirected())
        # for elem in connectedComponents:  
        #     mygraph = G.subgraph(elem)
        #     #print(G.subgraph(elem))
        #     print(mygraph.edges)

        disconnectedNodes = [elem[0] for elem in nodesAndDegreesUndirected if elem[1]==0]
        splitNodes = [elem[0] for elem in nodesAndDegreesDirectedOut if elem[1]>1]
        mergeNodes = [elem[0] for elem in nodesAndDegreesDirectedIn if elem[1]>1]
        nodeOrderForGraph = disconnectedNodes
        colorPaletteIndex = len(disconnectedNodes)
        for elem in mergeNodes:
            nodeOrderForGraph.append(elem)
            colorPaletteIndex = colorPaletteIndex + 1
            for i in [item for item in nx.ancestors(G, elem)]:
                nodeOrderForGraph.append(i)
                streamPlotDataColors[colorPaletteIndex] = streamPlotDataColors[colorPaletteIndex-1]
                colorPaletteIndex = colorPaletteIndex + 1
        for elem in splitNodes:
            nodeOrderForGraph.append(elem)
            colorPaletteIndex = colorPaletteIndex + 1
            for i in [item[0] for item in G[elem]]:
                nodeOrderForGraph.append(i)
                streamPlotDataColors[colorPaletteIndex] = streamPlotDataColors[colorPaletteIndex-1]
                colorPaletteIndex = colorPaletteIndex + 1
        return nodeOrderForGraph, streamPlotDataColors

    def onClickIntensityGraphCanvas(self, event):
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #     ('double' if event.dblclick else 'single', event.button,
        #     event.x, event.y, event.xdata, event.ydata))
        if event.dblclick:
            self.selectedNodeID = None
            self.stackedWidget_Graphs.setCurrentIndex(0)
        if(event.xdata != None):
            pass
            #x_loc = int(round(event.xdata))
            #print("click inside graph")
            #self.updateDefaultGraph(x_loc, None)
        else:
            pass
            #print("click outside graph")
            #self.updateDefaultGraph(None, None)

    # Mouse button is pressed.
    #def onClickDefaultStreamGraphCanvas(self, event):
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #     ('double' if event.dblclick else 'single', event.button,
        #     event.x, event.y, event.xdata, event.ydata))

        if(event.xdata == None or event.ydata == None):
            print("Clearing selection as the user clicked outside the graph")
            self.selectedNodeID = None
            self.updateDefaultGraph(None, None)
        return

    # Mouse button is released.
    def onReleaseDefaultStreamGraphCanvas(self, event):
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #     ('double' if event.dblclick else 'single', event.button,
        #     event.x, event.y, event.xdata, event.ydata))
        if (event.xdata != None and event.button == 3):
            print("Right mouse button released")

    # Stream Graph pick artist.
    def onPickDefaultStreamGraphCanvas(self, event):
        if event.mouseevent.button == 1 or (event.mouseevent.button == 3):  #  Return if user is pressing right mouse button.
            thisline = event.artist
            nodeID = thisline.get_label()
            self.selectedNodeID = nodeID
            xLoc, yLoc= int(round(event.mouseevent.xdata)), event.mouseevent.ydata

            # Check if this is a ctrl + right click
            if event.mouseevent.button == 3:
                self.isBasePlottingNeeded = True

            self.updateDefaultGraph(xLoc, [nodeID])

            # HIGHLIGHT A LESION IN LESION RENDERER
            if kb.is_pressed("ctrl"):
                self.clearLesionHighlights()
                self.horizontalSlider_TimePoint.setValue(self.vLineXvalue)
                for lesion in self.LesionActorList[self.currentTimeStep]:
                    lesion.GetProperty().SetColor(0.6196078431372549, 0.7372549019607843, 0.8549019607843137)  # default lesion color
                    lesionid = int(lesion.GetProperty().GetInformation().Get(self.keyID)) + 1
                    nodeIDForLesion = self.getNodeIDforPickedLesion(lesionid)
                    if str(nodeIDForLesion) == nodeID:
                            lesion.GetProperty().SetColor(1.0, 0.9686274509803922, 0.7372549019607843)  # yellowish color
                self.iren.Render()

            #self.plotOverlayGlyphs(nodeID) # deprecated
            self.plotIntensityAnalysisPlot(int(nodeID))
            self.plotIntensityChangeIndicatorGlyphs(int(nodeID))

    # Graph mouse move.
    def onMouseMoveDefaultStreamGraphCanvas(self, event):
        x, y = event.x, event.y
        if event.inaxes:
            ax = event.inaxes  # the axes instance
            #print('data coords %f %f' % (event.xdata, event.ydata))

    # plot intensity graph for main streamgraph
    def plotIntensityAnalysisPlot(self, nodeID=None):
        if(nodeID == None): # no manual pick from user
            nodeID = 0
            # Z = np.random.rand(2, dataCount)
            Z = np.vstack((self.intensityArray[nodeID], self.intensityArrayT2[nodeID]))
            self.intensityImage = self.axDefaultIntensity.imshow(Z, aspect='auto', cmap='gray') #  , vmin=0, vmax=255)
            #self.intensityImage = self.axDefaultIntensity.pcolormesh(Z)
            self.axDefaultIntensity.set_yticks([0, 1])  # Set two values as ticks.
            modalities = ["T2", "T1"]
            self.axDefaultIntensity.set_yticklabels(modalities)
            self.axDefaultIntensity.spines['right'].set_visible(False)
            self.axDefaultIntensity.spines['top'].set_visible(False)
            self.axDefaultIntensity.spines['bottom'].set_visible(False)
            self.axDefaultIntensity.spines['left'].set_visible(False)
            #self.axDefaultIntensity.xaxis.set_visible(False) # disable x axis ticks
            #self.axDefaultIntensity.set_xticklabels([])
            #self.axDefaultIntensity.yaxis.grid(True) # enable or keep grid support
            #self.axDefaultIntensity.hlines(y=np.arange(0, self.dataCount), xmin=np.full(self.dataCount, 0), color="white")
            #self.axDefaultIntensity.vlines(x=np.arange(0, 10) + 0.5, ymin=np.full(10, 0) - 0.5, ymax=np.full(10, 10) - 0.5, color="black")
            # Gridlines based on minor ticks
            minor_locator = AutoMinorLocator(2)
            self.axDefaultIntensity.xaxis.set_minor_locator(minor_locator)
            self.axDefaultIntensity.grid(which='minor', color='#ffffff', alpha=0.2, linestyle='-', linewidth=1)
        else:  # user picked an item from streamgraph
            realNodeID = self.graphLegendLabelList.index(str(nodeID))
            Z = np.vstack((self.intensityArray[realNodeID], self.intensityArrayT2[realNodeID]))
            self.intensityImage.set_data(Z)  # update intensity plot data
            self.canvasDefault.draw()

    # plot default graph
    def plotDefaultGraph(self, lesionAttributeString = "PhysicalSize"):
        print("Calling plot default graph")
        # clearing old figures
        #self.figureDefault.clear()
        self.axDefault.clear() #TODO: can remove this and implement setdata for performance?
        #self.figureDefault.tight_layout()
        plt.figure(3)
        # create an axis
        # self.axDefault = self.figureDefault.add_subplot(111)
        plt.subplots_adjust(wspace=0, hspace=0)

        # create axes for default, defaultIntensity and nodeGraph
        #self.axDefault = self.figureDefault.add_subplot(212)
        #self.axDefaultIntensity = self.figureDefault.add_subplot(211, sharex = self.axDefault)

        self.figureDefault.tight_layout()
        plt.subplots_adjust(wspace=None, hspace=None)

        # Data for plotting
        self.G = nx.read_gml("asset\\dataset\\Subject1\\preProcess\\lesionGraph.gml")
        self.UG = self.G.to_undirected()
        self.sub_graphs = list(nx.connected_components(self.UG))
        self.nodeOrderForGraph, self.plotColors = self.computeNodeOrderForGraph(self.G)

        ys = []
        self.dataArray = []
        self.graphLegendLabelList = []
        print("node order", self.nodeOrderForGraph)
        for id in self.nodeOrderForGraph:
            #print("Node order", id)
            self.graphLegendLabelList.append(str(id))
            timeList = self.G.nodes[id]["time"]
            labelList = self.G.nodes[id]["lesionLabel"]
            data = []
            for i in range(len(timeList)):
                time = timeList[i]
                label = labelList[i]
                dataItem = self.getLesionData(label, time, lesionAttributeString)
                data.append(dataItem)
            buckets = [0] * 81
            buckets[timeList[0]:timeList[-1]+1] = data
            #buckets = gaussian_filter1d(buckets, sigma = 2)
            arr = np.asarray(buckets, dtype=np.float64)
            self.dataArray.append(arr)
    
        #x = np.linspace(0, self.dataCount, self.dataCount)
        x = list(range(self.dataCount))
        #random.shuffle(dataArray)
        ys = self.dataArray

        self.polyCollection = self.axDefault.stackplot(x, ys, baseline='zero', picker=True, pickradius=1, labels = self.graphLegendLabelList,  colors = self.plotColors, alpha = 0.7,linewidth=0.5, linestyle='solid', edgecolor=(0.6,0.6,0.6,1.0))

        #print(self.polyCollection)
        # dArray = self.polyCollection[0].get_array()
        # print(dArray)
        # print(type(dArray))

        #with open('D://polyCollection_data.pkl', 'wb') as output:
        #    pickle.dump(self.polyCollection, output, pickle.HIGHEST_PROTOCOL)
        #print(len(self.polyCollection))
        #paths=self.polyCollection[0].get_paths()
        #print(paths)
        #print(self.polyCollection[0])

        #self.plotOverlayGlyphs()

        # # PLOTTING OVERLAY GLYPHS. (new)
        self.intensityArray = self.getIntensityDataForStackplotArtist(self.nodeOrderForGraph)
        self.intensityArrayT2 = self.getIntensityDataForStackplotArtist(self.nodeOrderForGraph, "MeanT2")
        self.plotIntensityAnalysisPlot()
        #print("Type of array is ", type(self.intensityArray[0]))
        #print(self.intensityArray[0].shape)

        self.axDefault.set_facecolor((1,1,1))
        self.axDefault.xaxis.label.set_color((0.2,0.2,0.2))
        self.axDefault.yaxis.label.set_color((0.2,0.2,0.2))
        self.axDefault.spines['bottom'].set_color((0.3411, 0.4824, 0.3608))
        self.axDefault.spines['bottom'].set_linewidth(0)
        self.axDefault.spines['left'].set_color((0.3411, 0.4824, 0.3608))
        self.axDefault.spines['left'].set_linewidth(0)
        self.axDefault.spines['right'].set_visible(False)
        self.axDefault.spines['top'].set_visible(False)
        self.axDefault.tick_params(axis='x', colors=(0.2,0.2,0.2))
        self.axDefault.tick_params(axis='y', colors=(0.2,0.2,0.2))
        #self.axDefault.set_xticks(list(range(self.dataCount)))
        #self.axDefault.tick_params(axis='x', which='minor', length=1)
        self.axDefault.set_xlabel("followup instance", fontname="Arial")#, fontsize=12)
        self.axDefault.set_ylabel(lesionAttributeString, fontname="Arial")#, fontsize=12)
        self.axDefault.xaxis.set_ticks_position('top')  # set x axis labels and ticks on the top of graph
        self.axDefault.title.set_color((0.2,0.2,0.2))

        plt.subplots_adjust(left=0.065, right=0.98, top=0.96, bottom=0.1)
        plt.xlim(xmin=0)
        plt.xlim(xmax=self.dataCount-1)
        #self.axDefault.xaxis.set_ticks(np.arange(0, self.dataCount-1, 1))
        #plt.minorticks_on()

        #minor_locator = AutoMinorLocator(2)
        #self.axDefault.xaxis.set_minor_locator(minor_locator)

        # Enable to add vertical grid lines in streamgraph.
        #self.axDefault.xaxis.grid(True, which='both', color='#f4f6fd', linestyle='-', alpha=0.2) # add vertical grid lines.
        #self.axDefault.grid()
        #fig.savefig("test.png")
        #plt.show()
        self.canvasDefault.draw()
        self.canvasDefault.mpl_connect('pick_event', self.onPickDefaultStreamGraphCanvas)
        #self.canvasDefault.mpl_connect('button_press_event', self.onButtonPressDefaultStreamGraphCanvas)

        #self.canvasDefault.mpl_connect('button_release_event', self.onReleaseDefaultStreamGraphCanvas)
        #self.canvasDefault.mpl_connect('motion_notify_event', self.onMouseMoveDefaultStreamGraphCanvas)
        #self.defaultGraphBackup = self.canvasDefault.copy_from_bbox(self.axDefault.bbox)
        #print("running here")

        self.vLine = None
        self.vLineXvalue = None
        scale = 1.1
        zpDefault = Utils.ZoomPan()
        figZoomDefault = zpDefault.zoom_factory(self.axDefault, base_scale = scale)
        figPanDefault = zpDefault.pan_factory(self.axDefault)


    # update default graph
    def updateDefaultGraph(self, vlineXloc=None, updateColorIndex=None):
        plt.figure(3)
        tempColors = list(self.plotColors)


        #self.canvasDefault.restore_region(self.defaultGraphBackup)
        if(vlineXloc != None):
            if(self.vLine == None):
                self.vLine = plt.axvline(x=vlineXloc, linewidth=2, color='r', linestyle=':', alpha=0.5)
                self.vLineXvalue = vlineXloc
            else:
                self.vLine.set_xdata([vlineXloc])
                self.vLineXvalue = vlineXloc
        else:
            if self.vLine is not None:
                self.vLine.remove()
                self.vLine = None


        if self.isBasePlottingNeeded:
            x = list(range(self.dataCount))
            arrayIndex = self.nodeOrderForGraph.index(updateColorIndex[0])
            ysOverlay = self.dataArray[self.nodeOrderForGraph.index(updateColorIndex[0])]
            # Clear all existing overlays
            if self.overlayLesionStripActivated == True:
                for i in range(len(self.polyCollectionOverlayStackPlot)):
                    self.polyCollectionOverlayStackPlot[i].set_visible(False)
            self.polyCollectionOverlayStackPlot = self.axDefault.stackplot(x, ysOverlay, baseline='zero', picker=False, pickradius=1, alpha=1, linewidth=0.5, linestyle='solid', edgecolor=(0.6, 0.6, 0.6, 1.0))
            self.isBasePlottingNeeded = False
            self.overlayLesionStripActivated = True

            for i in range(len(self.polyCollection)):
                self.polyCollection[i].set_alpha(0.1)  # lighten the background
            self.canvasDefault.draw()
            return
        else:
            if self.overlayLesionStripActivated:  # If overlay already activated once, hide them
                for i in range(len(self.polyCollectionOverlayStackPlot)):
                    self.polyCollectionOverlayStackPlot[i].set_visible(False)
                self.canvasDefault.draw()


        if updateColorIndex is not None:
            if len(updateColorIndex) > 0:
                # reset original colors
                for i in range(len(self.polyCollection)):
                    self.polyCollection[i].set_facecolor(tempColors[i])
                    self.polyCollection[i].set_alpha(0.7)

                for colorIndex in updateColorIndex:
                    newColor = self.adjust_lightness(tempColors[self.graphLegendLabelList.index(str(colorIndex))], 0.6)
                    self.polyCollection[self.graphLegendLabelList.index(str(colorIndex))].set_facecolor(newColor)

            # Clear stackplot colors if there is nothing picked from graph interaction. Checking for empty [] list.
            if len(updateColorIndex) == 0:
                tempColors = list(self.plotColors)
                for i in range(len(self.polyCollection)):
                    self.polyCollection[i].set_facecolor(tempColors[i])
                    self.polyCollection[i].set_alpha(0.7)

        # draw vertical line only without highlighting artists.
        if (vlineXloc != None and updateColorIndex == None):
            self.canvasDefault.draw()
            return
        #print("Enter here", vlineXloc, updateColorIndex)
        if updateColorIndex == None: # Reset graph to default colors.
            tempColors = list(self.plotColors)
            for i in range(len(self.polyCollection)):
                self.polyCollection[i].set_facecolor(tempColors[i])
                self.polyCollection[i].set_alpha(0.7)

        self.canvasDefault.draw()

    def computeIntensityDifference(self, matrix): # TODO: remove this. deprectated. new efficient derivative using diff in place
        output = []
        for i in range(len(matrix)-1):
            output.append([m - n for m,n in zip(matrix[i+1], matrix[i])])
        return output

    def plotIntensityChangeIndicatorGlyphs(self, nodeID):
        #print("plotting Intensity changes")
        if(nodeID == None):
            print("ERROR: Node ID is empty.")
            return

        #dataArray = self.getIntensityDataMatrix(nodeID)
        dataArray = self.getIntensityDataArray(nodeID)
        #print("DIM IS ", dataArray.shape)
        #print("ARRAY IS", intensityArray)
        dataArrayDerivative = diff(dataArray)
        #print("how many items", len(dataArrayDerivative))

        #y0 = dataArrayDerivative[0]
        #y1 = dataArrayDerivative[1]

        y0 = list(np.zeros(self.dataCount-1))
        y1 = list(np.ones(self.dataCount-1))

        x = list(range(1, self.dataCount))

        threshold = 0.004


        xTrendUp = [np.nan] * self.dataCount
        xTrendDown = [np.nan] * self.dataCount
        xSpikeUp = [np.nan] * self.dataCount
        xSpikeDown = [np.nan] * self.dataCount

        yTrendUp = [np.nan] * self.dataCount
        yTrendDown = [np.nan] * self.dataCount
        ySpikeUp = [np.nan] * self.dataCount
        ySpikeDown = [np.nan] * self.dataCount

        for y in range(len(dataArrayDerivative)):
            for x in range(1, self.dataCount):
                if math.isnan(dataArrayDerivative[y][x-1]): # No data point needed at locations where there is nan
                    continue
                if dataArrayDerivative[y][x - 1] > threshold:  # A significant increase.
                    xSpikeUp[x] = x
                    ySpikeUp[x] = y
                    continue
                if dataArrayDerivative[y][x - 1] < -threshold:  # A significant decrease.
                    xSpikeDown[x] = x
                    ySpikeDown[x] = y
                    continue
                if dataArrayDerivative[y][x - 1] > 0:  # An increasing trend of intensities.
                    xTrendUp[x] = x
                    yTrendUp[x] = y
                    continue
                if dataArrayDerivative[y][x - 1] < 0:  # A decreasing trend of intensities.
                    xTrendDown[x] = x
                    xTrendDown[x] = y
                    continue

        if (self.overlayGlyphActive == False):
            markerSize = 50
            # Colors based on color brewer https://colorbrewer2.org/#type=qualitative&scheme=Paired&n=4
            self.scatterTrendUp = self.axDefaultIntensity.scatter(xTrendUp, yTrendUp, s=markerSize, marker=r'$\wedge$', color="#33a02c", linewidth=0.2, edgecolor='#404040')  # increase trend
            self.scatterTrendDown = self.axDefaultIntensity.scatter(xTrendDown, yTrendDown, s=markerSize, marker=r'$\vee$', color="#a6cee3", linewidth=0.2, edgecolor='#404040')  # decrease trend
            self.scatterSpikeUp = self.axDefaultIntensity.scatter(xSpikeUp, ySpikeUp, s=markerSize, marker='^', color = "#b2df8a", linewidth=0.2, edgecolor='#404040')  # significant increase
            self.scatterSpikeDown = self.axDefaultIntensity.scatter(xSpikeDown, ySpikeDown, s=markerSize, marker='v',color="#1f78b4", linewidth=0.2, edgecolor='#404040')  # significant decrease
            #self.scatterTrendUp = self.axDefaultIntensity.plot(xTrendUp, yTrendUp, linestyle='None', markersize=glyphSize, marker=r'$\wedge$', color = "#33a02c", markeredgewidth=0.2, markeredgecolor=(0,0,0,1)) # increase trend
            #self.scatterTrendDown = self.axDefaultIntensity.plot(xTrendDown, yTrendDown, linestyle='None', markersize=glyphSize, marker=r'$\vee$', color="#a6cee3", markeredgewidth=0.2, markeredgecolor=(0,0,0,1))  # decrease trend
            #self.scatterSpikeUp = self.axDefaultIntensity.plot(xSpikeUp, ySpikeUp, linestyle='None', markersize=glyphSize, marker='^', markerfacecolor='g', markeredgewidth=0.2, markeredgecolor=(0,0,0,1))  # significant increase
            #self.scatterSpikeDown = self.axDefaultIntensity.plot(xSpikeDown, ySpikeDown, linestyle='None', markersize=glyphSize, marker='v', color="#1f78b4", markeredgewidth=0.2, markeredgecolor=(0,0,0,1))  # significant decrease
            self.overlayGlyphActive = True  # Glyphs are drawn now
        else:  # Glyphs are already drawn. Just need to refresh.
            offsetValuesTrendUp = np.transpose(np.vstack((xTrendUp, yTrendUp)))
            offsetValuesTrendDown = np.transpose(np.vstack((xTrendDown, yTrendDown)))
            offsetValuesSpikeUp = np.transpose(np.vstack((xSpikeUp, ySpikeUp)))
            offsetValuesSpikeDown = np.transpose(np.vstack((xSpikeDown, ySpikeDown)))
            self.scatterTrendUp.set_offsets(offsetValuesTrendUp)  # increase trend
            self.scatterTrendDown.set_offsets(offsetValuesTrendDown)  # decrease trend
            self.scatterSpikeUp.set_offsets(offsetValuesSpikeUp)  # significant increase
            self.scatterSpikeDown.set_offsets(offsetValuesSpikeDown)  # significant decrease

            #self.canvasDefault.draw()
            #self.canvasDefault.draw()

    def readIntensityDataFromJSON(self, timeList, labelList, modality = "Mean"):
        intensityList = []

        for i in range(len(timeList)):
            #intensityList.append((int(self.structureInfo[str(timeList[i])][0][str(labelList[i])][0]['Mean'])-self.intMin)/(self.intMax-self.intMin))
            intensityList.append(int(self.structureInfo[str(timeList[i])][0][str(labelList[i])][0][modality])/255)
            #print("min is", self.intMin, "max is", self.intMax)
        return intensityList

    def readDiffListFromJSON(self, timeList, labelList, propertyString = "Mean"):  # TODO: remove deprecated
        intensityList = []
        #propertyString = "Mean"
        #if(self.buttonGroupModalities.checkedButton().text() == "T2"):
        #    propertyString = "MeanT2"

        for i in range(len(timeList)):
            #intensityList.append((int(self.structureInfo[str(timeList[i])][0][str(labelList[i])][0]['Mean'])-self.intMin)/(self.intMax-self.intMin))
            intensityList.append(int(self.structureInfo[str(timeList[i])][0][str(labelList[i])][0][propertyString])/255)
            #print("min is", self.intMin, "max is", self.intMax)
        return intensityList

    # Return intensity data for all stackplot artists.
    def getIntensityDataForStackplotArtist(self, nodeOrderForGraph, modalityString = "Mean"):
        intensityMatrix = []
        G = nx.read_gml("asset\\dataset\\Subject1\\preProcess\\lesionGraph.gml")
        #nodeIDList = list(G.nodes)
        dataCount = 81
        for id in nodeOrderForGraph:
            intensityDiffArray = np.empty(dataCount)*np.nan
            timeList = G.nodes[id]["time"]
            labelList = G.nodes[id]["lesionLabel"]
            diffList = self.readDiffListFromJSON(timeList, labelList, modalityString)
            intensityDiffArray[timeList] = [elem for elem in diffList ]
            intensityMatrix.append(intensityDiffArray)
    
        return intensityMatrix

    # Compute and return intensity data as an 1-D array.
    def getIntensityDataArray(self, id):
        intensityArrayT1 = np.empty(self.dataCount)*np.nan
        intensityArrayT2 = np.empty(self.dataCount) * np.nan
        G = nx.read_gml("asset\\dataset\\Subject1\\preProcess\\lesionGraph.gml")
        #connectedComponents = nx.strongly_connected_components(G)
        timeList = G.nodes[str(id)]["time"]
        labelList = G.nodes[str(id)]["lesionLabel"]
        diffListT1 = self.readIntensityDataFromJSON(timeList, labelList, "Mean")
        diffListT2 = self.readIntensityDataFromJSON(timeList, labelList, "MeanT2")
        intensityArrayT1[timeList] = [elem for elem in diffListT1]
        intensityArrayT2[timeList] = [elem for elem in diffListT2]
        pairIntensityData = np.vstack((intensityArrayT1, intensityArrayT2))

        #print("LENGTH IS ", len(intensityArray))
        #print("ARRAY IS", intensityArray)
        return pairIntensityData

    def adjust_lightness(self, color, amount=0.5):
        try:
            c = mc.cnames[color]
        except:
            c = color
        c = colorsys.rgb_to_hls(*mc.to_rgb(c))
        return colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])

    def getLesionData(self, label, time=None, key = None):
        if(time==None):
            time = self.horizontalSlider_TimePoint.value()
        if(key != None): # Return specific attribute data.
            return self.structureInfo[str(time)][0][str(label)][0][key]
        else: # Return everything in dictionary.
            self.overlayDataMain["Lesion ID"] = str(label)
            self.overlayDataMain["Voxel Count"] = self.structureInfo[str(time)][0][str(label+1)][0]["NumberOfPixels"]
            self.overlayDataMain["Physical Size"] = "{0:.2f}".format(self.structureInfo[str(time)][0][str(label+1)][0]["PhysicalSize"])
            self.overlayDataMain["Centroid"] = str("{0:.2f}".format(self.structureInfo[str(time)][0][str(label+1)][0]['Centroid'][0])) +", " +  str("{0:.2f}".format(self.structureInfo[str(time)][0][str(label+1)][0]['Centroid'][0])) + ", " + str("{0:.2f}".format(self.structureInfo[str(time)][0][str(label+1)][0]['Centroid'][0]))
            self.overlayDataMain["Elongation"] = "{0:.2f}".format(self.structureInfo[str(time)][0][str(label+1)][0]['Elongation'])
            self.overlayDataMain["Lesion Perimeter"] = "{0:.2f}".format(self.structureInfo[str(time)][0][str(label+1)][0]['Perimeter'])
            self.overlayDataMain["Lesion Spherical Radius"] = "{0:.2f}".format(self.structureInfo[str(time)][0][str(label+1)][0]['SphericalRadius'])
            self.overlayDataMain["Lesion Spherical Perimeter"] = "{0:.2f}".format(self.structureInfo[str(time)][0][str(label+1)][0]['SphericalPerimeter'])
            self.overlayDataMain["Lesion Flatness"] = "{0:.2f}".format(self.structureInfo[str(time)][0][str(label+1)][0]['Flatness'])
            self.overlayDataMain["Lesion Roundness"] = "{0:.2f}".format(self.structureInfo[str(time)][0][str(label+1)][0]['Roundness'])
            return self.overlayDataMain

    # Handler for time point slider change
    @pyqtSlot()
    def displayLesionBorder_changed(self):
        self.plotIntensityGraph()
        self.canvasIntensity.draw()

    # Handler for show intensity classes change
    @pyqtSlot()
    def checkBox_ShowClasses_changed(self):
        self.plotIntensityGraph()
        self.canvasIntensity.draw()

    # Handler for displaying range comparison for lesions
    @pyqtSlot()
    def checkBox_RangeCompare_changed(self):
        if(self.checkBox_RangeCompare.isChecked() == True):
            self.spinBox_RangeMin.setEnabled(True)
            self.spinBox_RangeMax.setEnabled(True)
            self.pushButton_Compare.setEnabled(True)
            #self.slider3DCompare.setEnabled(True) #  TODO remove completely
        else:
            self.spinBox_RangeMin.setEnabled(False)
            self.spinBox_RangeMax.setEnabled(False)
            self.pushButton_Compare.setEnabled(False)
            #self.slider3DCompare.setEnabled(False)

    # Handler for time point slider change
    @pyqtSlot()
    def on_sliderChangedTimePoint(self):
        sliderValue = self.horizontalSlider_TimePoint.value()
        self.updateDefaultGraph(sliderValue, None) # update graph
        if(self.userPickedLesionID!=None):
            highlightLesionID = self.getLinkedLesionIDFromTimeStep(self.userPickedLesionID, sliderValue)
            #print("highlight id is", highlightLesionID)
            if(highlightLesionID!=None):
                self.userPickedLesionID = highlightLesionID
                self.overlayData = self.getLesionData(highlightLesionID-1)
                self.updateLesionOverlayText()
                self.computeApplyProjection(highlightLesionID, self.surfaceActors[1], self.surfaceActors[2], sliderValue)
            else:
                self.textActorLesionStatistics.SetInput("")
                self.userPickedLesionID = None
                self.style.LastPickedActor = None
                self.clearLesionHighlights()

        self.currentTimeStep = sliderValue
        self.label_currentDataIndex.setText(str(sliderValue))
        self.ren.RemoveAllViewProps()
        for lesion in self.LesionActorList[sliderValue]:
            lesion.GetProperty().SetColor(0.6196078431372549, 0.7372549019607843, 0.8549019607843137) # default lesion color
            lesionID = int(lesion.GetProperty().GetInformation().Get(self.keyID))
            if(self.userPickedLesionID!=None):
                if(lesionID == highlightLesionID-1):
                    lesion.GetProperty().SetColor(1.0, 0.9686274509803922, 0.7372549019607843) # yellowish color
            self.ren.AddActor(lesion)
        self.ren.AddActor(self.surfaceActors[0]) # ventricle
        self.ren.AddActor(self.textActorLesionStatistics) # Text overlay

        #self.ren.ResetCamera()
        self.iren.Render()

    # Handler for capturing the screenshot.
    @pyqtSlot()
    def on_click_CaptureScreeshot(self):
        Utils.captureScreenshot(self.ren.GetRenderWindow())
        #Utils.captureScreenshot(self.renDualLeft.GetRenderWindow())
        Utils.captureScreenshot(self.renNodeGraph.GetRenderWindow())

    # Handler for Riso slider change
    @pyqtSlot()
    def on_sliderChangedRiso(self):
        sliderValue = self.horizontalSlider_Riso.value()
        self.R_ISO = sliderValue * (0.3/99)
        self.label_Riso.setText(str("{:.1f}".format(self.R_ISO*100)+"%"))
        self.plotIntensityGraph()
        self.canvasIntensity.draw()

    # Compute projection for a selected lesion and apply it on active surface.
    def computeApplyProjection(self, highlightLesionID, surfaceLh, surfaceRh, sliderValue = None):
        if(sliderValue == None):
            sliderValue = self.horizontalSlider_TimePoint.value()
        dataKey = ""
        if (str(self.comboBox_ProjectionMethods.currentText())=="DTI"):
            dataKey = "DTI"
        if (str(self.comboBox_ProjectionMethods.currentText())=="Heat Equation"):
            dataKey = ""
        if (str(self.comboBox_ProjectionMethods.currentText())=="Danielsson"):
            dataKey = "Danielsson"

        # Project on brain surface.
        affectedLh = np.asarray(self.structureInfo[str(sliderValue)][0][str(highlightLesionID)][0]["AffectedPointIdsLh"+dataKey])
        affectedRh = np.asarray(self.structureInfo[str(sliderValue)][0][str(highlightLesionID)][0]["AffectedPointIdsRh"+dataKey])
        lesionMappingLh = np.isin(self.vertexIndexArrayLh, affectedLh)
        lesionMappingRh = np.isin(self.vertexIndexArrayRh, affectedRh)
        cLh = np.full(self.numberOfPointsLh*3,255, dtype='B')
        cRh = np.full(self.numberOfPointsRh*3,255, dtype='B')
        cLh =cLh.astype('B').reshape((self.numberOfPointsLh,3))
        cRh =cRh.astype('B').reshape((self.numberOfPointsRh,3))
        cLh[lesionMappingLh==True] = [255,0,0]
        cRh[lesionMappingRh==True] = [255,0,0]
        self.vtk_colorsLh.SetArray(cLh, cLh.size, True)
        self.vtk_colorsRh.SetArray(cRh, cRh.size, True)
        surfaceLh.GetMapper().GetInput().GetPointData().SetActiveScalars("projection")
        surfaceLh.GetMapper().GetInput().GetPointData().SetScalars(self.vtk_colorsLh)
        surfaceRh.GetMapper().GetInput().GetPointData().SetActiveScalars("projection")
        surfaceRh.GetMapper().GetInput().GetPointData().SetScalars(self.vtk_colorsRh)

        self.irenDual.Render()

    def clearLesionHighlights(self, timeStep = None):
        if(timeStep == None):
            timeStep = self.horizontalSlider_TimePoint.value()
        for lesion in self.LesionActorList[timeStep]:
            lesion.GetProperty().SetColor(0.6196078431372549, 0.7372549019607843, 0.8549019607843137) # default lesion color

    # Get lesion ID of any timestep provided the current ID and timestep.
    def getLinkedLesionIDFromTimeStep(self, currentLesionID, queryTimeStep=None):
        if(queryTimeStep == None):
            queryTimeStep = self.horizontalSlider_TimePoint.value()
        nodeIDList = list(self.G.nodes)
        for id in nodeIDList:
            timeList = self.G.nodes[id]["time"]
            labelList = self.G.nodes[id]["lesionLabel"]
            temporalData = list(zip(timeList, labelList))
            if((self.currentTimeStep, currentLesionID) in list(temporalData)):
                result = [elem[1] for elem in temporalData if elem[0]==queryTimeStep]
                if(len(result)!=0):
                    return result[0]
        return None

    # Get node ID for picked lesion.
    def getNodeIDforPickedLesion(self, pickedLesionID):
        timeStep = self.horizontalSlider_TimePoint.value()
        nodeIDList = list(self.G.nodes)
        for id in nodeIDList:
            timeList = self.G.nodes[id]["time"]
            labelList = self.G.nodes[id]["lesionLabel"]
            temporalData = list(zip(timeList, labelList))
            if((self.currentTimeStep, pickedLesionID) in list(temporalData)):
                return id
        return None

    # Load data automatically - To be removed in production.
    def autoLoadData(self):
        self.ren.RemoveAllViewProps()
        self.renDual.RemoveAllViewProps()
        self.iren.Render()
        self.irenDual.Render()
        self.folder = "asset\\dataset\\Subject1\\"
        if self.folder:
            self.lineEdit_DatasetFolder.setText(self.folder)
            self.LesionActorList = [[] for i in range(81)]
            self.surfaceActors = []
            if(self.readThread != None):
                self.readThread.terminate()
            self.readThread = QThread()
            self.worker = Utils.ReadThread(self.folder, self.LesionActorList, self.surfaceActors, self.keyType, self.keyID)
            self.worker.moveToThread(self.readThread)
            self.readThread.started.connect(self.worker.run)
            self.worker.progress.connect(self.reportProgress)
            self.worker.finished.connect(self.renderData)
            self.readThread.start()

    # Slider to capture range (left) for 3d comparison.
    def compare3DRangeSliderChangedLeft(self,val):
        self.spinBox_RangeMin.setValue(val)

    # Slider to capture range (right) for 3d comparison.
    def compare3DRangeSliderChangedRight(self,val):
        self.spinBox_RangeMax.setValue(val)

    # Slider to capture range for graph comparison.
    def graphRangeSliderChanged(self,val):
        print("graph slider changed", val)

    # Compare lesion changes between two time points and then update lesion surface display.
    def compareDataAndUpdateSurface(self):
        baselineIndex = self.spinBox_RangeMin.value()
        followupIndex = self.spinBox_RangeMax.value()
        #print(baselineIndex, followupIndex)
        rootFolder = "asset\\dataset\\Subject1\\"
        connectedComponentOutputFileName = rootFolder + "lesionMask\\ConnectedComponentsTemp.nii"
        
        # Creating uinion image
        maskFileName1 = rootFolder + "lesionMask\\Consensus" + str(baselineIndex) + ".nii"
        maskFileName2 = rootFolder + "lesionMask\\Consensus" + str(followupIndex) + ".nii"
        niftiReaderLesionMask1 = vtk.vtkNIFTIImageReader()
        niftiReaderLesionMask1.SetFileName(maskFileName1)
        niftiReaderLesionMask1.Update()
        niftiReaderLesionMask2 = vtk.vtkNIFTIImageReader()
        niftiReaderLesionMask2.SetFileName(maskFileName2)
        niftiReaderLesionMask2.Update()
        orImageFilter = vtk.vtkImageLogic()
        orImageFilter.SetInput1Data(niftiReaderLesionMask1.GetOutput())
        orImageFilter.SetInput2Data(niftiReaderLesionMask2.GetOutput())
        orImageFilter.SetOperationToOr()
        orImageFilter.Update()
        writer = vtk.vtkNIFTIImageWriter()
        writer.SetFileName("D:\\union.nii")
        writer.SetInputData(orImageFilter.GetOutput())
        writer.Write()

        # Creating subtracted image
        castedImage1 = vtk.vtkImageCast()
        castedImage1.SetInputData(niftiReaderLesionMask1.GetOutput())
        castedImage1.SetOutputScalarTypeToFloat()
        castedImage1.Update()
        castedImage2 = vtk.vtkImageCast()
        castedImage2.SetInputData(niftiReaderLesionMask2.GetOutput())
        castedImage2.SetOutputScalarTypeToFloat()
        castedImage2.Update()
        subtractImageFilter = vtk.vtkImageMathematics()
        subtractImageFilter.SetInput1Data(castedImage1.GetOutput())
        subtractImageFilter.SetInput2Data(castedImage2.GetOutput())
        subtractImageFilter.SetOperationToSubtract()
        subtractImageFilter.Update()
        writer.SetFileName("D:\\shr.nii")
        writer.SetInputData(subtractImageFilter.GetOutput())
        writer.Write()

        uinionImage = sitk.ReadImage("D:\\union.nii")
        connectedComponentFilter = sitk.ConnectedComponentImageFilter()
        connectedComponentImage = connectedComponentFilter.Execute(uinionImage)
        sitk.WriteImage(connectedComponentImage, connectedComponentOutputFileName)
        lesionCount = connectedComponentFilter.GetObjectCount()
        # Load lesion mask
        niftiReaderLesionMask = vtk.vtkNIFTIImageReader()
        niftiReaderLesionMask.SetFileName(connectedComponentOutputFileName)
        niftiReaderLesionMask.Update()

        # Read QForm matrix from mask data.
        QFormMatrixMask = niftiReaderLesionMask1.GetQFormMatrix()
        qFormListMask = [0] * 16 #the matrix is 4x4
        QFormMatrixMask.DeepCopy(qFormListMask, QFormMatrixMask)
        transform = vtk.vtkTransform()
        transform.Identity()
        transform.SetMatrix(qFormListMask)
        transform.Update()

        surface = vtk.vtkDiscreteMarchingCubes()
        surface.SetInputConnection(niftiReaderLesionMask.GetOutputPort())
        for i in range(lesionCount):
            surface.SetValue(i,i+1)
        surface.Update()

        transform = vtk.vtkTransform()
        transform.Identity()
        transform.SetMatrix(qFormListMask)
        transform.Update()
        transformFilter = vtk.vtkTransformFilter()
        transformFilter.SetInputConnection(surface.GetOutputPort())
        transformFilter.SetTransform(transform)
        transformFilter.Update()

        niftiReaderDifferenceImage = vtk.vtkNIFTIImageReader()
        niftiReaderDifferenceImage.SetFileName("D:\\shr.nii")
        niftiReaderDifferenceImage.Update()

        transformVolumeFilter = vtk.vtkTransformFilter()
        transformVolumeFilter.SetInputConnection(niftiReaderDifferenceImage.GetOutputPort())
        transformVolumeFilter.SetTransform(transform)
        transformVolumeFilter.Update()

        multiBlockDataset = vtk.vtkMultiBlockDataSet()
        for i in range(lesionCount):
            threshold = vtk.vtkThreshold()
            #threshold.SetInputData(surface.GetOutput())
            threshold.SetInputData(transformFilter.GetOutput())
            threshold.ThresholdBetween(i+1,i+1)
            threshold.Update()
            geometryFilter = vtk.vtkGeometryFilter()
            geometryFilter.SetInputData(threshold.GetOutput())
            geometryFilter.Update()
            lesionMapper = vtk.vtkOpenGLPolyDataMapper()
            lesionMapper.SetInputData(geometryFilter.GetOutput())
            lesionMapper.Update()   
            probeFilter = vtk.vtkProbeFilter()
            #probeFilter.SetSourceData(niftiReaderDifferenceImage.GetOutput())
            probeFilter.SetSourceData(transformVolumeFilter.GetOutput())
            probeFilter.SetInputData(lesionMapper.GetInput())
            probeFilter.CategoricalDataOff()
            probeFilter.Update()    

            scalars = probeFilter.GetOutput().GetPointData().GetScalars()
            lesionMapper.GetInput().GetPointData().SetActiveScalars("difference")
            lesionMapper.GetInput().GetPointData().SetScalars(scalars)
            lesionMapper.SetScalarRange(-127,127)
            numberOfPoints = scalars.GetNumberOfTuples()

            #transformFilter = vtk.vtkTransformFilter()
            #transformFilter.SetInputData(lesionMapper.GetInput())
            #transformFilter.SetTransform(transform)
            #transformFilter.Update()
            #multiBlockDataset.SetBlock(i,transformFilter.GetOutput())
            multiBlockDataset.SetBlock(i,lesionMapper.GetInput())

        nc = vtk.vtkNamedColors()

        lut = vtk.vtkLookupTable()
        lut.SetNumberOfTableValues(3)
        lut.SetTableRange(-128, 128)
        lut.Build()

        lut.SetTableValue(0,nc.GetColor4d("LightCoral"))
        lut.SetTableValue(1,nc.GetColor4d("LightSlateGray"))
        lut.SetTableValue(2,nc.GetColor4d("PaleGreen"))

        actorList = []
        for i in range(multiBlockDataset.GetNumberOfBlocks()):
            block = multiBlockDataset.GetBlock(i)
            newpoly = Utils.smoothPolyData(block)

            mapper = vtk.vtkPolyDataMapper()
            #mapper.SetInputData(block)
            mapper.SetInputData(newpoly)
            mapper.SetScalarRange(-128,128)
            mapper.SetLookupTable(lut)
            lesionActor = vtk.vtkActor()
            lesionActor.SetMapper(mapper)
            actorList.append(lesionActor)
        
        # Update renderer
        self.ren.RemoveAllViewProps()
        for lesion in actorList:
            self.ren.AddActor(lesion)
        self.ren.AddActor(self.surfaceActors[0]) # ventricle
        self.iren.Render()

    # # Load intensity analysis page.
    # def loadIntensityAnalysisPage(self):
    #     self.initializeIntensityGlyphGraph()
    #     self.plotIntensityGlyphGraph()
    #     self.stackedWidget_Graphs.setCurrentIndex(4)

    '''
    ##########################################################################
        Callback function for graph selection.
    ##########################################################################
    '''

    def graphSelectionCallback(self, obj, event):
        # arr = obj.GetCurrentSelection().GetNode(1).GetSelectionList()
        # for elem in arr:
        #     print(elem)
        numberOfTuples = obj.GetCurrentSelection().GetNode(1).GetSelectionList().GetNumberOfTuples()
        selectedNodes = [0] * numberOfTuples
        for tupleIndex in range(numberOfTuples):
            d = list(obj.GetCurrentSelection().GetNode(1).GetSelectionList().GetTuple(tupleIndex))
            selectedNodes[tupleIndex] = d

        flatListFloat = list(itertools.chain.from_iterable(selectedNodes))
        flatListInt = [int(a) + 1 for a in flatListFloat]  # Adding 1 to correct lesion numbering
        #print(flatListInt)

        # Clear all lesions
        for lesion in self.LesionActorList[self.currentTimeStep]:
            lesion.GetProperty().SetColor(0.6196078431372549, 0.7372549019607843, 0.8549019607843137)  # default lesion color

        for nodeIndex in range(len(flatListInt)):
            for lesion in self.LesionActorList[self.currentTimeStep]:
                lesionid = int(lesion.GetProperty().GetInformation().Get(self.keyID)) + 1
                nodeIDForLesion = self.getNodeIDforPickedLesion(lesionid)
                if str(nodeIDForLesion) == str(flatListInt[nodeIndex]):
                    lesion.GetProperty().SetColor(1.0, 0.9686274509803922, 0.7372549019607843)  # yellowish color
        self.iren.Render()

        # Update and highlight elements in stackplot
        self.updateDefaultGraph(None, flatListInt)

    # Handler for browse folder button click.
    @pyqtSlot()
    def on_click_browseFolder(self):
        self.ren.RemoveAllViewProps()
        self.renDual.RemoveAllViewProps()
        self.iren.Render()
        self.irenDual.Render()
        self.folder = str(QFileDialog.getExistingDirectory(self, "Select Patient Directory"))
        if self.folder:
            self.lineEdit_DatasetFolder.setText(self.folder)
            self.LesionActorList = [[] for i in range(81)]
            self.surfaceActors = []
            self.readThread = QThread()
            self.worker = Utils.ReadThread(self.folder, self.LesionActorList, self.surfaceActors)
            self.worker.moveToThread(self.readThread)
            self.readThread.started.connect(self.worker.run)
            self.worker.progress.connect(self.reportProgress)
            self.worker.finished.connect(self.renderData)
            self.readThread.start()

# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#     window = mainWindow()
#     window.setupUI()
#     window.show()
#     sys.exit(app.exec_())



###########################################
# QApplication ############################
###########################################
app = QtWidgets.QApplication(sys.argv)
window = mainWindow()
sys.exit(app.exec_())