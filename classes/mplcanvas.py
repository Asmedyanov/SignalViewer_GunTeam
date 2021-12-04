import matplotlib
import numpy as np

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        t = np.arange(0, 3, .01)
        self.fig.add_subplot(111
                             ).plot(t, 2 * np.sin(2 * np.pi * t))
        super(MplCanvas, self).__init__(self.fig)
        self.draw()
