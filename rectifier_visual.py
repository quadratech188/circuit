import math
import mna_visual
from mna_visual import VoltageSource, Wire, Diode, Ground, Capacitor, Resistor
import numpy as np
import time

"""

0------------2
|          /  \\
        Diode  Diode
        /        \\
Bat    4           5----------6--------9
       |\\        /           |        |
       |Diode  Diode          |        |
|      |   \\  /          Capacitor  Resistor
1------+-----3                |        |
|      |                      |        |
Ground 7--------------------- 8-------10

"""

I_s = 1e-9
k = 50

state = mna_visual.State(
        11,
        [
            VoltageSource(1, 0, lambda t: math.sin(2 * math.pi * 60 * t)),
            Wire(0, 2),
            Diode(4, 2, I_s, k),
            Diode(2, 5, I_s, k),
            Diode(4, 3, I_s, k),
            Diode(3, 5, I_s, k),
            Wire(1, 3),
            Ground(1),
            Wire(5, 6),
            Wire(6, 9),
            Capacitor(6, 8, 0.001),
            Resistor(9, 10, 100000),
            Wire(8, 10),
            Wire(7, 8),
            Wire(4, 7)
            ]
        )

simulation, lookup = state.compile()

simulation.dt = 0.0001
simulation.solver_iterations = 20
simulation.solver_threshold = 1e-10

print(*(k.__dict__ for k in simulation.elements))

history = []

sim_time = 1

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
print(lookup)
plt.plot(history[:, lookup[9]] - history[:, lookup[10]])
plt.legend(list(range(simulation.x.size)) + ["Actual voltage"])

plt.show()
