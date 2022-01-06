import vtk
import os
import sys


def main():
    colors = vtk.vtkNamedColors()

    # One render window, multiple viewports.
    rw = vtk.vtkRenderWindow()
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(rw)

    # Define viewport ranges.
    # xmins = [0, .5, 0, .5]
    # xmaxs = [0.5, 1, 0.5, 1]
    # ymins = [0, 0, .5, .5]
    # ymaxs = [0.5, 0.5, 1, 1]

    xmins = [0, 0, 0.2, 0.4, 0.6, 0.8]
    xmaxs = [1, 0.2, 0.4, 0.6, 0.8, 1]
    ymins = [0.3, 0, 0, 0, 0, 0]
    ymaxs = [1, 0.3, 0.3, 0.3, 0.3, 0.3]

    # Have some fun with colors.
    ren_bkg = ['AliceBlue', 'GhostWhite', 'WhiteSmoke', 'Seashell', 'GhostWhite', 'WhiteSmoke']
    actor_color = ['Bisque', 'RosyBrown', 'Goldenrod', 'Chocolate', 'RosyBrown', 'Goldenrod']

    sources = get_sources()
    for i in range(6):
        ren = vtk.vtkRenderer()
        rw.AddRenderer(ren)
        ren.SetViewport(xmins[i], ymins[i], xmaxs[i], ymaxs[i])

        # Share the camera between viewports.
        if i == 0:
            camera = ren.GetActiveCamera()
            camera.Azimuth(30)
            camera.Elevation(30)
        else:
            ren.SetActiveCamera(camera)

        # Create a mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sources[i].GetOutputPort())
        actor = vtk.vtkActor()
        actor.GetProperty().SetColor(colors.GetColor3d(actor_color[i]))
        actor.SetMapper(mapper)
        ren.AddActor(actor)
        ren.SetBackground(colors.GetColor3d(ren_bkg[i]))

        ren.ResetCamera()

    rw.Render()
    rw.SetWindowName('MultipleViewPorts')
    rw.SetSize(600, 600)
    iren.Start()


def get_sources():
    sources = list()

    # Create a sphere
    sphere =vtk.vtkSphereSource()
    sphere.SetCenter(0.0, 0.0, 0.0)
    sphere.Update()
    sources.append(sphere)
    # Create a cone
    cone = vtk.vtkConeSource()
    cone.SetCenter(0.0, 0.0, 0.0)
    cone.SetDirection(0, 1, 0)
    cone.Update()
    sources.append(cone)
    # Create a cube
    cube = vtk.vtkCubeSource()
    cube.SetCenter(0.0, 0.0, 0.0)
    cube.Update()
    sources.append(cube)
    # Create a cylinder
    cylinder = vtk.vtkCylinderSource()
    cylinder.SetCenter(0.0, 0.0, 0.0)
    cylinder.Update()
    sources.append(cylinder)

    # Create a cylinder2
    cylinder2 = vtk.vtkCylinderSource()
    cylinder2.SetCenter(0.0, 0.0, 0.0)
    cylinder2.Update()
    sources.append(cylinder2)

    # Create a cylinder3
    cylinder3 = vtk.vtkCylinderSource()
    cylinder3.SetCenter(0.0, 0.0, 0.0)
    cylinder3.Update()
    sources.append(cylinder3)

    return sources


if __name__ == '__main__':
    main()