###################################
# MUSCLEVIS LONGITUDINAL 
# Author: Sherin Sugathan
# Last Modified Date: 6th Jan 2021
###################################
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QCheckBox, QButtonGroup, QAbstractButton, QMessageBox, QDialog
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal, QUrl, QObject
from PyQt5.QtWebEngineWidgets import  QWebEngineView,QWebEnginePage
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from PyQt5.QtWebChannel import QWebChannel
from PyQt5 import QtCore, QtGui
from PyQt5 import Qt
from PyQt5.QtCore import QTimer
from OpenGL import GL
import sys
import os
from utils import Utils
import vtk
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

# Main window class.
class mainWindow(QtWidgets.QMainWindow):
    # Initialization
    def __init__(self, *args):
        super(mainWindow, self).__init__(*args)
        ui = os.path.join(os.path.dirname(__file__), 'mstemporal_uifile.ui')
        uic.loadUi(ui, self)
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
    def setupUI(self):  
        #print("\033[1;101m STARTING APPLICATION... \033[0m")
        pmMain = Qt.QPixmap("icons\\AppLogo.png")
        self.logoLabel.setPixmap(pmMain.scaled(self.logoLabel.size().width(), self.logoLabel.size().height(), 1,1))
        #self.showDialog()
        
        # Handlers
        #self.pushButton_LoadFolder.clicked.connect(self.on_click_browseFolder) # Attaching button click handler.
        self.pushButton_LoadFolder.clicked.connect(self.autoLoadData) # Attaching button click handler.
        self.horizontalSlider_TimePoint.valueChanged.connect(self.on_sliderChangedTimePoint) # Attaching slider value changed handler.
        self.mprA_Slice_Slider.valueChanged.connect(self.on_sliderChangedMPRA)
        self.mprB_Slice_Slider.valueChanged.connect(self.on_sliderChangedMPRB)
        self.mprC_Slice_Slider.valueChanged.connect(self.on_sliderChangedMPRC)

        self.vl = Qt.QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vtkWidget.Initialize()
        #self.vtkWidget.Start()

        #self.vtkWidget.AddObserver("ExitEvent", lambda o, e, a=app: a.quit())
        #self.vtkWidget.AddObserver("ExitEvent", self.vtkViewportEvent)

        self.vl.addWidget(self.vtkWidget)
        self.ren = vtk.vtkRenderer()
        self.frame.setLayout(self.vl)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        self.style = Utils.CustomMouseInteractor(self)
        self.style.SetDefaultRenderer(self.ren)
        self.style.main = self
        self.iren.SetInteractorStyle(self.style)
        self.readThread = None

        self.iren.Initialize()
        self.ren.ResetCamera()

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

    def reportProgress(self, n):
        self.progressBar.setValue(n)

    def renderData(self):
        Utils.smoothSurface(self.surfaceActors[0])
        numberOfActors = len(self.LesionActorList)
        self.horizontalSlider_TimePoint.setMaximum(numberOfActors-1)
        for lesion in self.LesionActorList[0]:
            self.ren.AddActor(lesion)
        self.ren.AddActor(self.surfaceActors[0])
        self.ren.SetBackground(0.0627, 0.0627, 0.0627)
        self.ren.ResetCamera()
        self.iren.Render()
        openglRendererInUse = self.ren.GetRenderWindow().ReportCapabilities().splitlines()[1].split(":")[1].strip()
        print(openglRendererInUse)

        self.displayOrientationCube() # Display orientation cube
        self.LoadStructuralSlices(self.folder, "T1", 0, True) # load slices
        self.initializeDefaultGraph() # Load graph data
        self.activateControls() # Activate controls.

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
        self.axesActor.GetCubeProperty().SetColor(0.9, 0.3, 0.4)
        self.axes = vtk.vtkOrientationMarkerWidget()
        self.axes.SetOrientationMarker(self.axesActor)
        self.axes.SetViewport( 0.9, 0.9, 1.0, 1.0 )
        self.axes.SetCurrentRenderer(self.ren)
        self.axes.SetInteractor(self.iren)
        self.axes.EnabledOn()

    def initializeDefaultGraph(self):
        self.vl_default = Qt.QVBoxLayout()
        self.figureDefault = plt.figure(num = 3, frameon=False, clear=True)
        self.canvasDefault = FigureCanvas(self.figureDefault)
        self.vl_default.addWidget(self.canvasDefault)
        self.frameDefaultGraph.setLayout(self.vl_default)
        self.plotDefaultGraph()

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

    # plot default graph
    def plotDefaultGraph(self): 
        # clearing old figures
        self.figureDefault.clear()
        plt.figure(3)
        # create an axis
        self.axDefault = self.figureDefault.add_subplot(111)
        #plt.axis('off')
        plt.subplots_adjust(wspace=None, hspace=None)

        # Data for plotting
        t = np.arange(0.0, 2.0, 0.01)
        s = 1 + np.sin(2 * np.pi * t)

        #fig, ax = plt.subplots()
        self.axDefault.plot(t, s)
        self.axDefault.set_facecolor((0.0627, 0.0627, 0.0627))
        self.axDefault.xaxis.label.set_color((0.6, 0.6, 0.6))
        self.axDefault.yaxis.label.set_color((0.6, 0.6, 0.6))
        self.axDefault.spines['bottom'].set_color((0.6, 0.6, 0.6))
        self.axDefault.spines['top'].set_color((0.6, 0.6, 0.6))
        self.axDefault.spines['left'].set_color((0.6, 0.6, 0.6))
        self.axDefault.spines['right'].set_color((0.6, 0.6, 0.6))
        self.axDefault.tick_params(axis='x', colors=(0.6, 0.6, 0.6))
        self.axDefault.tick_params(axis='y', colors=(0.6, 0.6, 0.6))

        self.axDefault.set(xlabel='time (s)', ylabel='lesion volume (ml)',
            title='About as simple as it gets, folks')
        #self.axDefault.grid()

        #fig.savefig("test.png")
        #plt.show()
        self.canvasDefault.draw()


        # if(refreshData == True):
        #     self.slice_MPRA = np.rot90(self.slice_MPRA)
        #     self.sliceMask_MPRA = np.rot90(self.sliceMask_MPRA)
        # if(self.pushButton_FLAIR.isChecked() == True):
        #     aspectCoronalData = self.spacingData[2]/self.spacingData[1]
        #     aspectCoronalMask = self.spacingMask[2]/self.spacingMask[1]
        # else:
        #     aspectCoronalData = self.spacingData[2]/self.spacingData[0]
        #     aspectCoronalMask = self.spacingMask[2]/self.spacingMask[0]
        # self.MPRA = plt.imshow(self.slice_MPRA, cmap='Greys_r', aspect=aspectCoronalData)
        # self.MPRAMask = plt.imshow(self.sliceMask_MPRA, cmap=self.MPROverlayColorMap, alpha=maskAlpha, aspect=aspectCoronalMask,  interpolation='none')
        # self.sliceNumberHandleMPRA = self.axMPRA.text(5, 5, str(self.midSliceX), verticalalignment='top', horizontalalignment='left', color='green', fontsize=12)
        

    # Handler for time point slider change
    @pyqtSlot()
    def on_sliderChangedTimePoint(self):
        sliderValue = self.horizontalSlider_TimePoint.value()
        self.label_currentDataIndex.setText(str(sliderValue))
        self.ren.RemoveAllViewProps()
        for lesion in self.LesionActorList[sliderValue]:
            self.ren.AddActor(lesion)
        self.ren.AddActor(self.surfaceActors[0])
        self.iren.Render()

    # Load data automatically - To be removed in production.
    def autoLoadData(self):
        self.ren.RemoveAllViewProps()
        self.iren.Render()
        self.folder = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\"
        if self.folder:
            self.lineEdit_DatasetFolder.setText(self.folder)
            self.LesionActorList = [[] for i in range(81)]
            self.surfaceActors = []
            if(self.readThread != None):
                self.readThread.terminate()
            self.readThread = QThread()
            self.worker = Utils.ReadThread(self.folder, self.LesionActorList, self.surfaceActors)
            self.worker.moveToThread(self.readThread)
            self.readThread.started.connect(self.worker.run)
            self.worker.progress.connect(self.reportProgress)
            self.worker.finished.connect(self.renderData)
            self.readThread.start()

    # Handler for browse folder button click.
    @pyqtSlot()
    def on_click_browseFolder(self):
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

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = mainWindow()
    window.setupUI()
    window.show()
    sys.exit(app.exec_())