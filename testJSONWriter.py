import json

file = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\preProcess\\test.json"

structureInfo = None
with open(file) as fp: # read source json file.
    structureInfo = json.load(fp)
numberOfLesionElements = len(structureInfo)

r = structureInfo[str(44)]
print(r[1][str(3)])

#for i in 81:

 #   data = {}
