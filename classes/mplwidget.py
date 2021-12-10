# Matplotlib widget
from classes.mplcanvas import MplCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
import constants


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

    def plot(self, datalist, header=''):
        self.canvas.fig.clear()
        n = len(datalist)  # Длина массива баз данных каналов
        if (n == 0):
            return
        gs = self.canvas.fig.add_gridspec(n, hspace=0.05)
        axes = gs.subplots(sharex=True)  # массив графиков
        timescale = 'сек'
        try:
            data = datalist[0]
            timescale = data.timeDim
            axes.plot(data['T'] * constants.timeScaleDict[timescale], data['V'])
            axes.set_ylabel(data.label)  # Подписать вертикальные оси
            gun_team_axes_stile(axes)
            axes.set_xlabel(f't, {timescale}')
            # Подписать заголовок
            axes.set_title(f'Данные {header}')
        except:
            for i, data in enumerate(datalist):
                try:
                    timescale = data.timeDim
                    axes[i].plot(data['T'] * constants.timeScaleDict[timescale], data['V'])
                    axes[i].set_ylabel(data.label)  # Подписать вертикальные оси
                    gun_team_axes_stile(axes[i])
                except:
                    continue

            # Подписать горизонтальную ось
            axes[n - 1].set_xlabel(f't, {timescale}')
            # Подписать заголовок
            axes[0].set_title(f'Данные {header}')
        self.canvas.draw()
