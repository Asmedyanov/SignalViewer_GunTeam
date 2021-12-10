import xml.etree.ElementTree as xml

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QMenu, QFileDialog, QPushButton

from classes.oscsettings import OscilloscopPage
from constants import *


class OscilloscopeEditor(QMainWindow):
    def __init__(self, master=None):
        self.master = master
        super(OscilloscopeEditor, self).__init__()
        uic.loadUi('ui/oscilloscopeeditor.ui', self)
        self.initActions()
        self.initTabs()
        self.initButtons()
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
        self.mainOscDict = dict()
        for text, page in self.mainTabPageDict.items():
            oscpage = OscilloscopPage()
            self.mainOscDict[text] = oscpage
            try:
                page.layout().addWidget(oscpage)
            except:
                layout = QVBoxLayout()
                layout.addWidget(oscpage)
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
        currentmenu['Открыть'].triggered.connect(self.loadFile)

    def initButtons(self):
        self.mainButtonDict = dict()
        for button in self.frame.findChildren(QPushButton):
            self.mainButtonDict[button.text()] = button
        self.mainButtonDict['Сохранить'].clicked.connect(self.save)
        self.mainButtonDict['Отменить'].clicked.connect(self.cancel)
        self.mainButtonDict['Применить'].clicked.connect(self.apply)

    def save(self, fileName=None):
        if type(fileName) is not str:
            name = QFileDialog.getSaveFileName(self, 'Сохраните файл шаблона эксперимента', "./experiment_templates", )[
                0]
        else:
            name = fileName
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
        oscsXML = rootXML.find('Осциллографы')
        if oscsXML is not None:
            rootXML.remove(oscsXML)
        oscsXML = xml.Element('Осциллографы')
        for oscname, osc in self.mainOscDict.items():
            osc.initChanals()
            oscXML = xml.Element('Осциллограф')
            nameXML = xml.Element('Имя')
            nameXML.text = oscname
            oscXML.append(nameXML)
            parsXML = xml.Element('Параметры')
            for parname, par in osc.parametersDict.items():
                parXML = xml.Element('Параметр')
                for fname, f in par.items():
                    fXML = xml.Element(fname)
                    fXML.text = f.text()
                    parXML.append(fXML)
                parsXML.append(parXML)
            oscXML.append(parsXML)
            chsXML = xml.Element('Каналы')
            for chname, ch in osc.chanalDict.items():
                chXML = xml.Element('Канал')
                for fname, f in ch.items():
                    fXML = xml.Element(fname)
                    fXML.text = f.text()
                    chXML.append(fXML)
                chsXML.append(chXML)
            oscXML.append(chsXML)
            oscsXML.append(oscXML)
        rootXML.append(oscsXML)
        mainTree = xml.ElementTree(rootXML)
        mainTree.write(name, encoding="UTF-8")
        if len(rootXML.findall('Диагностики')) == 0:
            self.master.diaSettings()
            self.master.diaTemplate.save(name)
            self.master.diaTemplate.close()

    def loadFile(self, default=None):
        name = default
        if type(default) is not str:
            name = QFileDialog.getOpenFileName(self, 'Откройте файл шаблона эксперимента', "./experiment_templates", )[
                0]
        if len(name) == 0:
            return
        rootXML = xml.ElementTree(file=name).getroot()
        oscsXML = rootXML.find('Осциллографы')
        oscXMLlist = oscsXML.findall('Осциллограф')
        self.returnOscDict = dict()
        for oscXML in oscXMLlist:
            oscname = oscXML.find('Имя').text
            self.mainOscDict[oscname].clear()
            oscdict = dict()
            parsXML = oscXML.find('Параметры')
            parsdict = dict()
            parXMLlist = parsXML.findall('Параметр')
            for parXML in parXMLlist:
                pardict = dict()
                for parvalue in parXML.iter():
                    if parvalue is parXML: continue
                    pardict[parvalue.tag] = parvalue.text
                parsdict[pardict['Имя']] = pardict
                self.mainOscDict[oscname].paramFromDict(pardict)
            oscdict[parsXML.tag] = parsdict

            chsXML = oscXML.find('Каналы')
            chsdict = dict()
            chXMLlist = chsXML.findall('Канал')
            for chXML in chXMLlist:
                chdict = dict()
                for chvalue in chXML.iter():
                    if chvalue is chXML: continue
                    chdict[chvalue.tag] = chvalue.text
                chsdict[chdict['Номер']] = chdict
                self.mainOscDict[oscname].chanalFromDict(chdict)
            oscdict[chsXML.tag] = chsdict
            self.returnOscDict[oscname] = oscdict
        self.master.experiment.oscDict = self.returnOscDict
        self.master.upDate()

    def cancel(self):
        self.loadFile(default_file)

    def apply(self):
        self.returnOscDict = dict()
        for osckey, osc in self.mainOscDict.items():
            oscdict = dict()
            parsdict = dict()
            for parkey, par in osc.parametersDict.items():
                pardict = dict()
                for fkey, f in par.items():
                    pardict[fkey] = f.text()
                parsdict[parkey] = pardict
            oscdict['Параметры'] = parsdict
            chsdict = dict()
            for chkey, ch in osc.chanalDict.items():
                chdict = dict()
                for fkey, f in ch.items():
                    chdict[fkey] = f.text()
                chsdict[chkey] = chdict
            oscdict['Каналы'] = chsdict
            self.returnOscDict[osckey] = oscdict
        self.master.experiment.oscDict = self.returnOscDict
        self.master.upDate()
