class Experiment:
    def __init__(self, master):
        self.master = master
        self.rawdatalist = []
        self.chanalDict = dict()
        self.oscDict = dict()

    def addRawdataList(self, rawdatalist):
        self.rawdatalist = self.rawdatalist + rawdatalist
        self.master.mainPlotDict['Сырые сигналы'].plot(self.rawdatalist)

    def clear(self):
        self.rawdatalist = []

    def __str__(self):
        return f'Experiment {len(self.rawdatalist)}'
