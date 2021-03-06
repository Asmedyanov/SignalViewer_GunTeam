# Matplotlib widget
import numpy as np

from classes.mplwidget import *

import constants

from functions.mymathfunctions import *
from scipy import ndimage


class MplWidget_teacher(MplWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent, teacher=True)
        self.left_pics_pi = []
        self.right_pics_pi = []
        self.left_pics_0 = []
        self.right_pics_0 = []

    def get_marks_pi(self):
        ret = self.pic_pi_prop
        ret['pic_time'] = self.pics_time_pi
        ret['marks'] = self.marks_pi
        return ret

    def get_marks_0(self):
        ret = self.pic_0_prop
        ret['pic_time'] = self.pics_time_0
        ret['marks'] = self.marks_0
        return ret

    def plot_picks(self, datalist, header='', style='-'):

        self.canvas.fig.clear()
        n = len(datalist)
        if (n == 0):
            return
        gs = self.canvas.fig.add_gridspec(n, hspace=0.05)
        self.axes = gs.subplots(sharex=True)  # массив графиков
        if n == 1:
            data = datalist[0]
            timescale = data.timeDim
            timemult = constants.timeScaleDict[timescale]
            self.signal = data['Values']

            self.time = data['Time'] * timemult
            self.axes.plot(self.time, self.signal, style)
            env_signal_max = ndimage.maximum_filter1d(self.signal, size=3)
            self.axes.plot(self.time, env_signal_max, style)
            pics = my_find_pics(-data['Values'])
            self.pic_0_prop = pics[1]
            # print(f'разница баз 0 пиков\n {pics[1]["right_bases"] - pics[1]["left_bases"]}')
            pics_indexes = pics[0]
            self.pics_indexes_0 = pics_indexes

            pics_time = data['Time'].values[pics_indexes] * timemult
            self.pics_time_0 = pics_time
            self.pics_prominences_0 = pics[1]['prominences']
            self.pics_widths_0 = pics[1]['widths']
            self.pics_width_heights_0 = pics[1]['width_heights']
            pics_values = data['Values'].values[pics_indexes]
            # self.axes.plot(pics_time, pics_values, 'o')
            self.checklist_0 = []
            for i, j in enumerate(pics_indexes):
                outputstring = f'{i}'
                xy = (pics_time[i], pics_values[i])
                xytext = (pics_time[i], pics_values[i] - 0.1)
                annotation = self.axes.annotate(outputstring,
                                                xy=xy, xycoords='data',
                                                xytext=xytext, textcoords='data',
                                                arrowprops=dict(arrowstyle="-|>",
                                                                connectionstyle="arc3"),
                                                bbox=dict(
                                                    boxstyle="round", fc="w"), picker=True
                                                )
                annotation.litera = '0'
                self.checklist_0.append(annotation)
            self.marks_0 = np.zeros(len(self.checklist_0))
            pics = my_find_pics(data['Values'])
            self.pic_pi_prop = pics[1]
            # print(f'разница баз Пи пиков\n {pics[1]["right_bases"] - pics[1]["left_bases"]}')
            pics_indexes = pics[0]
            self.pics_indexes_pi = pics_indexes

            pics_time = data['Time'].values[pics_indexes] * timemult
            self.pics_time_pi = pics_time
            self.pics_prominences_pi = pics[1]['prominences']
            self.pics_widths_pi = pics[1]['widths']
            self.pics_width_heights_pi = pics[1]['width_heights']
            pics_values = data['Values'].values[pics_indexes]
            self.checklist_pi = []
            for i, j in enumerate(pics_indexes):
                outputstring = f'{i}'
                xy = (pics_time[i], pics_values[i])
                xytext = (pics_time[i], pics_values[i] + 0.1)
                annotation = self.axes.annotate(outputstring,
                                                xy=xy, xycoords='data',
                                                xytext=xytext, textcoords='data',
                                                arrowprops=dict(arrowstyle="-|>",
                                                                connectionstyle="arc3"),
                                                bbox=dict(
                                                    boxstyle="round", fc="w"), picker=True
                                                )
                annotation.litera = 'pi'
                self.checklist_pi.append(annotation)

            self.marks_pi = np.zeros(len(self.checklist_pi))
            self.canvas.ActivateAnnotations()
            pics_all = np.concatenate([self.pics_time_0, self.pics_time_pi])
            pics_all = np.sort(pics_all)
            if (pics_all[0] in self.pics_time_0) and (pics_all[-1] in self.pics_time_pi):
                base_dif_0 = self.pic_0_prop["right_bases"][0] - self.pic_0_prop["left_bases"][0]
                base_dif_pi = self.pic_pi_prop["right_bases"][-1] - self.pic_pi_prop["left_bases"][-1]
                if base_dif_0 > base_dif_pi:
                    self.pics_indexes_0 = np.delete(self.pics_indexes_0, 0)
                else:
                    self.pics_indexes_pi = np.delete(self.pics_indexes_pi, -1)

            elif (pics_all[0] in self.pics_time_pi) and (pics_all[-1] in self.pics_time_0):
                base_dif_0 = self.pic_0_prop["right_bases"][-1] - self.pic_0_prop["left_bases"][-1]
                base_dif_pi = self.pic_pi_prop["right_bases"][0] - self.pic_pi_prop["left_bases"][0]
                if base_dif_0 > base_dif_pi:
                    self.pics_indexes_0 = np.delete(self.pics_indexes_0, -1)
                else:
                    self.pics_indexes_pi = np.delete(self.pics_indexes_pi, 0)
            pics_time_0 = data['Time'].values[self.pics_indexes_0] * timemult
            pics_values_0 = data['Values'].values[self.pics_indexes_0]
            pics_time_pi = data['Time'].values[self.pics_indexes_pi] * timemult
            pics_values_pi = data['Values'].values[self.pics_indexes_pi]
            self.axes.plot(pics_time_0, pics_values_0, 'o')
            self.axes.plot(pics_time_pi, pics_values_pi, 'o')
            self.axes.set_ylabel(data.label)  # Подписать вертикальные оси
            gun_team_axes_stile(self.axes)

            # Подписать горизонтальную ось
            self.axes.set_xlabel(f't, {timescale}')
            # Подписать заголовок
            self.axes.set_title(f'{header}')
            self.canvas.draw()

    def revers_signal(self, litera='0'):
        if litera == '0':
            if len(self.left_pics_0) == 0 or len(self.right_pics_0) == 0:
                return
        if litera == 'pi':
            if len(self.left_pics_pi) == 0 or len(self.right_pics_pi) == 0:
                return
        if litera == '0':
            left_time = self.left_pics_0[-1]
            right_time = self.right_pics_0[-1]

        if litera == 'pi':
            left_time = self.left_pics_pi[-1]
            right_time = self.right_pics_pi[-1]
        n_left = find_nearest(self.time, left_time)
        n_right = find_nearest(self.time, right_time)
        curvness_left = self.signal[n_left - 1] - 2.0 * self.signal[n_left] + self.signal[n_left + 1]
        curvness_right = self.signal[n_right - 1] - 2.0 * self.signal[n_right] + self.signal[n_right + 1]
        if curvness_left < 0 and curvness_right < 0:
            rev_value = max([self.signal[n_left], self.signal[n_right]])
        if curvness_left > 0 and curvness_right > 0:
            rev_value = min([self.signal[n_left], self.signal[n_right]])
        self.signal = np.where(((self.time > left_time) & (self.time < right_time)), 2 * rev_value - self.signal,
                               self.signal)
        self.axes.plot(self.time, self.signal)
        self.canvas.draw()
