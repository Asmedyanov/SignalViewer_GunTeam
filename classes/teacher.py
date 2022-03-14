from PyQt5 import uic
from classes.mplwidget import MplWidget
import functions.filefunctions as filefunctions
import functions.mymathfunctions as mymath
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QMenu, QFileDialog, QApplication
import os
import constants
import re
import numpy as np
import pandas as pd


class Teacher(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent=parent)
        uic.loadUi('./ui/teacher.ui', self)
        self.resultFrame_0 = pd.DataFrame()
        self.resultFrame_pi = pd.DataFrame()
        self.initTabs()
        self.initDatas()
        self.pushButton.clicked.connect(self.onNextFile)
        self.show()
    def DefaultStatusMassege(self):
        self.statusbar.showMessage("Жду Ваших указаний")
    def closeEvent(self, event):
        try:
            self.resultFrame_pi.to_csv('Pics_pi.txt', sep='\t')
            self.resultFrame_0.to_csv('Pics_0.txt', sep='\t')
            self.parent().DefaultStatusMassege()
        except:
            pass
        self.parent().isStadied = self.parent().CheckStadied()

    def onNextFile(self):
        trening_pi = self.mainPlotDict['Поворот вблизи п'].get_marks()
        oddness_pi = not np.sum(trening_pi['marks']) % 2
        # print(trening_pi)
        trening_0 = self.mainPlotDict['Поворот вблизи 0'].get_marks()
        oddness_0 = not np.sum(trening_0['marks']) % 2
        # print(trening_0)

        if oddness_0 and oddness_pi:
            self.statusbar.showMessage(f'Открываю следующий обучающий файл')
            new_dataFrame_pi = pd.DataFrame(trening_pi)
            if len(self.resultFrame_pi.columns) == 0:
                self.resultFrame_pi = new_dataFrame_pi
            else:
                self.resultFrame_pi = pd.concat([self.resultFrame_pi, new_dataFrame_pi])
            new_dataFrame_0 = pd.DataFrame(trening_0)
            if len(self.resultFrame_0.columns) == 0:
                self.resultFrame_0 = new_dataFrame_0
            else:
                self.resultFrame_0 = pd.concat([self.resultFrame_0, new_dataFrame_0])



            self.parent().openNextFile()
            self.initDatas()
            self.DefaultStatusMassege()

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
        self.setWindowTitle(self.parent().fileList[0])
        dataList = self.parent().experiment.diagnosticDataList
        self.mainPlotDict['Поворот вблизи п'].plot_pick_pi(dataList,
                                                           'Выберите четное количество точек поворота вблизи п')
        self.mainPlotDict['Поворот вблизи 0'].plot_pick_0(dataList,
                                                          'Выберите четное количество точек поворота вблизи 0')