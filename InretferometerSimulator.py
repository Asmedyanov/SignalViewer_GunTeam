import matplotlib.pyplot as plt
import numpy as np
from random import random
from scipy.fft import rfft, irfft, fftfreq, fft, ifft
import scipy.signal as ss

u1 = 3.0
u2 = 1.0
npoint = 1e5
dt = 0.1
t0 = -700.0
fgen = 3.0e2
tau0 = 1.0e6 / fgen
timeline = np.arange(npoint) * dt + t0
# fipiezo0 = random() * 2.0 * np.pi
fipiezo0 = 1.5 / 1.5
fipiezoA = 2.0 * np.pi
fipiezo = fipiezoA * np.sin(2 * np.pi * timeline / tau0 + fipiezo0)
tauplasma1 = 20.0
tauplasma2 = 30.0
tauplasma3 = 80.0
sigmaplasma1 = 10.0
sigmaplasma2 = 20.0
sigmaplasma3 = 10.0
Aplasma1 = np.pi * 15.0


# Aplasma2 = 1.5 * np.pi * 0.2
# Aplasma3 = 0.5 * np.pi * 0.2


def gauss(a, t0, s, t):
    return a * np.exp(-np.power((t - t0) / s, 2))


fplasma = gauss(Aplasma1, tauplasma1, sigmaplasma1, timeline)
''' + gauss(Aplasma2, tauplasma2, sigmaplasma2,
                                                                      timeline) + gauss(Aplasma3, tauplasma3,
                                                                                        sigmaplasma3, timeline)'''
fcom = fplasma + fipiezo
interfirence = u1 + u2 - 2.0 * np.power(u1 * u2, 0.5) * np.cos(fcom)
interfirence0 = interfirence

mininterf = interfirence.min()
interfirence = interfirence - mininterf
maxinterf = interfirence.max()
faseafter = np.arccos(1.0 - (2.0 * interfirence / maxinterf))
pic_max = faseafter.max() - faseafter.min()
pic_array_raw = \
    ss.find_peaks(-faseafter, prominence=[0.1 * pic_max, pic_max])[0]

pic_array_visinity = []
visinity = 0.5
for k in pic_array_raw:
    if faseafter[k] < visinity:
        pic_array_visinity.append(k)
pic_array_raw_time = timeline[pic_array_visinity]
pic_array_raw_value = faseafter[pic_array_visinity]

revers_t = []
for tk in pic_array_raw_time:
    if (tk > 0) and (tk < 100.0):
        revers_t.append(tk)

pic_array_raw_pi = \
    ss.find_peaks(faseafter, prominence=[0.01 * pic_max, pic_max])[0]

pic_array_visinity = []
visinity = 0.5
for k in pic_array_raw_pi:
    if faseafter[k] > np.pi - visinity:
        pic_array_visinity.append(k)
pic_array_raw_time = timeline[pic_array_visinity]
pic_array_raw_value = faseafter[pic_array_visinity]

revers_t_pi = []
for tk in pic_array_raw_time:
    if (tk > 0) and (tk < 100.0):
        revers_t_pi.append(tk)

fstart = 30.0 * fgen
ffinish = 1.0e7
f_signal = rfft(interfirence)
W = fftfreq(f_signal.size, d=dt * 1.0e-6)[:int(f_signal.size)]
cut_f_signal = f_signal.copy()
fend = ffinish
# fw = 1428.5714285714287 * 4
fw = fstart / 30
fwindow = np.exp(-np.power((W - fstart) / fw, 2)) + np.exp(-np.power((W - fend) / fw, 2))
fwindow = fwindow / np.max(fwindow)
fwindow = np.where(((np.abs(W) >= fstart) & (np.abs(W) <= fend)), 1, fwindow)
# fwindow = np.where(((np.abs(W) >= fstart) & (np.abs(W) <= fend)), 1, 0)
cut_signal = irfft(cut_f_signal * fwindow)
# faseafter_cut= np.arccos(1.0 - (2.0 * cut_signal / maxinterf))
cut_time = timeline[:cut_signal.size]

