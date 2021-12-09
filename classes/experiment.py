from constants import *
import xml.etree.ElementTree as xml
from classes.spectrdata import SpectrData


class Experiment:
    def __init__(self, master):
        self.master = master
        self.rawdatalist = []
        self.rawSpectraList = []
        self.oscDict = dict()
        self.loadDefaultSettings()

    def addRawdataList(self, rawdatalist):
        self.rawdatalist = self.rawdatalist + rawdatalist
        self.master.mainPlotDict['Сырые сигналы'].plot(self.rawdatalist)
        self.upDateRowSpectra()

    def upDateRowSpectra(self):
        self.rawSpectraList = []
        for rawdata in self.rawdatalist:
            self.rawSpectraList.append(SpectrData(rawdata))
        self.master.mainPlotDict['Сырые спектры'].plot(self.rawSpectraList)

    def clear(self):
        self.rawdatalist = []

    def loadDefaultSettings(self, ):
        self.oscDict = dict()
        rootXML = xml.ElementTree(file=default_file).getroot()
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

    def getOSC(self, mask):
        for osc in self.oscDict.values():
            if osc['Параметры']['Маска']['Значение'] == mask:
                return osc

    def __str__(self):
        return f'Experiment {len(self.rawdatalist)}'
