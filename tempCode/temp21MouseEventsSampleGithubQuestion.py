import matplotlib.pyplot as plt, numpy as np
from mpl_toolkits.mplot3d import proj3d

def visualize3DData (X, ids, subindus):
    """Visualize data in 3d plot with popover next to mouse position.

    Args:
        X (np.array) - array of points, of shape (numPoints, 3)
    Returns:
        None
    """
    fig = plt.figure(figsize = (16,10))
    ax = fig.add_subplot(111, projection = '3d')
    graph  = ax.scatter(X[:, 0], X[:, 1], X[:, 2], depthshade = False, picker = True)

    def distance(point, event):
        """Return distance between mouse position and given data point

        Args:
            point (np.array): np.array of shape (3,), with x,y,z in data coords
            event (MouseEvent): mouse event (which contains mouse position in .x and .xdata)
        Returns:
            distance (np.float64): distance (in screen coords) between mouse pos and data point
        """
        assert point.shape == (3,), "distance: point.shape is wrong: %s, must be (3,)" % point.shape

        # Project 3d data space to 2d data space
        x2, y2, _ = proj3d.proj_transform(point[0], point[1], point[2], plt.gca().get_proj())
        # Convert 2d data space to 2d screen space
        x3, y3 = ax.transData.transform((x2, y2))

        return np.sqrt ((x3 - event.x)**2 + (y3 - event.y)**2)


    def calcClosestDatapoint(X, event):
        """"Calculate which data point is closest to the mouse position.

        Args:
            X (np.array) - array of points, of shape (numPoints, 3)
            event (MouseEvent) - mouse event (containing mouse position)
        Returns:
            smallestIndex (int) - the index (into the array of points X) of the element closest to the mouse position
        """
        distances = [distance (X[i, 0:3], event) for i in range(X.shape[0])]
        return np.argmin(distances)


    def annotatePlot(X, index, ids):
        """Create popover label in 3d chart

        Args:
            X (np.array) - array of points, of shape (numPoints, 3)
            index (int) - index (into points array X) of item which should be printed
        Returns:
            None
        """
        # If we have previously displayed another label, remove it first
        if hasattr(annotatePlot, 'label'):
            annotatePlot.label.remove()
        # Get data point from array of points X, at position index
        x2, y2, _ = proj3d.proj_transform(X[index, 0], X[index, 1], X[index, 2], ax.get_proj())
        annotatePlot.label = plt.annotate( ids[index],
            xy = (x2, y2), xytext = (-20, 20), textcoords = 'offset points', ha = 'right', va = 'bottom',
            bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
            arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
        fig.canvas.draw()


    def onMouseMotion(event):
        """Event that is triggered when mouse is moved. Shows text annotation over data point closest to mouse."""
        closestIndex = calcClosestDatapoint(X, event)
        annotatePlot (X, closestIndex, ids)


    def onclick(event):
        print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              ('double' if event.dblclick else 'single', event.button,
               event.x, event.y, event.xdata, event.ydata))

    def on_key(event):
        """
        Function to be bound to the key press event
        If the key pressed is delete and there is a picked object,
        remove that object from the canvas
        """
        if event.key == u'delete':
            ax = plt.gca()
            if ax.picked_object:
                ax.picked_object.remove()
                ax.picked_object = None
                ax.figure.canvas.draw()

    def onpick(event):

        xmouse, ymouse = event.mouseevent.xdata, event.mouseevent.ydata
        artist = event.artist
        # print(dir(event.mouseevent))
        ind = event.ind
        # print('Artist picked:', event.artist)
        # # print('{} vertices picked'.format(len(ind)))
        print('ind', ind)
        # # print('Pick between vertices {} and {}'.format(min(ind), max(ind) + 1))
        # print('x, y of mouse: {:.2f},{:.2f}'.format(xmouse, ymouse))
        # # print('Data point:', x[ind[0]], y[ind[0]])
        #
        # # remove = [artist for artist in pickable_artists if     artist.contains(event)[0]]
        # remove = [artist for artist in X if artist.contains(event)[0]]
        #
        # if not remove:
        #     # add a pt
        #     x, y = ax.transData.inverted().transform_point([event.x,     event.y])
        #     pt, = ax.plot(x, y, 'o', picker=5)
        #     pickable_artists.append(pt)
        # else:
        #     for artist in remove:
        #         artist.remove()
        # plt.draw()
        # plt.draw_idle()

        xs, ys, zs = graph._offsets3d
        print(xs[ind[0]])
        print(ys[ind[0]])
        print(zs[ind[0]])
        print(dir(artist))

        # xs[ind[0]] = 0.5
        # ys[ind[0]] = 0.5
        # zs[ind[0]] = 0.5
        # graph._offsets3d = (xs, ys, zs)

        # print(artist.get_facecolor())
        # artist.set_facecolor('red')
        graph._facecolors[ind, :] = (1, 0, 0, 1)

        plt.draw()

    def forceUpdate(event):
        global graph
        graph.changed()

    fig.canvas.mpl_connect('motion_notify_event', onMouseMotion)  # on mouse motion
    fig.canvas.mpl_connect('button_press_event', onclick)
    fig.canvas.mpl_connect('pick_event', onpick)
    fig.canvas.mpl_connect('draw_event', forceUpdate)

    plt.tight_layout()

    plt.show()