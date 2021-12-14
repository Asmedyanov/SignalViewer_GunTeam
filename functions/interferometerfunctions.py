from scipy.signal import argrelextrema, find_peaks, butter, filtfilt
from functions.mymathfunctions import *
import matplotlib.pyplot as plt
import pandas as pd


def interferometer(d):
    dt = 0.1  # np.nan_to_num(np.gradient(d['T'])).mean()
    # Выделем участок с плазмой
    dataplasma = d.loc[(d['T'] < 100) & (d['T'] > 10)]
    dataplasma.index = pd.RangeIndex(len(dataplasma.index))
    # Находим максимумы и минимумы
    maxarray = argrelextrema(dataplasma['V'].values, np.greater, order=int(20.0 / dt))[0]
    minarray = argrelextrema(dataplasma['V'].values, np.less, order=int(20.0 / dt))[0]
    # print(np.max(d['V'][maxarray]))
    # Находим максимальный максимум и минимальный минимум
    maxmax = np.max(dataplasma['V'][maxarray])
    minmin = np.min(dataplasma['V'][minarray])
    # Решаем что брать в качестве границ плазмы
    if minarray.size == 0:
        minarray = np.array([dataplasma['T'].min(), dataplasma['T'].max()])
    if maxarray.size == 0:
        maxarray = np.array([dataplasma['T'].min(), dataplasma['T'].max()])
    borders = [minarray[0], minarray[-1]]

    if (abs(maxmax) < abs(minmin)):
        borders = [maxarray[0], maxarray[-1]]
        dataplasma['V'] = -dataplasma['V']
    shift = max([dataplasma['V'][borders[0]], dataplasma['V'][borders[1]]])

    dataplasma['V'] = dataplasma['V'] - shift
    # Занулим все слева и справа
    # dataplasma['V']=np.where(dataplasma['V']>0,dataplasma['V'],0)
    dataplasmaprobe = np.where(((dataplasma.index > borders[0]) & (dataplasma.index < borders[1])), dataplasma['V'], 0)
    if dataplasmaprobe.sum() != 0:
        dataplasma['V'] = dataplasmaprobe
    # Smooth_data(master, dataplasma)
    # Выправим зашкалы
    for rn in range(2):
        maxarray = argrelextrema(dataplasma['V'].values, np.greater, order=int(5.0 / dt))[0]
        # print(dataplasma['T'][maxarray])
        if (maxarray.size > 1) & (dataplasma['V'].max() > 0.7):
            # Выполним разворот
            maxrev = max([dataplasma['V'][maxarray[0]], dataplasma['V'][maxarray[-1]]])
            dataplasma['V'] = np.where(((dataplasma['T'] > dataplasma['T'][maxarray[0]])
                                        & (dataplasma['T'] < dataplasma['T'][maxarray[-1]])),
                                       2 * maxrev - dataplasma['V'], dataplasma['V'])
    dataplasma['V'] = np.where(dataplasma['V'] > 0, dataplasma['V'], 0)

    return dataplasma


def preinterferometer(data):
    d = data
    # сдвинем минимум в 0
    mininterf = d['V'].loc[d['T'] > d['T'].mean()].min()
    d['V'] = d['V'] - mininterf
    maxinterf = d['V'].loc[d['T'] > d['T'].mean()].max()
    d['V'] = np.where(d['V'] > maxinterf, maxinterf, d['V'])
    d['V'] = np.where(d['V'] < 0, 0, d['V'])
    # Пересчитаем в фазу
    d['V'] = np.arccos(1.0 - (2.0 * d['V'] / maxinterf))
    # вычислим неплазменную часть

    d = my_fft_filter_com(d, 1.0 / 50.0e-6, 1.0 / 0.5e-6)

    nnul = d['V'].loc[d['T'] > d['T'].mean()].mean()
    d['V'] = d['V'] - nnul
    no_plasma_data = d.loc[d['T'] < 20.0e-6]
    no_plasma_time = no_plasma_data['T'].values
    no_plasma_values = no_plasma_data['V'].values
    line_coef = np.polyfit(no_plasma_time, no_plasma_values, deg=1)
    line_approx = np.poly1d(line_coef)(d['T'].values)

    dataret = RawData('', d.diagnostic, d['T'].values, d['V'].values-line_approx)
    return dataret


