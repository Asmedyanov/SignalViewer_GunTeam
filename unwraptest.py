import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import rfft, irfft, fftfreq, fft, ifft
from scipy.signal import argrelextrema, find_peaks, butter, filtfilt, peak_prominences

dt = 0.1e-6
time = np.arange(0.125 * 1.0e6) * dt
phase0 = 2.1 * np.pi * np.sin(2.0 * np.pi * 300.0 * time)
plt.plot(time, phase0, label='Начальная')
signal = 1.0 + 1.0 - 2.0 * np.cos(phase0)
fmax = 1.0e7
df = 5.0
nfreq = int(fmax / df)
signal_f = fft(signal, n=nfreq)
# signal_f = fft(signal)
W = fftfreq(signal_f.size, d=dt)[:int(signal_f.size)]
signal_f_cut = np.where(W > 100.0, signal_f, 0)

signal_if = ifft(signal_f_cut)[:signal.size]

# plt.plot(W, np.real(signal_f), label='Re')
# plt.plot(W, np.imag(signal_f), label='Im')
Re = np.real(signal_if)
Im = np.imag(signal_if)
rebuild_phase = np.where((Im > 0) & (Re > 0), np.arctan(Im / Re), 0)
rebuild_phase = np.where((Im > 0) & (Re < 0), np.arctan(Im / Re) + np.pi, rebuild_phase)
rebuild_phase = np.where((Im < 0) & (Re < 0), np.arctan(Im / Re) - np.pi, rebuild_phase)
rebuild_phase = np.where((Im < 0) & (Re > 0), np.arctan(Im / Re), rebuild_phase)
#plt.plot(time, rebuild_phase, label='Восстановленная')
g_phase = -np.gradient(rebuild_phase)
pi_pics = find_peaks(g_phase, prominence=3.0, distance=30)[0]
u_phase = rebuild_phase
r = 1
for index, i in enumerate(pi_pics):
    u_phase = np.where(time > time[i - 2], -u_phase * r, u_phase)
    r = -r
# plt.plot(phase, label='Из сигнала')
# plt.plot(np.gradient(phase), label='Поизводная сигнала')
unwrap_phase = np.unwrap(rebuild_phase)
dev = np.pi
# plt.plot(time, dev * (np.round(unwrap_phase / dev)), label='Развернутая pi')
# plt.plot(time, unwrap_phase, label='Развернутая')
plt.plot(time, np.unwrap(u_phase), label='Развернутая')
# plt.plot(time, unwrap_phase - dev * (np.round(unwrap_phase / dev)), label='Развернутая Вычет')
plt.legend()
plt.show()
