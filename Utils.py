from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5 import QtCore, QtGui
import vtk

class ReadThread(QObject): 
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    def __init__(self, folder_name, actorList, transform, parent=None): 
        super(ReadThread, self).__init__(parent) 
        self.read_folder_name = folder_name + "\\surfaces\\lesions\\"
        
        self.surfaceList = actorList
        #self.mapperList = mapperList
        self.transform = transform
        
    def run(self):
        self.mapperList = []
        self.actorList = []
        for i in range(81):
            fileName = self.read_folder_name + "l" + str(i) + ".obj"
            self.reader = vtk.vtkOBJReader()
            print(fileName)
            self.reader.SetFileName(fileName) 
            self.reader.Update() 
            mapper = vtk.vtkOpenGLPolyDataMapper()
            mapper.SetInputConnection(self.reader.GetOutputPort())
            mapper.Update()
            self.mapperList.append(mapper)
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.SetUserTransform(self.transform)
            self.surfaceList.append(actor)
            #self.mapperList.append(mapper)
            print("MAPPER", id(mapper))
            print("ACTOR", id(actor))
            self.progress.emit(int((i/80)*100))
        self.finished.emit()
        print("Done")