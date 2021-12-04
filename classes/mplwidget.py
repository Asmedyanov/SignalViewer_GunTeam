# Matplotlib widget
from classes.mplcanvas import MplCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy


class MplWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)  # Inherit from QWidget
        self.canvas = MplCanvas()  # Create canvas object
        self.vbl = QVBoxLayout()  # Set box for plotting
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
