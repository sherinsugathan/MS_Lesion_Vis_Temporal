import vtk
from vtkmodules.vtkCommonColor import vtkNamedColors
import numpy as np

# Data paths (Please set manually)
root_folder = ""
volume_nifti_data_path = ""
volume_mask_data_path = ""

#Load volume data.
# niftiReader = vtk.vtkNIFTIImageReader()
# niftiReader.SetFileName("D:\\FilteredData\\OFAMS00001_DONE\\T1.nii")
# niftiReader.Update()

# Define colors
colors = vtkNamedColors()
ren_bkg = ['AliceBlue', 'GhostWhite', 'WhiteSmoke', 'Seashell']

#Load surface data.
# surfaceReader = vtk.vtkOBJReader()
# surfaceReader.SetFileName("D:\\FilteredData\\OFAMS00001_DONE\\lh.pial.obj")
# surfaceReader.Update()
# pial_mapper = vtk.vtkOpenGLPolyDataMapper()
# pial_mapper.SetInputConnection(surfaceReader.GetOutputPort())
# lh_pial_actor = vtk.vtkActor()
# lh_pial_actor.SetMapper(pial_mapper)

# Load Lesion Data
# lesionReader = vtk.vtkOBJReader()
# lesionReader.SetFileName("D:\\FilteredData\\OFAMS00001_DONE\\lesions.obj")
# lesionReader.Update()
# lesionMapper = vtk.vtkOpenGLPolyDataMapper()
# lesionMapper.SetInputConnection(lesionReader.GetOutputPort())
# lesionActor = vtk.vtkActor()
# lesionActor.SetMapper(lesionMapper)

# Transform pial surface
# transform = vtk.vtkTransform()
# # matrix = [1,0,0,0,\
# #           0,1,0,0,\
# #           0,0,1,0,\
# #           0,0,0,1]
# # matrix = [0.0139272,0.00522744,0.999889,-97.5782,\
# #            -0.999903,9.9809e-05,0.0139269,156.676,\
# #           2.69959e-05,0.999986,-0.00522832,-137.512,\
# #           0,0,0,1]
#
# mrmlDataFile = open ( "D:\\FilteredData\\OFAMS00001_DONE\\mrml.txt" , 'r')
# crasDataFile = open ( "D:\\FilteredData\\OFAMS00001_DONE\\cras.txt" , 'r')
# arrayList = list(np.asfarray(np.array(mrmlDataFile.readline().split(",")),float))
# transform.SetMatrix(arrayList)
# transform.Update()

# cras_t_vector = []
# for t in crasDataFile:
#     cras_t_vector.append(t)
# cras_t_vector = list(map(float, cras_t_vector))
# transform2 = vtk.vtkTransform()
# transform2.PostMultiply()
# transform2.Translate(cras_t_vector[0], cras_t_vector[1], cras_t_vector[2])
# #lh_pial_actor.SetUserTransform(transform2) # 1. Pial Surface Transformation
#
# mrmlDataFile.close()
# crasDataFile.close()

# Ray cast volume mapper
# volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
# volumeMapper.SetInputConnection(niftiReader.GetOutputPort())
# volume = vtk.vtkVolume()
# volume.SetMapper(volumeMapper)
# #volume.SetUserTransform(transform) # 2.Volume Transformation. Apply the IJK to RAS and origin transform.
# #lesionActor.SetUserTransform(transform) # 3. Lesion Transformation.

#
# opacityTransferFunction = vtk.vtkPiecewiseFunction()
# opacityTransferFunction.AddPoint(5,0.0)
# opacityTransferFunction.AddPoint(1500,0.1)
# volprop = vtk.vtkVolumeProperty()
# volprop.SetScalarOpacity(opacityTransferFunction)
# volume.SetProperty(volprop)
#


# Define viewport ranges
mpra = [0, 0, 0.3333, 0.3333]
mprb = [0, 0.3333, 0.3333, 0.6666]
mprc = [0, 0.6666, 0.3333, 1]
vr = [0.3333, 0, 1, 1]
viewports = [mpra, mprb, mprc, vr]

# One render window fr holding multiple viewports.
renWin = vtk.vtkRenderWindow()
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# # Display essentials
for i in range(4):
    ren = vtk.vtkRenderer()
    renWin.AddRenderer(ren)
    ren.SetViewport(viewports[i][0], viewports[i][1], viewports[i][2], viewports[i][3])
    ren.SetBackground(colors.GetColor3d(ren_bkg[i]))
    print(id(ren))

#ren.AddVolume(volume)







# Add the actors to the renderer, set the background and size
#ren.AddActor(lh_pial_actor)
#ren.AddActor(lesionActor)
#ren.AddActor(sphereActor)
ren.SetBackground(0, 0, 1.0)
print(id(ren))
renWin.SetSize(1000, 900)

# This allows the interactor to initalize itself. It has to be
# called before an event loop.
iren.Initialize()

# We'll zoom in a little by accessing the camera and invoking a "Zoom"
# method on it.
ren.ResetCamera()
ren.GetActiveCamera().Zoom(1)
renWin.Render()

# Start the event loop.
iren.Start()
