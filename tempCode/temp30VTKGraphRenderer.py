# implementation of vtk graph renderer
import vtk
import sys
import os
import glob
import networkx as nx
from vtkmodules.vtkCommonColor import vtkNamedColors
import itertools

def DummyFunc1(obj, ev):
    print('left button press')

colors = vtk.vtkNamedColors()

# Data Paths
rootPath = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\"
graphPath = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\preProcess\\lesionGraph.gml"
# tableData = "D:\\sample.csv"

# Read data
G = nx.read_gml(graphPath)
print(list(G.edges()))
print(G.nodes())

scales = vtk.vtkFloatArray()
scales.SetNumberOfComponents(1)
scales.SetName('Scales')

vertex_labels = vtk.vtkStringArray()
vertex_labels.SetName("VertexLabels")

nodes = G.nodes()
edges = list(G.edges())
vtkGraph = vtk.vtkMutableDirectedGraph()
vertices = [0] * len(nodes)

# Create the color array for the vertices
vertexColors = vtk.vtkIntArray()
vertexColors.SetNumberOfComponents(1)
vertexColors.SetName('VertexColors')

# Create the color array for the edges.
edgeColors = vtk.vtkIntArray()
edgeColors.SetNumberOfComponents(1)
edgeColors.SetName('EdgeColors')

lookupTableVertices = vtk.vtkLookupTable()
lookupTableVertices.SetNumberOfTableValues(10)
lookupTableVertices.SetTableValue(0, colors.GetColor4d('Green'))
lookupTableVertices.SetTableValue(1, colors.GetColor4d('Red'))
lookupTableVertices.SetTableValue(2, colors.GetColor4d('Green'))
lookupTableVertices.SetTableValue(3, colors.GetColor4d('Green'))
lookupTableVertices.SetTableValue(4, colors.GetColor4d('Green'))
lookupTableVertices.SetTableValue(5, colors.GetColor4d('Red'))
lookupTableVertices.SetTableValue(6, colors.GetColor4d('Green'))
lookupTableVertices.SetTableValue(7, colors.GetColor4d('Green'))
lookupTableVertices.SetTableValue(8, colors.GetColor4d('Green'))
lookupTableVertices.SetTableValue(9, colors.GetColor4d('Green'))
lookupTableVertices.Build()

lookupTableEdges = vtk.vtkLookupTable()
lookupTableEdges.SetNumberOfTableValues(len(edges))


for i in range(len(nodes)):
    vertices[i] = vtkGraph.AddVertex() # Add vertex to the graph
    scales.InsertNextValue(2)
    vertex_labels.InsertValue(vertices[i], str(int(vertices[i])+1))  # Add label.
    vertexColors.InsertNextValue(i)

for i in range(len(edges)):
    edgeColors.InsertNextValue(i)
    lookupTableEdges.SetTableValue(i, colors.GetColor4d('Gray'))


lookupTableEdges.Build()

# colorsArray = vtk.vtkUnsignedCharArray()
# colorsArray.SetNumberOfComponents(3)
# colorsArray.SetNumberOfTuples(len(edges))
# colorsArray.SetName('EdgeColors')
# for c in range(len(edges)):
#     colorsArray.SetTuple(c, [0, 0, 0])

for item in edges:
    vtkGraph.AddEdge(int(item[0])-1, int(item[1])-1)

# Add the scale array to the graph
vtkGraph.GetVertexData().AddArray(scales)

# Add vertex labels to the graphs
vtkGraph.GetVertexData().AddArray(vertex_labels)

# Add color data to vertices
vtkGraph.GetVertexData().AddArray(vertexColors)

# Add color array to edges
vtkGraph.GetEdgeData().AddArray(edgeColors)

def selectionCallback(obj, event):
    print(type(obj))
    # arr = obj.GetCurrentSelection().GetNode(1).GetSelectionList()
    # for elem in arr:
    #     print(elem)
    numberOfTuples = obj.GetCurrentSelection().GetNode(1).GetSelectionList().GetNumberOfTuples()
    selectedNodes = [0] * numberOfTuples
    for tupleIndex in range(numberOfTuples):
        d = list(obj.GetCurrentSelection().GetNode(1).GetSelectionList().GetTuple(tupleIndex))
        selectedNodes[tupleIndex] = d

    flatListFloat = list(itertools.chain.from_iterable(selectedNodes))
    flatListInt = [int(a)+1 for a in flatListFloat]  # Adding 1 to correct lesion numbering
    print(flatListInt)


    #print(obj.GetCurrentSelection().GetNode(1).GetSelectionList().GetNumberOfTuples())
    #print(obj.GetCurrentSelection().Dump())


#force_directed = vtk.vtkForceDirectedLayoutStrategy()

