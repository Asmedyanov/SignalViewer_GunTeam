from scipy.signal import argrelextrema, find_peaks, butter, filtfilt
from scipy.interpolate import interp1d, splrep, splev
import numpy as np


def my_fft(value, df, dt):
    fmax = 0.5 / dt
    n = value.size
    nf = int(fmax / df)
    kf = np.arange(nf)
    kt = -2j * np.pi * np.arange(n) / n

    def mode(k):
        sum = np.sum(value * np.exp(k * kt))
        return sum

    retvalue = np.vectorize(mode,cache=True)(kf)
    return retvalue
