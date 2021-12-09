import numpy as np
from scipy.fft import rfft, irfft, fftfreq
import pandas as pd
from classes.rawdata import RawData


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
    dataret = RawData(data.label, data.diagnostic, ret['T'], ret['V'])
    return dataret


def Diagnostic_belt(rawdata, master):
    diagnostic = 'Пояс'
    if rawdata.diagnostic != diagnostic:
        return None
    tstart = 0
    tfinish = 60.0e-6
    ffinish = 1.0 / 5.0e-7
    fstart = 1.0
    mult = -100. / 0.14 * 1.0e-3
    ret = ininterval(rawdata, tstart, tfinish)
    ret = my_fft_filter_com(ret, fstart, ffinish)
    ret['V'] = ret['V'] * mult
    ret.label = 'I, kA'
    return ret
