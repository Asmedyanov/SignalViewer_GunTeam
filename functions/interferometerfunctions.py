from scipy.signal import argrelextrema, find_peaks, butter, filtfilt, peak_prominences
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


def fase_interferometr(data):
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

    dataret = RawData('', d.diagnostic, d['T'].values, d['V'].values)
    return dataret


def preinterferometer(data,f_start):
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
    d = my_fft_filter_com(d, f_start, 1.0 / 0.1e-6)
    nnul = d['V'].loc[((d['T'] < 10.0e-6) & (d['T'] > 5.0e-6))].mean()
    d['V'] = d['V'] - nnul

    dataret = RawData('', d.diagnostic, d['T'].values, d['V'].values)
    return dataret


def scale_up_interferometr(data, rev_x, rev_y):
    signal = data['V'].values
    time = data['T'].values
    new_signal = np.where((time > rev_x[0]) & (time < rev_x[-1]),
                          (-1)*signal, signal)
    dataret = RawData('', data.diagnostic, time, new_signal)
    return dataret


def find_revers_0(data):
    # plt.cla()
    pic_width = 10.0e-6
    pic_dist = (49.5 - 26.4) * 1.0e-6
    signal = data['V'].values
    time = data['T'].values

    plt.plot(time, signal)

    pic_max = signal.max() - signal.min()
    tgrad = np.gradient(time)
    dt = np.mean(tgrad)
    pic_width_n = int(pic_width / dt)
    pic_dist_n = int(pic_dist / dt)
    pic_array_raw = \
        find_peaks(-signal, prominence=[0.1 * pic_max, pic_max])[0]

    pic_array_visinity = []
    visinity = 1
    for k in pic_array_raw:
        if signal[k] < visinity:
            pic_array_visinity.append(k)

    pic_array_raw_time = time[pic_array_visinity]
    pic_array_raw_value = signal[pic_array_visinity]
    return pic_array_raw_time
    # plt.plot(pic_array_raw_time, pic_array_raw_value, 'ro')
    # if (len(pic_array_visinity)==2):
    #    new_signal = -np.where((time>pic_array_raw_time[0])&(time<pic_array_raw_time[1]),2*pic_array_raw_value.min()-signal,signal)
    #    signal = new_signal
    #    #plt.plot(time, new_signal)
    # dataret = RawData('', data.diagnostic, time, signal)

    # plt.show()
def find_revers_pi(data):
    # plt.cla()

    signal = data['V'].values
    time = data['T'].values

    plt.plot(time, signal)

    pic_max = signal.max() - signal.min()
    tgrad = np.gradient(time)
    dt = np.mean(tgrad)

    pic_array_raw = \
        find_peaks(signal, prominence=[0.1 * pic_max, pic_max])[0]

    pic_array_visinity = []
    visinity = 2.0
    for k in pic_array_raw:
        if signal[k] > visinity:
            pic_array_visinity.append(k)

    pic_array_raw_time = time[pic_array_visinity]
    pic_array_raw_value = signal[pic_array_visinity]
    return pic_array_raw_time
    # plt.plot(pic_array_raw_time, pic_array_raw_value, 'ro')
    # if (len(pic_array_visinity)==2):
    #    new_signal = -np.where((time>pic_array_raw_time[0])&(time<pic_array_raw_time[1]),2*pic_array_raw_value.min()-signal,signal)
    #    signal = new_signal
    #    #plt.plot(time, new_signal)
    # dataret = RawData('', data.diagnostic, time, signal)

    # plt.show()


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
    if len(rev_pics) == 0:
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
