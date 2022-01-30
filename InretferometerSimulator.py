import matplotlib.pyplot as plt
import numpy as np
from random import random
from scipy.fft import rfft, irfft, fftfreq, fft, ifft

u1 = 3.0
u2 = 1.0
npoint = 1e5
dt = 0.1
t0 = -700.0
fgen = 3.0e2
tau0 = 1.0e6 / fgen
timeline = np.arange(npoint) * dt + t0
#fipiezo0 = random() * 2.0 * np.pi
fipiezo0 = 1.5/2
fipiezoA = 2.0 * np.pi
fipiezo = fipiezoA * np.sin(2 * np.pi * timeline / tau0 + fipiezo0)
tauplasma1 = 20.0
tauplasma2 = 30.0
tauplasma3 = 80.0
sigmaplasma1 = 10.0
sigmaplasma2 = 20.0
sigmaplasma3 = 10.0
Aplasma1 = np.pi * 1.0


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

fstart = 16*fgen
ffinish = 1.0e7
f_signal = rfft(interfirence)
W = fftfreq(f_signal.size, d=dt*1.0e-6)[:int(f_signal.size)]
cut_f_signal = f_signal.copy()
fend = ffinish
#fw = 1428.5714285714287 * 4
fw = fstart/30
fwindow = np.exp(-np.power((W - fstart) / fw, 2)) + np.exp(-np.power((W - fend) / fw, 2))
fwindow = fwindow/np.max(fwindow)
fwindow = np.where(((np.abs(W) >= fstart) & (np.abs(W) <= fend)), 1, fwindow)
#fwindow = np.where(((np.abs(W) >= fstart) & (np.abs(W) <= fend)), 1, 0)
cut_signal = irfft(cut_f_signal * fwindow)
faseafter_cut= np.arccos(1.0 - (2.0 * cut_signal / maxinterf))
cut_time = timeline[:cut_signal.size]

xaxis = timeline
yaxis = interfirence
fig, axes = plt.subplots(4, sharex=True)
axes[0].plot(xaxis, fplasma)
axes[1].plot(xaxis, interfirence0)
axes[2].plot(xaxis, faseafter)
axes[3].plot(cut_time, faseafter_cut)
plt.ylabel('interfirence')
plt.show()
