from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QSizePolicy, QVBoxLayout, QMenu, QFileDialog
from classes.oscsettings import OscilloscopPage
from classes.gumteamxml import GunTeamXML


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
        name = QFileDialog.getSaveFileName(self, 'Save File', "./experiment_templates", )[0]
        self.xml = GunTeamXML(name)


        for oscname, osc in self.mainOscDict.items():
            self.xml.addElement('Эксперимент', oscname)
            self.xml.addElement(oscname, 'Параметры')
            for pname, p in osc.parametersDict.items():
                self.xml.addElement('Параметры', pname)
                for ppname, pp in p.items():
                    self.xml.addElement(pname, ppname, pp.text())
            self.xml.addElement(oscname, 'Каналы')
            for cname, c in osc.chanalDict.items():
                self.xml.addElement('Каналы', f'Канал_{cname}')
                for ccname, cc in c.items():
                    self.xml.addElement(f'Канал_{cname}', ccname, cc.text())'''
        self.xml.updatafile()
