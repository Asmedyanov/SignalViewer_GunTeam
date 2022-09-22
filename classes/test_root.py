from scipy import optimize as optima
import numpy as np

A = 2.0 * 1.0e2


def fun(x):
    print(f'x = {x}')
    ret = 1.5 * np.log(x) - A * np.power(x, 1.5)-2.4
    return ret


def jac(x):
    return (1.5 / x) - 1.5 * A * np.power(x, 0.5)


sol = optima.root(fun,10.0 , method='lm')
