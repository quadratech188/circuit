import numpy as np

from src.Element import Element
from src.State import Equation
from src.StateBuilder import StateBuilder

class Diode(Element):
    def __init__(self, i: int, j: int, I_s: float, k: float):
        self.i = i
        self.j = j
        self.I_s = I_s
        self.k = k

    def stamp(self, t: float, equation: Equation, prev_state: np.ndarray):
        v_i = prev_state[self.i] if self.i != -1 else 0
        v_j = prev_state[self.j] if self.j != -1 else 0

        v_delta = v_i - v_j

        I = self.I_s * (np.exp(self.k * v_delta) - 1)

        dI_dV = self.k * self.I_s * np.exp(self.k * v_delta)

        # Resistor + CurrentSource

        if self.i != -1:
            equation.G[self.i, self.i] -= dI_dV
            equation.b[self.i] -= I
        if self.j != -1:
            equation.G[self.j, self.j] -= dI_dV
            equation.b[self.j] += I

        if self.i != -1 and self.j != -1:
            equation.G[self.i, self.j] += dI_dV
            equation.G[self.j, self.i] += dI_dV
