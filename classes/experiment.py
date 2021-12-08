from constants import *
import xml.etree.ElementTree as xml


class Experiment:
    def __init__(self, master):
        self.master = master
        self.rawdatalist = []
        self.chanalDict = dict()
        self.oscDict = dict()
        #self.loadDefaultSettings()

    def addRawdataList(self, rawdatalist):
        self.rawdatalist = self.rawdatalist + rawdatalist
        self.master.mainPlotDict['Сырые сигналы'].plot(self.rawdatalist)

    def clear(self):
        self.rawdatalist = []

    def loadDefaultSettings(self, ):
        rootXML = xml.ElementTree(file=default_file).getroot()
        oscsXML = rootXML.find('Осциллографы')

        def itemlist(parent):
            retlist = []
            for child in parent.iter():
                if child is parent: continue
                issubchild=0
                for subchild in child.iter():
                    if child is subchild:
                        retlist.append(y)
                        break
            print(retlist)
            return retlist

        for oscXML in itemlist(oscsXML):
            oscdict = dict()
            paramsdict = dict()
            parsXML = oscXML.find('Параметры')
            for par in itemlist(parsXML):
                paramdict = dict()
                for f in itemlist(par):
                    paramdict[f.tag] = f.text
                paramsdict[par.tag] = paramdict
            oscdict[parsXML.tag] = paramsdict
            chsXML = oscXML.find('Каналы')
            chsdict = dict()
            for ch in itemlist( chsXML):
                chdict = dict()
                for f in itemlist(ch):
                    chdict[f.tag] = f.text
                chsdict[chdict['Номер']] = chsdict
            oscdict[chsXML.tag] = chsdict
            self.oscDict[oscXML.tag] = oscdict
        print(self.oscDict)

    def __str__(self):
        return f'Experiment {len(self.rawdatalist)}'
