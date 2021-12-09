from pandas import DataFrame
import numpy as np
from scipy.fft import fft, fftfreq


class SpectrData(DataFrame):
    def __init__(self, data):
        super(SpectrData, self).__init__()
        time = data['T'].values
        value = data['V'].values
        self.label = data.label
        timeSteps = np.gradient(time)
        meanStep = np.mean(timeSteps)
        yvalue = np.abs(fft(value))
        xvalue = fftfreq(len(yvalue), meanStep)
        self['T'] = xvalue[:int(len(xvalue) / 2)]
        self['V'] = np.log10(yvalue[:int(len(yvalue) / 2)])
