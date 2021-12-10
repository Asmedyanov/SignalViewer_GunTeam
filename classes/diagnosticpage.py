from PyQt5 import uic
from PyQt5.QtWidgets import QFrame, QTableWidget, QPushButton, QTableWidgetItem


class DiagnosticPage(QFrame):
    def __init__(self, template=None):
        super(DiagnosticPage, self).__init__()
        uic.loadUi('ui/diagnosticpage.ui', self)
        self.initTabs()
        self.initParameters()
        self.initStatistic()
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

    def initStatistic(self):
        self.statDict = dict()
        statTable = (self.mainTabPageDict['Статистика'].findChildren(QTableWidget))[0]
        for i in range(statTable.verticalHeader().count()):
            stat = dict()
            for j in range(statTable.horizontalHeader().count()):
                stat[statTable.horizontalHeaderItem(j).text()] = statTable.item(i, j)
            if len(statTable.item(i, 0).text()) != 0:
                self.statDict[statTable.item(i, 0).text()] = stat

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
            selectRow = selectTable.rowCount() - 1
        selectTable.removeRow(selectRow)
        self.initStatistic()

    def addstatInTable(self, stat):
        selectPage = self.tabWidget.widget(1)
        selectTable = selectPage.findChildren(QTableWidget)[0]
        selectRow = selectTable.rowCount()
        selectTable.insertRow(selectRow)
        self.statDict[stat] = dict()
        for j in range(selectTable.horizontalHeader().count()):
            selectTable.setItem(selectRow, j, QTableWidgetItem())
            self.statDict[stat][selectTable.horizontalHeaderItem(j).text()] = selectTable.item(selectRow, j)
        self.statDict[stat]['Номер'].setText(stat)

    def clearStatistic(self):
        selectPage = self.tabWidget.widget(1)
        selectTable = selectPage.findChildren(QTableWidget)[0]
        selectTable.setRowCount(0)
        self.statDict = dict()

    def clearParams(self):
        selectPage = self.tabWidget.widget(0)
        selectTable = selectPage.findChildren(QTableWidget)[0]
        selectTable.setRowCount(0)
        self.parametersDict = dict()

    def clear(self):
        self.clearParams()
        self.clearStatistic()

    def statFromDict(self, chdict):
        selectPage = self.tabWidget.widget(1)
        selectTable = selectPage.findChildren(QTableWidget)[0]
        selectRow = selectTable.rowCount()
        selectTable.insertRow(selectRow)
        chnomer = chdict['Номер']
        self.statDict[chnomer] = dict()
        for j in range(selectTable.horizontalHeader().count()):
            selectTable.setItem(selectRow, j, QTableWidgetItem())
            self.statDict[chnomer][selectTable.horizontalHeaderItem(j).text()] = selectTable.item(selectRow, j)
            self.statDict[chnomer][selectTable.horizontalHeaderItem(j).text()].setText(
                chdict[selectTable.horizontalHeaderItem(j).text()]
            )
    def paramFromDict(self, pardict):
        selectPage = self.tabWidget.widget(0)
        selectTable = selectPage.findChildren(QTableWidget)[0]
        selectRow = selectTable.rowCount()
        selectTable.insertRow(selectRow)
        parname = pardict['Имя']
        self.parametersDict[parname] = dict()
        for j in range(selectTable.horizontalHeader().count()):
            selectTable.setItem(selectRow, j, QTableWidgetItem())
            self.parametersDict[parname][selectTable.horizontalHeaderItem(j).text()] = selectTable.item(selectRow, j)
            self.parametersDict[parname][selectTable.horizontalHeaderItem(j).text()].setText(
                pardict[selectTable.horizontalHeaderItem(j).text()]
            )
