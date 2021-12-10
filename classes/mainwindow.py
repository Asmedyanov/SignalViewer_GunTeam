from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QMenu, QFileDialog
from classes.mplwidget import MplWidget
import functions.filefunctions as filefunctions
from classes.experiment import Experiment
from classes.oscilloscopeeditor import OscilloscopeEditor
from classes.diagnosticeditor import DiagnosticEditor
import os
import constants
import re


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('ui/mainwindow.ui', self)
        self.fileList = []
        self.experiment = Experiment(self)
        self.foldername = ''
        self.initActions()
        self.initTabs()
        self.show()

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

    def initActions(self):
        self.mainMenuDict = dict()
        self.mainActionsDict = dict()
        for menu in self.menubar.findChildren(QMenu):
            self.mainMenuDict[menu.title()] = menu
            self.mainActionsDict[menu.title()] = dict()
            for act in menu.actions():
                self.mainActionsDict[menu.title()][act.text()] = act
        currentmenu = self.mainActionsDict['Файл']
        currentmenu['Добавить файл'].triggered.connect(self.addFile)
        currentmenu['Добавить папку'].triggered.connect(self.addFolder)
        currentmenu['Группировать папку по выстрелам'].triggered.connect(self.groupFolder)
        currentmenu['Открыть прошлую сессию'].triggered.connect(self.openResent)
        currentmenu = self.mainActionsDict['График']
        currentmenu['Очистить'].triggered.connect(self.clearAll)
        currentmenu = self.mainActionsDict['Настройки']
        currentmenu['Осциллографы'].triggered.connect(self.oscSettings)
        currentmenu['Диагностики'].triggered.connect(self.diaSettings)

    def addFile(self):
        self.lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Добавьте файл",
                                        constants.experiments_dir,
                                        ';;'.join(constants.filter_list))[0]
        self.fileList.append(self.lastFileName)
        folderName = '/'.join(self.lastFileName.split('/')[:-1])
        self.foldername=folderName
        addeddatalist = filefunctions.addFile(self.lastFileName, self.experiment)
        self.experiment.addRawdataList(addeddatalist)
        file = open('lastfilename.txt', 'w')
        for name in self.fileList:
            file.write(f'{name}\n')
        file.close()

    def addFolder(self):
        self.lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Выберете файл, чью папку Вы хотите добавить",
                                        constants.experiments_dir,
                                        ';;'.join(constants.filter_list))[0]
        folderName = '/'.join(self.lastFileName.split('/')[:-1])
        self.foldername = '/'.join(folderName.split('/')[-2:])
        curentDir = os.getcwd()
        os.chdir(folderName)
        for fileName in os.listdir():
            self.fileList.append(fileName)
            addeddatalist = filefunctions.addFile(fileName, self.experiment)
            self.experiment.addRawdataList(addeddatalist)
        os.chdir(curentDir)
        file = open('lastfilename.txt', 'w')
        for name in self.fileList:
            file.write(f'{folderName}/{name}\n')
        file.close()

    def groupFolder(self):
        lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Выберете файл, чью папку Вы хотите группировать по выстрелам",
                                        constants.experiments_dir,
                                        ';;'.join(constants.filter_list))[0]
        folderName = '/'.join(lastFileName.split('/')[:-1])
        currentDir = os.getcwd()
        os.chdir(folderName)
        for name in os.listdir(folderName):
            for name in os.listdir():
                with re.findall(r'\d*\.\d+|\d+', name) as numlist:
                    n_exper = int(numlist[0])
                    if len(numlist) == 0:
                        continue
                    os.makedirs(f'V{n_exper}', exist_ok=True)
                    os.rename(name, f'V{n_exper}/{name}')
        os.chdir(currentDir)

    def openResent(self):
        file = open('lastfilename.txt', 'r')
        namelist = file.read().split('\n')[:-1]
        for fileName in namelist:
            self.fileList.append(fileName)
            addeddatalist = filefunctions.addFile(fileName, self.experiment)
            self.experiment.addRawdataList(addeddatalist)

    def clearAll(self):
        self.experiment.clear()
        for plot in self.mainPlotDict.values():
            plot.canvas.fig.clear()
            plot.canvas.draw()

    def oscSettings(self):
        self.oscTemplate = OscilloscopeEditor(self)
    def diaSettings(self):
        self.diaTemplate = DiagnosticEditor(self)

    def upDate(self):
        self.clearAll()
        for filename in self.fileList:
            addeddatalist = filefunctions.addFile(filename, self.experiment)
            self.experiment.addRawdataList(addeddatalist)
