# importing the required module
import matplotlib.pyplot as plt
import numpy as np

Z = np.random.rand(2, 10)

Z[0][0] = np.nan
#Z = np.ma.masked_where((Z == np.nan), Z)
print(Z)

plt.imshow(Z)
plt.title("Lesion Intensity")
plt.show()

