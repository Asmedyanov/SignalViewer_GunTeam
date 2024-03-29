# Matplotlib widget
import numpy as np

from classes.mplcanvas import MplCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMenu, QCheckBox
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.widgets import CheckButtons
import constants
from scipy.signal import find_peaks
from classes.mplcanvas_teacher import MplCanvas_teacher
from scipy import ndimage
import functions.mymathfunctions as mymathfunctions


def gun_team_axes_stile(axis):
    # Включить вспомогательные засечки на шкалах
    axis.minorticks_on()

    #  Определяем внешний вид линий основной сетки:
    axis.grid(
        which='major',  # Основная сетка
        color='k',  # цвет сетки
        linewidth=1)  # Ширина линии сетки
    #  Определяем внешний вид линий вспомогательной сетки:
    axis.grid(
        which='minor',  # Вспомогрательная сетка
        color='k',  # Цвет сетки
        linestyle=':')  # Пунктирный стиль
    axis.tick_params(direction='in', top=True, right=True)
    axis.ticklabel_format(style='sci')


class MplWidget(QWidget):
    def __init__(self, parent=None,teacher=False):
        QWidget.__init__(self, parent)  # Inherit from QWidget
        if teacher:
            self.canvas = MplCanvas_teacher()  # Create canvas object
        else:
            self.canvas = MplCanvas()
        self.vbl = QVBoxLayout()  # Set box for plotting
        self.vbl.addWidget(self.canvas)
        self.vbl.addWidget(NavigationToolbar2QT(self.canvas, self))
        self.setLayout(self.vbl)

    def plot(self, datalist, header='', style='-'):
        self.canvas.fig.clear()
        overlaylist = []
        seriallist = []
        for data in datalist:
            try:
                Overlay = data.Overlay
                if data.Overlay == '0':
                    seriallist.append(data)
                else:
                    overlaylist.append(data)
            except:
                seriallist.append(data)
        n = len(seriallist)
        if len(overlaylist) != 0:
            n += 1
        if (n == 0):
            return
        gs = self.canvas.fig.add_gridspec(n, hspace=0.05)
        axes = gs.subplots(sharex=True)  # массив графиков
        timescale = 'сек'
        if n == 1:
            for data in datalist:
                try:
                    timescale = data.timeDim
                except:
                    timescale = 'сек'
                try:
                    timemult = constants.timeScaleDict[timescale]
                except:
                    timemult = 1
                axes.plot(data['Time'] * timemult, data['Values'], style, label=data.label)
                #pics_index = mymathfunctions.my_find_pics(data['Values'].values)[0]
                #pics_time = (data['Time'].values * timemult)[pics_index]
                #pics_val = data['Values'].values[pics_index]
                #axes.plot(pics_time, pics_val,'o')
                #pics_index = mymathfunctions.my_find_pics(-data['Values'].values)[0]
                #pics_time = (data['Time'].values * timemult)[pics_index]
                #pics_val = data['Values'].values[pics_index]
                #axes.plot(pics_time, pics_val, 'o')
                # axes.set_ylabel(data.label)  # Подписать вертикальные оси
            gun_team_axes_stile(axes)
            axes.set_xlabel(f't, {timescale}')
            axes.legend()
            # Подписать заголовок
            axes.set_title(f'Данные {header}')
        else:
            for i, data in enumerate(seriallist):
                try:
                    try:
                        timescale = data.timeDim
                    except:
                        timescale = 'сек'
                    try:
                        timemult = constants.timeScaleDict[timescale]
                    except:
                        timemult = 1
                    axes[i].plot(data['Time'] * timemult, data['Values'], style)

                    axes[i].set_ylabel(data.label)  # Подписать вертикальные оси
                    gun_team_axes_stile(axes[i])
                except:
                    continue
            for i, data in enumerate(overlaylist):
                try:
                    try:
                        timescale = data.timeDim
                    except:
                        timescale = 's'
                    axes[n - 1].plot(data['Time'] * constants.timeScaleDict[timescale], data['Values'],
                                     label=f'{data.label}')
                    axes[n - 1].set_ylabel(data.label)
                    axes[n - 1].legend()  # Подписать вертикальные оси
                    gun_team_axes_stile(axes[n - 1])
                except:
                    continue

            # Подписать горизонтальную ось
            axes[n - 1].set_xlabel(f't, {timescale}')
            # Подписать заголовок
            #axes[0].set_title(f'Данные {header}')
        self.canvas.draw()

