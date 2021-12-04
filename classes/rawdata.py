from pandas import DataFrame
import numpy as np


class RawData(DataFrame):
    def __init__(self, label='rawdata', time=np.array([]), values=np.array([])):
        super(RawData, self).__init__()
        self.label = label
        self['T'] = time
        self['V'] = values

    def __str__(self):
        try:
            mintime = np.min(self['T'])
            maxtime = np.max(self['T'])
            minvalues = np.min(self['V'])
            maxvalues = np.max(self['V'])
        except:
            mintime = 0
            maxtime = 0
            minvalues = 0
            maxvalues = 0

        return f'RawData {self.label}: len = {len(self)}; mintime = {mintime}; maxtime = {maxtime}; minvalues = {minvalues}; maxvalues = {maxvalues}'
