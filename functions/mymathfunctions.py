from scipy.signal import argrelextrema, find_peaks, butter, filtfilt
from scipy.interpolate import interp1d, splrep, splev
import numpy as np
from classes.rawdata import RawData
from scipy.fft import rfft, irfft, fftfreq, fft, ifft


def my_fft(value, df, dt):
    fmax = 0.5 / dt
    n = value.size
    nf = int(fmax / df)
    kf = np.arange(nf)
    kt = -2j * np.pi * np.arange(n) / n

    def mode(k):
        sum = np.sum(value * np.exp(k * kt))
        return sum

    retvalue = np.vectorize(mode, cache=True)(kf)
    return retvalue


def get_up_envelope(data):
    pic_width = 0.125 / 200.0
    pic_dist = 1.0 / 200.0
    pic_ampl_proc = 60.0
    signal = data['Values'].values
    time = data['Time'].values
    pic_max = data['Values'].loc[data['Time'] > data['Time'].mean()].max()
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
    dataret = RawData(label='', diagnostic= data.diagnostic,time= data['Time'].values,values= data['Values'].values - env_com)
    return dataret


def rolling_avg(data, t_window):
    signal = data['Values'].values
    time = data['Time'].values
    timeSteps = np.gradient(time)
    meanStep = np.mean(timeSteps)
    n_window = int(t_window / meanStep)
    if n_window != 0:
        signal = np.convolve(signal, np.ones(n_window), 'valid') / n_window
    time = (time + 0.5 * t_window)[:signal.size]
    dataret = RawData(label=data.label, diagnostic=data.diagnostic, time=time, values=signal)

    return dataret


def cut_negative(data):
    signal = data['Values'].values
    time = data['Time'].values
    new_signal = np.where(signal > 0, signal, 0)
    dataret = RawData(label= data.label,diagnostic= data.diagnostic,time= time,values= new_signal)

    return dataret


def integral(data):
    signal = data['Values'].values
    time = data['Time'].values
    timeSteps = np.gradient(time)
    meanStep = np.mean(timeSteps)
    return meanStep * np.sum(signal)


def my_fft_filter_fin(data, fstart, ffinish):
    signal = data['Values'].values
    time = data['Time'].values
    timeSteps = np.gradient(time)
    meanStep = np.mean(timeSteps)
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
    dataret = RawData(label= data.label,diagnostic= data.diagnostic,time= new_time,values= cut_signal)

    return dataret


def my_fft_filter_com(data, fstart, ffinish):
    # data = data.dropna()
    # data.index = pd.RangeIndex(len(data.index))
    signal = data['Values'].values
    time = data['Time'].values
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
    fw = 1428.5714285714287 * 4
    fwindow = np.exp(-np.power((W - fstart) / fw, 2)) + np.exp(-np.power((W - fend) / fw, 2))
    fwindow = fwindow / np.max(fwindow)
    fwindow = np.where(((np.abs(W) >= fstart) & (np.abs(W) <= fend)), 1, fwindow)

    cut_signal = irfft(cut_f_signal * fwindow)
    dataret = RawData(label=data.label, diagnostic=data.diagnostic, time=time[:cut_signal.size], values=cut_signal)

    return dataret


def my_fft_filter_sharp(data, fstart, ffinish):
    # data = data.dropna()
    # data.index = pd.RangeIndex(len(data.index))
    signal = data['Values'].values
    time = data['Time'].values
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
    fwindow = np.where(((np.abs(W) >= fstart) & (np.abs(W) <= fend)), 1, 0)

    cut_signal = irfft(cut_f_signal * fwindow)
    dataret = RawData(label=data.label, diagnostic=data.diagnostic, time=time[:cut_signal.size], values=cut_signal)

    return dataret


def my_fft_filter_back(data, fstart, ffinish):
    # data = data.dropna()
    # data.index = pd.RangeIndex(len(data.index))
    signal = data['Values'].values
    time = data['Time'].values
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
    ret = data.loc[(((data['Time'] >= left) & (data['Time'] <= right)))]
    dataret = RawData(label=data.label, diagnostic=data.diagnostic, time=ret['Time'].values,
                      values=ret['Values'].values)
    return dataret


def norm_data(data):
    signal = data['Values'].values
    time = data['Time'].values
    if abs(signal.max()) < abs(signal.min()):
        signal = signal * (-1)

    maxsignal = signal.max()
    signal = 100 * signal / maxsignal
    dataret = RawData(label="%", diagnostic=data.diagnostic, time=time, values=signal)
    return dataret


def find_nearest(a, value):
    a_val = np.abs(a - value)
    return a_val.argmin()


def regect_filter(data, f_gen=300.0):
    signal = data['Values'].values
    time = data['Time'].values
    tgrad = np.gradient(time)
    dt = np.mean(tgrad)

    nfur = 8 * len(signal)
    f_signal = rfft(signal, n=nfur)
    W = fftfreq(f_signal.size, d=dt)[:int(f_signal.size)]
    cut_f_signal = f_signal.copy()
    f_reg = 2.0 * np.pi * f_gen  # W[np.argmax(f_signal[200:])]
    fw = f_reg * 4
    fwindow = np.exp(-np.power(W / fw, 2))
    for n in range(1, 4):
        fwindow += np.exp(-np.power((W - f_reg * n) / fw, 2))
    fwindow += np.exp(-np.power((W - f_reg * 0.5) / fw, 2))
    fwindow = 1.0 - (fwindow / fwindow.max())
    cut_signal = irfft(cut_f_signal * fwindow)[:signal.size]
    cut_time = time[:cut_signal.size]

    dataret = RawData(label=data.label, diagnostic=data.diagnostic, time=cut_time, values=cut_signal)

    return dataret
