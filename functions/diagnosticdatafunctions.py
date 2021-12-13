import numpy as np
from scipy.fft import rfft, irfft, fftfreq, fft, ifft
import pandas as pd
from classes.rawdata import RawData
from scipy.signal import argrelextrema, find_peaks, butter, filtfilt
from scipy.interpolate import interp1d, splrep, splev
import matplotlib.pyplot as plt


def get_parameters(dia):
    tstart = float(dia['Параметры']['Время старт']['Значение'])
    tfinish = float(dia['Параметры']['Время финиш']['Значение'])
    ffinish = float(dia['Параметры']['Частота финиш']['Значение'])
    fstart = float(dia['Параметры']['Частота старт']['Значение'])
    mult = float(dia['Параметры']['Множитель']['Значение'])
    return tstart, tfinish, fstart, ffinish, mult


def set_parameters(dia, ret):
    label = dia['Параметры']['Подпись']['Значение']
    dim = dia['Параметры']['Единицы величины']['Значение']
    ret.label = f'{label}, {dim}'
    ret.timeDim = dia['Параметры']['Единицы времени']['Значение']
    try:
        ret.Overlay = dia['Параметры']['Наложение']['Значение']
    except:
        ret.Overlay = '0'


def my_fft(value, df, dt):
    fmax = 0.5 / dt
    n = value.size
    nf = int(fmax / df)
    kf = np.arange(nf)
    kt = -2j * np.pi * np.arange(n) / n

    def mode(k):
        np.sum(value * np.exp(k * kt))

    retvalue = np.vectorize(mode)(kf)
    return retvalue


def my_fft_filter_fin(data, fstart, ffinish):
    # data = data.dropna()
    # data.index = pd.RangeIndex(len(data.index))
    signal = data['V'].values
    time = data['T'].values
    timeSteps = np.gradient(time)
    meanStep = np.mean(timeSteps)
    '''wn1 = 2 * fstart * meanStep
    wn2 = 2 * ffinish * meanStep'''
    fmax = 0.5 / meanStep
    df = 1.0
    nf = int(fmax / df)
    f_signal = rfft(signal, n=nf)
    W = fftfreq(f_signal.size, d=meanStep)[:int(f_signal.size)]

    # If our original signal time was in seconds, this is now in Hz
    cut_f_signal = f_signal.copy()
    fstart = fstart
    fend = ffinish
    fw = 1e3
    # fwindow = np.exp(-np.power((W - fstart) / fw, 2)) + np.exp(-np.power((W - fend) / fw, 2))
    fwindow = np.where(((np.abs(W) >= fstart) & (np.abs(W) <= fend)), 1, 0)
    cut_signal = irfft(cut_f_signal * fwindow)[:signal.size]
    new_time = np.arange(0, cut_signal.size) * meanStep
    dataret = RawData(data.label, data.diagnostic, new_time, cut_signal)

    return dataret


def my_fft_filter_com(data, fstart, ffinish):
    # data = data.dropna()
    # data.index = pd.RangeIndex(len(data.index))
    signal = data['V'].values
    time = data['T'].values
    timeSteps = np.gradient(time)
    meanStep = np.mean(timeSteps)
    '''wn1 = 2 * fstart * meanStep
    wn2 = 2 * ffinish * meanStep'''
    f_signal = rfft(signal, )
    W = fftfreq(f_signal.size, d=meanStep)[:int(f_signal.size)]

    # If our original signal time was in seconds, this is now in Hz
    cut_f_signal = f_signal.copy()
    fstart = fstart
    fend = ffinish
    fw = 1e3
    # fwindow = np.exp(-np.power((W - fstart) / fw, 2)) + np.exp(-np.power((W - fend) / fw, 2))
    fwindow = np.where(((np.abs(W) >= fstart) & (np.abs(W) <= fend)), 1, 0)
    cut_signal = irfft(cut_f_signal * fwindow)
    dataret = RawData(data.label, data.diagnostic, time[:cut_signal.size], cut_signal)

    return dataret


def my_fft_filter_back(data, fstart, ffinish):
    # data = data.dropna()
    # data.index = pd.RangeIndex(len(data.index))
    signal = data['V'].values
    time = data['T'].values
    timeSteps = np.gradient(time)
    meanStep = np.mean(timeSteps)

    f_signal = fft(signal)
    W = fftfreq(signal.size, d=meanStep)[:int(f_signal.size)]
    # W = W[:int(f_signal.size / 2)]
    # f_signal=f_signal[:int(f_signal.size/2)]

    # If our original signal time was in seconds, this is now in Hz
    cut_f_signal = f_signal.copy()
    fstart = fstart
    fend = ffinish
    fw = 1e3
    # fwindow = np.exp(-np.power((W - fstart) / fw, 2)) + np.exp(-np.power((W - fend) / fw, 2))
    fwindow = np.where(((np.abs(W) <= fstart) | (np.abs(W) >= fend)), 1, 0)
    cut_signal = np.abs(ifft(cut_f_signal * fwindow))
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
    tstart, tfinish, fstart, ffinish, mult = get_parameters(dia)
    ret = my_fft_filter_com(rawdata, fstart, ffinish)
    ret = ininterval(ret, tstart, tfinish)
    ret['V'] = ret['V'] * mult
    set_parameters(dia, ret)
    return ret


