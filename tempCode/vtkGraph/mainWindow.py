from PyQt5 import QtWidgets as qWidget
from PyQt5 import QtGui as qGui
from PyQt5 import QtCore as qCore
from PyQt5.QtCore import pyqtSlot
from PyQt5 import uic
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog, QCheckBox, QButtonGroup, QAbstractButton
from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5 import QtCore, QtGui
from PyQt5 import Qt
import sys
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import os
import Utils
import vtk

class mainWindow(qWidget.QMainWindow):
    """Main window class."""

    def __init__(self, *args):
        """Init."""
        super(mainWindow, self).__init__(*args)
        ui = os.path.join(os.path.dirname(__file__), 'test.ui')
        uic.loadUi(ui, self)
        vtk.vtkObject.GlobalWarningDisplayOff()

    def setupUI(self):
        print("Starting application")
        self.on_click_printHello()

    def on_click_printHello(self):
        print("initializing node graph...")
        self.vlNodeGraph = Qt.QVBoxLayout()
        self.vtkWidgetNodeGraph = QVTKRenderWindowInteractor(self.frame)
        self.vlNodeGraph.addWidget(self.vtkWidgetNodeGraph)

        self.graph_layout_view = vtk.vtkGraphLayoutView()
        self.graph_layout_view.SetRenderWindow(self.vtkWidgetNodeGraph.GetRenderWindow())
        # self.renNodeGraph = vtk.vtkRenderer()
        self.renNodeGraph = self.graph_layout_view.GetRenderer()
        print("Renderer ID1 is ", id(self.renNodeGraph))
        self.renNodeGraph.SetBackground(255.0, 0.0, 0.0)
        self.vtkWidgetNodeGraph.GetRenderWindow().AddRenderer(self.renNodeGraph)


        self.irenNodeGraph = self.vtkWidgetNodeGraph.GetRenderWindow().GetInteractor()
        print("RENWIN ADDRESS", id(self.vtkWidgetNodeGraph.GetRenderWindow()))
        self.irenNodeGraph.SetRenderWindow(self.vtkWidgetNodeGraph.GetRenderWindow())
        self.irenNodeGraph.SetInteractorStyle(self.graph_layout_view.GetInteractorStyle())

        # self.irenNodeGraph = self.graph_layout_view.GetInteractor()
        # self.irenNodeGraph.SetRenderWindow(self.vtkWidgetNodeGraph.GetRenderWindow())

        self.renNodeGraph.ResetCamera()
        self.frame.setLayout(self.vlNodeGraph)
        self.irenNodeGraph.Initialize()

        print("RENWIN ADDRESS2", id(self.graph_layout_view.GetRenderWindow()))
        Utils.drawNodeGraph(self, "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\preProcess\\lesionGraph.gml", self.graph_layout_view)


app = qWidget.QApplication(sys.argv)
window = mainWindow()
window.setupUI()
window.show()
sys.exit(app.exec_())