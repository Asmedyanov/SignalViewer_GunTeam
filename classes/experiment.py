import re

from constants import *
import xml.etree.ElementTree as xml
from classes.spectrdata import SpectrData
from classes.diagnosticdata import DiagnosticData
from classes.correlationdata import CorrelationData
import numpy as np
import pandas as pd
from classes.rawdata import RawData
from functions.mymathfunctions import integral
from classes.StatisticSettings import StatisticSettings


class Experiment:
    def __init__(self, master):
        self.master = master
        self.rawdatalist = []
        self.rawSpectraList = []
        self.diagnosticDataList = []
        self.correlationDataList = []
        self.oscDict = dict()
        self.diaDict = dict()
        self.statDict = dict()
        self.loadSettings()

    def addRawdataList(self, rawdatalist):
        self.rawdatalist = self.rawdatalist + rawdatalist
        header = self.master.foldername

        try:
            fileName = self.master.fileList[0].split('/')[-1]
            header = f'{header}/{fileName}'
        except:
            pass
        self.master.mainPlotDict['Сырые сигналы'].plot(self.rawdatalist, header)
        # self.upDateRowSpectra()
        self.upDataDiacnosticData()
        self.upDataCorrelationData()
        self.upDataStatistic_new()
        # self.upDateDiaSpectra()

    def addRawdataList_NoUpdate(self, rawdatalist):
        self.rawdatalist = self.rawdatalist + rawdatalist
        header = self.master.foldername

        try:
            fileName = self.master.fileList[0].split('/')[-1]
            header = f'{header}/{fileName}'
        except:
            pass
        self.master.mainPlotDict['Сырые сигналы'].plot(self.rawdatalist, header)

    def exist_labels(self):
        ret = []
        for data in self.rawdatalist + self.diagnosticDataList + self.correlationDataList:
            ret.append(data.label.split('#')[0])
        return ret

    def upDateRowSpectra(self):
        self.rawSpectraList = []
        for rawdata in self.rawdatalist:
            self.rawSpectraList.append(SpectrData(rawdata))
        self.master.mainPlotDict['Сырые спектры'].plot(self.rawSpectraList, self.master.foldername)

    def upDateDiaSpectra(self):
        self.diaSpectraList = []
        for rawdata in self.diagnosticDataList:
            self.diaSpectraList.append(SpectrData(rawdata))
        header = self.master.foldername

        self.master.mainPlotDict['Итоговые спектры'].plot(self.diaSpectraList, header)

    def upDataDiacnosticData(self):
        self.diagnosticDataList = []
        diagnosticNames = dict()
        for rawdata in self.rawdatalist:
            dia_data = DiagnosticData(rawdata, self)
            label = dia_data.label
            try:
                diagnosticNames[label] += 1
                label = f'{label} #{diagnosticNames[label]}'
            except:
                diagnosticNames[label] = 1
            dia_data.label = label
            self.diagnosticDataList.append(dia_data)
        header = self.master.foldername
        try:
            fileName = self.master.fileList[-1].split('/')[-1]
            header = f'{header}/{fileName}'
        except:
            pass
        self.master.mainPlotDict['Итоговые сигналы'].plot(self.diagnosticDataList, header)

    def upDataCorrelationData(self):
        self.correlationDataList = []
        listForCorrelation = []
        for data in self.diagnosticDataList:
            try:
                if data.Overlay == '1':
                    listForCorrelation.append(data)
            except:
                pass
        n_cor = len(listForCorrelation)
        if n_cor == 0:
            return
        for i in range(n_cor):
            for j in range(i + 1, n_cor):
                self.correlationDataList.append(CorrelationData(listForCorrelation[i], listForCorrelation[j], self))
        header = self.master.foldername
        try:
            fileName = self.master.fileList[-1].split('/')[-1]
            header = f'{header}/{fileName}'
        except:
            pass
        self.master.mainPlotDict['Кросс-корреляции'].plot(self.correlationDataList, header)
        # l = 2.3e-1
        # t = self.correlationDataList[0].get_shift()
        # print(f'скорость {1.0e-3 * l / t} км/с')

    def clear(self):
        self.rawdatalist = []

    def clear_statistic(self):
        self.statDict = dict()

    def upDataStatistic(self):
        try:
            if self.master.foldername[1:] not in self.statDict['Выстрел']:
                self.statDict['Выстрел'].append(self.master.foldername[1:])
        except:
            self.statDict['Выстрел'] = []
            self.statDict['Выстрел'].append(self.master.foldername[1:])
        for data in self.diagnosticDataList:
            data_name = data.label
            if data_name[0] in ['Q', 'I']:
                if f'{data_name}_max' not in self.statDict.keys():
                    self.statDict[f'{data_name}_max'] = []
                self.statDict[f'{data_name}_max'].append(np.max(data['Values']))
            if data_name.split(',')[0] in ['$n_{e}$']:
                if f'{data_name}_int' not in self.statDict.keys():
                    self.statDict[f'{data_name}_int'] = []
                self.statDict[f'{data_name}_int'].append(integral(data))
        for i, data in enumerate(self.correlationDataList):
            if f'correlation {i}_speed' not in self.statDict.keys():
                self.statDict[f'correlation {i}_speed'] = []
            self.statDict[f'correlation {i}_speed'].append(0.2 / data.get_shift())

    def upDataStatistic_new(self, ):

        try:
            for diagnosticdata in self.diagnosticDataList:
                self.statDict[diagnosticdata.label] = pd.concat(
                    [self.statDict[diagnosticdata.label], diagnosticdata.get_statistic()], ignore_index=True)
            for diagnosticdata in self.correlationDataList:
                self.statDict[diagnosticdata.label] = pd.concat(
                    [self.statDict[diagnosticdata.label], diagnosticdata.get_statistic()], ignore_index=True)
            dataname = pd.DataFrame()
            dataname['name'] = [self.master.foldername]
            self.statDict['name'] = pd.concat([self.statDict['name'], dataname])
        except:
            for diagnosticdata in self.diagnosticDataList:
                self.statDict[diagnosticdata.label] = diagnosticdata.get_statistic()
            for diagnosticdata in self.correlationDataList:
                self.statDict[diagnosticdata.label] = diagnosticdata.get_statistic()
            self.statDict['name'] = pd.DataFrame()
            self.statDict['name']['name'] = [self.master.foldername]

    def saveStatistic(self, fileName='default.txt'):
        if len(self.statDict) == 0:
            return
        output = pd.DataFrame()
        # Создадим колонку энергии по интерферометру
        ne_list = []
        speed_list = []
        for my_key, my_value in self.statDict.items():
            if my_key.split(',')[0] in ['$n_{e}$']:
                ne_list.append(np.array(my_value))
            if my_key.split('_')[-1] in ['speed']:
                speed_list.append(np.array(my_value))
        ne = ne_list[0]
        '''for i in range(1, len(ne_list)):
            ne = ne + ne_list[i]
        ne = ne * 1.0 / len(ne_list)'''
        speed = speed_list[0]
        for i in range(1, len(speed_list)):
            speed += speed_list[i]
        speed = speed * 1.0 / len(speed_list)
        Energy = 1.67e-27 * np.pi * (2.0e-2 ** 2) * ne * 1.0e21 * (speed ** 3) * 0.5
        self.statDict['Energy_interf, Дж'] = Energy
        Energy_Ratio = 100.0 * Energy / self.statDict['Q, Дж_max']
        self.statDict['Energy_ratio, %'] = Energy_Ratio

        x_key = 'I, кА_max'
        plotStatList = []
        for mykey, myvalue in self.statDict.items():
            output[mykey] = myvalue
            if mykey == x_key:
                continue
            if mykey[0] not in ['Q', 'E']:
                continue
            time = np.array(self.statDict[x_key])
            values = np.array(self.statDict[mykey])
            Data_vs_x = RawData(label=mykey, time=time, values=values, diagnostic='Запуск')
            Data_vs_x.timeDim = x_key
            plotStatList.append(Data_vs_x)
        output.to_csv(fileName, sep='\t', float_format='%.1e')

        self.master.mainPlotDict['Сырая статистика'].plot(plotStatList, header='Сырая статистика', style='o')

    def viewStatistic(self):
        try:
            self.advanced_statistic()
        except:
            pass
        self.StatisticSettings = StatisticSettings(self)
        self.master.tabWidget.addTab(self.StatisticSettings, 'Просмотр стаитстики')

    def saveStatistic_new(self, fname='Статистика'):

        for [mykey, statdata] in self.statDict.items():
            statdata.to_csv(f'{fname}/{mykey}.txt', sep='\t')

    def advanced_statistic(self):
        self.statDict['Advanced'] = pd.DataFrame()
        interf_distance = 20.0e-2
        front_time_shift = \
            self.statDict['$n_{e}$, $10^{15} см^{-3}$ #2']['front50'] \
            - self.statDict['$n_{e}$, $10^{15} см^{-3}$']['front50']
        speed50 = interf_distance / front_time_shift
        speedCC = interf_distance / self.statDict['$n_{e}$, $10^{15} см^{-3}$ x $n_{e}$, $10^{15} см^{-3}$'][
            'Time_shift']
        self.statDict['Advanced']['V50, kms'] = speed50 * 1.0e-3
        self.statDict['Advanced']['VCC, kms'] = speedCC * 1.0e-3
        protonE = 1.7e-27 * speedCC * speedCC * 0.5
        self.statDict['Advanced']['Энергия протона, эВ'] = protonE / 1.6e-19
        ne1 = self.statDict['$n_{e}$, $10^{15} см^{-3}$']['max'] * 1.0e21
        ne2 = self.statDict['$n_{e}$, $10^{15} см^{-3}$ #2']['max'] * 1.0e21
        pressure50 = 1.7e-27 * ne1 * speed50 * speed50
        self.statDict['Advanced']['Давление по 50%, кПа'] = pressure50 * 1.0e-3
        int_ne1 = self.statDict['$n_{e}$, $10^{15} см^{-3}$']['integral'] * 1.0e21
        int_ne2 = self.statDict['$n_{e}$, $10^{15} см^{-3}$ #2']['integral'] * 1.0e21
        pressureCC = 1.7e-27 * ne1 * speedCC * speedCC
        self.statDict['Advanced']['Давление по корреляции, кПа'] = pressureCC * 1.0e-3
        S = np.pi * (2.0e-2) ** 2
        Ne1 = int_ne1 * S * speedCC
        Ne2 = int_ne2 * S * speedCC
        self.statDict['Advanced']['Количество электронов на 1, $10^{18}$'] = Ne1 * 1.0e-18
        self.statDict['Advanced']['Количество электронов на 2, $10^{18}$'] = Ne2 * 1.0e-18
        EnegryCC = protonE * Ne1
        self.statDict['Advanced']['Энергия по корреляции, Дж'] = EnegryCC

    def loadSettings(self, filename=default_file):
        self.oscDict = dict()
        rootXML = xml.ElementTree(file=filename).getroot()
        oscsXML = rootXML.find('Осциллографы')
        oscXMLlist = oscsXML.findall('Осциллограф')
        for oscXML in oscXMLlist:
            oscname = oscXML.find('Имя').text
            oscdict = dict()
            parsXML = oscXML.find('Параметры')
            parsdict = dict()
            parXMLlist = parsXML.findall('Параметр')
            for parXML in parXMLlist:
                pardict = dict()
                for parvalue in parXML.iter():
                    if parvalue is parXML: continue
                    pardict[parvalue.tag] = parvalue.text
                parsdict[pardict['Имя']] = pardict
            oscdict[parsXML.tag] = parsdict
            chsXML = oscXML.find('Каналы')
            chsdict = dict()
            chXMLlist = chsXML.findall('Канал')
            for chXML in chXMLlist:
                chdict = dict()
                for chvalue in chXML.iter():
                    if chvalue is chXML: continue
                    chdict[chvalue.tag] = chvalue.text
                chsdict[chdict['Номер']] = chdict
            oscdict[chsXML.tag] = chsdict
            self.oscDict[oscname] = oscdict
        diasXML = rootXML.find('Диагностики')
        diaXMLlist = diasXML.findall('Диагностика')
        for diaXML in diaXMLlist:
            dianame = diaXML.find('Имя').text
            diadict = dict()
            parsXML = diaXML.find('Параметры')
            parsdict = dict()
            parXMLlist = parsXML.findall('Параметр')
            for parXML in parXMLlist:
                pardict = dict()
                for parvalue in parXML.iter():
                    if parvalue is parXML: continue
                    pardict[parvalue.tag] = parvalue.text
                parsdict[pardict['Имя']] = pardict
            diadict[parsXML.tag] = parsdict
            statsXML = diaXML.find('Статистики')
            statsdict = dict()
            statXMLlist = statsXML.findall('Статистика')
            for statXML in statXMLlist:
                statdict = dict()
                for statvalue in statXML.iter():
                    if statvalue is statXML: continue
                    statdict[statvalue.tag] = statvalue.text
                statsdict[statdict['Измерение']] = statdict
            diadict[statsXML.tag] = statsdict
            self.diaDict[dianame] = diadict

    def getOSC(self, mask):
        for osc in self.oscDict.values():
            if osc['Параметры']['Маска']['Значение'] == mask:
                return osc

    def getDia(self, dia0):
        for dianame, dia in self.diaDict.items():
            if dianame == dia0:
                return dia

    def __str__(self):
        return f'Experiment {len(self.rawdatalist)}'
