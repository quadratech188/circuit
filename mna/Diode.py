import math
import numpy as np

from mna.Element import Element
from mna.State import Equation
from mna.StateBuilder import StateBuilder

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

        exp_term = math.exp(self.k * v_delta);

        I = self.I_s * (exp_term - 1)

        dI_dV = self.k * self.I_s * exp_term
        I_eff = I - dI_dV * v_delta

        # Resistor + CurrentSource

        if self.i != -1:
            equation.G[self.i, self.i] -= dI_dV
            equation.b[self.i] += I_eff
        if self.j != -1:
            equation.G[self.j, self.j] -= dI_dV
            equation.b[self.j] -= I_eff

        if self.i != -1 and self.j != -1:
            equation.G[self.i, self.j] += dI_dV
            equation.G[self.j, self.i] += dI_dV
