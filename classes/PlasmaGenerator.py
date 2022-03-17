# Генерирует радомный сигнал плазмы в настроенном диапазоне, нужен для обучения нейросети
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class PlasmaGenerator(pd.DataFrame):
    def __init__(self):
        super().__init__()
        self.Npoints = 125e3
        self.fdisc = 1.0e2  # MHz
        self.tdisc = 1 / self.fdisc  # mks
        self.sigma_left_min = 0.1  # mks
        self.sigma_left_max = 10.0  # mks
        self.sigma_right_min = 10.0  # mks
        self.sigma_right_max = 50.0  # mks
        self.tau_min = 20.0  # mks
        self.tau_max = 60.0  # mks
        self.a_min = 0.5 * np.pi  # rad
        self.a_max = 4 * np.pi  # rad
        self['Time'] = np.arange(self.Npoints) / self.fdisc

    def generate(self):
        sigma_left = np.random.random_sample() * (self.sigma_left_max - self.sigma_left_min)+self.sigma_left_min
        sigma_right = np.random.random_sample() * (self.sigma_right_max - self.sigma_right_min)+self.sigma_right_max
        tau = np.random.random_sample() * (self.tau_max - self.tau_min)+self.tau_min
        a = np.random.random_sample() * (self.a_max - self.a_min)+self.a_min
        self['Values'] = np.where(self['Time'] < tau, self.gauss(a, sigma_left, tau, self['Time']),
                                  self.gauss(a, sigma_right, tau, self['Time']))
        return self

    def show_plot(self):
        plt.plot(self['Time'], self['Values'])


    def gauss(self, a, s, tau, t):
        return a * np.exp(-np.power((t - tau) / s, 2))


generator = PlasmaGenerator()
for i in range(5):
    generator.generate()
    generator.show_plot()
plt.show()