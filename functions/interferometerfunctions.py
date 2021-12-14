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
    if np.abs(np.min(d['V'])) > np.abs(np.max(d['V'])):
        d['V'] = -d['V']

    nnul = d['V'].loc[d['T'] > d['T'].mean()].mean()
    d['V'] = d['V'] - nnul
    dataret = RawData('', d.diagnostic, d['T'].values, d['V'].values)
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
            if v > pic_array_raw_value[k - 1] * 3:
                time_plasma_start = 0.5*(pic_array_raw_time[k] + pic_array_raw_time[k-1])
                break
        except:
            continue
    print(f'Время старта плазмы {time_plasma_start}')

    plt.show()
