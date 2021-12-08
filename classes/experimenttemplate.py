from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QMenu, QFileDialog, QPushButton
from classes.oscsettings import OscilloscopPage
import xml.etree.ElementTree as xml

default_file = 'experiment_templates\default.xml'


class ExperimentTemplateEditor(QMainWindow):
    def __init__(self, master=None):
        self.master = master
        super(ExperimentTemplateEditor, self).__init__()
        uic.loadUi('ui/experimenttemplate.ui', self)
        self.initActions()
        self.initTabs()
        self.initButtons()
        #self.loadFile(default_file)
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

    def save(self):
        rootXML = xml.Element('Эксперимент')
        oscsXML = xml.Element('Осциллографы')
        for oscname, osc in self.mainOscDict.items():
            osc.initChanals()
            oscXML = xml.Element(oscname)
            parsXML = xml.Element('Параметры')
            for parname, par in osc.parametersDict.items():
                parXML = xml.Element(parname)
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

        name = QFileDialog.getSaveFileName(self, 'Сохраните файл шаблона эксперимента', "./experiment_templates", )[0]
        if len(name) == 0:
            return

        mainTree = xml.ElementTree(rootXML)

        mainTree.write(name, encoding="UTF-8")

    def loadFile(self, default=None):
        name = default
        if (default is None) or (default is not str):
            name = QFileDialog.getOpenFileName(self, 'Откройте файл шаблона эксперимента', "./experiment_templates", )[
                0]
        if len(name) == 0:
            return
        rootXML = xml.ElementTree(file=name).getroot()
        oscsXML = rootXML.find('Осциллографы')
        for oscname, osc in self.mainOscDict.items():
            oscXML = oscsXML.find(oscname)
            parsXML = oscXML.find('Параметры')
            for parname, par in osc.parametersDict.items():
                parXML = parsXML.find(parname)
                for fname, f in par.items():
                    fXML = parXML.find(fname)
                    f.setText(fXML.text)
            chsXML = oscXML.find('Каналы')
            chXMLall = chsXML.findall('Канал')
            osc.clearChanals()
            for chXML in chXMLall:
                numXML = chXML.find('Номер')
                try:
                    ch = osc.chanalDict[numXML.text]
                except:
                    osc.addChanalInTable(numXML.text)
                    ch = osc.chanalDict[numXML.text]
                for fname, f in ch.items():
                    fXML = chXML.find(fname)
                    f.setText(fXML.text)

    def cancel(self):
        self.loadFile(default_file)

    def apply(self):
        pass