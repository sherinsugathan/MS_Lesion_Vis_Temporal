# Preprocessing for lesion longitudinal visualizations.

# 1. Create tween mesh in blender.
# 2. Export as separate obj files in one shot.
# 3. Read every lesion mesh separately in blender and remesh it and save. This is done to remove polydata issues/artefacts.
# 4. Run MeshToVolume() to generate volume data(consensus mask data) for all the lesion meshes. 
# 5. Run ConnectedComponentsDataWriter() to read the consensus mask data, label lesions them based on connectivity and writes lesion statistics to json file.
# 6. Run ResliceMaskToMRIVoxelSpace() to do voxel space correction between (T1, T2, FLAIR) and consensus mask. This step creates >ConnectedComponents"+modality+"VoxelSpaceCorrected.nii< file.
# 7. Create syntheic holes in nodif brain mask for creating new dti fiber tracts.


import MeshToVolume
import LesionDataWriter
import ResliceMaskToMRIVoxelSpace
import CreateSyntheticHolesInNodifBrainMask

#MeshToVolume.MeshToVolume()
#LesionDataWriter.LesionDataWriter()
#ResliceMaskToMRIVoxelSpace.ResliceMaskToMRIVoxelSpace()
CreateSyntheticHolesInNodifBrainMask.CreateSyntheticHolesInNodifBrainMask()