# Преобразует сигнал симулятора АЦП в фазу интерферометра

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from classes.ADCsimulator import ADCsimulator
from scipy.fft import rfft, irfft, fftfreq, fft, ifft
from scipy.signal import find_peaks
from functions.mymathfunctions import find_nearest, my_find_pics


class BackInterferometerTransformator:
    def __init__(self):

        self.Low_freq = 300.0e-6  # MHz
        self.High_freq = 1.0 / 0.5  # MHz

    def High_pass_furie(self, signal, time):
        timeSteps = np.gradient(time)
        meanStep = np.mean(timeSteps)

        f_signal = rfft(signal, )
        W = fftfreq(f_signal.size, d=meanStep)[:int(f_signal.size)]

        # If our original signal time was in seconds, this is now in Hz
        cut_f_signal = f_signal.copy()
        fstart = self.Low_freq * 2 * np.pi
        ffinish = self.High_freq * 2 * np.pi
        fwindow = np.where(((np.abs(W) >= fstart) & (np.abs(W) <= ffinish)), 1, 0)
        cut_signal = irfft(cut_f_signal * fwindow)[:signal.size - 1]
        new_time = time[:signal.size - 1]
        return cut_signal, new_time

    def get_signal(self):
        adc = ADCsimulator()
        adc.Mesure()
        signal = adc.Values
        time = adc.Time
        self.dt = 1.0 / self.High_freq
        n_window = int(self.dt / adc.tdisc)
        if n_window != 0:
            new_signal = np.convolve(signal, np.ones(n_window), 'valid') / n_window
            # new_signal = np.convolve(new_signal, np.ones(n_window), 'valid') / n_window
        new_time = (time + 0.5 * self.dt)[:new_signal.size]
        new_signal, new_time = self.High_pass_furie(new_signal, new_time)
        clr_w = int(new_signal.size / 32)
        new_signal_clr = new_signal[clr_w:-clr_w]
        new_signal = new_signal - new_signal_clr.min()
        new_signal_clr = new_signal[clr_w:-clr_w]
        norm_signal = 1.0 - (2.0 * new_signal / new_signal_clr.max())
        norm_signal = np.where(norm_signal < -1, -1, norm_signal)
        norm_signal = np.where(norm_signal > 1, 1, norm_signal)
        new_signal = np.arccos(norm_signal)
        interval = np.nonzero(((new_time > 0) & (new_time < 140.0)))
        new_signal = new_signal[interval]
        new_time = new_time[interval]
        self.Values = new_signal
        self.Time = new_time

        Real_Pick_pi = my_find_pics(new_signal)
        Real_Pick_2pi = my_find_pics(-new_signal)
        self.real_pic_data_pi_Time = new_time[Real_Pick_pi[0]]
        self.real_pic_data_pi_Values = new_signal[Real_Pick_pi[0]]
        self.real_pic_data_2pi_Time = new_time[Real_Pick_2pi[0]]
        self.real_pic_data_2pi_Values = new_signal[Real_Pick_2pi[0]]
        self.real_pic_pi_data_output = Real_Pick_pi[1]
        self.real_pic_2pi_data_output = Real_Pick_2pi[1]
        mark_pi = np.zeros(self.real_pic_data_pi_Time.size)
        mark_2pi = np.zeros(self.real_pic_data_2pi_Time.size)

        revers_time_pi_left = []
        for t in adc.Pic_data_pi_left_Time:
            if self.real_pic_data_pi_Time.size != 0:
                revers_time_pi_left.append(find_nearest(self.real_pic_data_pi_Time, t))
        revers_time_2pi_left = []
        for t in adc.Pic_data_2pi_left_Time:
            if self.real_pic_data_2pi_Time.size != 0:
                revers_time_2pi_left.append(find_nearest(self.real_pic_data_2pi_Time, t))
        revers_time_pi_right = []
        for t in adc.Pic_data_pi_right_Time:
            if self.real_pic_data_pi_Time.size != 0:
                revers_time_pi_right.append(find_nearest(self.real_pic_data_pi_Time, t))
        revers_time_2pi_right = []
        for t in adc.Pic_data_2pi_right_Time:
            if self.real_pic_data_2pi_Time.size != 0:
                revers_time_2pi_right.append(find_nearest(self.real_pic_data_2pi_Time, t))

        mark_pi[revers_time_pi_right] = 1
        mark_pi[revers_time_pi_left] = -1
        mark_2pi[revers_time_2pi_right] = 1
        mark_2pi[revers_time_2pi_left] = -1
        self.real_pic_2pi_data_output['mark'] = mark_2pi
        self.real_pic_pi_data_output['mark'] = mark_pi

        self.compared_data_pi_Time = self.real_pic_data_pi_Time[revers_time_pi_left]
        self.compared_data_pi_Values = self.real_pic_data_pi_Values[revers_time_pi_left]

        self.compared_data_2pi_Time = self.real_pic_data_2pi_Time[revers_time_2pi_left]
        self.compared_data_2pi_Values = self.real_pic_data_2pi_Values[revers_time_2pi_left]

    def show_plot(self):
        plt.plot(self.Time, self.Values, label='Сам график')
        plt.plot(self.real_pic_data_pi_Time, self.real_pic_data_pi_Values, 'o', label='Пики пи')
        plt.plot(self.real_pic_data_2pi_Time, self.real_pic_data_2pi_Values, 'o', label='пики 2Пи')
        plt.plot(self.compared_data_pi_Time, self.compared_data_pi_Values, 'o', label='развороты Пи')
        plt.plot(self.compared_data_2pi_Time, self.compared_data_2pi_Values, 'o', label='развороты 2Пи')


BIT = BackInterferometerTransformator()
BIT.get_signal()
common_output_data_pi = pd.DataFrame(BIT.real_pic_pi_data_output)
common_output_data_2pi = pd.DataFrame(BIT.real_pic_2pi_data_output)
# BIT.show_plot()
# plt.legend()
# plt.show()

for i in range(500):
    BIT.get_signal()
    common_output_data_pi = pd.concat([common_output_data_pi, pd.DataFrame(BIT.real_pic_pi_data_output)])
    common_output_data_2pi = pd.concat([common_output_data_2pi, pd.DataFrame(BIT.real_pic_2pi_data_output)])
    print(i)

common_output_data_pi.to_csv('artif_pic_pi.txt', sep='\t')
common_output_data_2pi.to_csv('artif_pic_2pi.txt', sep='\t')
