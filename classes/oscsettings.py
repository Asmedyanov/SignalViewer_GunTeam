from PyQt5 import uic
from PyQt5.QtWidgets import QFrame, QTableWidget


class OscilloscopPage(QFrame):
    def __init__(self, template=None):
        super(OscilloscopPage, self).__init__()
        uic.loadUi('ui/oscilloscoppage.ui', self)
        self.initTabs()
        self.initParameters()
        self.initChanals()
        self.show()

    def initTabs(self):
        self.mainTabTextDict = dict()
        for i in range(self.tabWidget.count()):
            text = self.tabWidget.tabText(i)
            # print(text)
            self.mainTabTextDict[text] = i
        self.mainTabPageDict = dict()
        for text, i in self.mainTabTextDict.items():
            self.mainTabPageDict[text] = self.tabWidget.widget(i)

    def initParameters(self):
        self.parametersDict = dict()
        parametersTable = (self.mainTabPageDict['Параметры'].findChildren(QTableWidget))[0]
        for i in range(parametersTable.verticalHeader().count()):
            self.parametersDict[parametersTable.verticalHeaderItem(i).text()] = \
                parametersTable.item(i, 0).text()

    def initChanals(self):
        pass
