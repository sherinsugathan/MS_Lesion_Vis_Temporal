# This script is responsible for writing lesion projection information on both hemispheres for all supported projection methods.
import vtk
import numpy as np
import math
import json
import SimpleITK as sitk

'''
##########################################################################
    Compute streamlines using temperature scalars.
    Returns: Nothing
##########################################################################
'''
def computeStreamlines(subjectFolder, lesionPointDataSet = None, gradientFile = None):
    #temperatureDataFileName = subjectFolder + "\\heatMaps\\aseg.auto_temperature.nii"
    if(gradientFile == None):
        print("ERROR: GRADIENT FILE NOT FOUND.")
        quit()
    else:
        temperatureDataFileName = gradientFile

    niftiReaderTemperature = vtk.vtkNIFTIImageReader()
    niftiReaderTemperature.SetFileName(temperatureDataFileName)
    niftiReaderTemperature.Update()
    cellDerivatives = vtk.vtkCellDerivatives()
    cellDerivatives.SetInputConnection(niftiReaderTemperature.GetOutputPort())
    cellDerivatives.Update()
    cellDataToPointData = vtk.vtkCellDataToPointData()
    cellDataToPointData.SetInputConnection(cellDerivatives.GetOutputPort())
    cellDataToPointData.Update()

    # Transform for temperature/gradient data
    QFormMatrixTemperature = niftiReaderTemperature.GetQFormMatrix()
    qFormListTemperature = [0] * 16 #the matrix is 4x4
    QFormMatrixTemperature.DeepCopy(qFormListTemperature, QFormMatrixTemperature)
    transformGradient = vtk.vtkTransform()
    transformGradient.PostMultiply()
    transformGradient.SetMatrix(qFormListTemperature)
    transformGradient.Update()
    
    # Create point source and actor
    # psource = vtk.vtkPointSource()
    # if(seedCenter!=None):
    #     psource.SetNumberOfPoints(500)
    #     psource.SetCenter(seedCenter)
    #     psource.SetRadius(seedRadius)
    # else:
    #     psource.SetNumberOfPoints(500)
    #     psource.SetCenter(127,80,150)
    #     psource.SetRadius(80)
    #pointSourceMapper = vtk.vtkPolyDataMapper()
    #pointSourceMapper.SetInputConnection(psource.GetOutputPort())
    #pointSourceActor = vtk.vtkActor()
    #pointSourceActor.SetMapper(pointSourceMapper)

    # if(seedCenter!=None):
    transformFilter = vtk.vtkTransformFilter()
    transformFilter.SetInputConnection(cellDataToPointData.GetOutputPort())
    transformFilter.SetTransform(transformGradient)
    transformFilter.Update()

    # Perform stream tracing
    streamers = vtk.vtkStreamTracer()
    streamers.SetInputConnection(transformFilter.GetOutputPort())
    # if(seedCenter!=None):
    #     streamers.SetInputConnection(transformFilter.GetOutputPort())
    # else:
    #     streamers.SetInputConnection(cellDataToPointData.GetOutputPort())
    #streamers.SetIntegrationDirectionToForward()
    streamers.SetIntegrationDirectionToBoth()
    streamers.SetComputeVorticity(False)
    #streamers.SetSourceConnection(psource.GetOutputPort())
    streamers.SetSourceData(lesionPointDataSet)
    
    # streamers.SetMaximumPropagation(100.0)
    # streamers.SetInitialIntegrationStep(0.05)
    # streamers.SetTerminalSpeed(.51)

    streamers.SetMaximumPropagation(100.0)
    streamers.SetInitialIntegrationStep(0.2)
    streamers.SetTerminalSpeed(.01)
    streamers.Update()
    tubes = vtk.vtkTubeFilter()
    tubes.SetInputConnection(streamers.GetOutputPort())
    tubes.SetRadius(0.5)
    tubes.SetNumberOfSides(3)
    tubes.CappingOn()
    tubes.SetVaryRadius(0)
    tubes.Update()
    # lut = vtk.vtkLookupTable()
    # lut.SetHueRange(.667, 0.0)
    # lut.Build()
    # streamerMapper = vtk.vtkPolyDataMapper()
    # streamerMapper.SetInputConnection(tubes.GetOutputPort())
    # streamerMapper.SetLookupTable(lut)
    # streamerActor = vtk.vtkActor()
    # streamerActor.SetMapper(streamerMapper)
    # # if(seedCenter!=None):
    # #     pass
    # # else:
    # #     streamerActor.SetUserTransform(transformGradient)
    # streamerMapper.Update()

    # writer = vtk.vtkXMLPolyDataWriter()
    # writer.SetFileName("D:\\streamlines.vtp")
    # writer.SetInputData(tubes.GetOutput())
    # writer.Write()

    # plyWriter = vtk.vtkPLYWriter()
    # plyWriter.SetFileName("D:\\streamlines.ply")
    # plyWriter.SetInputData(tubes.GetOutput())
    # plyWriter.Write()
    return tubes.GetOutput()


