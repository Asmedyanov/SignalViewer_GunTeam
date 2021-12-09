from pandas import DataFrame
from functions import diagnosticdatafunctions
import numpy as np
from inspect import getmembers, isfunction


class DiagnosticData(DataFrame):
    def __init__(self, rawData,master):
        super(DiagnosticData, self).__init__()
        functions_list = [o[1] for o in getmembers(diagnosticdatafunctions) if
                          (isfunction(o[1]) and (o[0].split('_')[0] == 'Diagnostic'))]
        for open_function in functions_list:
            returndata = open_function(rawData, master)
            if not returndata is None:
                break
        if returndata is None:
            return
        self['T'] = returndata['T']
        self['V'] = returndata['V']
        self.label = returndata.label