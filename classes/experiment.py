class Experiment:
    def __init__(self, master):
        self.master = master
        self.rawdatalist = []

    def addRawdataList(self, rawdatalist):
        self.rawdatalist = self.rawdatalist + rawdatalist

    def clear(self):
        self.rawdatalist = []

    def __str__(self):
        return f'Experiment {len(self.rawdatalist)}'
