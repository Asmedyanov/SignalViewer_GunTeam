from pandas import DataFrame
import numpy as np


class RawData(DataFrame):
    def __init__(self, label='rawdata', time=np.array(), values=np.array()):
        super(RawData, self).__init__()
        self.label = label
        self['T'] = time
        self['V'] = values
