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
from OpenGL import GL

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
from matplotlib import colors
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.cm as cm
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import nibabel as nib
import json
import random
from scipy.ndimage.filters import gaussian_filter1d
import seaborn as sns

# Main window class.
class mainWindow(Qt.QMainWindow):
    # Initialization
    def __init__(self):
        super(mainWindow, self).__init__()
        ui = os.path.join(os.path.dirname(__file__), 'mstemporal_uifile.ui')
        uic.loadUi(ui, self)
        self.initUI()
        self.initVTK()
        self.showMaximized()

    def showDialog(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Loading Data...Please wait...")
        msgBox.setStyleSheet("background-color: rgb(46,46,46); color:rgb(200,200,200); font: 10pt 'Google Sans';")
        msgBox.setEscapeButton(None)
        msgBox.exec()
        dlg = QDialog(self)
        dlg.setWindowTitle("HELLO!")
        dlg.exec_()

    # UI setup.
    def initUI(self):  
        vtk.vtkObject.GlobalWarningDisplayOff() # Supress warnings.
        #print("\033[1;101m STARTING APPLICATION... \033[0m")
        pmMain = Qt.QPixmap("icons\\AppLogo.png")
        self.logoLabel.setPixmap(pmMain.scaled(self.logoLabel.size().width(), self.logoLabel.size().height(), 1,1))
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

        # Handlers
        #self.pushButton_LoadFolder.clicked.connect(self.on_click_browseFolder) # Attaching button click handler.
        self.pushButton_LoadFolder.clicked.connect(self.autoLoadData) # Attaching button click handler.
        self.horizontalSlider_TimePoint.valueChanged.connect(self.on_sliderChangedTimePoint) # Attaching slider value changed handler.
        self.mprA_Slice_Slider.valueChanged.connect(self.on_sliderChangedMPRA)
        self.mprB_Slice_Slider.valueChanged.connect(self.on_sliderChangedMPRB)
        self.mprC_Slice_Slider.valueChanged.connect(self.on_sliderChangedMPRC)
        self.comboBox_LesionAttributes.currentTextChanged.connect(self.on_combobox_changed_LesionAttributes) # Attaching handler for lesion filter combobox selection change.
        self.comboBox_ProjectionMethods.currentTextChanged.connect(self.on_combobox_changed_ProjectionMethods) # Attaching handler for projection methods combobox selection change.

    # Initialize vtk
    def initVTK(self):
        self.dataFolderInitialized = False
        # Renderer for lesions.
        self.vl = Qt.QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0.0627, 0.0627, 0.0627)
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

        self.vlDual = Qt.QVBoxLayout()
        self.vtkWidgetDual = QVTKRenderWindowInteractor(self.frameDual)
        self.vlDual.addWidget(self.vtkWidgetDual)
        self.renDual = vtk.vtkRenderer()
        self.renDual.SetBackground(0.0627, 0.0627, 0.0627)
        self.vtkWidgetDual.GetRenderWindow().AddRenderer(self.renDual)
        self.irenDual = self.vtkWidgetDual.GetRenderWindow().GetInteractor()
        self.irenDual.SetRenderWindow(self.vtkWidgetDual.GetRenderWindow())
        self.renDual.ResetCamera()
        self.frameDual.setLayout(self.vlDual)
        self.styleSurface = Utils.CustomMouseInteractorSurface(self)
        self.styleSurface.SetDefaultRenderer(self.renDual)
        self.styleSurface.main = self
        self.irenDual.SetInteractorStyle(self.styleSurface)
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
        self.dataCount = 0
        self.vtk_colorsLh = vtk.vtkUnsignedCharArray()
        self.vtk_colorsRh = vtk.vtkUnsignedCharArray()
        self.vtk_colorsLh.SetNumberOfComponents(3)
        self.vtk_colorsRh.SetNumberOfComponents(3)

        self.textActorLesionStatistics = vtk.vtkTextActor()
        self.textActorLesionStatistics.UseBorderAlignOff()
        self.textActorLesionStatistics.SetPosition(1,0)
        self.textActorLesionStatistics.GetTextProperty().SetFontFamily(4)
        self.textActorLesionStatistics.GetTextProperty().SetFontFile("asset\\GoogleSans-Medium.ttf")
        self.textActorLesionStatistics.GetTextProperty().SetFontSize(12)
        #self.textActorLesionStatistics.GetTextProperty().ShadowOn()
        self.textActorLesionStatistics.GetTextProperty().SetColor( 0.3411, 0.4824, 0.3608 )

        self.buttonGroupGraphs = QButtonGroup()
        self.buttonGroupGraphs.addButton(self.pushButton_DefaultGraph)
        self.buttonGroupGraphs.addButton(self.pushButton_GraphView)
        self.buttonGroupGraphs.setExclusive(True)
        self.buttonGroupGraphs.buttonClicked.connect(self.on_buttonGroupGraphsChanged)

        self.buttonGroupSurfaces = QButtonGroup()
        self.buttonGroupSurfaces.addButton(self.radioButton_White)
        self.buttonGroupSurfaces.addButton(self.radioButton_Inflated)
        self.buttonGroupSurfaces.setExclusive(True)
        self.buttonGroupSurfaces.buttonClicked.connect(self.on_buttonGroupSurfaceChanged)

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
        pass

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

    # Handler for mode change inside button group (graphs)
    @pyqtSlot(QAbstractButton)
    def on_buttonGroupGraphsChanged(self, btn):
        if(self.dataFolderInitialized == True):
            if(self.buttonGroupGraphs.checkedId() == -3): # Stream graph
                self.stackedWidget_Graphs.setCurrentIndex(0)

            if(self.buttonGroupGraphs.checkedId() == -2): # Graph vis
                self.stackedWidget_Graphs.setCurrentIndex(1)

    def updateLesionOverlayText(self):
        overlayText = ""
        for key in self.overlayDataMain.keys():
            overlayText = overlayText + "\n" + str(key) + ": " + str(self.overlayDataMain[key])
        self.textActorLesionStatistics.SetInput(overlayText)
        
    def renderData(self):
        Utils.smoothSurface(self.surfaceActors[0])
        self.dataCount = len(self.LesionActorList)
        self.horizontalSlider_TimePoint.setMaximum(self.dataCount-1)
        for lesion in self.LesionActorList[0]:
            self.ren.AddActor(lesion)
        self.ren.AddActor(self.surfaceActors[0]) # ventricle
        self.ren.ResetCamera()
        self.iren.Render()
        openglRendererInUse = self.ren.GetRenderWindow().ReportCapabilities().splitlines()[1].split(":")[1].strip()
        self.textEdit_Information.append("Resource: " + str(openglRendererInUse))

        self.renDual.AddActor(self.surfaceActors[1])
        self.renDual.AddActor(self.surfaceActors[2])
        self.renDual.ResetCamera()
        self.irenDual.Render()

        self.readInitializeLesionJSONData() # Read lesion data from JSON file.
        self.displayOrientationCube() # Display orientation cube
        self.LoadStructuralSlices(self.folder, "T1", 0, True) # load slices
        self.initializeDefaultGraph() # Load graph data
        self.initializeGraphVis() # Load graph visualization.
        self.activateControls() # Activate controls.
        self.ren.AddActor2D(self.textActorLesionStatistics) # Add lesion statistics overlay.
        self.dataFolderInitialized = True
        self.currentTimeStep = self.horizontalSlider_TimePoint.value()
        self.numberOfPointsLh = self.surfaceActors[3].GetMapper().GetInput().GetNumberOfPoints()
        self.numberOfPointsRh = self.surfaceActors[4].GetMapper().GetInput().GetNumberOfPoints()
        self.vtk_colorsLh.SetNumberOfTuples(self.numberOfPointsLh)
        self.vtk_colorsRh.SetNumberOfTuples(self.numberOfPointsRh)
        self.vertexIndexArrayLh = np.arange(self.numberOfPointsLh)
        self.vertexIndexArrayRh = np.arange(self.numberOfPointsRh)

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
            self.slice_MPRA = np.rot90(self.slice_MPRA)
            self.sliceMask_MPRA = np.rot90(self.sliceMask_MPRA)
        if(self.radioButton_FLAIR.isChecked() == True):
            aspectCoronalData = self.spacingData[2]/self.spacingData[1]
            aspectCoronalMask = self.spacingMask[2]/self.spacingMask[1]
        else:
            aspectCoronalData = self.spacingData[2]/self.spacingData[0]
            aspectCoronalMask = self.spacingMask[2]/self.spacingMask[0]

        my_cmap = self.MPROverlayColorMap
        my_cmap.set_under('k', alpha=0) # For setting background to alpha 0

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

    # Display orientation cube.
    def displayOrientationCube(self):
        self.axesActor = vtk.vtkAnnotatedCubeActor()
        self.axesActor.SetXPlusFaceText('R')
        self.axesActor.SetXMinusFaceText('L')
        self.axesActor.SetYMinusFaceText('H')
        self.axesActor.SetYPlusFaceText('F')
        self.axesActor.SetZMinusFaceText('P')
        self.axesActor.SetZPlusFaceText('A')
        self.axesActor.GetTextEdgesProperty().SetColor(1,1,1)
        self.axesActor.GetTextEdgesProperty().SetLineWidth(1)
        self.axesActor.GetCubeProperty().SetColor(0.7804, 0.4824, 0.4824)
        self.axes = vtk.vtkOrientationMarkerWidget()
        self.axes.SetOrientationMarker(self.axesActor)
        self.axes.SetViewport( 0.9, 0.9, 1.0, 1.0 )
        self.axes.SetCurrentRenderer(self.ren)
        self.axes.SetInteractor(self.iren)
        self.axes.EnabledOn()

        self.axesActorDual = vtk.vtkAnnotatedCubeActor()
        self.axesActorDual.SetXPlusFaceText('R')
        self.axesActorDual.SetXMinusFaceText('L')
        self.axesActorDual.SetYMinusFaceText('H')
        self.axesActorDual.SetYPlusFaceText('F')
        self.axesActorDual.SetZMinusFaceText('P')
        self.axesActorDual.SetZPlusFaceText('A')
        self.axesActorDual.GetTextEdgesProperty().SetColor(1,1,1)
        self.axesActorDual.GetTextEdgesProperty().SetLineWidth(1)
        self.axesActorDual.GetCubeProperty().SetColor(0.7804, 0.4824, 0.4824)
        self.axesDual = vtk.vtkOrientationMarkerWidget()
        self.axesDual.SetOrientationMarker(self.axesActorDual)
        self.axesDual.SetViewport( 0.9, 0.9, 1.0, 1.0 )
        self.axesDual.SetCurrentRenderer(self.renDual)
        self.axesDual.SetInteractor(self.irenDual)
        self.axesDual.EnabledOn()

    def initializeDefaultGraph(self):
        self.vl_default = Qt.QVBoxLayout()
        self.figureDefault = plt.figure(num = 3, frameon=False, clear=True)
        self.canvasDefault = FigureCanvas(self.figureDefault)
        self.vl_default.addWidget(self.canvasDefault)
        self.frameDefaultGraph.setLayout(self.vl_default)
        self.plotDefaultGraph("PhysicalSize")

    def initializeGraphVis(self):
        self.vl_graph = Qt.QVBoxLayout()
        self.figureGraph = plt.figure(num = 4, frameon=False, clear=True)
        self.canvasGraph = FigureCanvas(self.figureGraph)
        self.vl_graph.addWidget(self.canvasGraph)
        self.frameGraphVis.setLayout(self.vl_graph)
        self.plotGraphVis()

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
        self.slice_MPRA = np.rot90(self.epi_img_data[self.midSliceX, :, :])
        self.sliceMask_MPRA = np.rot90(self.alpha_mask[self.midSliceX, :, :])
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
        self.MPRC.set_data(self.slice_MPRC)
        self.sliceNumberHandleMPRC.set_text(self.midSliceZ)
        self.MPRCMask.set_data(self.sliceMask_MPRC)
        self.canvasMPRC.draw()

    # Actvate controls after dataset is loaded.
    def activateControls(self):
        self.mprA_Slice_Slider.setEnabled(True)
        self.mprB_Slice_Slider.setEnabled(True)
        self.mprC_Slice_Slider.setEnabled(True)

    # Plot graph visual
    def plotGraphVis(self):
        self.figureGraph.clear()
        plt.figure(4)
        plt.rcParams['font.family'] = 'Google Sans'
        plt.tight_layout()
        self.axGraph = self.figureGraph.add_subplot(111)
        #plt.subplots_adjust(wspace=None, hspace=None)
        plt.subplots_adjust(left=0.05, bottom=0.05, right=0.98, top=0.98)
        G = nx.read_gml("D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\preProcess\\lesionGraph.gml")
        edges = G.edges()
        weights = [3 for u,v in edges]
        nx.draw_planar(G, with_labels=True, node_size=800, node_color="#e54c66", node_shape="h", edge_color="#f39eac", font_color="#f39eac", font_weight="bold", alpha=0.5, linewidths=5, width=weights, arrowsize=20)
        #nx.draw_shell(G, with_labels=True, node_size=800, node_color="#c87b7b", node_shape="h", edge_color="#f39eac", font_color="#f39eac", font_weight="bold", alpha=0.5, linewidths=5, width=weights, arrowsize=20)
        self.canvasGraph.draw()

    def computeNodeOrderForGraph(self, G): #TODO NEED TO UPDATE CODE to support multilevel activity (eg split and merge in one sequence)
        # color palette
        #numberOfConnectedComponents = len(list(nx.strongly_connected_components(G))) # gets the number of disconnected components in the graph
        #print(numberOfConnectedComponents)
         
        #  
        nodeIDList = list(G.nodes)
        streamPlotDataColors = sns.color_palette("Set2", len(nodeIDList)) # visually pleasing colors from color brewer.
        nodesAndDegreesUndirected =  list(G.degree(nodeIDList))
        nodesAndDegreesDirectedOut =  list(G.out_degree(nodeIDList))
        nodesAndDegreesDirectedIn =  list(G.in_degree(nodeIDList))
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

    def onClickDefaultStreamGraphCanvas(self, event):
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #     ('double' if event.dblclick else 'single', event.button,
        #     event.x, event.y, event.xdata, event.ydata))
        if event.dblclick:
            print("double click")
        if(event.xdata != None):
            x_loc = int(round(event.xdata))
            print("click inside graph")
            self.updateDefaultGraph(x_loc, None)
        else:
            print("click outside graph")
            self.updateDefaultGraph(None, None)

    def onPickDefaultStreamGraphCanvas(self, event):
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #     ('double' if event.dblclick else 'single', event.button,
        #     event.x, event.y, event.xdata, event.ydata))
        thisline = event.artist
        labelValue = thisline.get_label()
        #artist = event.artist
        #ind = event.ind
        #print('onpick1 line:', labelValue)
        self.updateDefaultGraph(None, labelValue)
           
    # plot default graph
    def plotDefaultGraph(self, lesionAttributeString): 
        # clearing old figures
        self.figureDefault.clear()
        self.figureDefault.tight_layout()
        plt.figure(3)
        # create an axis
        self.axDefault = self.figureDefault.add_subplot(111)
        plt.subplots_adjust(wspace=None, hspace=None)
        #plt.axvline(x=40, linewidth=4, color='y')

        # Data for plotting
        self.G = nx.read_gml("D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\preProcess\\lesionGraph.gml")
        self.UG = self.G.to_undirected()
        self.sub_graphs = list(nx.connected_components(self.UG))
        nodeOrderForGraph, self.plotColors = self.computeNodeOrderForGraph(self.G)

        ys = []
        dataArray = []
        self.graphLegendLabelList = []
        for id in nodeOrderForGraph:
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
            dataArray.append(arr)

        x = np.linspace(0, self.dataCount, self.dataCount)
        #random.shuffle(dataArray)
        ys = dataArray
        self.polyCollection = self.axDefault.stackplot(x, ys, baseline='zero', picker=True, pickradius=1, labels = self.graphLegendLabelList, linewidth=0.5, edgecolor='white', colors = self.plotColors)
        self.axDefault.set_facecolor((0.0627, 0.0627, 0.0627))
        self.axDefault.xaxis.label.set_color((0.6, 0.6, 0.6))
        self.axDefault.yaxis.label.set_color((0.6, 0.6, 0.6))
        self.axDefault.spines['bottom'].set_color((0.3411, 0.4824, 0.3608))
        self.axDefault.spines['bottom'].set_linewidth(2)
        self.axDefault.spines['left'].set_color((0.3411, 0.4824, 0.3608))
        self.axDefault.spines['left'].set_linewidth(2)
        self.axDefault.spines['right'].set_visible(False)
        self.axDefault.spines['top'].set_visible(False)
        self.axDefault.tick_params(axis='x', colors=(0.6, 0.6, 0.6))
        self.axDefault.tick_params(axis='y', colors=(0.6, 0.6, 0.6))
        self.axDefault.set_xlabel("followup instance", fontname="Arial", fontsize=12)
        self.axDefault.set_ylabel(lesionAttributeString, fontname="Arial", fontsize=12)
        self.axDefault.set_title("activity graph", fontname="Arial", fontsize=15)
        self.axDefault.title.set_color((0.6, 0.6, 0.6))
        plt.xlim(xmin=0)
        plt.xlim(xmax=self.dataCount-1)
        #self.axDefault.grid()
        #fig.savefig("test.png")
        #plt.show()
        self.canvasDefault.draw()
        self.canvasDefault.mpl_connect('pick_event', self.onPickDefaultStreamGraphCanvas)
        self.canvasDefault.mpl_connect('button_press_event', self.onClickDefaultStreamGraphCanvas)
        self.defaultGraphBackup = self.canvasDefault.copy_from_bbox(self.axDefault.bbox)

        self.vLine = None

    # update default graph
    def updateDefaultGraph(self, vlineXloc=None, updateColorIndex=None):
        plt.figure(3)
        #self.canvasDefault.restore_region(self.defaultGraphBackup)
        if(vlineXloc != None):
            if(self.vLine == None):
                self.vLine = plt.axvline(x=vlineXloc, linewidth=1, color='r', linestyle='--')
            else:
                self.vLine.set_xdata([vlineXloc])
        else:
            if(self.vLine != None):
                self.vLine.remove()
                self.vLine = None

        if(updateColorIndex!=None):
            tempColors = list(self.plotColors)
            newColor = self.adjust_lightness(tempColors[self.graphLegendLabelList.index(updateColorIndex)], 0.6)

            for i in range(len(self.polyCollection)):
                self.polyCollection[i].set_facecolor(tempColors[i])

            updateIndex = self.graphLegendLabelList.index(updateColorIndex)
            for item in self.sub_graphs:
                if(updateColorIndex in item):
                    for nodeIndex in item:
                        self.polyCollection[self.graphLegendLabelList.index(nodeIndex)].set_facecolor(newColor)

        if(vlineXloc==None and updateColorIndex==None): # Reset graph to default colors.
            tempColors = list(self.plotColors)
            for i in range(len(self.polyCollection)):
                self.polyCollection[i].set_facecolor(tempColors[i])

        self.canvasDefault.draw()

    def adjust_lightness(self, color, amount=0.5):
        import matplotlib.colors as mc
        import colorsys
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
    def on_sliderChangedTimePoint(self):
        sliderValue = self.horizontalSlider_TimePoint.value()
        if(self.userPickedLesionID!=None):
            highlightLesionID = self.getLinkedLesionIDFromTimeStep(self.userPickedLesionID, sliderValue)
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
            lesion.GetProperty().SetColor(0.7804, 0.4824, 0.4824) # default lesion color
            lesionID = int(lesion.GetProperty().GetInformation().Get(self.keyID))
            if(self.userPickedLesionID!=None):
                if(lesionID == highlightLesionID-1):
                    lesion.GetProperty().SetColor(0.4627, 0.4627, 0.9568) # A blueish color.
            self.ren.AddActor(lesion)
        self.ren.AddActor(self.surfaceActors[0]) # ventricle
        self.ren.AddActor(self.textActorLesionStatistics) # Text overlay
        self.iren.Render()

    # Compute projection for a selected lesion and apply it on active surface.
    def computeApplyProjection(self, highlightLesionID, surfaceLh, surfaceRh, sliderValue = None):
        if(sliderValue == None):
            sliderValue = self.horizontalSlider_TimePoint.value()
        # Project on brain surface.
        affectedLh = np.asarray(self.structureInfo[str(sliderValue)][0][str(highlightLesionID)][0]['AffectedPointIdsLh'])
        affectedRh = np.asarray(self.structureInfo[str(sliderValue)][0][str(highlightLesionID)][0]['AffectedPointIdsRh'])
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
            lesion.GetProperty().SetColor(0.7804, 0.4824, 0.4824) # default lesion color

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

    # Load data automatically - To be removed in production.
    def autoLoadData(self):
        self.ren.RemoveAllViewProps()
        self.renDual.RemoveAllViewProps()
        self.iren.Render()
        self.irenDual.Render()
        self.folder = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\"
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