def Diagnostic_piezo(rawdata, master):
    diagnostic = 'Пьезодатчик'
    if rawdata.diagnostic != diagnostic:
        return None
    dia = master.getDia(diagnostic)
    tstart, tfinish, fstart, ffinish, mult = get_parameters(dia)
    ret = my_fft_filter_com(rawdata, fstart, ffinish)
    ret = ininterval(ret, tstart, tfinish)
    ret['V'] = np.where(ret['V'] < 0, 0, ret['V'])
    ret['V'] = ret['V'] * mult
    set_parameters(dia, ret)
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

    d = my_fft_filter_com(d, 1.0 / 80.0e-6, 1.0 / 1.0e-6)

    nnul = d['V'].loc[d['T'] > d['T'].mean()].mean()
    d['V'] = d['V'] - nnul
    dataret = RawData('$n_{e}, 10^{15} см^{-3}$', d.diagnostic, d['T'].values, d['V'].values)
    return dataret


def get_up_envelope(data):
    plt.cla()
    pic_width = 0.125 / 200.0
    pic_dist = 1.0 / 200.0
    pic_ampl_proc = 60.0
    signal = data['V'].values
    time = data['T'].values
    pic_max = data['V'].loc[data['T'] > data['T'].mean()].max()
    pic_ampl = 1.0e-2 * pic_ampl_proc * pic_max
    tgrad = np.gradient(time)
    dt = np.mean(tgrad)
    pic_width_n = int(pic_width / dt)
    pic_dist_n = int(pic_dist / dt)
    pic_array_raw = find_peaks(signal, width=[0.8 * pic_width_n, 8 * pic_width_n], prominence=pic_ampl)[0]
    pic_array_raw_time = time[pic_array_raw]
    pic_array_raw_value = signal[pic_array_raw]
    # plt.plot(time, signal)
    # plt.plot(pic_array_raw_time, pic_array_raw_value, 'ro')
    f = interp1d(pic_array_raw_time, pic_array_raw_value, kind='cubic', bounds_error=False, fill_value=0.0)
    env_up = f(time)
    signal = -signal
    pic_array_raw = find_peaks(signal, width=[0.2 * pic_width_n, 4 * pic_width_n], prominence=pic_ampl)[0]
    pic_array_raw_time = time[pic_array_raw]
    pic_array_raw_value = signal[pic_array_raw]
    f = interp1d(pic_array_raw_time, pic_array_raw_value, kind='cubic', bounds_error=False, fill_value=0.0)
    env_down = -f(time)
    env_com = 0.5 * (env_down + env_up)
    dataret = RawData('$n_{e}, 10^{15} см^{-3}$', data.diagnostic, data['T'].values, data['V'].values - env_com)
    return dataret

    # plt.plot(time, env)
    # plt.show()


def Diagnostic_Interferometer(rawdata, master):
    diagnostic = 'Интерферометр'
    if rawdata.diagnostic != diagnostic:
        return None
    dia = master.getDia(diagnostic)
    tstart, tfinish, fstart, ffinish, mult = get_parameters(dia)
    ret = my_fft_filter_com(rawdata, 1, ffinish)
    ret = my_fft_filter_fin(ret, fstart, ffinish)
    ret = preinterferometer(ret)
    ret = ininterval(ret, tstart, tfinish)
    ret['V'] = ret['V'] * mult
    set_parameters(dia, ret)
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
    tstart, tfinish, fstart, ffinish, mult = get_parameters(dia)
    ret = calorimetr(rawdata)
    ret = my_fft_filter_com(ret, fstart, ffinish)
    retmin = ret['V'].loc[ret['T'] < 0].mean()
    ret = ininterval(ret, tstart, tfinish)
    ret['V'] = np.abs(ret['V'] - retmin) * mult
    set_parameters(dia, ret)
    return ret


def get_init_value(data):
    u0 = data['V'].loc[data['T'] < 5.0e-6].mean()
    return u0


def reflectomert(data, u0):
    u = np.where(data['V'].values < 0, 0, data['V'].values)
    t = data['T'].values
    u = np.abs(u - u0)
    u = u - np.min(u)
    umax = np.max(u)
    T = u / umax
    dataret = RawData('', data.diagnostic, t, T)
    return dataret


def Diagnostic_Reflectometr(rawdata, master):
    diagnostic = 'Рефлектометр'
    if rawdata.diagnostic != diagnostic:
        return None
    dia = master.getDia(diagnostic)
    tstart, tfinish, fstart, ffinish, mult = get_parameters(dia)
    ret = my_fft_filter_com(rawdata, fstart, ffinish)
    u0 = get_init_value(ret)
    ret = ininterval(ret, tstart, tfinish)
    ret = reflectomert(ret, u0)
    # ret['V'] = ret['V'] * mult

    set_parameters(dia, ret)
    if (ret.Overlay != '1'):
        print('Проблема 326')
    return ret


def Diagnostic_Start(rawdata, master):
    diagnostic = 'Запуск'
    if rawdata.diagnostic != diagnostic:
        return None
    dia = master.getDia(diagnostic)
    tstart, tfinish, fstart, ffinish, mult = get_parameters(dia)
    ret = my_fft_filter_com(rawdata, fstart, ffinish)
    # retmin = ret['V'].loc[ret['T'] < 0].mean()
    ret = ininterval(ret, tstart, tfinish)
    ret['V'] = ret['V'] * mult
    set_parameters(dia, ret)
    return ret