'''
##########################################################################
    Retrieve precomputed streamline bundles (for DTI datasets only)
    Returns: Nothing
##########################################################################
'''
def computeStreamlinesDTI(timeStep, subjectFolder, lesionID):
    streamlineDataFilePath = subjectFolder + "\\surfaces\\streamlinesMultiBlockDatasetDTI" + str(timeStep) + ".xml"
    reader = vtk.vtkXMLMultiBlockDataReader()
    reader.SetFileName(streamlineDataFilePath)
    reader.Update()

    mb = reader.GetOutput()
    #print("DATACOUNT" , mb.GetNumberOfBlocks())

    polyData = vtk.vtkPolyData.SafeDownCast(mb.GetBlock(lesionID))
    if polyData and polyData.GetNumberOfPoints():
        tubeFilter = vtk.vtkTubeFilter()
        tubeFilter.SetInputData(polyData)
        tubeFilter.SetRadius(0.5)
        tubeFilter.SetNumberOfSides(50)
        tubeFilter.Update()
        return tubeFilter.GetOutput()
    else:
        return None

'''
##########################################################################
    Extract lesions by processing labelled lesion mask data.
    Returns: Lesion actors.
##########################################################################
'''
def extractLesions(timeStep, subjectFolder):
    # Generate connected components from lesion mask.
    maskFileName = subjectFolder + "lesionMask\\Consensus" + str(timeStep) + ".nii"
    connectedComponentOutputFileName = subjectFolder + "lesionMask\\ConnectedComponents.nii"
    imageLesionMask = sitk.ReadImage(maskFileName)
    # Connected component filter.
    connectedComponentFilter = sitk.ConnectedComponentImageFilter()
    connectedComponentImage = connectedComponentFilter.Execute(imageLesionMask)
    sitk.WriteImage(connectedComponentImage, connectedComponentOutputFileName)
    
    # Load lesion mask
    niftiReaderLesionMask = vtk.vtkNIFTIImageReader()
    niftiReaderLesionMask.SetFileName(subjectFolder + "lesionMask\\ConnectedComponents.nii")
    niftiReaderLesionMask.Update()

    # Read QForm matrix from mask data.
    QFormMatrixMask = niftiReaderLesionMask.GetQFormMatrix()
    qFormListMask = [0] * 16 #the matrix is 4x4
    QFormMatrixMask.DeepCopy(qFormListMask, QFormMatrixMask)

    lesionActors = []
    surface = vtk.vtkDiscreteMarchingCubes()
    surface.SetInputConnection(niftiReaderLesionMask.GetOutputPort())
    
    for i in range(connectedComponentFilter.GetObjectCount()):
        surface.SetValue(i,i+1)
    surface.Update()
    component = vtk.vtkPolyData()
    component.DeepCopy(surface.GetOutput())

    transform = vtk.vtkTransform()
    transform.Identity()
    transform.SetMatrix(qFormListMask)
    transform.Update()
    transformFilter = vtk.vtkTransformFilter()
    transformFilter.SetInputConnection(surface.GetOutputPort())
    transformFilter.SetTransform(transform)
    transformFilter.Update()

    for i in range(connectedComponentFilter.GetObjectCount()):
        threshold = vtk.vtkThreshold()
        threshold.SetInputData(transformFilter.GetOutput())
        threshold.ThresholdBetween(i+1,i+1)
        threshold.Update()

        geometryFilter = vtk.vtkGeometryFilter()
        geometryFilter.SetInputData(threshold.GetOutput())
        geometryFilter.Update()

        lesionMapper = vtk.vtkOpenGLPolyDataMapper()
        lesionMapper.SetInputConnection(geometryFilter.GetOutputPort())
        lesionActor = vtk.vtkActor()
        lesionActor.SetMapper(lesionMapper)
        #information = vtk.vtkInformation()
        #information.Set(informationKey,"lesions")
        #lesionActor.GetProperty().SetInformation(information)
        #informationID = vtk.vtkInformation()
        #informationID.Set(informationKeyID,str(i+1))
        #lesionActor.GetProperty().SetInformation(informationID)
        lesionActors.append(lesionActor)

    return lesionActors

