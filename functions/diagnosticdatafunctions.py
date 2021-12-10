import numpy as np
from scipy.fft import rfft, irfft, fftfreq, fft, ifft
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
    # fwindow = np.exp(-np.power((W - fstart) / fw, 2)) + np.exp(-np.power((W - fend) / fw, 2))
    fwindow = np.where(((W > fstart) & (W < fend)), 1, 0)
    # fwindow=fwindow/np.sum(fwindow)
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
    dia = master.getDia(diagnostic)
    tstart = float(dia['Параметры']['Время старт']['Значение'])
    tfinish = float(dia['Параметры']['Время финиш']['Значение'])
    ffinish = float(dia['Параметры']['Частота финиш']['Значение'])
    fstart = float(dia['Параметры']['Частота старт']['Значение'])
    mult = float(dia['Параметры']['Множитель']['Значение'])
    ret = my_fft_filter_com(rawdata, fstart, ffinish)
    ret = ininterval(ret, tstart, tfinish)

    ret['V'] = ret['V'] * mult
    label = dia['Параметры']['Подпись']['Значение']
    dim = dia['Параметры']['Единицы величины']['Значение']
    ret.label = f'{label}, {dim}'
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
    # сдвинем минимум в 0
    mininterf = d['V'].loc[d['T'] > d['T'].mean()].min()
    d['V'] = d['V'] - mininterf
    maxinterf = d['V'].loc[d['T'] > d['T'].mean()].max()
    d['V'] = np.where(d['V'] > maxinterf, maxinterf, d['V'])
    d['V'] = np.where(d['V'] < 0, 0, d['V'])
    # Пересчитаем в фазу
    d['V'] = np.arccos(1.0 - (2.0 * d['V'] / maxinterf))
    # вычислим неплазменную часть

    d = my_fft_filter_com(d, 1.0 / 120.0e-6, 1.0 / 1.0e-7)

    nnul = d['V'].loc[d['T'] > d['T'].mean()].mean()
    d['V'] = d['V'] - nnul
    dataret = RawData('$n_{e}, 10^{15} см^{-3}$', d.diagnostic, d['T'].values, d['V'].values)
    return dataret


def Diagnostic_Interferometer(rawdata, master):
    diagnostic = 'Интерферометр'
    if rawdata.diagnostic != diagnostic:
        return None
    dia = master.getDia(diagnostic)
    tstart = float(dia['Параметры']['Время старт']['Значение'])
    tfinish = float(dia['Параметры']['Время финиш']['Значение'])
    ffinish = float(dia['Параметры']['Частота финиш']['Значение'])
    fstart = float(dia['Параметры']['Частота старт']['Значение'])
    mult = float(dia['Параметры']['Множитель']['Значение'])
    ret = my_fft_filter_com(rawdata, fstart, ffinish)
    ret = preinterferometer(ret)
    ret = ininterval(ret, tstart, tfinish)
    ret['V'] = ret['V'] * mult
    label = dia['Параметры']['Подпись']['Значение']
    dim = dia['Параметры']['Единицы величины']['Значение']
    ret.label = f'{label}, {dim}'
    return ret


def calorimetr(data):
    u = data['V'].values
    t = data['T'].values
    U0 = 1.1
    R0 = 910.0
    r = R0 * u / (U0 - u)
    dataret = RawData('', data.diagnostic, t, r)
    return dataret


def Diagnostic_Calorimetr(rawdata, master):
    diagnostic = 'Калориметр'
    if rawdata.diagnostic != diagnostic:
        return None
    dia = master.getDia(diagnostic)
    tstart = float(dia['Параметры']['Время старт']['Значение'])
    tfinish = float(dia['Параметры']['Время финиш']['Значение'])
    ffinish = float(dia['Параметры']['Частота финиш']['Значение'])
    fstart = float(dia['Параметры']['Частота старт']['Значение'])
    mult = float(dia['Параметры']['Множитель']['Значение'])
    ret = calorimetr(rawdata)
    ret = my_fft_filter_com(ret, fstart, ffinish)
    retmin = ret['V'].loc[ret['T'] < 0].mean()
    ret = ininterval(ret, tstart, tfinish)
    ret['V'] = np.abs(ret['V']-retmin) * mult
    label = dia['Параметры']['Подпись']['Значение']
    dim = dia['Параметры']['Единицы величины']['Значение']
    ret.label = f'{label}, {dim}'
    return ret
