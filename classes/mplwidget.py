# Matplotlib widget
import numpy as np

from classes.mplcanvas import MplCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMenu, QCheckBox
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.widgets import CheckButtons
import constants
from scipy.signal import find_peaks


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
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)  # Inherit from QWidget
        self.canvas = MplCanvas()  # Create canvas object
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
                        timescale = 'сек'
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
            axes[0].set_title(f'Данные {header}')
        self.canvas.draw()

    def get_marks(self):
        mark_array = np.zeros(len(self.pics_time))

        for i, annotation in enumerate(self.checklist):
            try:
                mark_array[i] = annotation.clicked
            except:
                pass

        return {'pict': self.pics_time, 'marks': mark_array}

    def plot_pick_pi(self, datalist, header='', style='-'):
        self.canvas.fig.clear()
        n = len(datalist)
        if (n == 0):
            return
        gs = self.canvas.fig.add_gridspec(n, hspace=0.05)
        axes = gs.subplots(sharex=True)  # массив графиков
        timescale = 'сек'
        if n == 1:
            data = datalist[0]
            timescale = data.timeDim
            timemult = constants.timeScaleDict[timescale]
            axes.plot(data['Time'] * timemult, data['Values'], style)
            pics = find_peaks(data['Values'])
            pics_indexes = pics[0]

            pics_time = data['Time'].values[pics_indexes] * timemult
            self.pics_time = pics_time
            pics_values = data['Values'].values[pics_indexes]
            self.checklist = []
            for i, j in enumerate(pics_indexes):
                self.outputstring = f'{i}'
                self.xy = (pics_time[i], pics_values[i])
                self.xytext = (pics_time[i], pics_values[i] + 0.2)
                annotation = axes.annotate(self.outputstring,
                                           xy=self.xy, xycoords='data',
                                           xytext=self.xytext, textcoords='data',
                                           arrowprops=dict(arrowstyle="-|>",
                                                           connectionstyle="arc3"),
                                           bbox=dict(
                                               boxstyle="round", fc="w"), picker=True
                                           )

                self.checklist.append(annotation)
            self.canvas.ActivateAnnotations()
            axes.plot(pics_time, pics_values, 'o')
            axes.set_ylabel(data.label)  # Подписать вертикальные оси
            gun_team_axes_stile(axes)

            # Подписать горизонтальную ось
            axes.set_xlabel(f't, {timescale}')
            # Подписать заголовок
            axes.set_title(f'{header}')
            self.canvas.draw()
            return
        for i, data in enumerate(datalist):
            timescale = data.timeDim
            timemult = constants.timeScaleDict[timescale]
            axes[i].plot(data['Time'] * timemult, data['Values'], style)
            axes[i].set_ylabel(data.label)  # Подписать вертикальные оси
            gun_team_axes_stile(axes[i])

            # Подписать горизонтальную ось
            axes[n - 1].set_xlabel(f't, {timescale}')
            # Подписать заголовок
            axes[0].set_title(f'Данные {header}')
        self.canvas.draw()
