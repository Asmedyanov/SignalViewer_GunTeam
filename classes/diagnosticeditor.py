from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QMenu, QFileDialog, QPushButton, QInputDialog
from classes.diagnosticpage import DiagnosticPage
import xml.etree.ElementTree as xml
from constants import *


class DiagnosticEditor(QMainWindow):
    def __init__(self, master=None):
        self.master = master
        super(DiagnosticEditor, self).__init__()
        uic.loadUi('ui/diagnosticeditor.ui', self)
        self.initActions()
        self.initTabs()
        self.initButtons()
        try:
            self.loadFile(master.exptempFileName)
        except:
            self.loadFile(default_file)
        self.show()

    def initTabs(self):
        self.mainTabTextDict = dict()
        for i in range(self.tabWidget.count()):
            text = self.tabWidget.tabText(i)
            self.mainTabTextDict[text] = i
        self.mainTabPageDict = dict()
        for text, i in self.mainTabTextDict.items():
            self.mainTabPageDict[text] = self.tabWidget.widget(i)
        self.mainDiaDict = dict()
        for text, page in self.mainTabPageDict.items():
            Diapage = DiagnosticPage()
            self.mainDiaDict[text] = Diapage
            try:
                page.layout().addWidget(Diapage)
            except:
                layout = QVBoxLayout()
                layout.addWidget(Diapage)
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
        currentmenu['Сохранить'].triggered.connect(self.save)
        currentmenu['Сохранить как'].triggered.connect(self.saveAs)
        currentmenu['Открыть'].triggered.connect(self.loadFile)
        currentmenu = self.mainActionsDict['Редактировать']
        currentmenu['Добавить диагностику'].triggered.connect(self.addDia)
        currentmenu['Удалить диагностику'].triggered.connect(self.remDia)

    def initButtons(self):
        self.mainButtonDict = dict()
        for button in self.frame.findChildren(QPushButton):
            self.mainButtonDict[button.text()] = button
        self.mainButtonDict['Сохранить'].clicked.connect(self.save)
        self.mainButtonDict['Отменить'].clicked.connect(self.cancel)
        self.mainButtonDict['Применить'].clicked.connect(self.apply)

    def saveAs(self, fileName=None):
        if type(fileName) is not str:
            self.fileName = \
            QFileDialog.getSaveFileName(self, 'Сохраните файл шаблона эксперимента', "./experiment_templates", )[
                0]
        else:
            self.fileName = fileName
        self.save()

    def save(self):
        name = self.fileName
        if type(name) is not str:
            return
        if name == '':
            return
        try:
            try:
                mainTree = xml.ElementTree(file=name)
            except:
                file = open(name, 'w')
                file.close()
                mainTree = xml.ElementTree(file=name)
            rootXML = mainTree.getroot()
            if rootXML.tag != 'Эксперимент':
                rootXML = xml.Element('Эксперимент')
        except:
            rootXML = xml.Element('Эксперимент')
        DiasXML = rootXML.find('Диагностики')
        if DiasXML is not None:
            rootXML.remove(DiasXML)
        DiasXML = xml.Element('Диагностики')
        for Dianame, Dia in self.mainDiaDict.items():
            Dia.initStatistic()
            DiaXML = xml.Element('Диагностика')
            nameXML = xml.Element('Имя')
            nameXML.text = Dianame
            DiaXML.append(nameXML)
            parsXML = xml.Element('Параметры')
            for parname, par in Dia.parametersDict.items():
                parXML = xml.Element('Параметр')
                for fname, f in par.items():
                    fXML = xml.Element(fname)
                    fXML.text = f.text()
                    parXML.append(fXML)
                parsXML.append(parXML)
            DiaXML.append(parsXML)
            statsXML = xml.Element('Статистики')
            for statname, stat in Dia.statDict.items():
                statXML = xml.Element('Статистика')
                for fname, f in stat.items():
                    fXML = xml.Element(fname)
                    fXML.text = f.text()
                    statXML.append(fXML)
                statsXML.append(statXML)
            DiaXML.append(statsXML)
            DiasXML.append(DiaXML)
        rootXML.append(DiasXML)
        mainTree = xml.ElementTree(rootXML)
        mainTree.write(name, encoding="UTF-8")
        if len(rootXML.findall('Осциллографы')) == 0:
            self.master.oscSettings()
            self.master.oscTemplate.saveAs(name)
            self.master.oscTemplate.close()

    def loadFile(self, default=None):
        name = default
        if type(default) is not str:
            name = QFileDialog.getOpenFileName(self, 'Откройте файл шаблона эксперимента', "./experiment_templates", )[
                0]
        if len(name) == 0:
            return
        self.fileName = name
        self.setWindowTitle(f'Диагностики файл {name.split("/")[-1]}')
        rootXML = xml.ElementTree(file=name).getroot()
        DiasXML = rootXML.find('Диагностики')
        DiaXMLlist = DiasXML.findall('Диагностика')
        self.returnDiaDict = dict()
        self.mainDiaDict = dict()
        self.tabWidget.clear()
        for DiaXML in DiaXMLlist:
            Dianame = DiaXML.find('Имя').text
            self.tabWidget.addTab(DiagnosticPage(), Dianame)
            self.mainDiaDict[Dianame] = self.tabWidget.widget(len(self.mainDiaDict))
            self.mainDiaDict[Dianame].clear()
            Diadict = dict()
            parsXML = DiaXML.find('Параметры')
            parsdict = dict()
            parXMLlist = parsXML.findall('Параметр')
            for parXML in parXMLlist:
                pardict = dict()
                for parvalue in parXML.iter():
                    if parvalue is parXML: continue
                    pardict[parvalue.tag] = parvalue.text
                parsdict[pardict['Имя']] = pardict
                self.mainDiaDict[Dianame].paramFromDict(pardict)
            Diadict[parsXML.tag] = parsdict

            statsXML = DiaXML.find('Статистики')
            statsdict = dict()
            statXMLlist = statsXML.findall('Статистика')
            for statXML in statXMLlist:
                statdict = dict()
                for statvalue in statXML.iter():
                    if statvalue is statXML: continue
                    statdict[statvalue.tag] = statvalue.text
                statsdict[statdict['Измерение']] = statdict
                self.mainDiaDict[Dianame].statFromDict(statdict)
            Diadict[statsXML.tag] = statsdict
            self.returnDiaDict[Dianame] = Diadict
        self.master.experiment.DiaDict = self.returnDiaDict
        self.master.upDate()

    def cancel(self):
        self.loadFile(default_file)

    def apply(self):
        self.returnDiaDict = dict()
        for Diakey, Dia in self.mainDiaDict.items():
            Diadict = dict()
            parsdict = dict()
            for parkey, par in Dia.parametersDict.items():
                pardict = dict()
                for fkey, f in par.items():
                    pardict[fkey] = f.text()
                parsdict[parkey] = pardict
            Diadict['Параметры'] = parsdict
            chsdict = dict()
            for chkey, ch in Dia.statDict.items():
                chdict = dict()
                for fkey, f in ch.items():
                    chdict[fkey] = f.text()
                chsdict[chkey] = chdict
            Diadict['Диагностики'] = chsdict
            self.returnDiaDict[Diakey] = Diadict
        self.master.experiment.diaDict = self.returnDiaDict
        self.master.upDate()

    def addDia(self, name=None):
        text, ok = QInputDialog().getText(self, 'Введите название новой диагностики', 'Название диагностики:')
        if not (ok and text):
            return
        self.tabWidget.addTab(DiagnosticPage(), text)
        self.mainDiaDict[text] = self.tabWidget.widget(len(self.mainDiaDict))

    def remDia(self):
        pass
