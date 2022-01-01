from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5 import QtCore, QtGui
import vtk
import os
import glob
import math
import numpy as np
import networkx as nx
from vtkmodules.vtkCommonColor import vtkNamedColors


def drawNodeGraph(selfObject, graphPath, graph_layout_view):
    print("entering here 1")
    colors = vtk.vtkNamedColors()
    # Read data
    G = nx.read_gml(graphPath)
    print(list(G.edges()))
    print(G.nodes())
    # For scaling vertices or nodes.
    scales = vtk.vtkFloatArray()
    scales.SetNumberOfComponents(1)
    scales.SetName('Scales')

    vertex_labels = vtk.vtkStringArray()
    vertex_labels.SetName("VertexLabels")

    nodes = G.nodes()
    edges = list(G.edges())
    vtkGraph = vtk.vtkMutableDirectedGraph()
    vertices = [0] * len(nodes)
    for i in range(len(nodes)):
        vertices[i] = vtkGraph.AddVertex()
        scales.InsertNextValue(2.0)
        vertex_labels.InsertValue(vertices[i], str(int(vertices[i]) + 1))

    colorsArray = vtk.vtkUnsignedCharArray()
    colorsArray.SetNumberOfComponents(3)
    colorsArray.SetNumberOfTuples(len(edges))
    colorsArray.SetName('EdgeColors')
    for c in range(len(edges)):
        colorsArray.SetTuple(c, [255, 0, 0])

    for item in edges:
        vtkGraph.AddEdge(int(item[0]) - 1, int(item[1]) - 1)

    # Add the scale array to the graph
    vtkGraph.GetVertexData().AddArray(scales)

    # Add vertex labels to the graph
    vtkGraph.GetVertexData().AddArray(vertex_labels)

    # Add color array
    vtkGraph.GetEdgeData().AddArray(colorsArray)

    #graph_layout_view = vtk.vtkGraphLayoutView()
    #graph_layout_view.SetRenderWindow(selfObject.vtkWidgetNodeGraph.GetRenderWindow())

    layout = vtk.vtkGraphLayout()
    strategy = vtk.vtkSimple2DLayoutStrategy()
    strategy.SetRestDistance(100.0)
    layout.SetInputData(vtkGraph)
    layout.SetLayoutStrategy(strategy)
    graph_layout_view.SetLayoutStrategyToPassThrough()
    graph_layout_view.SetEdgeLayoutStrategyToPassThrough()
    graph_layout_view.SetVertexLabelArrayName('VertexLabels')
    #graph_layout_view.SetVertexLabelVisibility(True)
    print("entering here 3")
    graphToPoly = vtk.vtkGraphToPolyData()
    graphToPoly.SetInputConnection(layout.GetOutputPort())
    graphToPoly.EdgeGlyphOutputOn()
    graphToPoly.SetEdgeGlyphPosition(0.9)

    arrowSource = vtk.vtkGlyphSource2D()
    arrowSource.SetGlyphTypeToEdgeArrow()
    arrowSource.FilledOn()
    arrowSource.SetColor(255, 255.0, 0)
    print(arrowSource.GetColor())
    arrowSource.SetScale(2)
    arrowSource.Update()

    arrowGlyph = vtk.vtkGlyph3D()
    arrowGlyph.SetInputConnection(0, graphToPoly.GetOutputPort(1))
    arrowGlyph.SetInputConnection(1, arrowSource.GetOutputPort())

    arrowMapper = vtk.vtkPolyDataMapper()
    arrowMapper.SetInputConnection(arrowGlyph.GetOutputPort())
    arrowActor = vtk.vtkActor()
    arrowActor.SetMapper(arrowMapper)

    graph_layout_view.AddRepresentationFromInputConnection(layout.GetOutputPort())
    graph_layout_view.ScaledGlyphsOn()
    graph_layout_view.SetScalingArrayName('Scales')

    #rGraph = vtk.vtkRenderedGraphRepresentation()
    #gGlyph = vtk.vtkGraphToGlyphs()
    #rGraph.SafeDownCast(graph_layout_view.GetRepresentation()).SetGlyphType(gGlyph.CIRCLE)
    graph_layout_view.GetRenderer().AddActor(arrowActor)
    print("Renderer ID2 is ", id(graph_layout_view.GetRenderer()))
    # graph_layout_view.GetRenderer().AddActor(edgeActor)
    #graph_layout_view.GetRenderer().SetBackground(colors.GetColor3d('Black'))
    #graph_layout_view.GetRenderer().SetBackground2(colors.GetColor3d('White'))
    graph_layout_view.SetEdgeColorArrayName("EdgeColors")
    graph_layout_view.ColorEdgesOn()
    print("fine")
    graph_layout_view.ResetCamera()
    selfObject.renNodeGraph.ResetCamera()
    #graph_layout_view.Render()
    #graph_layout_view.GetInteractor().Start()