graph_layout_view = vtk.vtkGraphLayoutView()


layout = vtk.vtkGraphLayout()
strategy = vtk.vtkSimple2DLayoutStrategy()
strategy.SetRestDistance(100.0)
layout.SetInputData(vtkGraph)
layout.SetLayoutStrategy(strategy)
graph_layout_view.SetLayoutStrategyToPassThrough()
graph_layout_view.SetEdgeLayoutStrategyToPassThrough()
graph_layout_view.SetVertexLabelArrayName('VertexLabels')
graph_layout_view.SetVertexLabelVisibility(True)
#graph_layout_view.SetVertexColorArrayName("VertexColors")
graph_layout_view.SetVertexColorArrayName("VertexColors")
graph_layout_view.SetEdgeColorArrayName('EdgeColors')
graph_layout_view.ColorVerticesOn()
graph_layout_view.ColorEdgesOn()

#print("Sherin array name is", graph_layout_view.GetVertexColorArrayName())

graphToPoly = vtk.vtkGraphToPolyData()
graphToPoly.SetInputConnection(layout.GetOutputPort())
graphToPoly.EdgeGlyphOutputOn()
graphToPoly.SetEdgeGlyphPosition(0.95)
graphToPoly.Update()
#print("DEBUG LOGO:", graphToPoly.GetOutput().GetPoints().GetScalarData())
#print("DEBUG LOGO:", graphToPoly.GetOutput().GetPointData())
#graphToPoly.GetOutput().GetPointData().SetScalars(colorsVertices)

#print(vtkGraph.GetEdgeData())

arrowSource = vtk.vtkGlyphSource2D()
arrowSource.SetGlyphTypeToEdgeArrow()
arrowSource.FilledOn()
arrowSource.SetScale(2)
arrowSource.Update()

vertexCircleSource = vtk.vtkGlyphSource2D()
vertexCircleSource.SetGlyphTypeToCircle()
vertexCircleSource.FilledOn()
vertexCircleSource.SetScale(3)
vertexCircleSource.SetResolution(20)
vertexCircleSource.Update()

arrowGlyph = vtk.vtkGlyph3D()
arrowGlyph.SetColorModeToColorByScalar()
arrowGlyph.SetScaleFactor(1)

arrowGlyph.SetInputConnection(0, graphToPoly.GetOutputPort(1))
arrowGlyph.SetInputConnection(1, arrowSource.GetOutputPort())

arrowMapper = vtk.vtkPolyDataMapper()
arrowMapper.SetInputConnection(arrowGlyph.GetOutputPort())
arrowActor = vtk.vtkActor()
arrowActor.SetMapper(arrowMapper)
arrowActor.GetProperty().SetColor(0.5, 0.5, 0.5)

vertexGlyph = vtk.vtkGlyph3D()
vertexGlyph.SetColorModeToColorByScalar()
vertexGlyph.SetScaleFactor(4)

vertexGlyph.SetInputConnection(0, graphToPoly.GetOutputPort(0))
vertexGlyph.SetInputConnection(1, vertexCircleSource.GetOutputPort())


vertexMapper = vtk.vtkPolyDataMapper()
vertexMapper.SetInputConnection(vertexGlyph.GetOutputPort())
vertexActor = vtk.vtkActor()
vertexActor.SetMapper(vertexMapper)
#vertexActor.GetProperty().SetColor(0.0, 0.0, 0.0)
#vertexActor.GetMapper().ScalarVisibilityOff()
#vertexActor.GetMapper().GetInput().GetPointData().SetScalars(colorsVertices)
#vertexActor.GetMapper().GetInput().GetPointData().SetActiveScalars("VertexColors")
#vertexMapper.Update()
#print("DEBUG LOGO:", vertexActor.GetMapper().GetInput().GetPointData())


#edgeMapper = vtk.vtkPolyDataMapper()
#edgeMapper.SetInputConnection(graphToPoly.GetOutputPort())
#edgeMapper.SetScalarVisibility(True)
#edgeActor = vtk.vtkActor()
#edgeActor.SetMapper(edgeMapper)
#edgeActor.GetProperty().SetLineWidth(2)

#graph_layout_view.AddRepresentationFromInput(vtkGraph)
graph_layout_view.AddRepresentationFromInputConnection(layout.GetOutputPort())
# If we create a layout object directly, just set the pointer through this method.
# graph_layout_view.SetLayoutStrategy(force_directed)

#graph_layout_view.SetLayoutStrategyToForceDirected()
#graph_layout_view.ScaledGlyphsOn()
#graph_layout_view.SetScalingArrayName('Scales')

