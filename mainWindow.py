###################################
# MUSCLEVIS LONGITUDINAL 
# Author: Sherin Sugathan
# Last Modified Date: 6th Jan 2021
###################################
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QCheckBox, QButtonGroup, QAbstractButton, QMessageBox, QDialog
from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5 import QtCore, QtGui
from PyQt5 import Qt
from PyQt5.QtCore import QTimer
import sys
import os
import Utils
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import networkx as nx

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

        #fileName = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\surfaces\\lesions\\l0.obj"

        # fileName = "D:\\OneDrive - University of Bergen\\Datasets\\MS_SegmentationChallengeDataset\\DTIDATA\\surfaces\\lesions.obj"
        # reader = vtk.vtkOBJReader()
        # reader.SetFileName(fileName) 
        # reader.Update() 
        # mapper = vtk.vtkOpenGLPolyDataMapper()
        # mapper.SetInputConnection(reader.GetOutputPort())
        # mapper.Update()
        # actor = vtk.vtkActor()
        # actor.SetMapper(mapper)

        # self.niftyReaderT1 = vtk.vtkNIFTIImageReader() 
        # self.niftyReaderT1.SetFileName("D:\\OneDrive - University of Bergen\\Datasets\\MS_SegmentationChallengeDataset\\DTIDATA\\structural\\T1.nii")
        # self.niftyReaderT1.Update()
        # transform = vtk.vtkTransform()
        # QFormMatrixT1 = self.niftyReaderT1.GetQFormMatrix()
        # qFormListT1 = [0] * 16 #the matrix is 4x4
        # QFormMatrixT1.DeepCopy(qFormListT1, QFormMatrixT1)
        # transform.SetMatrix(qFormListT1)
        # actor.SetUserTransform(transform)

        self.vl = Qt.QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)
        self.ren = vtk.vtkRenderer()
        self.frame.setLayout(self.vl)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.iren.Initialize()
        self.ren.ResetCamera()

    def reportProgress(self, n):
        self.progressBar.setValue(n)

    def renderData(self):
        numberOfActors = len(self.LesionActorList)
        self.horizontalSlider_TimePoint.setMaximum(numberOfActors-1)
        self.ren.AddActor(self.LesionActorList[0])
        self.ren.AddActor(self.surfaceActors[0])
        self.ren.ResetCamera()
        self.iren.Render()

    # Handler for time point slider change
    @pyqtSlot()
    def on_sliderChangedTimePoint(self):
        sliderValue = self.horizontalSlider_TimePoint.value()
        self.label_currentDataIndex.setText(str(sliderValue))
        self.ren.RemoveAllViewProps()
        self.ren.AddActor(self.LesionActorList[sliderValue])
        self.ren.AddActor(self.surfaceActors[0])
        self.iren.Render()

    # Load data automatically - To be removed in production.
    def autoLoadData(self):
        self.folder = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\"
        if self.folder:
            self.niftyReaderT1 = vtk.vtkNIFTIImageReader() 
            self.niftyReaderT1.SetFileName("D:\\OneDrive - University of Bergen\\Datasets\\MS_SegmentationChallengeDataset\\DTIDATA\\structural\\T1.nii")
            self.niftyReaderT1.Update()
            self.transform = vtk.vtkTransform()
            QFormMatrixT1 = self.niftyReaderT1.GetQFormMatrix()
            qFormListT1 = [0] * 16 #the matrix is 4x4
            QFormMatrixT1.DeepCopy(qFormListT1, QFormMatrixT1)
            self.transform.SetMatrix(qFormListT1)

            self.lineEdit_DatasetFolder.setText(self.folder)
            self.LesionActorList = []
            self.surfaceActors = []
            self.readThread = QThread()
            self.worker = Utils.ReadThread(self.folder, self.LesionActorList, self.transform, self.surfaceActors)
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
            self.niftyReaderT1 = vtk.vtkNIFTIImageReader() 
            self.niftyReaderT1.SetFileName("D:\\OneDrive - University of Bergen\\Datasets\\MS_SegmentationChallengeDataset\\DTIDATA\\structural\\T1.nii")
            self.niftyReaderT1.Update()
            self.transform = vtk.vtkTransform()
            QFormMatrixT1 = self.niftyReaderT1.GetQFormMatrix()
            qFormListT1 = [0] * 16 #the matrix is 4x4
            QFormMatrixT1.DeepCopy(qFormListT1, QFormMatrixT1)
            self.transform.SetMatrix(qFormListT1)

            self.lineEdit_DatasetFolder.setText(self.folder)
            self.LesionActorList = []
            self.ventricleActor = None
            self.readThread = QThread()
            self.worker = Utils.ReadThread(self.folder, self.LesionActorList, self.transform, self.ventricleActor)
            self.worker.moveToThread(self.readThread)
            self.readThread.started.connect(self.worker.run)
            self.worker.progress.connect(self.reportProgress)
            self.worker.finished.connect(self.renderData)
            self.readThread.start()

app = QtWidgets.QApplication(sys.argv)
window = mainWindow()
window.setupUI()
window.show()
sys.exit(app.exec_())