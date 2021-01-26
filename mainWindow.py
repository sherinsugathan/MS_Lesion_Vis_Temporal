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
import Utils
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import networkx as nx

class CallHandler(QObject):
    @pyqtSlot(result=str)
    def myHello(self):
        print('call received')
        return 'hello, Python'

# Main window class.
class mainWindow(QtWidgets.QMainWindow):

    # Initialization
    def __init__(self, *args):
        super(mainWindow, self).__init__(*args)
        ui = os.path.join(os.path.dirname(__file__), 'mstemporal_uifile.ui')
        uic.loadUi(ui, self)
        self.showMaximized()

    def closeEvent(self, event):
        #self.vtkWidget.Finalize() # This will also work --> self.vtkWidget.close()
        pass

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

    def initializeD3VisView(self):
        self.view = QWebEngineView()
        print(type(self.view))
        self.view.settings().setAttribute(QWebEngineSettings.WebGLEnabled, True)
        self.view.settings().setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, False)
        self.view.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        #self.view.loadFinished.connect(self._loadFinish)
        #self.channel = QWebChannel()
        #self.handler = CallHandler()
        #self.channel.registerObject('handler', self.handler)
        #self.view.page().setWebChannel(self.channel)
        
        self.layout = Qt.QVBoxLayout()
        self.layout.addWidget(self.view)
        self.frameVis.setLayout(self.layout)
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "interactionD3.html"))
        htmlUrl = QUrl.fromLocalFile(file_path)
        self.view.load(QUrl(htmlUrl))
        #self.view.load(QUrl("http://www.google.com"))
        self.view.show()


    def _loadFinish(self, *args, **kwargs):
        print("Loading finished")

    def mousePress(self):
        print("asdasdsad")

    def vtkViewportEvent(self, obj,event):
        print("bingo")

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

        self.vl = Qt.QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vtkWidget.Initialize()
        #self.vtkWidget.Start()

        #self.vtkWidget.AddObserver("ExitEvent", lambda o, e, a=app: a.quit())
        self.vtkWidget.AddObserver("ExitEvent", self.vtkViewportEvent)

        self.vl.addWidget(self.vtkWidget)
        self.ren = vtk.vtkRenderer()
        self.frame.setLayout(self.vl)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()


        self.initializeD3VisView()

        self.style = Utils.CustomMouseInteractor(self)
        self.style.SetDefaultRenderer(self.ren)
        self.style.main = self
        self.iren.SetInteractorStyle(self.style)
        self.readThread = None

        self.iren.Initialize()
        self.ren.ResetCamera()



    def reportProgress(self, n):
        self.progressBar.setValue(n)

    def renderData(self):
        Utils.smoothSurface(self.surfaceActors[0])
        numberOfActors = len(self.LesionActorList)
        self.horizontalSlider_TimePoint.setMaximum(numberOfActors-1)
        for lesion in self.LesionActorList[0]:
            self.ren.AddActor(lesion)
        self.ren.AddActor(self.surfaceActors[0])
        self.ren.ResetCamera()
        self.iren.Render()
        openglRendererInUse = self.ren.GetRenderWindow().ReportCapabilities().splitlines()[1].split(":")[1].strip()
        print(openglRendererInUse)

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