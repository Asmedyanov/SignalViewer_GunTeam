from inspect import getmembers, isfunction
from functions import rawdatafunctions


def addFile(file_name, master):
    functions_list = [o[1] for o in getmembers(rawdatafunctions) if
                      (isfunction(o[1]) and (o[0].split('_')[0] == 'Open'))]
    for open_function in functions_list:
        returnlist = open_function(file_name, master)
        if not returnlist is None:
            return returnlist
    return []
