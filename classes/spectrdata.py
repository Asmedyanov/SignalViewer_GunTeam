from pandas import DataFrame
import numpy as np
from scipy.fft import fft, fftfreq
from functions import mymathfunctions


class SpectrData(DataFrame):
    def __init__(self, data):
        super(SpectrData, self).__init__()
        time = data['Time'].values
        value = data['Values'].values
        #value = value-value.mean()
        self.label = data.label

        timeSteps = np.gradient(time)
        meanStep = np.mean(timeSteps)

        fmax = 0.1 / meanStep
        df = 150.0
        nf = int(fmax / df)
        yvalue = np.abs(fft(value, n=nf))
        #yvalue = np.abs(fft(value))
        xvalue = fftfreq(len(yvalue), meanStep)
        self['Time'] = xvalue[:int(xvalue.size / (2))]
        #self['Values'] = np.nan_to_num(np.log10(yvalue[:int(yvalue.size / (2))]))
        self['Values'] = np.nan_to_num(yvalue[:int(yvalue.size / (2))])