'''
##########################################################################
    Compute surface mapping and write to json file
    Returns: none.
##########################################################################
'''
def computeAndWriteMapping(timeStep, jsonPath, dataType, gradientFile = None):
    # load precomputed lesion properties
    structureInfo = None
    with open(jsonPath) as fp: # read source json file.
        structureInfo = json.load(fp)
    #numberOfLesionElements = len(structureInfo)

    lesionActors = extractLesions(timeStep, rootPath)

    numberOfLesionActors = len(lesionActors)
    numberOfLesionElements = numberOfLesionActors

    if(numberOfLesionElements!=numberOfLesionElements):
        print("LESION COUNT MISMATCH. PREMATURE TERMINATION!")

    #actorindex = 23
    for jsonElementIndex in (range(1,numberOfLesionElements+1)):
        # Compute streamlines.
        print("Processing lesions at timestep :", timeStep, ",", str(jsonElementIndex), "/", str(numberOfLesionActors))
        streamLinePolyData = None
        if(dataType == "STRUCTURAL"):
            streamLinePolyData = computeStreamlines(rootPath, lesionActors[jsonElementIndex-1].GetMapper().GetInput(), gradientFile)
        if(dataType == "DTI"):
            streamLinePolyData = computeStreamlinesDTI(timeStep, rootPath, jsonElementIndex-1)
        if(dataType == "DANIELSSONDISTANCE"):
            streamLinePolyData = computeStreamlines(rootPath, lesionActors[jsonElementIndex-1].GetMapper().GetInput(), gradientFile)
        
        if(streamLinePolyData != None): # If there is a polydata available for selected lesion.
            streamerMapper = vtk.vtkPolyDataMapper()
            streamerMapper.SetInputData(streamLinePolyData)
            streamerActor = vtk.vtkActor()
            streamerActor.SetMapper(streamerMapper)
            #Load streamlines data
            #readerStreamlines = vtk.vtkXMLPolyDataReader()
            #readerStreamlines.SetFileName(streamlinesFile)
            #readerStreamlines.Update()

            #streamLinePolyData = readerStreamlines.GetOutput()
            spacing = [0] * 3  # desired volume spacing
            spacing[0] = 0.5
            spacing[1] = 0.5
            spacing[2] = 0.5
            bounds = [0]*6
            streamLinePolyData.GetBounds(bounds)
            #print(bounds)


            streamLineVolumeImage = vtk.vtkImageData()
            streamLineVolumeImage.SetSpacing(spacing)
            streamDims = [0]*3
            for i in range(3):
                streamDims[i] = int(math.ceil((bounds[i * 2 + 1] - bounds[i * 2]) / spacing[i]))
            streamLineVolumeImage.SetDimensions(streamDims)
            streamLineVolumeImage.SetExtent(0, streamDims[0] - 1, 0, streamDims[1] - 1, 0, streamDims[2] - 1)
            streamOrigin = [0]*3
            streamOrigin[0] = bounds[0] + spacing[0] / 2
            streamOrigin[1] = bounds[2] + spacing[1] / 2
            streamOrigin[2] = bounds[4] + spacing[2] / 2
            streamLineVolumeImage.SetOrigin(streamOrigin)
            streamLineVolumeImage.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)

            inVal = 255
            outVal = 0
            count = streamLineVolumeImage.GetNumberOfPoints()
            for i in range(count):
                streamLineVolumeImage.GetPointData().GetScalars().SetTuple1(i, inVal)

            pol2stencil = vtk.vtkPolyDataToImageStencil()
            pol2stencil.SetInputData(streamLinePolyData)
            pol2stencil.SetOutputOrigin(streamOrigin)
            pol2stencil.SetOutputSpacing(spacing)
            pol2stencil.SetOutputWholeExtent(streamLineVolumeImage.GetExtent())
            pol2stencil.Update()

            imgStencil = vtk.vtkImageStencil()
            imgStencil.SetInputData(streamLineVolumeImage)
            imgStencil.SetStencilConnection(pol2stencil.GetOutputPort())
            imgStencil.ReverseStencilOff()
            imgStencil.SetBackgroundValue(outVal)
            imgStencil.Update()

            # writer = vtk.vtkMetaImageWriter()
            # writer.SetFileName("D:\\SphereVolume.mhd")
            # writer.SetInputData(imgStencil.GetOutput())
            # writer.Write()  

            # mapperStreamlines = vtk.vtkPolyDataMapper()
            # mapperStreamlines.SetInputConnection(readerStreamlines.GetOutputPort())
            # actorStreamlines = vtk.vtkActor()
            # actorStreamlines.SetMapper(mapperStreamlines)


            #myImageReader = vtk.vtkMetaImageReader()
            #myImageReader.SetFileName("D:\\SphereVolume.mhd")
            #myImageReader.Update()

            volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
            volumeMapper.SetInputConnection(imgStencil.GetOutputPort())
            volume = vtk.vtkVolume()
            volume.SetMapper(volumeMapper)
            opacityTransferFunction = vtk.vtkPiecewiseFunction()
            opacityTransferFunction.AddPoint(0,0.0)
            opacityTransferFunction.AddPoint(255,1)
            volprop = vtk.vtkVolumeProperty()
            volprop.SetScalarOpacity(opacityTransferFunction)
            volume.SetProperty(volprop)
            print("VOLUME GENERATED")

            #Load surface data Lh
            surfaceReaderLh = vtk.vtkOBJReader()
            surfaceReaderLh.SetFileName(surfaceFileLh)
            surfaceReaderLh.Update()
            mapperLh = vtk.vtkOpenGLPolyDataMapper()
            mapperLh.SetInputConnection(surfaceReaderLh.GetOutputPort())
            actorLh = vtk.vtkActor()
            actorLh.SetMapper(mapperLh)

            #Load surface data Rh
            surfaceReaderRh = vtk.vtkOBJReader()
            surfaceReaderRh.SetFileName(surfaceFileRh)
            surfaceReaderRh.Update()
            mapperRh = vtk.vtkOpenGLPolyDataMapper()
            mapperRh.SetInputConnection(surfaceReaderRh.GetOutputPort())
            actorRh = vtk.vtkActor()
            actorRh.SetMapper(mapperRh)

            # Apply necessary transforms
            actorLh.SetUserTransform(transform)
            actorRh.SetUserTransform(transform)

            # Apply transformations to data Rh. This is needed in addition to previous step which applied only to display data/
            transformFilterRh = vtk.vtkTransformPolyDataFilter()
            transformFilterRh.SetInputData(surfaceReaderRh.GetOutput()) 
            transformFilterRh.SetTransform(transform)
            transformFilterRh.Update()
            # Apply transformations to data Lh. This is needed in addition to previous step which applied only to display data/
            transformFilterLh = vtk.vtkTransformPolyDataFilter()
            transformFilterLh.SetInputData(surfaceReaderLh.GetOutput()) 
            transformFilterLh.SetTransform(transform)
            transformFilterLh.Update()

            mapperRh.Update()
            mapperLh.Update()
            # Probe Filtering
            probeFilterRh = vtk.vtkProbeFilter()
            probeFilterRh.SetSourceConnection(imgStencil.GetOutputPort())
            probeFilterRh.SetInputData(transformFilterRh.GetOutput())
            probeFilterRh.Update()
            probeFilterLh = vtk.vtkProbeFilter()
            probeFilterLh.SetSourceConnection(imgStencil.GetOutputPort())
            probeFilterLh.SetInputData(transformFilterLh.GetOutput())
            probeFilterLh.Update()

            # probedSurfaceMapperRh = vtk.vtkPolyDataMapper()
            # probedSurfaceMapperRh.SetInputConnection(probeFilterRh.GetOutputPort())
            # probedSurfaceMapperRh.SetScalarRange(probeFilterRh.GetOutput().GetScalarRange())
            # probedSurfaceMapperRh.ScalarVisibilityOn()
            # lesionStreamActorRh = vtk.vtkActor()
            # lesionStreamActorRh.SetMapper(probedSurfaceMapperRh)
            # probedSurfaceMapperLh = vtk.vtkPolyDataMapper()
            # probedSurfaceMapperLh.SetInputConnection(probeFilterLh.GetOutputPort())
            # probedSurfaceMapperLh.SetScalarRange(probeFilterLh.GetOutput().GetScalarRange())
            # probedSurfaceMapperLh.ScalarVisibilityOn()
            # lesionStreamActorLh = vtk.vtkActor()
            # lesionStreamActorLh.SetMapper(probedSurfaceMapperLh)

            # Get color/point data array.
            #print(probeFilterLh.GetOutput().GetPointData())
            pointDataArrayRh = probeFilterRh.GetOutput().GetPointData().GetArray("ImageScalars")
            pointDataArrayLh = probeFilterLh.GetOutput().GetPointData().GetArray("ImageScalars")

            # Set Colors for vertices
            vtk_colorsRh = vtk.vtkUnsignedCharArray()
            vtk_colorsRh.SetNumberOfComponents(3)
            vtk_colorsLh = vtk.vtkUnsignedCharArray()
            vtk_colorsLh.SetNumberOfComponents(3)
            clrGreen = [0,255,0] # Red color representing pathology.
            clrRed = [255,0,0] # Green color representing normal areas
            numberOfPointsRh = mapperRh.GetInput().GetNumberOfPoints()
            numberOfPointsLh = mapperLh.GetInput().GetNumberOfPoints()

            mappingIndicesRh = []
            mappingIndicesLh = []
            #Assign colors based on thresholding probed values.
            for index in range(numberOfPointsLh):
                if(pointDataArrayLh.GetValue(index)>0):
                    vtk_colorsLh.InsertNextTuple3(clrRed[0], clrRed[1], clrRed[2])
                    mappingIndicesLh.append(index)
                else:
                    vtk_colorsLh.InsertNextTuple3(clrGreen[0], clrGreen[1], clrGreen[2])
            for index in range(numberOfPointsRh):
                if(pointDataArrayRh.GetValue(index)>0):
                    vtk_colorsRh.InsertNextTuple3(clrRed[0], clrRed[1], clrRed[2])
                    mappingIndicesRh.append(index)
                else:
                    vtk_colorsRh.InsertNextTuple3(clrGreen[0], clrGreen[1], clrGreen[2])
            print("PROBING COMPLETED")
            #print("Impact on Lh=", len(mappingIndicesLh))
            #print("Impact on Rh=", len(mappingIndicesRh))
            print("Results timeStep", timeStep, ",", str(jsonElementIndex), "/", str(numberOfLesionActors), "IMPACT_LH :", str(len(mappingIndicesLh)))
            print("Results timeStep", timeStep, ",", str(jsonElementIndex), "/", str(numberOfLesionActors), "IMPACT_RH :", str(len(mappingIndicesRh)))
        else: # Empty polyline Data. this can happen for tiny lesions.
            mappingIndicesRh = []
            mappingIndicesLh = []
            print("Results timeStep", timeStep, ",", str(jsonElementIndex), "/", str(numberOfLesionActors), "IMPACT_LH :", str(len(mappingIndicesLh)))
            print("Results timeStep", timeStep, ",", str(jsonElementIndex), "/", str(numberOfLesionActors), "IMPACT_RH :", str(len(mappingIndicesRh)))
        # Set Color Data as scalars on the point data.
        # probedSurfaceMapperRh.GetInput().GetPointData().SetScalars(vtk_colorsRh)
        # probedSurfaceMapperLh.GetInput().GetPointData().SetScalars(vtk_colorsLh)
        # probedSurfaceMapperRh.Update()
        # probedSurfaceMapperLh.Update()

        r = structureInfo[str(timeStep)]
        # Preparing JSON data
        for p in r[0][str(jsonElementIndex)]:
            lesionDataDict = p
            if(dataType == "STRUCTURAL"):
                lesionDataDict['AffectedPointIdsLh'] = mappingIndicesLh
                lesionDataDict['AffectedPointIdsRh'] = mappingIndicesRh
            if(dataType == "DTI"):
                lesionDataDict['AffectedPointIdsLhDTI'] = mappingIndicesLh
                lesionDataDict['AffectedPointIdsRhDTI'] = mappingIndicesRh
            if(dataType == "DANIELSSONDISTANCE"):
                lesionDataDict['AffectedPointIdsLhDanielsson'] = mappingIndicesLh
                lesionDataDict['AffectedPointIdsRhDanielsson'] = mappingIndicesRh
            data[jsonElementIndex]=[]
            data[jsonElementIndex].append(lesionDataDict) 

    print("Processed timstep:", timeStep, "JSON File FLUSH: ", dataType)


