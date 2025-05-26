import numpy as np
from mna.State import Equation

class StateBuilder:
    def __init__(self, n: int):
        self.n = n
        self.total = n

    def add_variable(self):
        self.total += 1
        return self.total - 1

    def equation(self):
        return Equation.zero(self.total)

    def state(self):
        return np.ndarray(self.total)
