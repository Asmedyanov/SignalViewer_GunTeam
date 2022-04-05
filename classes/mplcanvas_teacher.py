import matplotlib
import numpy as np
from classes.mplcanvas import *

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QMenu
from PyQt5.QtCore import pyqtSignal



class MplCanvas_teacher(MplCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        super().__init__(parent=parent, width=width, height=height, dpi=dpi)
        self.pic_side_pi = 'left'
        self.pic_side_0 = 'left'

    def on_click_annotate(self, event):
        try:
            clicked = event.artist.clicked
        except:
            event.artist.clicked = 0
            clicked = event.artist.clicked
        if clicked:
            color = 'w'
        else:
            color = 'g'

        event.artist.set_bbox(dict(boxstyle="round", fc=color))
        event.artist.clicked = not clicked
        index = int(event.artist.get_text())
        if event.artist.litera == '0':

            if self.pic_side_0 == 'left':
                self.parent().left_pics_0.append(event.artist.get_position()[0])
                self.pic_side_0 = 'right'
                self.parent().marks_0[index] = -1
            else:
                self.parent().right_pics_0.append(event.artist.get_position()[0])
                self.parent().revers_signal('0')
                self.pic_side_0 = 'left'
                self.parent().marks_0[index] = 1
        if event.artist.litera == 'pi':

            if self.pic_side_pi == 'left':
                self.parent().left_pics_pi.append(event.artist.get_position()[0])
                self.pic_side_pi = 'right'
                self.parent().marks_pi[index] = -1
            else:
                self.parent().right_pics_pi.append(event.artist.get_position()[0])
                self.parent().revers_signal('pi')
                self.pic_side_pi = 'left'
                self.parent().marks_pi[index] = 1
        self.fig.canvas.draw()

    def ActivateAnnotations(self):
        self.id_click = self.fig.canvas.mpl_connect(
            'pick_event',
            self.on_click_annotate)
