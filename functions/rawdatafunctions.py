# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 13:14:34 2020

@author: asmedyanov
"""

# модуль работ с матрицами
import numpy as np
# модуль баз данных
import pandas as pd
from classes.rawdata import RawData
from fnmatch import fnmatch
# модуль бинарных файлов
import pickle as pk

mks = 1.0e6


def Open_A_CSV(a):
    """
    Открытие файла типа A*.CSV по строке a
    """
    mask = 'A*.CSV'
    if not fnmatch(a, mask):
        return None

    data = pd.read_csv(a, skiprows=2, error_bad_lines=False,
                       names=['T', 'V1', 'V2'])
    stmin = data['V1'].min()
    stmax = data['V1'].max()
    st = 0.5 * (stmax + stmin)
    t0 = data['T'].loc[data['V1'] < st].values.min()
    time = data['T'] - t0
    values1 = data['V1']
    values2 = data['V2']
    returnlist = [
        RawData(mask, time, values1),
        RawData(mask, time, values2)
    ]
    return returnlist


def Open_F_CSV(a):
    """
    Открытие файла типа F*.CSV по строке a
    """
    mask = 'F*.CSV'
    if not fnmatch(a, mask):
        return None
    data = pd.read_csv(a, skiprows=19, error_bad_lines=False, names=[
        'T', 'V', 'e'], skipinitialspace=True)
    returnlist = [RawData(mask, data['T'], data['V'])]
    return returnlist


def Open_PRN(a):
    """
    Открытие файла типа *.PRN по строке a
    """

    mask = '*.PRN'
    if not fnmatch(a, mask):
        return None

    parametr_data = pd.read_csv(a, nrows=29, error_bad_lines=False,
                                names=['P', 'V1', 'V5'])
    parametr_data.set_index('P')
    namesch = ['CH' + str(i) for i in range(1, 5)]
    CHDisplay = np.array(
        parametr_data.loc[parametr_data['P'].str.contains('Disp')].V1 == 'On')
    t0 = float(parametr_data['Trigger Address']['V1'])
    dt = float(parametr_data['Delta(second)']['V1'])
    data = pd.read_csv(a, sep=' ', skiprows=30,
                       error_bad_lines=False,
                       names=namesch)
    time = [(i - t0) * dt for i in range(len(data))]
    returnlist = []
    for k in range(len(CHDisplay)):
        if CHDisplay[k] == True:
            returnlist.append(RawData(mask, time, data['CH' + str(k + 1)]))
    return returnlist


def Open_bin(a):
    """
    Открытие файла типа *.bin по строке a
    """

    mask = '*.bin'
    if not fnmatch(a, mask):
        return None
    f = open(a, 'rb')
    value0 = np.fromfile(f, dtype='>i2').byteswap().newbyteorder()
    dt = 0.1e-6
    t0 = (2.3 - 310.0 - 300) * 1.0e-6
    Nsemp = (value0[0] << 16) + value0[1]
    time = np.arange(Nsemp) * dt - t0
    returnlist = []
    for k in range(2 * 4):
        values = (value0[4 + k::16] - (1 << 11)) * (1.6 / (1 << 11))
        if np.min(values) == np.max(values):
            continue
        returnlist.append(RawData(mask, time, values))
    return returnlist


def Open_tek_csv(a):
    """
    Открытие файла типа tek*.CSV по строке a
    """
    mask = 'tek*.CSV'
    if not fnmatch(a, mask):
        return None
    data = pd.read_csv(a, skiprows=20)
    time = data['TIME'] * 1.0e6
    data_ret = []
    data_ret.append(pd.DataFrame())
    data_ret[0]['T'] = time
    data_ret[0]['V'] = data['CH2']
    data_ret.append(pd.DataFrame())
    data_ret[1]['T'] = time
    data_ret[1]['V'] = data['CH3']
    data_ret.append(pd.DataFrame())
    data_ret[2]['T'] = time
    data_ret[2]['V'] = data['CH4']
    return data_ret
