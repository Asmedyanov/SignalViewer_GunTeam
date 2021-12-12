import matplotlib.pyplot as plt
import numpy as np


def exppolinom(t, n, a, sigma, tau):
    sum = 0
    for m in range(n):
        sum += a[m]*np.exp(-np.power((t - tau[m]), 2.0) / sigma[m])
    return sum


x = np.arange(0.0, 100.0, 0.1)

n = 2
a = [4.0, 1.0]
sigma = [10.0, 10.0]
tau = [20.0, 60.0]
y = np.array([np.arccos(np.cos(exppolinom(t, n, a, sigma, tau)))
              for t in x])

plt.plot(x, y)
plt.show()
