import re
def addFile(file_name):
    print(file_name)
    short_file_name = file_name.split('/')[-1]
    numlist = re.findall(r'\d+', short_file_name)
    num = int(numlist[0])
    