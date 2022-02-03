from pandas import DataFrame
import numpy as np


class WaveForm(DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__()
        if len(args == 0) and (len(kwargs)) == 0:
            self.default()
            return
        try:
            self['T'] = kwargs['time']
        except:
            self['T'] = args[0]
        try:
            self['V'] = kwargs['value']
        except:
            self['V'] = args[1]

    def default(self):
        self['T'] = np.array([])
        self['V'] = np.array([])

    def samlePeriod(self):
        try:
            timeSteps = np.gradient(self['T'])
            meanStep = np.mean(timeSteps)
            return meanStep
        except:
            return 0
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
        return f'WaveForm {self.label}: len = {len(self)}; mintime = {mintime}; maxtime = {maxtime}; minvalues = {minvalues}; maxvalues = {maxvalues}'