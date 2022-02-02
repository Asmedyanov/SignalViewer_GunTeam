from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QMenu, QFileDialog, QApplication
from PyQt5.QtGui import QImage
import io
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
        uic.loadUi('./ui/mainwindow.ui', self)
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
        currentmenu = self.mainActionsDict['Шаблон эксперимента']
        currentmenu['Открыть шаблон эксперимента'].triggered.connect(self.openExperimentTemplate)
        currentmenu['Открыть последний шаблон эксперимента'].triggered.connect(self.openLastExperimentTemplate)
        currentmenu = self.mainActionsDict['Файл']
        currentmenu['Добавить файл'].triggered.connect(self.addFile)
        currentmenu['Добавить папку'].triggered.connect(self.addFolder)
        currentmenu['Группировать папку по выстрелам'].triggered.connect(self.groupFolder)
        currentmenu['Открыть прошлую сессию'].triggered.connect(self.openResent)
        currentmenu['Открыть следующий файл'].triggered.connect(self.openNextFile)
        currentmenu['Открыть предыдущий файл'].triggered.connect(self.openPrevFile)
        currentmenu = self.mainActionsDict['График']
        currentmenu['Очистить'].triggered.connect(self.clearAll)
        currentmenu['Копировать в буфер обмена'].triggered.connect(self.copyToBuffer)
        currentmenu = self.mainActionsDict['Настройки']
        currentmenu['Осциллографы'].triggered.connect(self.oscSettings)
        currentmenu['Диагностики'].triggered.connect(self.diaSettings)
        currentmenu = self.mainActionsDict['Пакетная обработка папки']
        currentmenu['Пакетная обработка по сырым данным'].triggered.connect(self.packetRowData)
        currentmenu['Пакетная обработка по итоговым данным'].triggered.connect(self.packetResultData)
        #currentmenu['Пакетная обработка по итоговым данным'].triggered.connect(self.packetКResultData)

    def addFile(self):
        '''self.lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Добавьте файл",
                                        constants.experiments_dir,
                                        ';;'.join(constants.filter_list))[0]'''
        self.lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Добавьте файл")[0]
        self.fileList.append(self.lastFileName)
        folderName = '/'.join(self.lastFileName.split('/')[:-1])
        self.foldername = '/'.join(folderName.split('/')[-2:])
        addeddatalist = filefunctions.addFile(self.lastFileName, self.experiment)
        self.experiment.addRawdataList(addeddatalist)
        #self.experiment.upDataDiacnosticData()
        file = open('lastfilename.txt', 'w')
        for name in self.fileList:
            file.write(f'{name}\n')
        file.close()

    def addFolder(self):
        '''self.lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Выберете файл, чью папку Вы хотите добавить",
                                        constants.experiments_dir,
                                        ';;'.join(constants.filter_list))[0]'''
        self.lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Выберете файл, чью папку Вы хотите добавить")[0]
        folderName = '/'.join(self.lastFileName.split('/')[:-1])
        self.foldername = '/'.join(folderName.split('/')[-2:])
        curentDir = os.getcwd()
        os.chdir(folderName)
        for fileName in os.listdir():
            self.fileList.append(f'{folderName}/{fileName}')
            addeddatalist = filefunctions.addFile(fileName, self.experiment)
            self.experiment.addRawdataList(addeddatalist)
        #self.experiment.upDataDiacnosticData()
        os.chdir(curentDir)
        file = open('lastfilename.txt', 'w')
        for name in self.fileList:
            file.write(f'{name}\n')
        file.close()

    def groupFolder(self):
        '''lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Выберете файл, чью папку Вы хотите группировать по выстрелам",
                                        constants.experiments_dir,
                                        ';;'.join(constants.filter_list))[0]'''
        lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Выберете файл, чью папку Вы хотите группировать по выстрелам")[0]
        folderName = '/'.join(lastFileName.split('/')[:-1])
        currentDir = os.getcwd()
        os.chdir(folderName)
        for name in os.listdir(folderName):
            for name in os.listdir():
                try:
                    numlist = re.findall(r'\d*\.\d+|\d+', name)

                    n_exper = int(numlist[0])
                    if len(numlist) == 0:
                        continue
                    os.makedirs(f'V{n_exper}', exist_ok=True)
                    os.rename(name, f'V{n_exper}/{name}')
                except:
                    pass
        os.chdir(currentDir)

    def openResent(self):
        self.clearAll()
        file = open('lastfilename.txt', 'r')
        namelist = file.read().split('\n')[:-1]
        for fileName in namelist:
            self.fileList.append(fileName)
            folderName = '/'.join(fileName.split('/')[:-1])
            self.foldername = '/'.join(folderName.split('/')[-2:])
            addeddatalist = filefunctions.addFile(fileName, self.experiment)
            self.experiment.addRawdataList(addeddatalist)

    def openNextFile(self):
        if len(self.fileList) == 0:
            return
        name = self.fileList[0]
        numlist = re.findall(r'v\d+\.bin', name)
        if len(numlist) == 0:
            numlist = re.findall(r'0*\d+\.PRN', name)
            if len(numlist) == 0:
                self.openResent()
                return
            new_name = name.replace(numlist[-1], f'{10000 + int(numlist[-1][:-4]) + 1}.PRN'[1:])
        else:
            new_name = name.replace(numlist[-1], f'v{int(numlist[-1][1:-4]) + 1}.bin')
        self.clearAll()
        try:
            addeddatalist = filefunctions.addFile(new_name, self.experiment)
            self.fileList.append(new_name)
            self.experiment.addRawdataList(addeddatalist)

            folderName = '/'.join(new_name.split('/')[:-1])
            self.foldername = '/'.join(folderName.split('/')[-2:])

        except:
            self.openResent()
            return

    def openPrevFile(self):
        if len(self.fileList) == 0:
            return
        name = self.fileList[0]
        numlist = re.findall(r'v\d+\.bin', name)
        if len(numlist) == 0:
            numlist = re.findall(r'\d+\.PRN', name)
            if len(numlist) == 0:
                self.openResent()
                return
            new_name = name.replace(numlist[-1], f'{10000 + int(numlist[-1][:-4]) - 1}.PRN'[1:])
        else:
            new_name = name.replace(numlist[-1], f'v{int(numlist[-1][1:-4]) - 1}.bin')
        self.clearAll()

        try:
            addeddatalist = filefunctions.addFile(new_name, self.experiment)
            self.fileList.append(new_name)
            folderName = '/'.join(new_name.split('/')[:-1])
            self.foldername = '/'.join(folderName.split('/')[-2:])
            self.experiment.addRawdataList(addeddatalist)

        except:
            self.openResent()
            return

    def clearAll(self):
        self.experiment.clear()
        self.fileList = []
        for plot in self.mainPlotDict.values():
            plot.canvas.fig.clear()
            plot.canvas.draw()

    def oscSettings(self):
        self.oscTemplate = OscilloscopeEditor(self)

    def diaSettings(self):
        self.diaTemplate = DiagnosticEditor(self)

    def openExperimentTemplate(self, name=None):
        if (name is None) or (name == '') or (type(name) is not str):
            self.exptempFileName = \
                QFileDialog.getOpenFileName(self,
                                            "Добавьте файл",
                                            './experiment_templates',
                                            ';;'.join(constants.filter_list))[0]
        else:
            self.exptempFileName = name
        if self.exptempFileName != '':
            self.experiment.loadSettings(self.exptempFileName)
        self.setWindowTitle(f'Просмотр сигналов по шаблону {self.exptempFileName.split("/")[-1]}')
        file = open('lastexpname.txt', 'w')
        file.write(self.exptempFileName)
        file.close()

    def openLastExperimentTemplate(self):
        try:
            file = open('lastexpname.txt', 'r')
            name = file.read()
            file.close()
            self.openExperimentTemplate(name)
        except:
            return

    def upDate(self):
        # self.clearAll()
        self.experiment.rawdatalist = []
        for filename in self.fileList:
            addeddatalist = filefunctions.addFile(filename, self.experiment)
            self.experiment.addRawdataList(addeddatalist)

    def copyToBuffer(self):
        buf = io.BytesIO()
        self.tabWidget.currentWidget().findChild(MplWidget).canvas.fig.savefig(buf)
        QApplication.clipboard().setImage(QImage.fromData(buf.getvalue()))
        buf.close()

    def packetRowData(self):
        self.lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Выберете файл, чью папку Вы хотите добавить")[0]
        folderName = '/'.join(self.lastFileName.split('/')[:-2])
        self.foldername = '/'.join(folderName.split('/')[-3:])
        curentDir = os.getcwd()
        os.chdir(folderName)
        os.makedirs('Сырые сигналы', exist_ok=True)
        for tfolderName in os.listdir():
            os.chdir(tfolderName)
            for fileName in os.listdir():
                try:
                    addeddatalist = filefunctions.addFile(fileName, self.experiment)
                    self.fileList.append(fileName)
                    self.foldername = tfolderName
                    self.experiment.addRawdataList_NoUpdate(addeddatalist)
                except:
                    pass
            os.chdir(folderName)
            self.mainPlotDict['Сырые сигналы'].canvas.fig.savefig(f'Сырые сигналы/{tfolderName}.png')
            self.clearAll()
        os.chdir(curentDir)
    def packetResultData(self):
        self.lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Выберете файл, чью папку Вы хотите добавить")[0]
        folderName = '/'.join(self.lastFileName.split('/')[:-2])
        self.foldername = '/'.join(folderName.split('/')[-3:])
        curentDir = os.getcwd()
        os.chdir(folderName)
        os.makedirs('Итоговые сигналы', exist_ok=True)
        for tfolderName in os.listdir():
            os.chdir(tfolderName)
            for fileName in os.listdir():
                try:
                    addeddatalist = filefunctions.addFile(fileName, self.experiment)
                    self.fileList.append(fileName)
                    self.foldername = tfolderName
                    self.experiment.addRawdataList(addeddatalist)
                except:
                    pass
            print(tfolderName)
            os.chdir(folderName)
            self.mainPlotDict['Итоговые сигналы'].canvas.fig.savefig(f'Итоговые сигналы/{tfolderName}.png')
            self.clearAll()
        os.chdir(curentDir)
