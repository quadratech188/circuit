import numpy as np

from src.State import Equation
from src.StateBuilder import StateBuilder

class Element:
    def build(self, builder: StateBuilder):
        pass

    def const_stamp(self, equation: Equation):
        pass

    def stamp(self, t: float, equation: Equation, prev_state: np.ndarray):
        pass
