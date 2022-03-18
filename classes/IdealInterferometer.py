# Добавляет к сигналу гармонику пьезокорректора. Делает преобразование идельного интерферометра Майкельсона. Выдает метки

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from classes.PlasmaGenerator import PlasmaGenerator
from scipy.signal import find_peaks


class IdealInterferometer(pd.DataFrame):
    def __init__(self):
        super().__init__()
        self.u1 = 0.5  # V
        self.u2 = 0.2  # V
        self.piez_freq = 300.0e-6  # MHz
        self.piez_a = 0.9 * 3.0 * np.pi  # рад

    def transformation(self, data):
        signal = data['Values'].values
        time = data['Time'].values
        fase0 = 2.0 * np.pi * np.random.random_sample()
        fase_piez = self.piez_a * np.sin(2.0 * np.pi * self.piez_freq * time + fase0)
        fase_sum = fase_piez + signal
        fase_2pi = np.remainder(fase_sum, 2.0 * np.pi)
        fase_pi = np.remainder(fase_sum, np.pi)
        pics_2pi = find_peaks(-fase_2pi, height=-0.01 * np.pi)[0]
        pics_pi = np.array(list(set(find_peaks(-fase_pi, height=-0.01 * np.pi)[0]).difference(set(pics_2pi))))
        self['Values'] = self.u1 + self.u2 - 2.0 * np.sqrt(self.u1 * self.u2) * np.cos(fase_sum)
        self['Time'] = time

        self.PicData_pi = pd.DataFrame()
        self.PicData_pi['Time'] = self['Time'].values[pics_pi]
        self.PicData_pi['Values'] = self['Values'].values[pics_pi]
        self.PicData_2pi = pd.DataFrame()
        self.PicData_2pi['Time'] = self['Time'].values[pics_2pi]
        self.PicData_2pi['Values'] = self['Values'].values[pics_2pi]

    def show_plot(self):
        plt.plot(self['Time'], self['Values'])
        plt.plot(self.PicData_pi['Time'], self.PicData_pi['Values'], 'o')
        plt.plot(self.PicData_2pi['Time'], self.PicData_2pi['Values'], 'o')


'''plasma_data = PlasmaGenerator()
interferometer = IdealInterferometer()
for i in range(1):
    plasma_data.generate()
    interferometer.transformation(plasma_data)
    interferometer.show_plot()
plt.show()'''
