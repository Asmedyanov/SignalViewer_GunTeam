default_file = './experiment_templates/default.xml'
experiments_dir = './Examples'
filter_list = [
    'Любые файлы (*.*)',
    'АЦП Хильченко(*.bin)',
    'Дистанционный АКИП(A*.CSV)',
    'Старый Тектроникс (F*\d.CSV)',
    'Лекрой (*.PRN)',
    'Дистанционный АКИП (INT*.CSV)',
    'Старый Тектроникс (tek*.csv)'
]
timeScaleDict = {
    'сек': 1.0,
    'мс': 1.0e3,
    'мкс': 1.0e6,
}
pic_parameters = [
    #'peak_heights',
    'left_thresholds',
    #'right_thresholds',
    'prominences',
    #'left_bases',
    #'right_bases',
    #'widths',
    #'width_heights',
    #'left_ips',
    #'right_ips',
    #'pic_time'
]

pic_parameters_all = [

    'left_thresholds',
    'right_thresholds',
    'prominences',
    'left_bases',
    'right_bases',
    'widths',
    'width_heights',
    'left_ips',
    'right_ips',
    'pic_time'
]
