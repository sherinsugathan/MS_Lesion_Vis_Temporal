# This program reads free surfer parcellation annotation and renders colored surface.
import SimpleITK as sitk
import vtk
import numpy as np
import sys, os
import math
import ctypes
import json
import cv2
from nibabel import freesurfer
from datetime import datetime 
import networkx as nx 


# import graph and fetch related lesion surfaces.
#G = nx.read_gml("D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\preProcess\\lesionGraph.gml")


# perform comparon between meshes.
mesh1 = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\surfaces\\lesions\\lesions0\\lesions0_1.vtp"
mesh2 = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\surfaces\\lesions\\lesions8\\lesions8_1.vtp"
readerPoly1 = vtk.vtkXMLPolyDataReader()
readerPoly1.SetFileName(mesh1)
readerPoly1.Update()
poly1Tri = vtk.vtkTriangleFilter()
poly1Tri.SetInputData(readerPoly1.GetOutput())
poly1Tri.Update()

readerPoly2 = vtk.vtkXMLPolyDataReader()
readerPoly2.SetFileName(mesh2)
readerPoly2.Update()
poly2Tri = vtk.vtkTriangleFilter()
poly2Tri.SetInputData(readerPoly2.GetOutput())
poly2Tri.Update()

mapper1 = vtk.vtkPolyDataMapper()
mapper1.SetInputConnection(readerPoly1.GetOutputPort())
actor1 = vtk.vtkActor()
actor1.SetMapper(mapper1)

booleanOperation = vtk.vtkBooleanOperationPolyDataFilter()
#booleanOperation.SetOperationToIntersection()
booleanOperation.SetOperationToUnion()
booleanOperation.SetInputData(0, poly1Tri.GetOutput())
booleanOperation.SetInputData(1, poly2Tri.GetOutput())
#booleanOperation.Update()
print(booleanOperation.GetOutput())
booleanOperationMapper = vtk.vtkPolyDataMapper()
booleanOperationMapper.SetInputData(booleanOperation.GetOutput())
booleanOperationMapper.ScalarVisibilityOff()
booleanOperationActor = vtk.vtkActor()
booleanOperationActor.SetMapper(booleanOperationMapper)

# use vtk slider mechanism to drive and display data.

# Visualize
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderer.AddActor(booleanOperationActor)
renderWindow.Render()
renderWindowInteractor.Start()