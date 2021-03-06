import matplotlib
import numpy as np

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QMenu
from PyQt5.QtCore import pyqtSignal


def formPlotStr(n, x, y):
    # if x>100 and y>100:
    outstring = f'№{n:d} ({x:1.3g}, {y:1.3g})'
    return outstring


class MplCanvas(FigureCanvas):
    MarkChosed = pyqtSignal()
    MarkLabelChosed = pyqtSignal()
    AnnotationsActived = pyqtSignal()

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.textlist = []
        t = np.arange(0, 3, .01)
        self.fig.add_subplot(111
                             ).plot(t, 2 * np.sin(2 * np.pi * t))
        super().__init__(self.fig)
        self.draw()
        self.interactive_flag = 0

    def contextMenuEvent(self, event):
        self.event = event
        contextMenu = QMenu(self)
        # newAct = contextMenu.addAction("Метка", self.activateMark)
        newMark = contextMenu.addAction("Умная метка", self.activateCleverMark)
        removeAllMarks = contextMenu.addAction("Удалить все метки", self.clear_annotations)
        openAct = contextMenu.addAction("Линейка")
        quitAct = contextMenu.addAction("Прямоугольник")
        selected_action = contextMenu.exec_(event.globalPos())

    def clear_annotations(self):
        if len(self.textlist) == 0:
            return
        for k in self.textlist:
            k.remove()
        self.textlist = []
        self.fig.canvas.draw()

    def activateMark(self):
        try:
            if (self.interactive_flag == 0):
                self.clear_annotations()
                self.fig.canvas.mpl_disconnect(self.id_click)
                self.fig.canvas.draw()
                self.interactive_flag = 1
                return
                # Рисовать график
            self.id_click = self.fig.canvas.mpl_connect(
                'button_press_event',
                self.on_click)
            self.interactive_flag = 0
        except:
            self.id_click = self.fig.canvas.mpl_connect(
                'button_press_event',
                self.on_click)
            self.interactive_flag = 0

    def activateCleverMark(self):
        self.id_click = self.fig.canvas.mpl_connect(
            'button_press_event',
            self.on_click_clever)
        self.MarkChosed.connect(self.onMarkChosed)

    def on_click_clever(self, event):
        try:
            xdata = float(getattr(event, 'xdata'))
            ydata = float(getattr(event, 'ydata'))
        except:
            return
        self.outputstring = formPlotStr(
            len(self.textlist) + 1, xdata, ydata)
        self.xy = (xdata, ydata)
        for axis in self.fig.axes:
            if axis == event.inaxes:
                self.axis = axis
        self.MarkChosed.emit()

    def onMarkChosed(self):
        self.fig.canvas.mpl_disconnect(self.id_click)
        self.id_click = self.fig.canvas.mpl_connect(
            'button_press_event',
            self.on_click_clever_label)
        self.MarkLabelChosed.connect(self.onMarkLabelChosed)

    def on_click_clever_label(self, event):
        try:
            xdata = float(getattr(event, 'xdata'))
            ydata = float(getattr(event, 'ydata'))
        except:
            return
        self.xytext = (xdata, ydata)
        self.textlist.append(self.axis.annotate(self.outputstring,
                                                xy=self.xy, xycoords='data',
                                                xytext=self.xytext, textcoords='data',
                                                arrowprops=dict(arrowstyle="-|>",
                                                                connectionstyle="arc3"),
                                                bbox=dict(
                                                    boxstyle="round", fc="w"),
                                                ))
        self.MarkLabelChosed.emit()

    def onMarkLabelChosed(self):
        self.fig.canvas.mpl_disconnect(self.id_click)
        self.fig.canvas.draw()

    def on_click(self, event):
        if event.dblclick != 1:
            return
        try:
            xdata = float(getattr(event, 'xdata'))
            ydata = float(getattr(event, 'ydata'))
        except:
            return
        outputstring = formPlotStr(
            len(self.textlist) + 1, xdata, ydata)
        for axis in self.fig.axes:
            if axis == event.inaxes:
                labelshiftx = (axis.get_xlim()[1] - axis.get_xlim()[0]) * 0.05
                labelshifty = (axis.get_ylim()[1] - axis.get_ylim()[0]) * 0.05
                self.textlist.append(axis.annotate(outputstring,
                                                   xy=(xdata,
                                                       ydata), xycoords='data',
                                                   xytext=(xdata + labelshiftx, ydata + labelshifty), textcoords='data',
                                                   arrowprops=dict(arrowstyle="-|>",
                                                                   connectionstyle="arc3"),
                                                   bbox=dict(
                                                       boxstyle="round", fc="w"),
                                                   ))
        self.fig.canvas.draw()
