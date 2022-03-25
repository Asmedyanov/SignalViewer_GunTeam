from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QMenu, QFileDialog, QApplication
from PyQt5.QtGui import QImage
import io
from classes.mplwidget import MplWidget
import functions.filefunctions as filefunctions
from classes.experiment import Experiment
from classes.oscilloscopeeditor import OscilloscopeEditor
from classes.diagnosticeditor import DiagnosticEditor
import os
import constants
import re
from classes.teacher import Teacher
import pandas as pd
# from sklearn.metrics import classification_report
# from sklearn.metrics import confusion_matrix
# from sklearn.metrics import accuracy_score
# from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
# from sklearn.neighbors import KNeighborsClassifier
# from sklearn.naive_bayes import GaussianNB
# from sklearn.tree import DecisionTreeClassifier
# from sklearn.svm import SVC
import itertools


# from sklearn.model_selection import train_test_split


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('./ui/mainwindow.ui', self)
        self.fileList = []
        self.experiment = Experiment(self)
        self.foldername = ''
        self.initActions()
        self.initTabs()
        self.isStadied = True  # self.CheckStadied()
        self.show()

    def DefaultStatusMassege(self):
        self.statusbar.showMessage("Жду Ваших указаний")

    '''def CheckStadied(self):
        try:
            trening_data_0 = pd.read_csv('artif_pic_2pi.txt', sep='\t')
            trening_data_pi = pd.read_csv('artif_pic_pi.txt', sep='\t')
            trening_data = pd.concat([trening_data_0, trening_data_pi])
            if (len(trening_data_pi) == 0) or (len(trening_data_0) == 0):
                self.statusbar.showMessage("Нейросеть НЕ обучена")
                return False

            self.Classificator_0 = DecisionTreeClassifier()
            self.Classificator_test = DecisionTreeClassifier()

            comblist = []
            iter_len = len(constants.pic_parameters_all) + 1
            for i in range(2, 3):
                for combo in itertools.combinations(constants.pic_parameters_all, i):
                    comblist.append(list(combo))
            optimal_heads = comblist[0]
            optimal_heads_matrix = comblist[0]
            max_accurecy = 0
            matrix_coef_max = 0

            for heads in comblist:
                X_train, X_test, Y_train, Y_test = train_test_split(trening_data[heads].values,
                                                                    trening_data['mark'].values, test_size=0.60,
                                                                    random_state=27)

                self.Classificator_test.fit(X_train, Y_train)
                prediction = self.Classificator_test.predict(X_test)
                accuracy = accuracy_score(prediction, Y_test)
                matrix = confusion_matrix(prediction, Y_test)
                matrix_coef = matrix[0][0] + matrix[2][2]
                if accuracy > max_accurecy:
                    max_accurecy = accuracy
                    optimal_heads = heads
                if matrix_coef > matrix_coef_max:
                    matrix_coef_max = matrix_coef
                    optimal_heads_matrix = heads
                # print(f'При сочетании заголовков {heads} получена точность {accuracy} матрица {matrix_coef}')
            print(f'Оптимальное сочетание заголовков {optimal_heads} с точностью {max_accurecy}')
            # print(f'Оптимальное сочетание заголовков по матрице {optimal_heads_matrix} с {matrix_coef_max} совпадений')
            constants.optimal_heads = optimal_heads
            # self.Classificator_0 = KNeighborsClassifier(n_neighbors=10)
            # self.Classificator_0 = LinearDiscriminantAnalysis()
            # self.Classificator_0 = GaussianNB()
            X = trening_data[constants.pic_parameters].values
            Y = trening_data['mark'].values
            self.Classificator_0.fit(X, Y)
            # X = trening_data_pi[constants.pic_parameters].values
            # Y = trening_data_pi['marks'].values
            # self.Classificator_pi = GaussianNB()
            # self.Classificator_pi.fit(X, Y)

            self.statusbar.showMessage("Нейросеть обучена")
            return True
        except:
            self.statusbar.showMessage("Нейросеть НЕ обучена")
            return False'''

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
        currentmenu = self.mainActionsDict['Шаблон эксперимента']
        currentmenu['Открыть шаблон эксперимента'].triggered.connect(self.openExperimentTemplate)
        currentmenu['Открыть последний шаблон эксперимента'].triggered.connect(self.openLastExperimentTemplate)
        currentmenu = self.mainActionsDict['Файл']
        currentmenu['Добавить файл'].triggered.connect(self.addFile)
        currentmenu['Добавить папку'].triggered.connect(self.addFolder)
        currentmenu['Группировать папку по выстрелам'].triggered.connect(self.groupFolder)
        currentmenu['Открыть прошлую сессию'].triggered.connect(self.openResent)
        currentmenu['Открыть следующий файл'].triggered.connect(self.openNextFile)
        currentmenu['Открыть предыдущий файл'].triggered.connect(self.openPrevFile)
        currentmenu = self.mainActionsDict['График']
        currentmenu['Очистить'].triggered.connect(self.clearAll)
        currentmenu['Копировать в буфер обмена'].triggered.connect(self.copyToBuffer)
        currentmenu = self.mainActionsDict['Настройки']
        currentmenu['Осциллографы'].triggered.connect(self.oscSettings)
        currentmenu['Диагностики'].triggered.connect(self.diaSettings)
        currentmenu = self.mainActionsDict['Пакетная обработка папки']
        currentmenu['Пакетная обработка по сырым данным'].triggered.connect(self.packetRowData)
        currentmenu['Пакетная обработка по итоговым данным'].triggered.connect(self.packetResultData)
        # currentmenu['Пакетная обработка по итоговым данным'].triggered.connect(self.packetКResultData)

        '''currentmenu = self.mainActionsDict['Нейросеть']
        currentmenu['Начать обучение'].triggered.connect(self.startLearning)
        currentmenu['Обучение на первую левую'].triggered.connect(self.startLearning_1_l)
        currentmenu['Обучение на первую правую'].triggered.connect(self.startLearning_1_r)
        currentmenu['Обучение на вторую левую'].triggered.connect(self.startLearning_2_l)
        currentmenu['Обучение на вторую правую'].triggered.connect(self.startLearning_2_r)'''
        currentmenu = self.mainActionsDict['Статистика']
        currentmenu['Просмотр сырой из папки'].triggered.connect(self.on_watch_raw_statistic)

    def addFile(self):
        '''self.lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Добавьте файл",
                                        constants.experiments_dir,
                                        ';;'.join(constants.filter_list))[0]'''
        self.lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Добавьте файл")[0]
        self.statusbar.showMessage(f"Открываю файл {self.lastFileName}")
        self.fileList.append(self.lastFileName)
        folderName = '/'.join(self.lastFileName.split('/')[:-1])
        self.foldername = '/'.join(folderName.split('/')[-2:])
        addeddatalist = filefunctions.addFile(self.lastFileName, self.experiment)
        self.experiment.addRawdataList(addeddatalist)
        # self.experiment.upDataDiacnosticData()
        file = open('lastfilename.txt', 'w')
        for name in self.fileList:
            file.write(f'{name}\n')
        file.close()

        self.DefaultStatusMassege()

    def addFolder(self):
        '''self.lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Выберете файл, чью папку Вы хотите добавить",
                                        constants.experiments_dir,
                                        ';;'.join(constants.filter_list))[0]'''
        self.lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Выберете файл, чью папку Вы хотите добавить")[0]
        folderName = '/'.join(self.lastFileName.split('/')[:-1])
        self.statusbar.showMessage(f"Открываю папку {folderName}")
        self.foldername = '/'.join(folderName.split('/')[-2:])
        curentDir = os.getcwd()
        os.chdir(folderName)
        for fileName in os.listdir():
            self.fileList.append(f'{folderName}/{fileName}')
            addeddatalist = filefunctions.addFile(fileName, self.experiment)
            self.experiment.addRawdataList(addeddatalist)
        # self.experiment.upDataDiacnosticData()
        os.chdir(curentDir)
        file = open('lastfilename.txt', 'w')
        for name in self.fileList:
            file.write(f'{name}\n')
        file.close()
        self.DefaultStatusMassege()

    def groupFolder(self):
        '''lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Выберете файл, чью папку Вы хотите группировать по выстрелам",
                                        constants.experiments_dir,
                                        ';;'.join(constants.filter_list))[0]'''
        lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Выберете файл, чью папку Вы хотите группировать по выстрелам")[0]
        folderName = '/'.join(lastFileName.split('/')[:-1])
        self.statusbar.showMessage(f"Группирую папку {folderName}")
        currentDir = os.getcwd()
        os.chdir(folderName)
        for name in os.listdir(folderName):
            for name in os.listdir():
                try:
                    numlist = re.findall(r'\d*\.\d+|\d+', name)

                    n_exper = int(numlist[0])
                    if len(numlist) == 0:
                        continue
                    os.makedirs(f'V{n_exper}', exist_ok=True)
                    os.rename(name, f'V{n_exper}/{name}')
                except:
                    pass
        os.chdir(currentDir)
        self.DefaultStatusMassege()

    def openResent(self):
        self.clearAll()
        file = open('lastfilename.txt', 'r')
        namelist = file.read().split('\n')[:-1]
        self.statusbar.showMessage(f"Откываю прошлую сессию")
        for fileName in namelist:
            self.fileList.append(fileName)
            folderName = '/'.join(fileName.split('/')[:-1])
            self.foldername = '/'.join(folderName.split('/')[-2:])
            addeddatalist = filefunctions.addFile(fileName, self.experiment)
            self.experiment.addRawdataList(addeddatalist)
        self.DefaultStatusMassege()

    def openNextFile(self):
        if len(self.fileList) == 0:
            return
        name = self.fileList[0]
        curentDir = os.getcwd()
        self.statusbar.showMessage(f"Откываю следующий файл")
        try:

            os.chdir(self.folderName)
        except:
            self.folderName = '/'.join(name.split('/')[:-1])

            os.chdir(self.folderName)
        fileList = os.listdir()
        next_index = fileList.index(name.split('/')[-1]) + 1
        if next_index >= len(fileList):
            next_index = 0
        new_name = fileList[next_index]
        self.clearAll()
        try:
            addeddatalist = filefunctions.addFile(new_name, self.experiment)
            self.fileList.append(new_name)
            self.experiment.addRawdataList(addeddatalist)

            folderName = '/'.join(new_name.split('/')[:-1])
            self.foldername = '/'.join(folderName.split('/')[-2:])

        except:
            pass
        os.chdir(curentDir)
        self.DefaultStatusMassege()

    def openPrevFile(self):
        if len(self.fileList) == 0:
            return
        name = self.fileList[0]
        curentDir = os.getcwd()
        self.statusbar.showMessage(f"Откываю предыдущий файл")
        try:

            os.chdir(self.folderName)
        except:
            self.folderName = '/'.join(name.split('/')[:-1])

            os.chdir(self.folderName)
        fileList = os.listdir()
        next_index = fileList.index(name.split('/')[-1]) - 1
        if next_index < 0:
            next_index = len(fileList) - 1
        new_name = fileList[next_index]
        self.clearAll()
        try:
            addeddatalist = filefunctions.addFile(new_name, self.experiment)
            self.fileList.append(new_name)
            self.experiment.addRawdataList(addeddatalist)

            folderName = '/'.join(new_name.split('/')[:-1])
            self.foldername = '/'.join(folderName.split('/')[-2:])

        except:
            pass
        os.chdir(curentDir)
        self.DefaultStatusMassege()

    def clearAll(self):
        self.experiment.clear()
        self.fileList = []
        for plot in self.mainPlotDict.values():
            plot.canvas.fig.clear()
            plot.canvas.draw()

    def oscSettings(self):
        self.oscTemplate = OscilloscopeEditor(self)

    def diaSettings(self):
        self.diaTemplate = DiagnosticEditor(self)

    def openExperimentTemplate(self, name=None):
        if (name is None) or (name == '') or (type(name) is not str):
            self.exptempFileName = \
                QFileDialog.getOpenFileName(self,
                                            "Добавьте файл",
                                            './experiment_templates',
                                            ';;'.join(constants.filter_list))[0]
        else:
            self.exptempFileName = name
        self.statusbar.showMessage(f"Открываю шаблон {self.exptempFileName}")
        if self.exptempFileName != '':
            self.experiment.loadSettings(self.exptempFileName)
        self.setWindowTitle(f'Просмотр сигналов по шаблону {self.exptempFileName.split("/")[-1]}')
        file = open('lastexpname.txt', 'w')
        file.write(self.exptempFileName)
        file.close()
        self.DefaultStatusMassege()

    def openLastExperimentTemplate(self):
        try:
            file = open('lastexpname.txt', 'r')
            self.statusbar.showMessage(f"Открываю последний шаблон")
            name = file.read()
            file.close()
            self.openExperimentTemplate(name)
        except:
            pass
        self.DefaultStatusMassege()

    def upDate(self):
        # self.clearAll()
        self.statusbar.showMessage(f"Перечитываю файлы")
        self.experiment.rawdatalist = []
        for filename in self.fileList:
            addeddatalist = filefunctions.addFile(filename, self.experiment)
            self.experiment.addRawdataList(addeddatalist)
        self.DefaultStatusMassege()

    def copyToBuffer(self):
        buf = io.BytesIO()
        self.tabWidget.currentWidget().findChild(MplWidget).canvas.fig.savefig(buf)
        QApplication.clipboard().setImage(QImage.fromData(buf.getvalue()))
        buf.close()

    def packetRowData(self):
        self.lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Выберете файл, чью папку Вы хотите добавить")[0]
        folderName = '/'.join(self.lastFileName.split('/')[:-2])

        self.foldername = '/'.join(folderName.split('/')[-3:])
        defaultstr = f"Обработка папки {self.foldername} по сырым данным"
        self.statusbar.showMessage(defaultstr)
        curentDir = os.getcwd()
        try:
            os.chdir(folderName)
        except:
            return
        os.makedirs('Сырые сигналы', exist_ok=True)
        folderNameList = [name for name in os.listdir() if os.path.isdir(name)]
        for tfolderName in folderNameList:
            os.chdir(tfolderName)
            for fileName in os.listdir():
                try:
                    self.statusbar.showMessage(f'{defaultstr} файл: {fileName}')
                    addeddatalist = filefunctions.addFile(fileName, self.experiment)
                    self.fileList.append(fileName)
                    self.foldername = tfolderName
                    self.experiment.addRawdataList_NoUpdate(addeddatalist)
                except:
                    pass
            os.chdir(folderName)
            self.mainPlotDict['Сырые сигналы'].canvas.fig.savefig(f'Сырые сигналы/{tfolderName}.png')
            self.clearAll()
        os.chdir(curentDir)
        self.DefaultStatusMassege()

    def packetResultData(self):
        self.lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Выберете файл, чью папку Вы хотите добавить")[0]
        if self.lastFileName in ['', None]:
            return
        folderName = '/'.join(self.lastFileName.split('/')[:-2])

        self.foldername = '/'.join(folderName.split('/')[-3:])
        defaultstr = f"Обработка папки {self.foldername} по итоговым данным"
        self.statusbar.showMessage(defaultstr)
        self.experiment.clear_statistic()
        curentDir = os.getcwd()
        os.chdir(folderName)
        os.makedirs('Итоговые сигналы', exist_ok=True)
        os.makedirs('Статистика', exist_ok=True)
        folderNameList = [name for name in os.listdir() if os.path.isdir(name)]
        for tfolderName in folderNameList:
            if not tfolderName[0] == 'V':
                continue
            os.chdir(tfolderName)
            addeddatalist = []
            for fileName in os.listdir():

                try:
                    self.statusbar.showMessage(f'{defaultstr} файл: {fileName}')
                    addeddatalist = addeddatalist + filefunctions.addFile(fileName, self.experiment)
                    self.fileList.append(fileName)
                    self.foldername = tfolderName

                except:
                    pass
            self.experiment.addRawdataList(addeddatalist)
            print(tfolderName)
            os.chdir(folderName)
            self.mainPlotDict['Итоговые сигналы'].canvas.fig.savefig(f'Итоговые сигналы/{tfolderName}.png')
            self.clearAll()
        self.experiment.saveStatistic_new(f'Статистика')
        self.experiment.viewStatistic()
        # self.mainPlotDict['Сырая статистика'].canvas.fig.savefig(f'Статистика/Статистика.png')
        os.chdir(curentDir)
        self.DefaultStatusMassege()

    def startLearning(self):
        self.statusbar.showMessage(f'Начал обучать нейросеть')
        self.clearAll()
        self.isStadied = False
        self.openExperimentTemplate("experiment_templates/Отладка интреферометра.xml")
        self.addFile()
        if self.fileList != 0:
            self.mTeacher = Teacher(self, 'pic')

    def startLearning_1_l(self):
        self.statusbar.showMessage(f'Начал обучать нейросеть на первую левую')
        self.clearAll()
        self.isStadied = False
        self.openExperimentTemplate("experiment_templates/Отладка интреферометра 1.xml")
        self.addFile()
        if self.fileList != 0:
            self.mTeacher = Teacher(self, 'pic_1_l')

    def startLearning_1_r(self):
        self.statusbar.showMessage(f'Начал обучать нейросеть на первую правую')
        self.clearAll()
        self.isStadied = False
        self.openExperimentTemplate("experiment_templates/Отладка интреферометра 1.xml")
        self.addFile()
        if self.fileList != 0:
            self.mTeacher = Teacher(self, 'pic_1_r')

    def startLearning_2_l(self):
        self.statusbar.showMessage(f'Начал обучать нейросеть на вторую левую')
        self.clearAll()
        self.isStadied = False
        self.openExperimentTemplate("experiment_templates/Отладка интреферометра 2.xml")
        self.addFile()
        if self.fileList != 0:
            self.mTeacher = Teacher(self, 'pic_2_l')

    def startLearning_2_r(self):
        self.statusbar.showMessage(f'Начал обучать нейросеть на вторую правую')
        self.clearAll()
        self.isStadied = False
        self.openExperimentTemplate("experiment_templates/Отладка интреферометра 2.xml")
        self.addFile()
        if self.fileList != 0:
            self.mTeacher = Teacher(self, 'pic_2_r')

    def on_watch_raw_statistic(self):
        self.lastFileName = \
            QFileDialog.getOpenFileName(self,
                                        "Выберете файл, чью папку Вы хотите добавить")[0]
        if self.lastFileName in ['', None]:
            return
        folderName = '/'.join(self.lastFileName.split('/')[:-1])
        currentdir = os.getcwd()
        os.chdir(folderName)
        self.experiment.clear()
        self.experiment.statDict = dict()
        for filename in os.listdir():
            if filename.split('.')[-1] != 'txt':
                continue
            dia_name = filename.split('.')[0]
            data = pd.read_csv(filename, sep='\t').iloc[:, 1:]
            self.experiment.statDict[dia_name] = data

        self.experiment.viewStatistic()