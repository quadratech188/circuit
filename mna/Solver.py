import numpy as np

from mna.State import Equation

def trapezoidal_step(dt: float, x: np.ndarray, equation: Equation):
    # Trapezoidal Rule
    # Gx + C dx/dt = b
    # G (x_1 + x_0) / 2 + C (x_1 - x_0) / dt = b
    # (G / 2 + C / dt) x_1 = b - (G / 2 - C / dt) x_0
    dividend = equation.G / 2 + equation.C / dt
    divisor = equation.b - (equation.G / 2 - equation.C / dt) @ x

    return np.linalg.solve(dividend, divisor)

def gear2_step(dt:float, x_0: np.ndarray, x_1: np.ndarray, equation: Equation):
    # x_2 - 4/3 x_1 + 1/3 x_0 = 2/3 dt dx/dt
    # dx/dt = (3x_2 - 4x_1 + x_0) / 2dt

    # Gx_2 + C(3x_2 - 4x_1 + x_0) / 2dt = b
    # (G + 3C / 2dt)x_2 = b + C(4x_1 - x_0) / 2dt
    dividend = equation.G + 3 * equation.C / 2 / dt
    divisor = equation.b + equation.C @ (4 * x_1 - x_0) / 2 / dt

    return np.linalg.solve(dividend, divisor)
