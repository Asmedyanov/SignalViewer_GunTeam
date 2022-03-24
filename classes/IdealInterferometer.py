# Добавляет к сигналу гармонику пьезокорректора. Делает преобразование идельного интерферометра Майкельсона. Выдает метки

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from classes.PlasmaGenerator import PlasmaGenerator
from scipy.signal import find_peaks


class IdealInterferometer:
    def __init__(self):
        self.u1 = 0.5  # V
        self.u2 = 0.2  # V
        self.piez_freq = 300.0e-6  # MHz
        self.piez_a = 0.9 * 3.0 * np.pi  # рад

    def transformation(self, data):
        signal = data.Values
        time = data.Time
        fase0 = 2.0 * np.pi * np.random.random_sample()
        fase_piez = self.piez_a * np.sin(2.0 * np.pi * self.piez_freq * time + fase0)
        fase_sum = fase_piez + signal
        fase_2pi = np.remainder(fase_sum, 2.0 * np.pi)  # остаток от деления
        fase_pi = np.remainder(fase_sum, np.pi)
        pics_2pi = find_peaks(-fase_2pi, height=-0.01 * np.pi)[0]
        pics_pi = np.array(list(set(find_peaks(-fase_pi, height=-0.01 * np.pi)[0]).difference(set(pics_2pi))))
        self.Values = self.u1 + self.u2 - 2.0 * np.sqrt(self.u1 * self.u2) * np.cos(fase_sum)
        self.Time = time

        self.PicData_pi_Time = self.Time[pics_pi]
        self.PicData_pi_Values = self.Values[pics_pi]
        self.PicData_2pi_Time = self.Time[pics_2pi]
        self.PicData_2pi_Values = self.Values[pics_2pi]

        pics_pi_grad = np.gradient(fase_sum)[pics_pi]
        pics_2pi_grad = np.gradient(fase_sum)[pics_2pi]
        pics_pi_left = []
        pics_2pi_left = []
        pics_pi_right = []
        pics_2pi_right = []
        for i, grad in enumerate(pics_pi_grad):
            if grad > 0:
                pics_pi_left.append(pics_pi[i])
            elif grad < 0:
                pics_pi_right.append(pics_pi[i])
        for i, grad in enumerate(pics_2pi_grad):
            if grad > 0:
                pics_2pi_left.append(pics_2pi[i])
            elif grad < 0:
                pics_2pi_right.append(pics_2pi[i])

        self.PicData_pi_left_Time = self.Time[pics_pi_left]
        self.PicData_pi_left_Values = self.Values[pics_pi_left]
        self.PicData_2pi_left_Time = self.Time[pics_2pi_left]
        self.PicData_2pi_left_Values = self.Values[pics_2pi_left]
        self.PicData_pi_right = pd.DataFrame()
        self.PicData_pi_right_Time = self.Time[pics_pi_right]
        self.PicData_pi_right_Values = self.Values[pics_pi_right]
        self.PicData_2pi_right = pd.DataFrame()
        self.PicData_2pi_right_Time = self.Time[pics_2pi_right]
        self.PicData_2pi_right_Values = self.Values[pics_2pi_right]

    def show_plot(self):
        plt.plot(self.Time, self.Values, label='Сам график')
        plt.plot(self.PicData_pi_left_Time, self.PicData_pi_left_Values, 'o', label='левые развороты пи')
        plt.plot(self.PicData_2pi_left_Time, self.PicData_2pi_left_Values, 'o', label='левые развороты 2пи')
        plt.plot(self.PicData_pi_right_Time, self.PicData_pi_right_Values, 'o', label='правые развороты пи')
        plt.plot(self.PicData_2pi_right_Time, self.PicData_2pi_right_Values, 'o', label='правые развороты 2пи')


plasma_data = PlasmaGenerator()
interferometer = IdealInterferometer()
for i in range(1):
    plasma_data.generate()
    interferometer.transformation(plasma_data)
    interferometer.show_plot()
plt.legend()
plt.show()
