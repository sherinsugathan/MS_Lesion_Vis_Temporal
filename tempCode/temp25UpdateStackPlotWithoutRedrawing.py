# Update a stackplot without redrawing.

import matplotlib.pyplot as plt
x = [1, 2, 3, 4, 5]
y1 = [5, 6, 4, 5, 7]
y2 = [1, 6, 4, 5, 6]
y3 = [1, 1, 2, 3, 2]

fig, ax = plt.subplots()
polyCollectionList = ax.stackplot(x, y1, y2, y3)
print(polyCollectionList[0].get_array())

ax.clear()
y1 = [5, 6, 4, 5, 7]
y2 = [1, 6, 4, 5, 6]
y3 = [1, 1, 1, 1, 0]

polyCollectionList[0].set_data(y3)
#ax.stackplot(x, y1, y2, y3)

plt.show()