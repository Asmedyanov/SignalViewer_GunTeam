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

        def crosscorr(a, b, tau):
            ret = 0
            ret1 = 0
            ret2 = 0
            n = len(a) - tau
            # ret = np.sum(a[:n] * b[tau:tau + n])
            # ret1 = np.sum(a[tau:tau + n] * a[tau:tau + n])
            # ret2 = np.sum(b[tau:tau + n] * b[tau:tau + n])
            for k in range(n):
                ret += a[k] * b[k + tau]
                ret1 += a[k + tau] * a[k + tau]
                ret2 += b[k + tau] * b[k + tau]
            return (ret * ret) / (ret1 * ret2)

        acrosscorr = []
        for tau in range(int(len(leftdata) * 0.125) - 1):
            acrosscorr.append(crosscorr(leftdata['V'], rightdata['V'], tau))
        # correlation_value = np.convolve(leftdata['V'], rightdata['V'], mode='same')
        correlation_value = np.array(acrosscorr)

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
