from PyQt5 import Qt, QtGui, QtCore
from PyQt5 import QtWidgets, uic
#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys
import seaborn as sns
import matplotlib.pyplot as plt


tips = sns.load_dataset("tips")


def seabornplot():
    g = sns.FacetGrid(tips, col="sex", hue="time", palette="Set1",
                                hue_order=["Dinner", "Lunch"])
    g.map(plt.scatter, "total_bill", "tip", edgecolor="w")
    return g.fig


class MainWindow(Qt.QMainWindow):
    send_fig = QtCore.pyqtSignal(str)

    def __init__(self):
        super(MainWindow, self).__init__()

        self.main_widget = Qt.QWidget(self)

        self.fig = seabornplot()
        self.canvas = FigureCanvas(self.fig)

        self.canvas.setSizePolicy(Qt.QSizePolicy.Expanding,
                      Qt.QSizePolicy.Expanding)
        self.canvas.updateGeometry()
        self.button = Qt.QPushButton("Button")
        self.label = Qt.QLabel("A plot:")

        self.layout = Qt.QGridLayout(self.main_widget)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.canvas)

        self.setCentralWidget(self.main_widget)
        self.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())