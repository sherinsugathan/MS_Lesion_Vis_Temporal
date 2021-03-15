import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.text import Text
from matplotlib.image import AxesImage
import numpy as np
from numpy.random import rand
from matplotlib.sankey import Sankey

def pick_simple():
    # simple picking, lines, rectangles and text
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, xticks=[], yticks=[],
                     title="Lesion intensity timeline")
    #ax.set_title('click on points, rectangles or text', picker=True)
    #ax.set_ylabel('ylabel', picker=True, bbox=dict(facecolor='red'))
    #line, = ax.plot(rand(100), 'o', picker=5)  # 5 points tolerance
    sankey = Sankey(ax=ax, scale=0.1, offset=0.2, head_angle=180, format='%.0f', trunklength=1.0)
    #sankey.add(flows=[1,-1,-1], labels=['', 'split1', 'split2'], orientations=[0, 0, 0], pathlengths=[0.25, 0.25,0.25])#, #patchlabel="Widget\nA")  # Arguments to matplotlib.patches.PathPatch
    sankey.add(flows=[1,-1,-1], labels=['', 'split1', 'split2'], orientations=[0, 0, 0], pathlengths=[0, 0,0])#, #patchlabel="Widget\nA")  # Arguments to matplotlib.patches.PathPatch
    
    diagrams = sankey.finish()
    #diagrams[0].texts[-1].set_color('r')
    #diagrams[0].text.set_fontweight('bold')

    def onpick1(event):
        if isinstance(event.artist, Line2D):
            thisline = event.artist
            xdata = thisline.get_xdata()
            ydata = thisline.get_ydata()
            ind = event.ind
            print('onpick1 line:', np.column_stack([xdata[ind], ydata[ind]]))
        elif isinstance(event.artist, Rectangle):
            patch = event.artist
            print('onpick1 patch:', patch.get_path())
        elif isinstance(event.artist, Text):
            text = event.artist
            print('onpick1 text:', text.get_text())

    fig.canvas.mpl_connect('pick_event', onpick1)



    def onpick4(event):
        artist = event.artist
        if isinstance(artist, AxesImage):
            im = artist
            A = im.get_array()
            print('onpick4 image', A.shape)

    fig.canvas.mpl_connect('pick_event', onpick4)


if __name__ == '__main__':
    pick_simple()
    plt.show()