# Симулирует работу АЦП
# Получате сигнал с фотодетектора, в соответствие со совоей тактовой частотой
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from classes.IdealInterferometer import IdealInterferometer
from classes.PlasmaGenerator import PlasmaGenerator
from classes.Photodetector import Photodetector


class ADCsimulator(pd.DataFrame):
    def __init__(self):
        super().__init__()
        self.fdisc = 1.0e1  # MHz
        self.tdisc = 1.0 / self.fdisc

    def Mesure(self):
        photodetector = Photodetector()
        plasmagenerator = PlasmaGenerator()
        interferometer = IdealInterferometer()
        plasmagenerator.generate()
        interferometer.transformation(plasmagenerator)
        photodetector.transformation(interferometer)
        self.Pic_data_pi_left = interferometer.PicData_pi_left
        self.Pic_data_2pi_left = interferometer.PicData_2pi_left
        self.Pic_data_pi_right = interferometer.PicData_pi_right
        self.Pic_data_2pi_right = interferometer.PicData_2pi_right
        signal = photodetector['Values'].values
        time = photodetector['Time'].values
        ndisc = int(self.tdisc / photodetector.dt)
        self['Time'] = time[::ndisc]
        self['Values'] = signal[::ndisc]

    def show_plot(self):
        plt.plot(self['Time'], self['Values'])


'''adc = ADCsimulator()

for i in range(1):
    adc.Mesure()
    adc.show_plot()
plt.show()'''
