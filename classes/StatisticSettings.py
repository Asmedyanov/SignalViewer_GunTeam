import numpy as np
from PyQt5.QtWidgets import QRadioButton, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QFrame, QPushButton, \
    QGroupBox, QInputDialog
import matplotlib.pyplot as plt


class StatisticSettings(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.master = parent
        hbl = QHBoxLayout()
        panelX = QGroupBox('По оси X')
        panelY = QGroupBox('По оси Y')
        vblX = QVBoxLayout()
        vblY = QVBoxLayout()
        self.rbuttonList = []
        self.chbuttonList = []
        for mykey, data in self.master.statDict.items():
            for datakey in data.columns:
                chstr = f'{mykey}/{datakey}'
                rbutton = QRadioButton(chstr)
                chbutton = QCheckBox(chstr)
                if chstr == 'U, кВ/start_value':
                    rbutton.setChecked(True)
                if chstr == 'Q, Дж/max':
                    chbutton.setChecked(True)
                self.rbuttonList.append(rbutton)
                self.chbuttonList.append(chbutton)
                vblX.addWidget(rbutton)
                vblY.addWidget(chbutton)
        panelX.setLayout(vblX)
        panelY.setLayout(vblY)
        hbl.addWidget(panelX)
        hbl.addWidget(panelY)
        panelButton = QWidget()
        vblButton = QVBoxLayout()
        self.button_raw = QPushButton('Просмотреть сырую')
        self.button_raw.clicked.connect(self.apply_view_raw)
        vblButton.addWidget(self.button_raw)
        self.button_errorbar = QPushButton('Просмотреть с усами')
        self.button_errorbar.clicked.connect(self.apply_view_errorbar)
        vblButton.addWidget(self.button_errorbar)
        panelButton.setLayout(vblButton)
        hbl.addWidget(panelButton)
        self.setLayout(hbl)
        # self.show()

    def getXY(self):
        for rbutton in self.rbuttonList:
            if rbutton.isChecked():
                strX = rbutton.text()
                break

        strY = []
        for chbutton in self.chbuttonList:
            if chbutton.isChecked():
                strY.append(chbutton.text())
        return strX, strY

    def apply_view_raw(self):

        strX, strY = self.getXY()


        diaX = strX.split('/')[0]
        keyX = strX.split('/')[1]
        dataX = self.master.statDict[diaX][keyX]
        dataY = dict()
        for stry in strY:
            try:
                diaY = stry.split('/')[0]
                keyY = stry.split('/')[1]
                dataY[stry] = self.master.statDict[diaY][keyY]
                plt.plot(dataX, dataY[stry], 'o', label=stry)
            except:
                continue
        plt.legend()
        plt.show()


    def apply_view_errorbar(self):

        strX, strY = self.getXY()
        xstep, ok = QInputDialog().getDouble(self,
                                             "ВВедите шаг статистики по X",
                                             "ВВедите шаг статистики по X",
                                             0.5,
                                             0, 100)

        diaX = strX.split('/')[0]
        keyX = strX.split('/')[1]
        dataX = self.master.statDict[diaX][keyX]
        dataY = dict()
        for stry in strY:
            diaY = stry.split('/')[0]
            keyY = stry.split('/')[1]
            dataY[stry] = self.master.statDict[diaY][keyY]

        dataX_steped = np.around(dataX.values / xstep)
        dataX_steped_set = set(dataX_steped)
        dataX_steped_units = [[] for i in range(len(dataX_steped_set))]
        for i, x in enumerate(dataX_steped):
            for j, x_set in enumerate(dataX_steped_set):
                if x == x_set:
                    dataX_steped_units[j].append(i)
        dataX_avg = []
        dataX_std = []
        for indexes in dataX_steped_units:
            dataX_avg.append(np.average(dataX[indexes]))
            dataX_std.append(np.std(dataX[indexes]))

        dataY_avg = dict()
        dataY_std = dict()
        for stry in strY:
            try:
                data_avg = []
                data_std = []
                for indexes in dataX_steped_units:
                    try:
                        data_avg.append(np.average(dataY[stry][indexes]))
                        data_std.append(np.std(dataY[stry][indexes]))
                    except:
                        print('Не могу это добавить')
                        continue
                dataY_avg[stry] = data_avg
                dataY_std[stry] = data_std
                plt.errorbar(x=dataX_avg, xerr=dataX_std, y=data_avg, yerr=data_std, marker='o', label=stry)
            except:
                print("Не могу это построить")
                continue
        plt.title('Статистика')
        plt.xlabel(strX)
        plt.ylabel(strY[-1])
        plt.grid()
        plt.legend()
        plt.show()
