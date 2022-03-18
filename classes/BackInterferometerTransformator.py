# Преобразует сигнал симулятора АЦП в фазу интерферометра

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from classes.ADCsimulator import ADCsimulator
from scipy.fft import rfft, irfft, fftfreq, fft, ifft
from scipy.signal import find_peaks
from functions.mymathfunctions import find_nearest


class BackInterferometerTransformator(pd.DataFrame):
    def __init__(self):
        super().__init__()
        self.Low_freq = 300.0e-6  # MHz
        self.High_freq = 1.0 / 1.6  # MHz

    def High_pass_furie(self, signal, time):
        timeSteps = np.gradient(time)
        meanStep = np.mean(timeSteps)

        f_signal = rfft(signal, )
        W = fftfreq(f_signal.size, d=meanStep)[:int(f_signal.size)]

        # If our original signal time was in seconds, this is now in Hz
        cut_f_signal = f_signal.copy()
        fstart = self.Low_freq * np.pi
        fwindow = np.where((np.abs(W) >= fstart), 1, 0)
        cut_signal = irfft(cut_f_signal * fwindow)[:signal.size]
        new_time = time[:signal.size - 1]
        return cut_signal, new_time

    def get_signal(self):
        adc = ADCsimulator()
        adc.Mesure()
        signal = adc['Values'].values
        time = adc['Time'].values
        self.dt = 1.0 / self.High_freq
        n_window = int(self.dt / adc.tdisc)
        if n_window != 0:
            new_signal = np.convolve(signal, np.ones(n_window), 'valid') / n_window
        new_time = (time + 0.5 * self.dt)[:new_signal.size]
        new_signal, new_time = self.High_pass_furie(new_signal, new_time)
        clr_w = int(new_signal.size / 32)
        new_signal_clr = new_signal[clr_w:-clr_w]
        new_signal = new_signal - new_signal_clr.min()
        new_signal_clr = new_signal[clr_w:-clr_w]
        new_signal = np.arccos(1.0 - (2.0 * new_signal / new_signal_clr.max()))

        self['Values'] = new_signal
        self['Time'] = new_time

        self.Real_Pick_pi = find_peaks(new_signal,
                                       threshold=[0, np.pi],
                                       distance=7.0,
                                       width=[7.0, 10000.0],
                                       prominence=[1.0e-3, np.pi])
        self.Real_Pick_2pi = find_peaks(-new_signal,
                                        threshold=[0, np.pi],
                                        distance=7.0,
                                        width=[7.0, 1000.0],
                                        prominence=[1.0e-3, np.pi])
        self.real_pic_data_pi = pd.DataFrame()
        self.real_pic_data_pi['Time'] = new_time[self.Real_Pick_pi[0]]
        self.real_pic_data_pi['Values'] = new_signal[self.Real_Pick_pi[0]]
        self.real_pic_data_2pi = pd.DataFrame()
        self.real_pic_data_2pi['Time'] = new_time[self.Real_Pick_2pi[0]]
        self.real_pic_data_2pi['Values'] = new_signal[self.Real_Pick_2pi[0]]
        self.realpic_pi_data_output = pd.DataFrame(self.Real_Pick_pi[1])
        self.realpic_2pi_data_output = pd.DataFrame(self.Real_Pick_2pi[1])
        self.realpic_2pi_data_output['mark'] = np.zeros(self.real_pic_data_2pi['Time'].size)
        self.realpic_pi_data_output['mark'] = np.zeros(self.real_pic_data_pi['Time'].size)

        revers_time_pi = []
        for t in adc.Pic_data_pi['Time']:
            revers_time_pi.append(find_nearest(self.real_pic_data_pi['Time'], t))
        revers_time_2pi = []
        for t in adc.Pic_data_2pi['Time']:
            revers_time_2pi.append(find_nearest(self.real_pic_data_2pi['Time'], t))

        self.realpic_2pi_data_output['mark'][revers_time_2pi] = 1
        self.realpic_pi_data_output['mark'][revers_time_pi] = 1
        self.compared_data_pi = pd.DataFrame()
        self.compared_data_pi['Time'] = self.real_pic_data_pi['Time'].values[revers_time_pi]
        self.compared_data_pi['Values'] = self.real_pic_data_pi['Values'].values[revers_time_pi]
        self.compared_data_2pi = pd.DataFrame()
        self.compared_data_2pi['Time'] = self.real_pic_data_2pi['Time'].values[revers_time_2pi]
        self.compared_data_2pi['Values'] = self.real_pic_data_2pi['Values'].values[revers_time_2pi]

    def show_plot(self):
        plt.plot(self['Time'], self['Values'])
        # plt.plot(self.real_pic_data_pi['Time'], self.real_pic_data_pi['Values'], 'o')
        # plt.plot(self.real_pic_data_2pi['Time'], self.real_pic_data_2pi['Values'], 'o')
        plt.plot(self.compared_data_pi['Time'], self.compared_data_pi['Values'], 'o')
        plt.plot(self.compared_data_2pi['Time'], self.compared_data_2pi['Values'], 'o')


BIT = BackInterferometerTransformator()
BIT.get_signal()
common_output_data_pi = BIT.realpic_pi_data_output
common_output_data_2pi = BIT.realpic_2pi_data_output

for i in range(2):
    BIT.get_signal()
    common_output_data_pi = pd.concat([common_output_data_pi, BIT.realpic_pi_data_output])
    common_output_data_2pi = pd.concat([common_output_data_2pi, BIT.realpic_2pi_data_output])

common_output_data_pi.to_csv('artif_pic_pi.txt', sep='\t')
common_output_data_2pi.to_csv('artif_pic_2pi.txt', sep='\t')
