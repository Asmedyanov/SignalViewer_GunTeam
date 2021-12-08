from PyQt5 import uic
from PyQt5.QtWidgets import QFrame, QTableWidget, QPushButton, QTableWidgetItem


class OscilloscopPage(QFrame):
    def __init__(self, template=None):
        super(OscilloscopPage, self).__init__()
        uic.loadUi('ui/oscilloscoppage.ui', self)
        self.initTabs()
        self.initParameters()
        self.initChanals()
        self.initButtons()
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
            parametr = dict()
            for j in range(parametersTable.horizontalHeader().count()):
                parametr[parametersTable.horizontalHeaderItem(j).text()] = parametersTable.item(i, j)
            self.parametersDict[parametersTable.verticalHeaderItem(i).text()] = parametr

    def initChanals(self):
        self.chanalDict = dict()
        chanalTable = (self.mainTabPageDict['Каналы'].findChildren(QTableWidget))[0]
        for i in range(chanalTable.verticalHeader().count()):
            chanal = dict()
            for j in range(chanalTable.horizontalHeader().count()):
                chanal[chanalTable.horizontalHeaderItem(j).text()] = chanalTable.item(i, j)
            if len(chanalTable.item(i, 0).text()) != 0:
                self.chanalDict[chanalTable.item(i, 0).text()] = chanal

    def initButtons(self):
        self.mainButtonDict = dict()
        for button in self.frame.findChildren(QPushButton):
            self.mainButtonDict[button.text()] = button
        self.mainButtonDict['Добавить'].clicked.connect(self.addClick)
        self.mainButtonDict['Удалить'].clicked.connect(self.remClick)

    def addClick(self):
        if not self.tabWidget.currentIndex():
            return
        selectPage = self.tabWidget.widget(self.tabWidget.currentIndex())
        selectTable = selectPage.findChildren(QTableWidget)[0]
        selectRow = selectTable.rowCount()
        selectTable.insertRow(selectRow)

    def remClick(self):
        if not self.tabWidget.currentIndex():
            return
        selectPage = self.tabWidget.widget(self.tabWidget.currentIndex())
        selectTable = selectPage.findChildren(QTableWidget)[0]
        try:
            selectRow = selectTable.selectionModel().selectedRows()[0].row()
            print(selectRow)
        except:
            selectRow = selectTable.rowCount()-1
        selectTable.removeRow(selectRow)

    def addChanalInTable(self, chanal):
        selectPage = self.tabWidget.widget(1)
        selectTable = selectPage.findChildren(QTableWidget)[0]
        selectRow = selectTable.rowCount()
        selectTable.insertRow(selectRow)
        self.chanalDict[chanal] = dict()
        for j in range(selectTable.horizontalHeader().count()):
            selectTable.setItem(selectRow, j, QTableWidgetItem())
            self.chanalDict[chanal][selectTable.horizontalHeaderItem(j).text()] = selectTable.item(selectRow, j)
        self.chanalDict[chanal]['Номер'].setText(chanal)
