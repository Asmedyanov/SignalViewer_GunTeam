from PyQt5.QtWidgets import QRadioButton, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QFrame, QPushButton
import matplotlib.pyplot as plt


class StatisticSettings(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.master = parent
        hbl = QHBoxLayout()
        panelX = QWidget()
        panelY = QWidget()
        vblX = QVBoxLayout()
        vblY = QVBoxLayout()
        self.rbuttonList = []
        self.chbuttonList = []
        for mykey, data in self.master.statDict.items():
            for datakey in data.columns:
                rbutton = QRadioButton(f'{mykey}/{datakey}')
                chbutton = QCheckBox(f'{mykey}/{datakey}')
                self.rbuttonList.append(rbutton)
                self.chbuttonList.append(chbutton)
                vblX.addWidget(rbutton)
                vblY.addWidget(chbutton)
        panelX.setLayout(vblX)
        panelY.setLayout(vblY)
        hbl.addWidget(panelX)
        hbl.addWidget(panelY)
        self.button = QPushButton('Просмотреть')
        self.button.clicked.connect(self.apply_view)
        hbl.addWidget(self.button)
        self.setLayout(hbl)
        # self.show()

    def apply_view(self):

        for rbutton in self.rbuttonList:
            if rbutton.isChecked():
                strX = rbutton.text()
                break

        strY = []
        for chbutton in self.chbuttonList:
            if chbutton.isChecked():
                strY.append(chbutton.text())

        try:
            diaX = strX.split('/')[0]
            keyX = strX.split('/')[1]
            dataX = self.master.statDict[diaX][keyX]
            dataY = dict()
            for stry in strY:
                diaY = stry.split('/')[0]
                keyY = stry.split('/')[1]
                dataY[stry] = self.master.statDict[diaY][keyY]
                plt.plot(dataX,dataY[stry],'o',label=stry)
            plt.legend()
            plt.show()
        except:
            pass
