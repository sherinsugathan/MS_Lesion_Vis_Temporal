import numpy as np
import matplotlib.pyplot as plt
import SimpleITK as sitk
import pickle
import networkx as nx

def adjacent_values(vals, q1, q3):
    upper_adjacent_value = q3 + (q3 - q1) * 1.5
    upper_adjacent_value = np.clip(upper_adjacent_value, q3, vals[-1])

    lower_adjacent_value = q1 - (q3 - q1) * 1.5
    lower_adjacent_value = np.clip(lower_adjacent_value, vals[0], q1)
    return lower_adjacent_value, upper_adjacent_value


def set_axis_style(ax, labels):
    ax.xaxis.set_tick_params(direction='out')
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xticks(np.arange(1, len(labels) + 1))
    ax.set_xticklabels(labels)
    ax.set_xlim(0.25, len(labels) + 0.75)
    ax.set_xlabel('Sample name')


###############################################################
########### WRITER PART #######################################
###############################################################
# rootPath = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\"
# dataCount = 81
# modalities = ["T1", "T2"]

# lesionLabelWiseVoxelData = {}
# for modality in modalities:
#     print("Processing modality", modality)
#     for i in range(dataCount):
#         print("Processing data", i)
#         filePath = rootPath + "structural\\" + modality + "_" + str(i) + ".nii"
#         maskPath = rootPath + "lesionMask\\Consensus" + modality + "VoxelSpaceCorrected" + str(i) + ".nii"
#         structuralData = sitk.ReadImage(filePath)
#         imageConsensus = sitk.ReadImage(maskPath)
#         connectedComponentFilter = sitk.ConnectedComponentImageFilter()
#         connectedComponentImage = connectedComponentFilter.Execute(imageConsensus)
#         structuralArray = list(sitk.GetArrayFromImage(structuralData).flat)
#         labelArray = list(sitk.GetArrayFromImage(connectedComponentImage).flat)
#         objectCount = connectedComponentFilter.GetObjectCount()
#         lesionLabelWiseVoxelData[i] = []
#         for labelVal in range(1, objectCount+1):
#             result = [a for (a,b) in zip(structuralArray,labelArray) if b==labelVal]
#             print(len(result), labelVal)
#             lesionLabelWiseVoxelData[i].append(result)

#     # Save data to file.
#     intensityFile = open("D:\\voxelIntensities" + modality + ".pkl", "wb")
#     pickle.dump(lesionLabelWiseVoxelData, intensityFile)
#     intensityFile.close()


perLabelIntensityDataRoot = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\structural\\"
modalities = ["T1", "T2"]
T1file = perLabelIntensityDataRoot + "voxelIntensitiesT1.pkl"

a_file = open(T1file, "rb")
lesionLabelWiseVoxelData = pickle.load(a_file)
#print(type(lesionLabelWiseVoxelData))

G = nx.read_gml("D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\preProcess\\lesionGraph.gml")
nodeID = 1
nodeIDList = list(G.nodes)
timeList = G.nodes[str(nodeID)]["time"]
labelList = G.nodes[str(nodeID)]["lesionLabel"]
temporalData = list(zip(timeList, labelList))
print(temporalData[0])
print(len(temporalData))





#dataList = lesionLabelWiseVoxelData[0]
#print(len(dataList))



# generate some random data
#data1 = np.random.normal(0, 6, 100)
#data2 = np.random.normal(0, 7, 100)
#data3 = np.random.normal(0, 8, 100)
#data4 = np.random.normal(0, 9, 100)
data = []
timeIndex = 0
for item in temporalData:
    data.append(lesionLabelWiseVoxelData[item[0]][item[1]-1])

# data1 = lesionLabelWiseVoxelData[0][0]
# data2 = lesionLabelWiseVoxelData[0][1]
# data3 = lesionLabelWiseVoxelData[0][2]
# data4 = lesionLabelWiseVoxelData[0][3]
# data5 = lesionLabelWiseVoxelData[0][4]
# data6 = lesionLabelWiseVoxelData[0][5]


# print("Hi", len(data1), type(data1))
# print(len(data2))
# print(len(data3))
# print(len(data4))

#data = list([data1, data2, data3, data4, data5, data6])
#data = list([data1])

fig, ax = plt.subplots()

# build a violin plot
ax.violinplot(data, showmeans=False, showmedians=True)

# add title and axis labels
ax.set_title('violin plot')
ax.set_xlabel('followup')
ax.set_ylabel('intensity')

# add x-tick labels
xticklabels = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6']
#ax.set_xticks([1,2,3,4,5,6])
ax.set_xticks(timeList)
#ax.set_xticklabels(xticklabels)

# add horizontal grid lines
ax.yaxis.grid(True)

# show the plot
plt.show()
