import math
import numpy as np
from typing import List
import time

from mna import Element, Capacitor, VoltageSource, Resistor, Inductor, Diode, Simulation

I_s = 1e-9
k = 50

elements: List[Element] = [
    VoltageSource(-1, 0, lambda t: math.sin(2 * math.pi * 60 * t)),
    Diode(1, 0, I_s, k),
    Diode(0, 2, I_s, k),
    Diode(1, -1, I_s, k),
    Diode(-1, 2, I_s, k),
    Resistor(1, 2, 100000),
    Capacitor(1, 2, 0.001)
]

simulation = Simulation(3, elements,
                        dt=0.0001,
                        solver_iterations=20,
                        solver_threshold=1e-10)

history = []

sim_time = 0.1

steps = int(sim_time / simulation.dt)

history = np.zeros((steps, simulation.x.size))

before = time.time()

for index in range(steps):
    simulation.step(simulation.dt * index)

    history[index] = simulation.x

after = time.time()

print(f'Simulation speed: {sim_time / (after - before)}x realtime')

import matplotlib.pyplot as plt

plt.plot(history)
plt.plot(history[:, 2] - history[:, 1])
plt.legend(list(range(simulation.x.size)))

plt.show()
