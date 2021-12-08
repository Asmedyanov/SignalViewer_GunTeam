from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QMenu, QFileDialog
from classes.mplwidget import MplWidget
import functions.filefunctions as filefunctions
from classes.experiment import Experiment
from classes.experimenttemplate import ExperimentTemplateEditor


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('ui/mainwindow.ui', self)
        self.experiment = Experiment(self)
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
        currentmenu = self.mainActionsDict['График']
        currentmenu['Очистить'].triggered.connect(self.clearAll)
        currentmenu = self.mainActionsDict['Настройки']
        currentmenu['Осциллографы'].triggered.connect(self.oscSettings)

    def addFile(self):
        filterlist = [
            'Любые файлы (*.*)',
            'АЦП Хильченко(*.bin)',
            'Дистанционный АКИП(A*.CSV)',
            'Старый Тектроникс (F*\d.CSV)',
            'Лекрой (*.PRN)',
            'Дистанционный АКИП (INT*.CSV)',
            'Старый Тектроникс (tek*.csv)'
        ]
        self.lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Добавьте файл",
                                        "D:/1.Clouds/GUN_TEAM/Experiments",
                                        ';;'.join(filterlist))[0]
        addeddatalist = filefunctions.addFile(self.lastFileName, self.experiment)
        self.experiment.addRawdataList(addeddatalist)

    def clearAll(self):
        self.experiment.clear()
        for plot in self.mainPlotDict.values():
            plot.canvas.fig.clear()
            plot.canvas.draw()

    def oscSettings(self):
        self.expTemplate = ExperimentTemplateEditor(self)
