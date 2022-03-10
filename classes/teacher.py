from PyQt5 import uic
from classes.mplwidget import MplWidget
import functions.filefunctions as filefunctions
import functions.mymathfunctions as mymath
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QMenu, QFileDialog, QApplication
import os
import constants
import re


class Teacher(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent=parent)
        uic.loadUi('./ui/teacher.ui', self)
        self.initTabs()
        self.initDatas()
        self.pushButton.clicked.connect(self.onNextFile)
        self.show()

    def onNextFile(self):
        trening = self.mainPlotDict['Поворот вблизи п'].get_marks()
        print(trening)

    def initTabs(self):
        self.mainTabTextDict = dict()
        for i in range(self.tabWidget.count()):
            text = self.tabWidget.tabText(i)
            self.mainTabTextDict[text] = i
        self.mainTabPageDict = dict()
        for text, i in self.mainTabTextDict.items():
            self.mainTabPageDict[text] = self.tabWidget.widget(i)
        self.mainPlotDict = dict()
        for text, page in self.mainTabPageDict.items():
            plotter = MplWidget()
            self.mainPlotDict[text] = plotter
            try:
                page.layout().addWidget(plotter)
            except:
                layout = QVBoxLayout()
                layout.addWidget(plotter)
                page.setLayout(layout)

    def initDatas(self):
        dataList = self.parent().experiment.diagnosticDataList

        self.mainPlotDict['Поворот вблизи п'].plot_pick_pi(dataList, 'Обучите нейросеть на интерферограмме')
