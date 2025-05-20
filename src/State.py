import numpy as np

class Equation:
    @staticmethod
    def zero(n) -> 'Equation':
        return Equation(
                np.zeros((n, n)),
                np.zeros((n, n)),
                np.zeros(n)
                )

    def __init__(self, G: np.ndarray, C: np.ndarray, b: np.ndarray):
        self.G = G
        self.C = C
        self.b = b

    def copy(self):
        return Equation(
                self.G.copy(),
                self.C.copy(),
                self.b.copy()
                )
