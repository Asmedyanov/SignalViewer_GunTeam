from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QSizePolicy, QVBoxLayout, QMenu, QFileDialog
from classes.oscsettings import OscilloscopPage
import xml.etree.ElementTree as xml
import xml.etree as etree


class ExperimentTemplateEditor(QMainWindow):
    def __init__(self, master=None):
        self.master = master
        super(ExperimentTemplateEditor, self).__init__()
        uic.loadUi('ui/experimenttemplate.ui', self)
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

    def save(self):
        rootXML = xml.Element('Эксперимент')
        oscsXML = xml.Element('Осциллографы')
        for oscname, osc in self.mainOscDict.items():
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
                numXML = xml.Element('Номер')
                numXML.text = chname
                chXML.append(numXML)
                for fname, f in par.items():
                    fXML = xml.Element(fname)
                    fXML.text = f.text()
                    chXML.append(fXML)
                chsXML.append(chXML)
            oscXML.append(chsXML)
            oscsXML.append(oscXML)
        rootXML.append(oscsXML)

        name = QFileDialog.getSaveFileName(self, 'Save File', "./experiment_templates", )[0]

        mainTree = xml.ElementTree(rootXML)

        mainTree.write(name, encoding="UTF-8")