def post_interferometer(data):
    # data = my_fft_filter_com(data0, 200.0, 1.0 / 2.0e-6)
    plt.cla()
    pic_width = 10.0e-6
    pic_dist = (49.5 - 26.4) * 1.0e-6
    pic_ampl_proc = 60.0
    signal = data['V'].values
    time = data['T'].values
    plt.plot(time, signal)

    data1 = my_fft_filter_com(data, 10.0, 1.0 / 2.5e-6)
    signal1 = data1['V'].values
    grsignal = np.abs(np.gradient(signal1))
    grsignal = grsignal / np.max(grsignal)
    plt.plot(time[:grsignal.size], grsignal)

    pic_max = data['V'].loc[data['T'] > data['T'].mean()].max()
    pic_ampl = 1.0e-2 * pic_ampl_proc * pic_max
    tgrad = np.gradient(time)
    dt = np.mean(tgrad)
    pic_width_n = int(pic_width / dt)
    pic_dist_n = int(pic_dist / dt)
    pic_array_raw_up = \
        find_peaks(grsignal, width=[0.1 * pic_width_n, 2.0 * pic_width_n])[0][1:-1]

    pic_array_raw_time = time[pic_array_raw_up]
    pic_array_raw_value = grsignal[pic_array_raw_up]
    plt.plot(pic_array_raw_time, pic_array_raw_value, 'ro')
    time_plasma_start = 0
    for k, v in enumerate(pic_array_raw_value):
        try:
            if v > np.mean(pic_array_raw_value[:k]) * 3:
                time_plasma_start = 0.5 * (pic_array_raw_time[k] + pic_array_raw_time[k - 1])
                break
        except:
            continue
    time_plasma_stop = time_plasma_start
    for k, v in enumerate(pic_array_raw_value):
        try:
            if v > np.mean(pic_array_raw_value[k:]) * 2:
                time_plasma_stop = 0.5 * (pic_array_raw_time[k] + pic_array_raw_time[k + 1])
                # if time_plasma_stop > time_plasma_start:
                #   break
        except:
            continue
    print(f'Время старта плазмы {time_plasma_start}')
    print(f'Время конца плазмы {time_plasma_stop}')
    no_plasma_data = data.loc[((data['T'] > time_plasma_start) & (data['T'] < time_plasma_stop))]
    no_plasma_signal = no_plasma_data['V'].values
    no_plasma_time = no_plasma_data['T'].values

    no_plasma_interp = np.interp(time, no_plasma_time, no_plasma_signal)
    clear_plasma_signal = signal - no_plasma_interp
    plt.plot(time, clear_plasma_signal)
    plt.show()


def post_interferometer_2(data):
    # выделим участок с плазмой:
    data_plasma = data.loc[((data['T'] > 22.0e-6) & (data['T'] < 57.0e-6))]
    plasma_signal = data_plasma['V'].values
    plasma_time = data_plasma['T'].values

    #   plt.plot(plasma_time, plasma_signal)
    pic_w_min = 1.0e-6
    pic_w_max = 10.0e-6
    tgrad = np.gradient(plasma_time)
    dt = np.mean(tgrad)
    pic_width_min = int(pic_w_min / dt)
    pic_width_max = int(pic_w_max / dt)
    rev_pics = find_peaks(-plasma_signal, width=[pic_width_min, pic_width_max])[0]
    if len(rev_pics)==0:
        return data
    pic_array_raw_time = plasma_time[rev_pics]
    pic_array_raw_value = plasma_signal[rev_pics]
    #    plt.plot(pic_array_raw_time, pic_array_raw_value, 'ro')
    left_pic = rev_pics[0]
    right_pic = rev_pics[-1]
    over_signal = plasma_signal[left_pic:right_pic]
    liner_base_signal = np.linspace(over_signal[0], over_signal[-1], over_signal.size)
    reversed_signal = 2 * liner_base_signal - over_signal
    reversed_time = plasma_time[left_pic:right_pic]
    #    plt.plot(reversed_time, reversed_signal)
    signal = data['V'].values
    time = data['T'].values
    real_start_index = np.where(time == reversed_time[0])[0][0]
    real_stop_index = np.where(time == reversed_time[-1])[0][0]
    signal.flat[real_start_index:real_stop_index] = reversed_signal
    dataret = RawData('', data.diagnostic, time, -signal)

    #    plt.show()
    return dataret
