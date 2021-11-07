# importing the required module
import matplotlib.pyplot as plt

# x axis values
x = list(range(1, 10+1))
# corresponding y axis values
y = [0.1]*10
y2 = [0.15]*10

# plotting the points
plt.scatter(x, y)
plt.figure(dpi=600)
ax = plt.gca()
fig = plt.gcf()

ax.xaxis.set_tick_params(width=5)
ax.set_ylim([0, 0.4])

bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
width, height = bbox.width, bbox.height
drawRegionWidth = width*600
drawRegionHeight = height*600
markerSize = drawRegionWidth/10

sc1 = plt.scatter(x, y, s=markerSize**2, alpha=0.5, marker="s")  # , label="Luck")
sc2 = plt.scatter(x, y2, s=markerSize**2, alpha=0.5, marker="s")  # , label="Luck")

# naming the x axis
plt.xlabel('x - axis')
# naming the y axis
plt.ylabel('y - axis')

# giving a title to my graph
#plt.title('My first graph!')

# function to show the plot
plt.savefig('D://plot.png', dpi=600, bbox_inches='tight')
plt.show()
