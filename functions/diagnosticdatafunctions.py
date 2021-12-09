import numpy as np
from scipy.fft import rfft, irfft, fftfreq
import pandas as pd
from classes.rawdata import RawData
from scipy.signal import argrelextrema


def my_fft_filter_com(data, fstart, ffinish):
    # data = data.dropna()
    # data.index = pd.RangeIndex(len(data.index))
    signal = data['V'].values
    time = data['T'].values
    timeSteps = np.gradient(time)
    meanStep = np.mean(timeSteps)

    f_signal = rfft(signal)
    W = fftfreq(signal.size, d=meanStep)[:int(f_signal.size)]
    # W = W[:int(f_signal.size / 2)]
    # f_signal=f_signal[:int(f_signal.size/2)]

    # If our original signal time was in seconds, this is now in Hz
    cut_f_signal = f_signal.copy()
    fstart = fstart
    fend = ffinish
    fw = 1e3
    fwindow = np.exp(-np.power((W - fstart) / fw, 2)) + np.exp(-np.power((W - fend) / fw, 2))
    fwindow = np.where(((W > fstart) & (W < fend)), 1, fwindow)
    cut_signal = irfft(cut_f_signal * fwindow)
    dataret = RawData(data.label, data.diagnostic, time[:cut_signal.size], cut_signal)

    return dataret


def ininterval(data, left, right):
    ret = data.loc[(((data['T'] >= left) & (data['T'] <= right)))]
    dataret = RawData(data.label, data.diagnostic, ret['T'].values, ret['V'].values)
    return dataret


def Diagnostic_belt(rawdata, master):
    diagnostic = 'Пояс'
    if rawdata.diagnostic != diagnostic:
        return None
    tstart = 0
    tfinish = 100.0e-6
    ffinish = 1.0 / 5.0e-7
    fstart = 1.0
    mult = -8*100. / 0.14 * 1.0e-3
    ret = my_fft_filter_com(rawdata, fstart, ffinish)
    ret = ininterval(ret, tstart, tfinish)

    ret['V'] = ret['V'] * mult
    ret.label = 'I, kA'
    return ret


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
    d['V'] = np.nan_to_num(d['V'])
    # master.array_plots[0].plot(d)
    # сдвинем минимум в 0
    d['V'] = d['V'] - d['V'].min()
    # Пересчитаем в фазу
    d['V'] = np.arccos(1.0 - (2.0 * d['V'] / d['V'].max()))
    # вычислим неплазменную часть

    d = my_fft_filter_com(d, 1.0 / 120.0e-6, 1.0 / 1.0e-7)
    # d=my_fft_filter_interf(d)

    # master.array_plots[0].plot(d)
    nnul = d['V'].loc[d['T'] > d['T'].mean()].mean()
    d['V'] = d['V'] - nnul

    # вычислим плотность плазмы
    d['V'] = d['V'] * 7.00979
    # d['label'] = 'фаза'
    dataret = RawData('$n_{e}, 10^{15} см^{-3}$', d.diagnostic, d['T'].values, d['V'].values)
    return dataret


def Diagnostic_Interferometer(rawdata, master):
    diagnostic = 'Интерферометр'
    if rawdata.diagnostic != diagnostic:
        return None
    tstart = 0
    tfinish = 100.0e-6
    ffinish = 1.0 / 5.0e-7
    fstart = 1.0 / 1.0e2
    mult = 1
    ret = my_fft_filter_com(rawdata, fstart, ffinish)
    ret = preinterferometer(ret)
    ret = ininterval(ret, tstart, tfinish)
    ret['V'] = ret['V'] * mult
    # ret.label = 'ne, cm^-3'
    return ret
