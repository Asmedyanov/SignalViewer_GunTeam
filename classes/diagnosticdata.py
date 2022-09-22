from pandas import DataFrame
from functions import diagnosticdatafunctions
import numpy as np
from inspect import getmembers, isfunction


class DiagnosticData(DataFrame):
    def __init__(self, rawData, master):
        super(DiagnosticData, self).__init__()
        functions_list = [o[1] for o in getmembers(diagnosticdatafunctions) if
                          (isfunction(o[1]) and (o[0].split('_')[0] == 'Diagnostic'))]
        for open_function in functions_list:
            returndata = open_function(rawData, master)
            if not returndata is None:
                break
        if returndata is None:
            return
        self['Time'] = returndata['Time']
        self['Values'] = returndata['Values']
        self.label = returndata.label
        self.timeDim = returndata.timeDim
        self.Overlay = returndata.Overlay

    def get_statistic(self):
        ret = DataFrame()

        predata = self['Values'].values[20:40]
        ret['start_value'] = [np.mean(predata)]

        ret['max'] = [np.max(self['Values'])]
        ret['min'] = [np.min(self['Values'])]
        ret['mean'] = [np.mean(self['Values'])]
        # ret['integral'] = [np.sum(self['Values']) * np.gradient(self['Time']).mean()]
        try:
            ret['integral'] = [np.sum(self['Values']) * np.gradient(self['Time']).mean()]
            ret['front50'] = [
                self['Time'][
                    np.min(np.nonzero(np.where(self['Values'] / self['Values'].max() > 0.5, self['Time'], 0)))]]
            ret['length10'] = [
                self['Time'][
                    np.max(np.nonzero(np.where(self['Values'] / self['Values'].max() > 0.2, self['Time'], 0)))] -
                self['Time'][np.min(np.nonzero(np.where(self['Values'] / self['Values'].max() > 0.1, self['Time'], 0)))]
            ]
        except:
            ret['front50'] = [0]
            ret['integral'] = [0]
        return ret