xaxis = timeline
yaxis = interfirence
fig, axes = plt.subplots(5, sharex=True)
axes[0].plot(xaxis, fplasma)
axes[0].set_ylabel('Пр-ль\nп-мы')
axes[1].plot(xaxis, interfirence0)
axes[1].set_ylabel('Пок-я\nф.д-ра')
axes[2].plot(xaxis, faseafter)
axes[2].set_ylabel('Обр-ая\nинф-ция')
axes[2].plot(pic_array_raw_time, pic_array_raw_value, 'ro')
'''for n in np.arange(20.0,30.0,1.0):
    fstart = fgen*n
    ffinish = 1.0e7
    f_signal = rfft(interfirence)
    W = fftfreq(f_signal.size, d=dt * 1.0e-6)[:int(f_signal.size)]
    cut_f_signal = f_signal.copy()
    fend = ffinish
    # fw = 1428.5714285714287 * 4
    fw = fstart / 30
    fwindow = np.exp(-np.power((W - fstart) / fw, 2)) + np.exp(-np.power((W - fend) / fw, 2))
    fwindow = fwindow / np.max(fwindow)
    fwindow = np.where(((np.abs(W) >= fstart) & (np.abs(W) <= fend)), 1, fwindow)
    # fwindow = np.where(((np.abs(W) >= fstart) & (np.abs(W) <= fend)), 1, 0)
    cut_signal = irfft(cut_f_signal * fwindow)
    # faseafter_cut= np.arccos(1.0 - (2.0 * cut_signal / maxinterf))
    cut_time = timeline[:cut_signal.size]
    axes[3].plot(cut_time, cut_signal,label=f'fstart = {n} * fgen')
    axes[3].legend()'''
nfur = 100 * len(faseafter)
f_signal = rfft(faseafter, n=nfur)
W = fftfreq(f_signal.size, d=dt * 1.0e-6)[:int(f_signal.size)]
cut_f_signal = f_signal.copy()
# print(W[200])
f_reg = 2.0 * np.pi * fgen  # W[np.argmax(f_signal[200:])]
fw = f_reg * 4
print(fw)
fwindow = np.exp(-np.power((W) / fw, 2))
for n in range(1, 4):
    fwindow += np.exp(-np.power((W - f_reg * n) / fw, 2))
fwindow += np.exp(-np.power((W - f_reg * 0.5) / fw, 2))

fwindow = 1.0 - (fwindow / fwindow.max())
# fwindow = fwindow / np.max(fwindow)
# fwindow = np.where(((np.abs(W) >= fstart) & (np.abs(W) <= fend)), 1, fwindow)
# fwindow = np.where(((np.abs(W) >= fstart) & (np.abs(W) <= fend)), 1, 0)
cut_signal = irfft(cut_f_signal * fwindow)[:interfirence.size]
faseafter_cut = np.arccos(1.0 + (2.0 * (cut_signal - mininterf) / maxinterf))
cut_time = timeline[:cut_signal.size]
axes[3].plot(cut_time, cut_signal)
axes[3].set_ylabel('Ф-ая\nобр-ая\nинт-я')


# axes[4].plot(cut_time, faseafter_cut)
def find_nearest(a, value):
    a_val = np.abs(a - value)
    return a_val.argmin()


new_fase = cut_signal
if len(revers_t) % 2 == 0:
    while len(revers_t) > 0:
        n_left = find_nearest(cut_time, revers_t[0])
        n_right = find_nearest(cut_time, revers_t[-1])
        new_fase = np.where(
            (cut_time > cut_time[n_left]) & (cut_time < cut_time[n_right]),
            2 * min([new_fase[n_left], new_fase[n_right]]) - new_fase, new_fase)
        revers_t = revers_t[1:-1]

if len(revers_t_pi) % 2 == 0:
    while len(revers_t_pi) > 0:
        n_left = find_nearest(cut_time, revers_t_pi[0])
        n_right = find_nearest(cut_time, revers_t_pi[-1])
        revers_n = n_left
        if abs(new_fase[n_left]) < abs(new_fase[n_right]):
            revers_n = n_right
        new_fase = np.where(
            (cut_time > cut_time[n_left]) & (cut_time < cut_time[n_right]),
            2 * new_fase[revers_n] - new_fase, new_fase)
        revers_t_pi = revers_t_pi[1:-1]

if np.abs(new_fase.min())>np.abs(new_fase.max()):
    new_fase =-new_fase

axes[4].plot(cut_time, new_fase)
axes[4].set_ylabel('Развер\nф-ая\nобр.\nинтерф')

axes[0].set_title('Пример обработки на идеальном интерферометре')
axes[-1].set_xlabel('t, мкс')
# plt.ylabel('interfirence')
plt.show()
