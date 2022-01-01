import networkx as nx
import matplotlib.pyplot as plt
import graphistry
from pylab import *

class AnnoteFinder:  # thanks to http://www.scipy.org/Cookbook/Matplotlib/Interactive_Plotting
    """
    callback for matplotlib to visit a node (display an annotation) when points are clicked on.  The
    point which is closest to the click and within xtol and ytol is identified.
    """
    def __init__(self, xdata, ydata, annotes, axis=None, xtol=None, ytol=None):
        self.data = list(zip(xdata, ydata, annotes))
        if xtol is None: xtol = ((max(xdata) - min(xdata))/float(len(xdata)))/2
        if ytol is None: ytol = ((max(ydata) - min(ydata))/float(len(ydata)))/2
        self.xtol = xtol
        self.ytol = ytol
        if axis is None: axis = gca()
        self.axis= axis
        self.drawnAnnotations = {}
        self.links = []

    def __call__(self, event):
        if event.inaxes:
            clickX = event.xdata
            clickY = event.ydata
            print(dir(event),event.key)
            if self.axis is None or self.axis==event.inaxes:
                annotes = []
                smallest_x_dist = float('inf')
                smallest_y_dist = float('inf')

                for x,y,a in self.data:
                    if abs(clickX-x)<=smallest_x_dist and abs(clickY-y)<=smallest_y_dist :
                        dx, dy = x - clickX, y - clickY
                        annotes.append((dx*dx+dy*dy,x,y, a) )
                        smallest_x_dist=abs(clickX-x)
                        smallest_y_dist=abs(clickY-y)
                        print(annotes,'annotate')
                    # if  clickX-self.xtol < x < clickX+self.xtol and  clickY-self.ytol < y < clickY+self.ytol :
                    #     dx,dy=x-clickX,y-clickY
                    #     annotes.append((dx*dx+dy*dy,x,y, a) )
                print(annotes,clickX,clickY,self.xtol,self.ytol )
                if annotes:
                    annotes.sort() # to select the nearest node
                    distance, x, y, annote = annotes[0]
                    self.drawAnnote(event.inaxes, x, y, annote)

    def drawAnnote(self, axis, x, y, annote):
        if (x, y) in self.drawnAnnotations:
            markers = self.drawnAnnotations[(x, y)]
            for m in markers:
                m.set_visible(not m.get_visible())
            self.axis.figure.canvas.draw()
        else:
            t = axis.text(x, y, "%s" % (annote), )
            m = axis.scatter([x], [y], marker='d', c='r', zorder=100)
            self.drawnAnnotations[(x, y)] = (t, m)
            self.axis.figure.canvas.draw()


df = pd.DataFrame("LOAD YOUR DATA")

# Build your graph
G = nx.from_pandas_edgelist(df, 'from', 'to')
pos = nx.spring_layout(G,k=0.1, iterations=20)  # the layout gives us the nodes position x,y,annotes=[],[],[] for key in pos:
x, y, annotes = [], [], []
for key in pos:
    d = pos[key]
    annotes.append(key)
    x.append(d[0])
    y.append(d[1])

fig = plt.figure(figsize=(10,10))
ax = fig.add_subplot(111)
ax.set_title('select nodes to navigate there')

nx.draw(G, pos, font_size=6,node_color='#A0CBE2', edge_color='#BB0000', width=0.1,
                  node_size=2,with_labels=True)


af = AnnoteFinder(x, y, annotes)
connect('button_press_event', af)

show()