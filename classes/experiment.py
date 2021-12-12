from constants import *
import xml.etree.ElementTree as xml
from classes.spectrdata import SpectrData
from classes.diagnosticdata import DiagnosticData


class Experiment:
    def __init__(self, master):
        self.master = master
        self.rawdatalist = []
        self.rawSpectraList = []
        self.diagnosticDataList = []
        self.oscDict = dict()
        self.diaDict = dict()
        self.loadSettings()

    def addRawdataList(self, rawdatalist):
        self.rawdatalist = self.rawdatalist + rawdatalist
        self.master.mainPlotDict['Сырые сигналы'].plot(self.rawdatalist, self.master.foldername)
        #self.upDateRowSpectra()
        self.upDataDiacnosticData()
        self.upDateDiaSpectra()


    def upDateRowSpectra(self):
        self.rawSpectraList = []
        for rawdata in self.rawdatalist:
            self.rawSpectraList.append(SpectrData(rawdata))
        self.master.mainPlotDict['Сырые спектры'].plot(self.rawSpectraList, self.master.foldername)
    def upDateDiaSpectra(self):
        self.diaSpectraList = []
        for rawdata in self.diagnosticDataList:
            self.diaSpectraList.append(SpectrData(rawdata))
        self.master.mainPlotDict['Итоговые спектры'].plot(self.diaSpectraList, self.master.foldername)

    def upDataDiacnosticData(self):
        self.diagnosticDataList = []
        for rawdata in self.rawdatalist:
            self.diagnosticDataList.append(DiagnosticData(rawdata, self))
        self.master.mainPlotDict['Итоговые сигналы'].plot(self.diagnosticDataList, self.master.foldername)

    def clear(self):
        self.rawdatalist = []

    def loadSettings(self, filename = default_file):
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
