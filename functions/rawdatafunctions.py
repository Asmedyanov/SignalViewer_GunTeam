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
        # print(f'file is not {mask}')
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
        # print(f'file is not {mask}')
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
        # print(f'file is not {mask}')
        return None

    parametr_data = pd.read_csv(a, nrows=29, error_bad_lines=False,
                                names=['P', 'V1', 'V5'])
    parametrDict = {parametr_data['P'][i]: parametr_data['V1'][i] for i in range(len(parametr_data))}
    namesch = ['CH' + str(i) for i in range(1, 5)]
    CHDisplay = [parametrDict[f'CH{i} Display'] == 'On' for i in [1, 2, 3, 4]]
    t0 = float(parametrDict['Trigger Address'])
    dt = float(parametrDict['Delta(second)'])
    data = pd.read_csv(a, sep=' ', skiprows=30,
                       error_bad_lines=False,
                       names=namesch)
    time = [(i - t0) * dt for i in range(len(data))]
    returnlist = []
    for k in range(len(CHDisplay)):
        if CHDisplay[k] == True:
            returnlist.append(RawData(f'{mask} #{k + 1}', time, data[f'CH{k + 1}']))
    return returnlist


def Open_bin(a):
    """
    Открытие файла типа *.bin по строке a
    """

    mask = '*.bin'
    if not fnmatch(a, mask):
        # print(f'file is not {mask}')
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
        returnlist.append(RawData(f'{mask} #{k}', time, values))
    return returnlist


def Open_tek_csv(a):
    """
    Открытие файла типа tek*.CSV по строке a
    """
    mask = 'tek*.CSV'
    if not fnmatch(a, mask):
        # print(f'file is not {mask}')
        return None
    data = pd.read_csv(a, skiprows=20)
    time = data['TIME']
    returnlist = [
        RawData(f'{mask} #{i}', time, data[f'CH{i}']) for i in [2, 3, 4]
    ]
    return returnlist
