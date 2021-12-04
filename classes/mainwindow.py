from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QSizePolicy, QVBoxLayout, QMenu
from classes.mplwidget import MplWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('ui/mainwindow.ui', self)
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

    def addFile(self):
        print('Добавить файл')
