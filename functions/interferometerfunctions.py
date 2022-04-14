import numpy as np
from scipy.signal import argrelextrema, find_peaks, butter, filtfilt, peak_prominences
from functions.mymathfunctions import *
import matplotlib.pyplot as plt
import pandas as pd
from constants import pic_parameters
from scipy import ndimage

visinity = 1.0
prominence = 0.1


def fase_interferometr(data):
    d = data
    # сдвинем минимум в 0

    mininterf = ndimage.minimum_filter1d(data['Values'], size=int(1.0 / (600.0 * 1.0e-7)))
    d['Values'] = d['Values'] - mininterf

    maxinterf = ndimage.maximum_filter1d(data['Values'], size=int(1.0 / (600.0 * 1.0e-7)))

    # Пересчитаем в фазу
    d['Values'] = np.arccos(1.0 - (2.0 * d['Values'] / maxinterf))
    # вычислим неплазменную часть

    dataret = RawData(label='', diagnostic=d.diagnostic, time=d['Time'].values, values=d['Values'].values)
    return dataret


def preinterferometer(data, f_start):
    d = data
    # сдвинем минимум в 0
    mininterf = ndimage.minimum_filter1d(data['Values'], size=int(1.0 / (600.0 * 1.0e-7)))
    d['Values'] = d['Values'] - mininterf

    maxinterf = ndimage.maximum_filter1d(data['Values'], size=int(1.0 / (600.0 * 1.0e-7)))
    # Пересчитаем в фазу
    d['Values'] = np.arccos(1.0 - (2.0 * d['Values'] / maxinterf))
    # вычислим неплазменную часть
    # d = regect_filter(d,f_gen=f_start)
    d = high_pass_filter(d, f_start)
    nnul = d['Values'].loc[((d['Time'] < 10.0e-6) & (d['Time'] > 5.0e-6))].mean()
    d['Values'] = d['Values'] - nnul

    dataret = RawData(label='', diagnostic=d.diagnostic, time=d['Time'].values, values=d['Values'].values)
    return dataret


def scale_up_interferometr_0(data, rev_x):
    signal = data['Values'].values
    time = data['Time'].values
    n_left = find_nearest(time, rev_x[0])
    n_right = find_nearest(time, rev_x[-1])
    # rev_value = min(signal[[n_left, n_right]])
    rev_value = signal[n_left]
    '''mult = 1
    if rev_value<0:
        mult = -1
    rev_value = abs(rev_value)
    must_be = 2.0*np.pi
    rev_value = (int(rev_value/must_be)+1)*must_be*mult'''
    if abs(signal[n_left]) < abs(signal[n_right]):
        rev_value = signal[n_right]
    new_signal = np.where((time > rev_x[0]) & (time < rev_x[-1]),
                          2 * rev_value - signal, signal)
    dataret = RawData(label='', diagnostic=data.diagnostic, time=time, values=new_signal)
    return dataret


def scale_up_interferometr_pi(data, rev_x):
    signal = data['Values'].values
    time = data['Time'].values
    n_left = find_nearest(time, rev_x[0])
    n_right = find_nearest(time, rev_x[-1])
    rev_value = signal[n_left]
    if abs(signal[n_left]) < abs(signal[n_right]):
        rev_value = signal[n_right]
    '''mult = 1
    if rev_value < 0:
        mult = -1
    rev_value = abs(rev_value)
    rev_value = (int(rev_value / np.pi) + 1) * np.pi * mult'''

    new_signal = np.where((time > rev_x[0]) & (time < rev_x[-1]),
                          2 * rev_value - signal, signal)
    dataret = RawData(label='', diagnostic=data.diagnostic, time=time, values=new_signal)
    return dataret


def find_revers_0(data, classificator):
    # plt.cla()
    signal = data['Values'].values
    time = data['Time'].values
    # plt.plot(time, signal)
    # pic_max = signal.max() - signal.min()
    pic_array_raw = my_find_pics(-signal)
    pic_data = pd.DataFrame(pic_array_raw[1])
    pic_data['pic_time'] = pic_array_raw[0]
    X = pic_data[pic_parameters].values
    Y = classificator.predict(X)
    pic_indexec_left = pic_data['pic_time'].values[np.nonzero(Y < 0)]
    pic_indexec_right = pic_data['pic_time'].values[np.nonzero(Y > 0)]

    if len(pic_indexec_left) > len(pic_indexec_right):
        while len(pic_indexec_left) > len(pic_indexec_right):
            n_remove = np.argmax(signal[pic_indexec_left])
            pic_indexec_left = np.delete(pic_indexec_left, n_remove)

    if len(pic_indexec_left) < len(pic_indexec_right):
        while len(pic_indexec_left) < len(pic_indexec_right):
            n_remove = np.argmax(signal[pic_indexec_right])
            pic_indexec_right = np.delete(pic_indexec_right, n_remove)

    pic_array_raw_time = []
    for t in time[pic_indexec_left]:
        pic_array_raw_time.append(t)
    for t in time[pic_indexec_right]:
        pic_array_raw_time.append(t)
    # plt.show()

    return pic_array_raw_time


