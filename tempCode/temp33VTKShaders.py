#!/usr/bin/env python

# This simple example shows how to do basic rendering and pipeline
# creation.

import vtk
# The colors module defines various useful colors.
from vtk.util.colors import tomato


vtk.vtkObject.GlobalWarningDisplayOff()
# This creates a polygonal cylinder model with eight circumferential
# facets.
cylinder = vtk.vtkCylinderSource()
cylinder.SetResolution(8)

# The mapper is responsible for pushing the geometry into the graphics
# library. It may also do color mapping, if scalars or other
# attributes are defined.
cylinderMapper = vtk.vtkOpenGLPolyDataMapper()
cylinderMapper.SetInputConnection(cylinder.GetOutputPort())

vert = """
    varying vec3 n;
    varying vec3 l;

    void propFuncVS(void)
    {
        n = normalize(gl_Normal);
        l = vec3(gl_ModelViewMatrix * vec4(n,0));
        gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    }
"""

frag = """
    varying vec3 n;
    varying vec3 l;

    void propFuncFS( void )
    {
        vec3 cl = vec3(.2,0,.5);
        vec3 light = normalize(l.xyz);
        float vdn = light.z;
        cl = round(vdn * 5) / 5 * cl;
        gl_FragColor = vec4(cl*vdn,1);
        if (vdn < 0.3)
        {
            gl_FragColor = vec4(vec3(0),1);
        }
    }
"""

vert = """
    //VTK::System::Dec
    attribute vec4 vertexMC;
    attribute vec3 normalMC;
    uniform mat3 normalMatrix;
    uniform mat4 MCDCMatrix;
    uniform mat4 MCVCMatrix;  // Combined model to view transform.
    varying vec3 normalVCVSOutput2;
    varying vec4 vertexVCVSOutput2;
    attribute vec2 tcoordMC;
    out vec3 color;
    varying vec2 tcoordVCVSOutput;
    void main () {
      normalVCVSOutput2 = normalMatrix * normalMC;
      tcoordVCVSOutput = tcoordMC;
      vertexVCVSOutput2 = MCVCMatrix * vertexMC;
      gl_Position = MCDCMatrix * vertexMC;
    }
"""
frag = """
   //VTK::System::Dec
   varying vec4 vColor;
   in vec3 color;
   void main()
   {
       gl_FragColor = vec4(1.0,1.0,0.0,1.0);
       //gl_FragColor = vColor;
    }
"""

cylinderMapper.SetVertexShaderCode(vert)
cylinderMapper.SetFragmentShaderCode(frag)

# The actor is a grouping mechanism: besides the geometry (mapper), it
# also has a property, transformation matrix, and/or texture map.
# Here we set its color and rotate it -22.5 degrees.
cylinderActor = vtk.vtkActor()
cylinderActor.SetMapper(cylinderMapper)
cylinderActor.GetProperty().SetColor(tomato)
cylinderActor.RotateX(30.0)
cylinderActor.RotateY(-45.0)

# Create the graphics structure. The renderer renders into the render
# window. The render window interactor captures mouse events and will
# perform appropriate camera or actor manipulation depending on the
# nature of the events.
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)


op = vtk.vtkOpenGLProperty()
openGLproperty = cylinderActor.GetProperty()
openGLproperty.EdgeVisibilityOn()
#openGLproperty.SetPropProgram(pgm)
openGLproperty.ShadingOn()

# Add the actors to the renderer, set the background and size
ren.AddActor(cylinderActor)
ren.SetBackground(0.1, 0.2, 0.4)
renWin.SetSize(200, 200)

# This allows the interactor to initalize itself. It has to be
# called before an event loop.
iren.Initialize()

# We'll zoom in a little by accessing the camera and invoking a "Zoom"
# method on it.
ren.ResetCamera()
ren.GetActiveCamera().Zoom(1.5)
renWin.Render()

# Start the event loop.
iren.Start()