from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5 import QtCore, QtGui
import vtk

class ReadThread(QObject): 
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    def __init__(self, folder_name, actorList, transform, SurfacesList, parent=None): 
        super(ReadThread, self).__init__(parent) 
        self.read_folder_name = folder_name + "\\surfaces\\lesions\\"
        self.surfaceList = actorList
        self.transform = transform
        self.surfaceActor = SurfacesList
        
    def run(self):
        self.actorList = []
        for i in range(81):
            fileName = self.read_folder_name + "l" + str(i) + ".obj"
            self.reader = vtk.vtkOBJReader()
            self.reader.SetFileName(fileName) 
            self.reader.Update() 
            mapper = vtk.vtkOpenGLPolyDataMapper()
            mapper.SetInputConnection(self.reader.GetOutputPort())
            mapper.Update()
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.SetUserTransform(self.transform)
            self.surfaceList.append(actor)
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
        return actor
        #self.ren.AddActor(actor)
        #self.ren.ResetCamera()
        #self.iren.Render()