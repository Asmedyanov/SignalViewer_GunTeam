import numpy as np
import matplotlib.pyplot as plt
dt = 0.1e-6
time = np.arange(0.125*1.0e6)*dt
phase0 = 1.5*np.pi*np.sin(2.0*np.pi*300.0*time)
#plt.plot(phase0,label='Начальная')
signal = 1.0+1.0-2.0*np.cos(phase0)
#plt.plot(signal,label='Сигнал')
signal = signal-np.min(signal)
phase = np.arccos(1.0 - (2.0 * signal / np.max(signal)))
#plt.plot(phase, label='Из сигнала')
plt.plot(np.gradient(phase), label='Поизводная сигнала')
unwrap_phase = np.unwrap(phase) / 2
#plt.plot(unwrap_phase+np.pi, label='Развернутая')
plt.legend()
plt.show()

