import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import rfft, irfft, fftfreq, fft, ifft
from scipy.signal import argrelextrema, find_peaks, butter, filtfilt, peak_prominences

dt = 0.1e-6
time = np.arange(0.125 * 1.0e6) * dt
phase0 = 1.5 * np.pi * np.sin(2.0 * np.pi * 300.0 * time)

t0 = 6.0e3 * 1.0e-6
sigma = 30.0 * 1.0e-6
ampl = np.pi * 2.0

phase1 = ampl * np.exp(-np.power((time - t0) / sigma,2))

phase0 = phase0 + phase1
signal = 1.0 + 1.0 - 2.0 * np.cos(phase0)
plt.subplot(4, 1, 1)
plt.plot(time, signal, label='Интерферограмма')
plt.legend()
fmax = 1.0e7
df = 3.0
nfreq = int(fmax / df)
# signal_f = fft(signal, n=nfreq)

signal_f = fft(signal)
W = fftfreq(signal_f.size, d=dt)[:int(signal_f.size)]

Re_f = np.real(signal_f)
Im_f = np.imag(signal_f)
#plt.subplot(4, 1, 1)
#plt.plot(W, Re_f, label='Спектр Re')
#plt.plot(W, Im_f, label='Спектр Im')
#plt.legend()

signal_f_cut = np.where(W > 200.0, signal_f, 0)

signal_if = ifft(signal_f_cut)[:signal.size]
Re = np.real(signal_if)
Im = np.imag(signal_if)
Re_abs = np.abs(np.real(signal_if))
Im_abs = np.abs(np.imag(signal_if))
atan = np.arctan(Im_abs / Re_abs)

rebuild_phase = np.where((Im > 0) & (Re > 0), atan, 0)
rebuild_phase = np.where((Im > 0) & (Re < 0), np.pi - atan, rebuild_phase)
rebuild_phase = np.where((Im < 0) & (Re < 0), -np.pi + atan, rebuild_phase)
rebuild_phase = np.where((Im < 0) & (Re > 0), - atan, rebuild_phase)
plt.subplot(4, 1, 2)
plt.plot(time[np.nonzero(((Im > 0) & (Re > 0)))], rebuild_phase[np.nonzero(((Im > 0) & (Re > 0)))], 'o', label='I')
plt.plot(time[np.nonzero(((Im > 0) & (Re < 0)))], rebuild_phase[np.nonzero(((Im > 0) & (Re < 0)))], 'o', label='II')
plt.plot(time[np.nonzero(((Im < 0) & (Re < 0)))], rebuild_phase[np.nonzero(((Im < 0) & (Re < 0)))], 'o', label='III')
plt.plot(time[np.nonzero(((Im < 0) & (Re > 0)))], rebuild_phase[np.nonzero(((Im < 0) & (Re > 0)))], 'o', label='IV')
plt.legend()

g_phase = -np.gradient(rebuild_phase)
pi_pics = find_peaks(g_phase, prominence=3.0, distance=30)[0]
u_phase = rebuild_phase
r = 1
for index, i in enumerate(pi_pics):
    if index%2==0:
        u_phase = np.where(time > time[i], u_phase * r, u_phase)
        r=-r
plt.subplot(4, 1, 3)
plt.plot(time, u_phase,'o', label='Начальная')

# plt.plot(phase, label='Из сигнала')
# plt.plot(np.gradient(phase), label='Поизводная сигнала')
unwrap_phase = np.unwrap(rebuild_phase)
dev = np.pi
# plt.plot(time, dev * (np.round(unwrap_phase / dev)), label='Развернутая pi')
# plt.plot(time, unwrap_phase, label='Развернутая')
plt.subplot(4, 1, 4)
plt.plot(time, phase0, label='Начальная')
plt.plot(time, np.unwrap(u_phase), label='Развернутая')
# plt.plot(time, unwrap_phase - dev * (np.round(unwrap_phase / dev)), label='Развернутая Вычет')
plt.legend()
plt.show()
