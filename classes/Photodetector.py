# Преобразует сигнал симулируя действие фотодетектора
# (добаляет наводку, параллельный сдвиг, сглаживание на собственной емкости, фильтр высоких частот),
# нужен для обучения нейросети
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from classes.IdealInterferometer import IdealInterferometer
from classes.PlasmaGenerator import PlasmaGenerator
from scipy.fft import rfft, irfft, fftfreq, fft, ifft


class Photodetector(pd.DataFrame):
    def __init__(self):
        super().__init__()
        self.tau = 0.88  # mks
        self.noize_a = 0.2  # V
        self.shift_freq_min = 100.0e-6  # MHz
        self.shift_freq_max = 400.0e-6  # MHz
        self.shift_a_min = 0.01  # V
        self.shift_a_max = 0.1  # V
        self.filter_tau = 5.0e3  # mks
        self.Low_freq = 1.0/(2.0*np.pi*5.0e3)

    def High_pass_furie(self, signal, time):
        timeSteps = np.gradient(time)
        meanStep = np.mean(timeSteps)

        f_signal = rfft(signal, )
        W = fftfreq(f_signal.size, d=meanStep)[:int(f_signal.size)]

        # If our original signal time was in seconds, this is now in Hz
        cut_f_signal = f_signal.copy()
        fstart = self.Low_freq * np.pi*2.0
        fwindow = np.where((np.abs(W) >= fstart), 1, 0)
        cut_signal = irfft(cut_f_signal * fwindow)[:signal.size]
        new_time = time[:signal.size - 1]
        return cut_signal, new_time
    def transformation(self, data):
        self.shift_a = (self.shift_a_max - self.shift_a_min) * np.random.random_sample() + self.shift_a_min
        self.shift_fi = 2.0 * np.pi * np.random.random_sample()
        signal = data.Values
        time = data.Time
        self.dt = time[1] - time[0]
        signal_noize = self.noize_a * np.random.rand(time.size)
        signal_shift = self.shift_function(time)
        new_signal = signal + signal_shift + signal_noize
        n_window = int(self.tau / self.dt)
        if n_window != 0:
            new_signal = np.convolve(new_signal, np.ones(n_window), 'valid') / n_window
        new_time = (time + 0.5 * self.tau)[:new_signal.size]
        new_signal, new_time = self.High_pass_furie(new_signal, new_time)
        self['Time'] = new_time
        self['Values'] = new_signal


        self.low_freq_filter()
        return self





    def shift_function(self, t):
        omega = 2.0 * np.pi * (
                (self.shift_freq_max - self.shift_freq_min) * np.random.random_sample() + self.shift_freq_min)
        return self.shift_a * np.sin(omega * t + self.shift_fi)

    def low_freq_filter(self):
        ...

    def show_plot(self):
        plt.plot(self['Time'], self['Values'])


'''photodetector = Photodetector()
plasmagenerator = PlasmaGenerator()
interferometer = IdealInterferometer()

for i in range(1):
    plasmagenerator.generate()
    interferometer.transformation(plasmagenerator)
    photodetector.transformation(interferometer)
    photodetector.show_plot()
plt.show()'''
