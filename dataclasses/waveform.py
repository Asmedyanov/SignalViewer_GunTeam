from pandas import DataFrame
import numpy as np


class WaveForm(DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__()
        if len(args == 0) and (len(kwargs)) == 0:
            self.default()
            return
        try:
            self['Time'] = kwargs['time']
        except:
            self['Time'] = args[0]
        try:
            self['Values'] = kwargs['value']
        except:
            self['Values'] = args[1]

    def default(self):
        self['Time'] = np.array([])
        self['Values'] = np.array([])

    def samlePeriod(self):
        try:
            timeSteps = np.gradient(self['Time'])
            meanStep = np.mean(timeSteps)
            return meanStep
        except:
            return 0
    def __str__(self):
        try:
            mintime = np.min(self['Time'])
            maxtime = np.max(self['Time'])
            minvalues = np.min(self['Values'])
            maxvalues = np.max(self['Values'])
        except:
            mintime = 0
            maxtime = 0
            minvalues = 0
            maxvalues = 0
        return f'WaveForm {self.label}: len = {len(self)}; mintime = {mintime}; maxtime = {maxtime}; minvalues = {minvalues}; maxvalues = {maxvalues}'