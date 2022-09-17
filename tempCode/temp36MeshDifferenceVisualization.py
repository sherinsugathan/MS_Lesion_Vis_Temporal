import vtk
import SimpleITK as sitk
from vtkmodules.vtkCommonColor import vtkNamedColors


test = sitk.Elastix()
# Create a sphere
sphere = vtk.vtkSphereSource()
sphere.SetCenter(0.0, 0.0, 0.0)
sphere.Update()

# Create a cone
cone = vtk.vtkConeSource()
cone.SetCenter(0.0, 0.0, 0.0)
cone.SetDirection(0, 1, 0)
cone.Update()

colors = vtk.vtkNamedColors()

# Define viewport ranges.
xmins = [0, .5]
xmaxs = [0.5, 1]
ymins = [0, 0]
ymaxs = [1.0, 1.0]

ren_bkg = ['AliceBlue', 'GhostWhite']
actor_color = ['Bisque', 'RosyBrown']

for i in range(2):
    ren = vtk.vtkRenderer()
    renWin.AddRenderer()