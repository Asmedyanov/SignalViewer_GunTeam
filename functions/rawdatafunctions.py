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


def Open_A_CSV(a, master):
    """
    Открытие файла типа A*.CSV по строке a
    """
    shorta = a.split('/')[-1]
    mask = 'A*.CSV'
    if not fnmatch(shorta, mask):
        # print(f'file is not {mask}')
        return None

    osc = master.getOSC(mask)
    nameslist = [
        'P', 'P1', 'P2', 'T'
    ]
    chlist = list(osc['Каналы'].keys())
    chlist.sort()
    for i in chlist:
        nameslist.append(f'CH{i}')
    data = pd.read_csv(a, skiprows=10, error_bad_lines=False,
                       names=nameslist, engine='python')
    for ch in osc['Каналы'].values():
        if ch['Диагностика'] == 'Запуск':
            startdata = data[f'CH{ch["Номер"]}']
            stmin = startdata.min()
            stmax = startdata.max()
            st = 0.5 * (stmax + stmin)
            t0 = data['T'].loc[startdata < st].values.min()
    time = data['T']-t0
    returnlist = [
        RawData(osc['Каналы'][i]['Подпись'], time, data[f'CH{i}']) for i in osc['Каналы'].keys() if
        osc['Каналы'][i]['Отображение'] == '1'

    ]
    return returnlist


def Open_F_CSV(a, master):
    """
    Открытие файла типа F*.CSV по строке a
    """
    mask = 'F*.CSV'
    if not fnmatch(a, mask):
        # print(f'file is not {mask}')
        return None

    osc = master.getOSC(mask)

    data = pd.read_csv(a, skiprows=19, error_bad_lines=False, names=[
        'T', 'V', 'e'], skipinitialspace=True)
    returnlist = [RawData(mask, data['T'], data['V'])]
    return returnlist


def Open_PRN(a, master):
    """
    Открытие файла типа *.PRN по строке a
    """

    mask = '*.PRN'
    if not fnmatch(a, mask):
        # print(f'file is not {mask}')
        return None
    osc = master.getOSC(mask)
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


def Open_bin(a, master):
    """
    Открытие файла типа *.bin по строке a
    """

    mask = '*.bin'
    if not fnmatch(a, mask):
        # print(f'file is not {mask}')
        return None

    osc = master.getOSC(mask)
    f = open(a, 'rb')
    value0 = np.fromfile(f, dtype='>i2').byteswap().newbyteorder()
    dt = 0.1e-6
    t0 = float(osc['Параметры']['Сдвиг времени']['Значение'])
    Nsemp = (value0[0] << 16) + value0[1]
    time = np.arange(Nsemp) * dt + t0
    returnlist = []
    for k in [int(i) for i in osc['Каналы'].keys()]:
        values = (value0[4 + k::16] - (1 << 11)) * (1.6 / (1 << 11))
        if np.min(values) == np.max(values):
            continue
        returnlist.append(RawData(osc['Каналы'][str(k)]['Подпись'], time, values))
    return returnlist


def Open_tek_csv(a, master):
    """
    Открытие файла типа tek*.CSV по строке a
    """
    mask = 'tek*.CSV'
    if not fnmatch(a, mask):
        # print(f'file is not {mask}')
        return None
    osc = master.getOSC(mask)
    data = pd.read_csv(a, skiprows=20)
    time = data['TIME']
    returnlist = [
        RawData(f'{mask} #{i}', time, data[f'CH{i}']) for i in [2, 3, 4]
    ]
    return returnlist
