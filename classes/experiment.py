import re

from constants import *
import xml.etree.ElementTree as xml
from classes.spectrdata import SpectrData
from classes.diagnosticdata import DiagnosticData
from classes.correlationdata import CorrelationData
import numpy as np
import pandas as pd


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
        self.upDataStatistic()
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
            if f'{data_name}_max' not in self.statDict.keys():
                self.statDict[f'{data_name}_max'] = []
            self.statDict[f'{data_name}_max'].append(np.max(data['V']))
        for i, data in enumerate(self.correlationDataList):
            if f'correlation {i}_speed' not in self.statDict.keys():
                self.statDict[f'correlation {i}_speed'] = []
            self.statDict[f'correlation {i}_speed'].append(0.2/data.get_shift())

    def saveStatistic(self, fileName='default.txt'):
        if len(self.statDict) == 0:
            return
        output = pd.DataFrame()
        for mykey, myvalue in self.statDict.items():
            output[mykey] = myvalue
        output.to_csv(fileName, sep='\t',float_format='%.1e')

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
