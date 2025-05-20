from typing import List
import numpy as np

from src.Solver import gear2_step, trapezoidal_step
from src.StateBuilder import StateBuilder
from src.State import Equation
from src.Element import Element

class Simulation:
    def __init__(self, n: int, elements: List[Element], x: np.ndarray = np.zeros(0),
                 dt: float = 0.01,
                 solver_iterations: int = 20,
                 solver_threshold: float = 1e-6
                 ):
        self.n = n
        self.elements = elements

        self.builder = StateBuilder(n)

        for element in elements:
            element.build(self.builder)

        self.x = self.builder.state()

        self.equation = self.builder.equation()

        for element in elements:
            element.const_stamp(self.equation)

        self.x_prev = self.builder.state()
        for i in range(len(x)):
            self.x_prev[i] = x[i]

        equation_copy = self.equation.copy()

        for element in elements:
            element.stamp(0, equation_copy, self.x_prev)

        self.x = trapezoidal_step(dt, self.x_prev, equation_copy)

        self.dt = dt
        self.solver_iterations = solver_iterations
        self.solver_threshold = solver_threshold

    def step(self, t: float):
        x_next = self.x.copy()

        for _ in range(self.solver_iterations):
            equation_copy = self.equation.copy()

            for element in self.elements:
                element.stamp(t, equation_copy, self.x)

            x_next_iter = gear2_step(self.dt, self.x_prev, self.x, equation_copy)

            if np.linalg.norm(x_next_iter - x_next) < self.solver_threshold:
                x_next = x_next_iter
                break

            x_next = x_next_iter
        else:
            print(f"\033[33mt = {t}: Failed to converge after {self.solver_iterations} iterations\033[97m")

        self.x_prev = self.x
        self.x = x_next
