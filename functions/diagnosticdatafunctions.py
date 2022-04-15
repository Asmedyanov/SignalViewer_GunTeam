# import numpy as np
# from scipy.fft import rfft, irfft, fftfreq, fft, ifft
# import pandas as pd
# from classes.rawdata import RawData
# from scipy.signal import argrelextrema, find_peaks, butter, filtfilt
# from scipy.interpolate import interp1d, splrep, splev
# import matplotlib.pyplot as plt
# from mymathfunctions import *
from functions.interferometerfunctions import *


def get_parameters(dia):
    tstart = float(dia['Параметры']['Время старт']['Значение'])
    tfinish = float(dia['Параметры']['Время финиш']['Значение'])
    ffinish = float(dia['Параметры']['Частота финиш']['Значение'])
    fstart = float(dia['Параметры']['Частота старт']['Значение'])
    mult = dia['Параметры']['Множитель']['Значение']
    if mult != 'На себя':
        mult = float(mult)
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


def Diagnostic_belt(rawdata, master):
    diagnostic = 'Пояс'
    if rawdata.diagnostic != diagnostic:
        return None
    dia = master.getDia(diagnostic)
    tstart, tfinish, fstart, ffinish, mult = get_parameters(dia)
    # ret = my_fft_filter_com(rawdata, fstart, ffinish)
    ret = rolling_avg(rawdata, 1.0 / ffinish)
    ret = ininterval(ret, tstart, tfinish)
    ret['Values'] = ret['Values'] * mult
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
    # ret['Values'] = np.where(ret['Values'] < 0, 0, ret['Values'])
    if mult == 'На себя':
        ret['Values'] = ret['Values'] * (-1)
        ret = norm_data(ret)

    else:
        ret['Values'] = ret['Values'] * mult
    set_parameters(dia, ret)
    return ret


def Diagnostic_Interferometer(rawdata, master):
    diagnostic = 'Интерферометр'
    if rawdata.diagnostic != diagnostic:
        return None
    dia = master.getDia(diagnostic)
    tstart, tfinish, fstart, ffinish, mult = get_parameters(dia)
    # data = my_fft_filter_sharp(rawdata, fstart, ffinish)
    data = rolling_avg(rawdata, 0.5e-6)
    data = fase_interferometr_tan(data)
    # data = ininterval(data, tstart, tfinish)
    data = my_unwrop(data)
    ret = data
    # data = rolling_avg(data, 0.5e-6)
    # noize_ample = get_noize_ample(data, fstart)
    # noize_freq = get_noize_freq(data, fstart)
    # print(f'амплитуда шума {noize_ample} рад')
    # print(f'частота шума {noize_freq} Гц')
    # data = ininterval(data, tstart, tfinish)
    # data = rolling_avg(data, 0.5e-6)
    # ret = high_pass_filter(data,fstart)
    # ret['Values'] = np.unwrap(ret['Values'].values, axis=0,period=np.pi,discont=np.pi)
    '''if master.master.isStadied:
        ret = rolling_avg(rawdata, 1.0 / ffinish)
        ret = preinterferometer(ret, fstart)
        ret = ininterval(ret, tstart, tfinish)
        #ret['Values'] = np.unwrap(ret['Values'],period=0.5*np.pi)
        rev_x_0, rev_x_pi = find_reverse(data, noize_ample,noize_freq)



        # if len(rev_x_0) % 2 == 0:
        while len(rev_x_0) > 1:
            ret = scale_up_interferometr_0(ret, rev_x_0)
            rev_x_0 = rev_x_0[1:-1]

        # if len(rev_x_pi) % 2 == 0:
        while len(rev_x_pi) > 1:
            ret = scale_up_interferometr_pi(ret, rev_x_pi)
            rev_x_pi = rev_x_pi[1:-1]

    if mult == 'На себя':
        ret = norm_data(ret)
    else:
        if abs(ret['Values'].max()) < abs(ret['Values'].min()):
            mult *= (-1)
        ret['Values'] = ret['Values'] * mult
    ret = cut_negative(ret)'''

    set_parameters(dia, ret)
    return ret


def calorimetr(data):
    u = np.abs(data['Values'].values)
    t = data['Time'].values
    U0 = 1.52
    R0 = 910.0
    r = np.abs(R0 * u / (U0 - u))
    dataret = RawData(label='', diagnostic=data.diagnostic, time=t, values=r)
    return dataret


def Diagnostic_Calorimetr(rawdata, master):
    diagnostic = 'Калориметр'
    if rawdata.diagnostic != diagnostic:
        return None
    dia = master.getDia(diagnostic)
    tstart, tfinish, fstart, ffinish, mult = get_parameters(dia)
    ret = calorimetr(rawdata)
    ret = rolling_avg(ret, 1.0 / ffinish)
    # ret = ininterval(ret, tstart, tfinish)#
    retmin = ret['Values'].loc[ret['Time'] < 0].min()

    ret['Values'] = (ret['Values'] - retmin) * mult

    # ret['Values'] = (ret['Values']-85) * mult
    set_parameters(dia, ret)
    return ret


def get_init_value(data):
    u0 = data['Values'].loc[data['Time'] < 5.0e-6].mean()
    return u0


def reflectomert(data, u0):
    u = np.where(data['Values'].values < 0, 0, data['Values'].values)
    t = data['Time'].values
    u = np.abs(u - u0)
    u = u - np.min(u)
    umax = np.max(u)
    T = u / umax
    dataret = RawData(label='', diagnostic=data.diagnostic, time=t, values=T)
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
    # ret['Values'] = ret['Values'] * mult

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
    # retmin = ret['Values'].loc[ret['Time'] < 0].mean()
    ret = ininterval(ret, tstart, tfinish)
    ret['Values'] = ret['Values'] * mult
    set_parameters(dia, ret)
    return ret


def Diagnostic_Devider(rawdata, master):
    diagnostic = 'Делитель напряжения'
    if rawdata.diagnostic != diagnostic:
        return None
    dia = master.getDia(diagnostic)
    tstart, tfinish, fstart, ffinish, mult = get_parameters(dia)
    # ret = my_fft_filter_com(rawdata, fstart, ffinish)
    ret = rolling_avg(rawdata, 1.0 / ffinish)
    # retmin = ret['Values'].loc[ret['Time'] < 0].mean()
    ret = ininterval(ret, tstart, tfinish)
    ret['Values'] = ret['Values'] * mult
    set_parameters(dia, ret)
    return ret
