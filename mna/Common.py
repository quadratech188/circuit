import numpy as np
from typing import Callable

from mna.Element import Element
from mna.State import Equation
from mna.StateBuilder import StateBuilder

class CurrentSource(Element):
    def __init__(self, i: int, j: int, I: Callable[[float], float]):
        self.i = i
        self.j = j
        self.I  = I

    def stamp(self, t: float, state: Equation, prev_state: np.ndarray):
        I = self.I(t)
        if self.i != -1:
            state.b[self.i] += I
        if self.j != -1:
            state.b[self.j] -= I

class VoltageSource(Element):
    def __init__(self, i: int, j: int, V: Callable[[float], float]):
        self.i = i
        self.j = j 
        self.V = V

    def build(self, builder: StateBuilder):
        self.idx = builder.add_variable()

    def const_stamp(self, equation: Equation):
        if self.i != -1:
            # Add current contributions
            equation.G[self.i, self.idx] -= 1 # 0 = ... - I_i + ...

            # Constrain voltage difference
            equation.G[self.idx, self.i] -= 1 # V_e = ... - V_i + ...

        if self.j != -1:
            equation.G[self.j, self.idx] += 1 # 0 = ... + I_j + ...

            equation.G[self.idx, self.j] += 1 # V_e = ... + V_j + ...

    def stamp(self, t: float, equation: Equation, prev_state: np.ndarray):
        equation.b[self.idx] = self.V(t)


class Resistor(Element):
    def __init__(self, i: int, j: int, R: float):
        self.i = i
        self.j = j 
        self.R = R

    def const_stamp(self, equation: Equation):
        inv = 1 / self.R
        if self.i != -1:
            equation.G[self.i, self.i] -= inv # I_i = ... - V_i / R + ...
        if self.j != -1:
            equation.G[self.j, self.j] -= inv # I_j = ... - V_j / R + ...

        if self.i != -1 and self.j != -1:
            equation.G[self.i, self.j] += inv # I_i = ... + V_j / R + ...
            equation.G[self.j, self.i] += inv # I_j = ... + V_i / R + ...

    def current(self, state: np.ndarray):
        V_i = state[self.i] if self.i != -1 else 0
        V_j = state[self.j] if self.j != -1 else 0

        return (V_i - V_j) / self.R

class Capacitor(Element):
    def __init__(self, i: int, j: int, C: float):
        self.i = i
        self.j = j 
        self.C = C

    def const_stamp(self, equation: Equation):
        if self.i != -1:
            equation.C[self.i, self.i] -= self.C # I_i = ... - C * dV_i/dt + ...
        if self.j != -1:
            equation.C[self.j, self.j] -= self.C # I_j = ... - C * dV_j/dt + ...

        if self.i != -1 and self.j != -1:
            equation.C[self.i, self.j] += self.C # I_i = ... + C * dV_j/dt + ...
            equation.C[self.j, self.i] += self.C # I_j = ... + C * dV_i/dt + ...


class Inductor(Element):
    def __init__(self, i: int, j: int, L: float):
        self.i = i
        self.j = j 
        self.L = L

    def build(self, builder: StateBuilder):
        self.idx = builder.add_variable()

    def const_stamp(self, equation: Equation):
        if self.i != -1:
            equation.G[self.i, self.idx] = -1 # 0 = ... - I_L + ...
            equation.G[self.idx, self.i] = 1 # L dI_L/dt = ... + V_i + ...
        if self.j != -1:
            equation.G[self.j, self.idx] = 1 # 0 = ... + I_L + ...
            equation.G[self.idx, self.j] = -1 # L dI_L/dt = ... - V_j + ...

        equation.C[self.idx, self.idx] = - self.L
