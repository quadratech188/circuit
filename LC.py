import math
import numpy as np
from typing import List

from src.Element import Element
from src.Common import Capacitor, VoltageSource, Resistor, Inductor
from src.Diode import Diode
from src.Simulation import Simulation

I_s = 1e-9
k = 50

elements: List[Element] = [
    Inductor(0, -1, 1),
    Capacitor(-1, 0, 1)
]

simulation = Simulation(1, elements,
                        x = np.array([1]),
                        dt=0.01,
                        solver_iterations=20,
                        solver_threshold=1e-6)

history = []

sim_time = 20

steps = int(sim_time / simulation.dt)

history = np.zeros((steps, simulation.x.size))

for index in range(steps):
    simulation.step(simulation.dt * index)

    history[index] = simulation.x
    print(simulation.x)

import matplotlib.pyplot as plt

plt.plot(history)

plt.show()