'''
##########################################################################
    MAIN SCRIPT
    Returns: Success :)
##########################################################################
'''
dataCount = 81
rootPath = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\"
outputFile = rootPath + "preProcess\\lesionStatistics.json"

dataDictMain = {}
# Process every time step
for i in range(dataCount):
    surfaceFileLh = rootPath + "surfaces\\lh.white.obj"
    surfaceFileRh = rootPath + "surfaces\\rh.white.obj"
    translationFilePath = rootPath + "meta\\cras.txt"
    f = open(translationFilePath, "r")
    t_vector = []
    for t in f:
        t_vector.append(t)
    t_vector = list(map(float, t_vector))
    transform = vtk.vtkTransform()
    transform.PostMultiply()
    transform.Translate(t_vector[0], t_vector[1], t_vector[2])
    f.close()

    data = {}
    #computeAndWriteMapping(i, outputFile, "STRUCTURAL", rootPath + "heatMaps\\aseg.auto_temperature.nii")
    #computeAndWriteMapping(i, outputFile, "DANIELSSONDISTANCE", rootPath + "sdm\\sdm_gradient.nii")
    computeAndWriteMapping(i, outputFile, "DTI")

    dataDictMain[i] = []
    dataDictMain[i].append(data)

    print("Processed time step ", i)



with open(outputFile, 'w') as fp:
    json.dump(dataDictMain, fp, indent=4)

print("Processing completed successfully")

