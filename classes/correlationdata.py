from pandas import DataFrame
import numpy as np
from functions.mymathfunctions import find_nearest
from scipy.signal import find_peaks


def sampletime(data):
    tgrad = np.gradient(data['T'])
    return np.mean(tgrad)


class CorrelationData(DataFrame):
    def __init__(self, Data1, Data2, master):
        super().__init__()
        dt1 = sampletime(Data1)
        dt2 = sampletime(Data2)
        leftdata = Data1
        rightdata = Data2
        if (dt1 != dt2):
            minFreqData = Data1
            maxFreqData = Data2

            if dt2 > dt1:
                minFreqData = Data2
                maxFreqData = Data1
            new_value = []
            new_time = []
            for t in minFreqData['T']:
                new_value.append(maxFreqData['V'][find_nearest(maxFreqData['T'], t)])
                new_time.append(maxFreqData['T'][find_nearest(maxFreqData['T'], t)])
            leftdata = minFreqData
            rightdata['V'] = new_value
            rightdata['T'] = new_time
        dt = max(dt1, dt2)
        a = leftdata['V'].values
        b = rightdata['V'].values

        def crosscorr(tau):
            n0 = int(len(a))
            n = int(len(a) - tau)
            v1 = a[:n]
            v2 = b[int(tau):n0]
            ret = np.dot(v1, v2)
            ret1 = np.dot(v1, v1)
            ret2 = np.dot(v2, v2)
            return (ret * ret) / (ret1 * ret2)

        vcrosscorr = np.vectorize(crosscorr)
        tau = np.arange(len(leftdata) * 1 / 7)
        correlation_value = vcrosscorr(tau)

        self['T'] = dt * np.arange(len(correlation_value))
        self['V'] = correlation_value
        self.label = f'{Data1.label} x {Data1.label}'
        self.timeDim = Data1.timeDim
        self.Overlay = "0"

    def get_shift(self):

        try:
            ret = self['T'].values[np.argmax(self['V'].values)]
        except:
            ret = 0
        return ret