textActorTitle = vtk.vtkTextActor()
textActorTitle.UseBorderAlignOff()
textActorTitle.SetDisplayPosition(10, 10)
textActorTitle.GetTextProperty().SetFontFamily(4)
#textActorTitle.GetTextProperty().SetFontFile("asset\\GoogleSans-Medium.ttf")
textActorTitle.GetTextProperty().SetFontSize(16)
textActorTitle.GetTextProperty().SetColor(0.3411, 0.4824, 0.3608)
textActorTitle.SetInput("Lesion Activity Graph")


rGraph = vtk.vtkRenderedGraphRepresentation()
gGlyph = vtk.vtkGraphToGlyphs()
rGraph.SafeDownCast(graph_layout_view.GetRepresentation()).SetGlyphType(gGlyph.CIRCLE)
graph_layout_view.GetRepresentation().ScalingOn()

graph_layout_view.GetRenderer().AddActor(arrowActor)
#graph_layout_view.GetRenderer().AddActor(vertexActor)
graph_layout_view.GetRenderer().AddActor(textActorTitle)

viewTheme = vtk.vtkViewTheme()
viewTheme.SetLineWidth(3.0)
viewTheme.SetOutlineColor(0.0, 0.0, 0.0)
viewTheme.SetPointSize(5)
viewTheme.SetVertexLabelColor(0.0, 0.0, 0.0)
viewTheme.SetPointLookupTable(lookupTableVertices)
viewTheme.SetCellLookupTable(lookupTableEdges)
viewTheme.SetVertexLabelColor(0,0,0)

labelTextProperty = vtk.vtkTextProperty()
labelTextProperty.SetColor(0,0,0)
labelTextProperty.SetFontSize(18)
labelTextProperty.ShadowOn()
labelTextProperty.BoldOn()

viewTheme.SetPointTextProperty(labelTextProperty)

graph_layout_view.GetRepresentation().ApplyViewTheme(viewTheme)
graph_layout_view.GetRepresentation().ScalingOn()
graph_layout_view.GetRepresentation().SetScalingArrayName('Scales')



#graph_layout_view.GetRepresentation().EdgeVisibilityOff()
print("color is ", colors.GetColor4d('Green'))

#graph_layout_view.GetRenderer().AddActor(edgeActor)
graph_layout_view.GetRenderer().SetBackground(colors.GetColor3d('White'))
graph_layout_view.GetRenderer().SetBackground2(colors.GetColor3d('White'))
#graph_layout_view.GetRenderWindow().SetWindowName('ConstructGraph')
graph_layout_view.SetEdgeColorArrayName("EdgeColors")


graph_layout_view.GetRepresentation().GetAnnotationLink().AddObserver("AnnotationChangedEvent", selectionCallback)


#print("Edge visibility", graph_layout_view.GetColorEdges())
graph_layout_view.ResetCamera()
graph_layout_view.Render()
graph_layout_view.GetInteractor().Start()

randomStrategy = vtk.vtkRandomLayoutStrategy()
randomStrategy.SetGraphBounds(0, 800, 0, 800, 0, 0)

# tableToGraph = vtk.vtkTableToGraph()
# tableToGraph.SetInputData(reader.GetOutput())
# tableToGraph.AddLinkVertex("source", "dom1")
# tableToGraph.AddLinkVertex("target", "dom2")
# tableToGraph.AddLinkEdge('source', 'target')
# tableToGraph.SetDirected(True)

# graphLayout = vtk.vtkGraphLayout()
# graphLayout.SetInputConnection(tableToGraph.GetOutputPort())
# graphLayout.SetLayoutStrategy(randomStrategy)
# graphLayout.Update()
#
# graphItem = vtk.vtkGraphItem()
# graphItem.SetGraph(graphLayout.GetOutput())

# trans = vtk.vtkContextTransform()
# trans.SetInteractive(True)
# trans.AddItem(graphItem)
#
# actor = vtk.vtkContextActor()
# actor.GetScene().AddItem(trans)
#
# # Renderer
# renderer = vtk.vtkRenderer()
# renderer.SetBackground(1.0, 1.0, 1.0)
#
# renderWindow = vtk.vtkRenderWindow()
# renderWindow.SetSize(800, 800)
# renderWindow.AddRenderer(renderer)
# renderer.AddActor(actor)
#
# interactorStyle = vtk.vtkContextInteractorStyle()
# interactorStyle.SetScene(actor.GetScene())
#
# interactor = vtk.vtkRenderWindowInteractor()
# interactor.SetInteractorStyle(interactorStyle)
# interactor.SetRenderWindow(renderWindow)
# renderWindow.SetLineSmoothing(True)
# renderWindow.Render()
# graphItem.StartLayoutAnimation(interactor)
# interactor.Start()


print("Successfully completed")
