from pandas import DataFrame
import numpy as np


class RawData(DataFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(columns=['Time', 'Values'])
        self.timeDim = 'сек'
        self.Overlay = '0'
        try:
            self.label = kwargs['label']
            self.diagnostic = kwargs['diagnostic']
            self['Time'] = kwargs['time']
            self['Values'] = kwargs['values']
        except:
            self.label = 'EMPTY RAW DATA'
            self.diagnostic = 'Запуск'
            # Рисуем круг

            t = np.arange(0.0, 2.0 * np.pi, 0.1)
            self['Time'] = np.cos(2.0 * np.pi * t)
            self['Values'] = np.sin(2.0 * np.pi * t)

    def samlePeriod(self):
        timeSteps = np.gradient(self['Time'])
        meanStep = np.mean(timeSteps)
        return meanStep

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
        return f'RawData {self.label}: len = {len(self)}; mintime = {mintime}; maxtime = {maxtime}; minvalues = {minvalues}; maxvalues = {maxvalues}'
