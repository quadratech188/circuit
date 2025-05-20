import math
from typing import Callable, List
import numpy as np

class StateBuilder:
    def __init__(self, n: int):
        self.n = n
        self.total = n

    def add_variable(self):
        self.total += 1
        return self.total - 1

    def size(self):
        return self.total


class Element:
    def __init__(self, i: int, j: int):
        self.i = i
        self.j = j

    def build(self, state: StateBuilder):
        pass
    
    def stamp_matrices(self, G: np.ndarray, C: np.ndarray):
        pass

    def stamp_source(self, t: float, source: np.ndarray):
        pass


class VoltageSource(Element):
    def __init__(self, i: int, j: int, V: Callable[[float], float]):
        super().__init__(i, j)
        self.V = V

    def build(self, state: StateBuilder):
        self.idx = state.add_variable()

    def stamp_matrices(self, G: np.ndarray, C: np.ndarray):
        if self.i != -1:
            # Add current contributions
            G[self.i, self.idx] -= 1 # 0 = ... - I_i + ...

            # Constrain voltage difference
            G[self.idx, self.i] -= 1 # V_e = ... - V_i + ...

        if self.j != -1:
            G[self.j, self.idx] += 1 # 0 = ... + I_j + ...

            G[self.idx, self.j] += 1 # V_e = ... + V_j + ...

    def stamp_source(self, t: float, source: np.ndarray):
        source[self.idx] = self.V(t)

class Resistor(Element):
    def __init__(self, i: int, j: int, R: float):
        super().__init__(i, j);
        self.R = R

    def stamp_matrices(self, G: np.ndarray, C: np.ndarray):
        inv = 1 / self.R
        if self.i != -1:
            G[self.i, self.i] -= inv # I_i = ... - V_i / R + ...
        if self.j != -1:
            G[self.j, self.j] -= inv # I_j = ... - V_j / R + ...

        if self.i != -1 and self.j != -1:
            G[self.i, self.j] += inv # I_i = ... + V_j / R + ...
            G[self.j, self.i] += inv # I_j = ... + V_i / R + ...


class Capacitor(Element):
    def __init__(self, i: int, j: int, C: float):
        super().__init__(i, j)
        self.C = C

    def stamp_matrices(self, G: np.ndarray, C: np.ndarray):
        if self.i != -1:
            C[self.i, self.i] -= self.C # I_i = ... - C * dV_i/dt + ...
        if self.j != -1:
            C[self.j, self.j] -= self.C # I_j = ... - C * dV_j/dt + ...

        if self.i != -1 and self.j != -1:
            C[self.i, self.j] += self.C # I_i = ... + C * dV_j/dt + ...
            C[self.j, self.i] += self.C # I_j = ... + C * dV_i/dt + ...


class Inductor(Element):
    def __init__(self, i: int, j: int, L: float):
        super().__init__(i, j)
        self.L = L

    def build(self, state: StateBuilder):
        self.idx = state.add_variable()

    def stamp_matrices(self, G: np.ndarray, C: np.ndarray):
        if self.i != -1:
            G[self.i, self.idx] = -1 # 0 = ... - I_L + ...
            G[self.idx, self.i] = 1 # L dI_L/dt = ... + V_i + ...
        if self.j != -1:
            G[self.j, self.idx] = 1 # 0 = ... + I_L + ...
            G[self.idx, self.j] = -1 # L dI_L/dt = ... - V_j + ...

        C[self.idx, self.idx] = - self.L

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

state = StateBuilder(4)

elements: List[Element] = [
    VoltageSource(-1, 0, lambda t: 1),
    Resistor(0, 1, 1),
    Inductor(1, -1, 1),
    VoltageSource(-1, 2, lambda t: 2),
    Resistor(2, 3, 1),
    Inductor(3, -1, 1),
]

for element in elements:
    element.build(state)

G = np.zeros((state.size(), state.size()))
C = np.zeros((state.size(), state.size()))

for element in elements:
    element.stamp_matrices(G, C)

print(G)
print(C)

dt = 0.01


x_prev = np.zeros(state.size())

b = np.zeros(state.size())
for element in elements:
    element.stamp_source(0, b)

x = trapezoidal_step(dt, x_prev, G, C, b)

import matplotlib.pyplot as plt

history = []

for index in range(100):
    print(x)
    t = dt * index

    for element in elements:
        element.stamp_source(t, b)

    x_next = gear2_step(dt, x_prev, x, G, C, b)

    x_prev = x
    x = x_next

    history.append(x)

plt.plot(history)
plt.legend(['V0 Voltage', 'V1 Voltage', 'V2 Voltage', 'V3 Voltage', 'V0 current', 'V2 current', 'V1 current', 'V3 current'])
plt.show()
