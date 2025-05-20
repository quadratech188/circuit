import math
from typing import Callable, List
import numpy as np

from src.StateBuilder import StateBuilder
from src.Element import Element
from src.Common import Capacitor, VoltageSource, Resistor, Inductor
from src.Diode import Diode

def trapezoidal_step(dt: float, x: np.ndarray, G: np.ndarray, C: np.ndarray, b: np.ndarray):
    # Trapezoidal Rule
    # Gx + C dx/dt = b
    # G (x_1 + x_0) / 2 + C (x_1 - x_0) / dt = b
    # (G / 2 + C / dt) x_1 = b - (G / 2 - C / dt) x_0
    dividend = G / 2 + C / dt
    divisor = b - (G / 2 - C / dt) @ x

    return np.linalg.solve(dividend, divisor)

def gear2_step(dt: float, x_0: np.ndarray, x_1: np.ndarray, G: np.ndarray, C: np.ndarray, b: np.ndarray):
    # x_2 - 4/3 x_1 + 1/3 x_0 = 2/3 dt dx/dt
    # dx/dt = (3x_2 - 4x_1 + x_0) / 2dt

    # Gx_2 + C(3x_2 - 4x_1 + x_0) / 2dt = b
    # (G + 3C / 2dt)x_2 = b + C(4x_1 - x_0) / 2dt
    dividend = G + 3 * C / 2 / dt
    divisor = b + C @ (4 * x_1 - x_0) / 2 / dt

    return np.linalg.solve(dividend, divisor)

builder = StateBuilder(2)

I_s = 0.01
k = 10

elements: List[Element] = [
    VoltageSource(-1, 0, lambda t: math.sin(2 * math.pi * t)),
    Diode(0, 1, I_s, k),
    Capacitor(1, -1, 3),
    Resistor(1, -1, 1)
]

for element in elements:
    element.build(builder)

equation = builder.equation()

for element in elements:
    element.const_stamp(equation)

dt = 0.01

equation_copy = equation.copy()

x_prev = builder.state()

for element in elements:
    element.stamp(0, equation_copy, x_prev)

x = trapezoidal_step(dt, x_prev, equation_copy.G, equation_copy.C, equation_copy.b)

import matplotlib.pyplot as plt

history = []

for index in range(500):
    print(x)
    t = dt * index

    x_next = x.copy()

    i = 0
    while True:
        equation_copy = equation.copy()

        for element in elements:
            element.stamp(t, equation_copy, x_next)

        x_next_iter = gear2_step(dt, x_prev, x, equation_copy.G, equation_copy.C, equation_copy.b)

        if np.linalg.norm(x_next_iter - x_next) < 1e-6:
            break

        x_next = 0.5 * x_next_iter + 0.5 * x_next

        i += 1

        if i > 40:
            print("\033[33mFailed to converge after 40 iterations\033[97m")
            break

    x_prev = x
    x = x_next

    history.append(x)

import matplotlib.pyplot as plt

plt.plot(history)
plt.legend([str(k) for k in range(len(history))])
plt.show()