def find_revers_pi(data, classificator):
    # plt.cla()

    signal = data['Values'].values
    time = data['Time'].values

    # plt.plot(time, signal)

    pic_max = signal.max() - signal.min()
    tgrad = np.gradient(time)
    dt = np.mean(tgrad)

    pic_array_raw = my_find_pics(signal)
    pic_data = pd.DataFrame(pic_array_raw[1])
    pic_data['pic_time'] = pic_array_raw[0]
    X = pic_data[pic_parameters].values
    Y = classificator.predict(X)
    pic_indexec_left = pic_data['pic_time'].values[np.nonzero(Y < 0)]
    pic_indexec_left = np.sort(pic_indexec_left)
    pic_indexec_right = pic_data['pic_time'].values[np.nonzero(Y > 0)]
    pic_indexec_right = np.sort(pic_indexec_right)

    if len(pic_indexec_left) > len(pic_indexec_right):
        while len(pic_indexec_left) > len(pic_indexec_right):
            n_remove = np.argmin(signal[pic_indexec_left])
            pic_indexec_left = np.delete(pic_indexec_left, n_remove)

    if len(pic_indexec_left) < len(pic_indexec_right):
        while len(pic_indexec_left) < len(pic_indexec_right):
            n_remove = np.argmin(signal[pic_indexec_right])
            pic_indexec_right = np.delete(pic_indexec_right, n_remove)

    for i, pic in enumerate(pic_indexec_left):
        if pic_indexec_right[i] < pic:
            buffer = pic_indexec_right[i]
            pic_indexec_right[i] = pic
            pic_indexec_left[i] = buffer

    pic_array_raw_time = []
    for t in time[pic_indexec_left]:
        pic_array_raw_time.append(t)
    for t in time[pic_indexec_right]:
        pic_array_raw_time.append(t)
    # plt.show()
    return pic_array_raw_time


def find_reverse(data):
    signal = data['Values'].values
    time = data['Time'].values
    pics_pi_raw = my_find_pics(signal)
    pics_pi_index = pics_pi_raw[0]
    pics_0_raw = my_find_pics(-signal)
    pics_0_index = pics_0_raw[0]
    pics_all_index = np.concatenate([pics_0_index, pics_pi_index])
    pics_all_index = np.sort(pics_all_index)
    visinity = 0.6
    try:
        for i, index in enumerate(pics_0_index):
            if signal[index] > visinity:
                pics_0_index = np.delete(pics_0_index, i)
    except:
        pass

    try:
        for i, index in enumerate(pics_pi_index):
            if signal[index] < np.pi - visinity:
                pics_pi_index = np.delete(pics_pi_index, i)
    except:
        pass

    try:
        if (pics_all_index[0] in pics_0_index) and (pics_all_index[-1] in pics_pi_index):
            base_dif_0 = pics_0_raw[1]["right_bases"][0] - pics_0_raw[1]["left_bases"][0]
            base_dif_pi = pics_pi_raw[1]["right_bases"][-1] - pics_pi_raw[1]["left_bases"][-1]
            if base_dif_0 > base_dif_pi:
                pics_0_index = np.delete(pics_0_index, 0)
            else:
                pics_pi_index = np.delete(pics_pi_index, -1)

        elif (pics_all_index[0] in pics_pi_index) and (pics_all_index[-1] in pics_0_index):
            base_dif_0 = pics_0_raw[1]["right_bases"][-1] - pics_0_raw[1]["left_bases"][-1]
            base_dif_pi = pics_pi_raw[1]["right_bases"][0] - pics_pi_raw[1]["left_bases"][0]
            if base_dif_0 > base_dif_pi:
                pics_0_index = np.delete(pics_0_index, -1)
            else:
                pics_pi_index = np.delete(pics_pi_index, 0)
    except:
        pass

    return time[pics_0_index], time[pics_pi_index]


def post_interferometer_2(data):
    # выделим участок с плазмой:
    data_plasma = data.loc[((data['Time'] > 22.0e-6) & (data['Time'] < 57.0e-6))]
    plasma_signal = data_plasma['Values'].values
    plasma_time = data_plasma['Time'].values

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
    signal = data['Values'].values
    time = data['Time'].values
    real_start_index = np.where(time == reversed_time[0])[0][0]
    real_stop_index = np.where(time == reversed_time[-1])[0][0]
    signal.flat[real_start_index:real_stop_index] = reversed_signal
    dataret = RawData('', data.diagnostic, time, -signal)

    #    plt.show()
    return dataret
