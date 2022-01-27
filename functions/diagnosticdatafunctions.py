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
    #ret['V'] = np.where(ret['V'] < 0, 0, ret['V'])
    ret['V'] = ret['V'] * mult
    set_parameters(dia, ret)
    return ret


def Diagnostic_Interferometer(rawdata, master):
    diagnostic = 'Интерферометр'
    if rawdata.diagnostic != diagnostic:
        return None
    dia = master.getDia(diagnostic)
    tstart, tfinish, fstart, ffinish, mult = get_parameters(dia)
    ret = my_fft_filter_com(rawdata, 1, ffinish)
    #ret = my_fft_filter_fin(ret, fstart, ffinish)
    ret = preinterferometer(ret)
    ret = ininterval(ret, tstart, tfinish)
    #if rawdata.label=='ne2':
    #    ret = post_interferometer_2(ret)
    ret['V'] = ret['V'] * mult
    set_parameters(dia, ret)
    return ret


def calorimetr(data):
    u = data['V'].values
    t = data['T'].values
    U0 = 1.5
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
    ret = my_fft_filter_sharp(ret, fstart, ffinish)
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
