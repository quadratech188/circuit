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

import math
import numpy as np
import time
import matplotlib.pyplot as plt
from vpython import *
import mna_visual
from mna_visual import VoltageSource, Wire, Diode, Ground, Capacitor, Resistor

# === 노드 정의 ===
node_pos = [
    vector(0, 5, 0), vector(0, 1, 0), vector(4, 5, 0), vector(4, 1, 0),
    vector(2, 3, 0), vector(6, 3, 0), vector(8, 3, 0), vector(2, 0, 0),
    vector(8, 0, 0), vector(10, 3, 0), vector(10, 0, 0)
]
for i in range(len(node_pos)):
    node_pos[i] -= vector(5, 2, 0)

# === 회로 시각화 함수들 ===
def line(p1, p2, color=color.white): cylinder(pos=p1, axis=p2 - p1, radius=0.05, color=color)
def wire(n1, n2, color=color.white): line(node_pos[n1], node_pos[n2], color)
def diode(n1, n2, color=color.red):
    p1, p2 = node_pos[n1], node_pos[n2]
    axis = norm(p2 - p1)
    mid = (p1 + p2) / 2
    line(p1, mid - axis * 0.2)
    line(mid + axis * 0.2, p2)
    cone(pos=mid - axis * 0.2, axis=axis * 0.4, radius=0.2, color=color)
def capacitor(n1, n2):
    p1, p2 = node_pos[n1], node_pos[n2]
    axis = norm(p2 - p1)
    mid = (p1 + p2) / 2
    box(pos=mid - axis * 0.2, axis=axis, size=vector(0.1, 0.6, 0.6), color=color.cyan)
    box(pos=mid + axis * 0.2, axis=axis, size=vector(0.1, 0.6, 0.6), color=color.cyan)
    line(p1, mid - axis * 0.2, color.cyan)
    line(mid + axis * 0.2, p2, color.cyan)
def resistor(n1, n2):
    wire(n1, n2, color=color.orange)
    label(pos=(node_pos[n1] + node_pos[n2]) / 2, text='R', height=10, color=color.black)
def vsource(n1, n2):
    cylinder(pos=node_pos[n1], axis=node_pos[n2] - node_pos[n1], radius=0.1, color=color.yellow)
    label(pos=(node_pos[n1] + node_pos[n2]) / 2, text='AC', height=10, color=color.black)
def ground(n):
    p = node_pos[n]
    for i in range(3):
        box(pos=p - vector(0, 0.1 + i * 0.05, 0), size=vector(0.2 - i * 0.05, 0.01, 0.2 - i * 0.05), color=color.green)

# === 초기화 ===
scene.title = "Diode Bridge Circuit"
scene.background = color.white
scene.append_to_caption("\n\n[ Simulation Parameters ]\n")
scene.append_to_caption("\n\n[ Simulation Parameters ]\n")

I_s_slider = slider(min=0.01, max=10, value=1, length=300, step=0.01, bind=lambda x: update_param_labels())
I_s_text = wtext(text=f" I_s = {I_s_slider.value:.2f} μA\n")

k_slider = slider(min=10, max=100, value=50, length=300, step=1, bind=lambda x: update_param_labels())
k_text = wtext(text=f" k = {k_slider.value:.0f} 1/V\n")

R_slider = slider(min=1000, max=200000, value=100000, length=300, step=1000, bind=lambda x: update_param_labels())
R_text = wtext(text=f" R = {R_slider.value:.0f} Ω\n")

C_slider = slider(min=0.001, max=1.0, value=0.1, length=300, step=0.001, bind=lambda x: update_param_labels())
C_text = wtext(text=f" C = {C_slider.value:.3f} F\n")

def update_param_labels():
    I_s_text.text = f" I_s = {I_s_slider.value:.2f} A\n"
    k_text.text   = f" k = {k_slider.value:.0f} 1/V\n"
    R_text.text   = f" R = {R_slider.value:.0f} Ω\n"
    C_text.text   = f" C = {C_slider.value:.3f} F\n"

bars, voltage_labels, voltage_curves = [], [], []
resistor_voltage_label = None
resistor_voltage_curve = None
t_index_slider = None
slider_label = None
play_button = None
voltage_graph = graph(title="Node Voltages", xtitle="Time (s)", ytitle="Voltage (V)", width=800, height=300)

def run_simulation():
    global simulation, history, lookup, steps, t_index_slider, voltage_curves, resistor_voltage_curve
    global playing, current_index, slider_label, play_button, bars, voltage_labels, resistor_voltage_label

    I_s = I_s_slider.value
    k = k_slider.value
    R = R_slider.value
    C = C_slider.value

    state = mna_visual.State(
        11,
        [
            VoltageSource(1, 0, lambda t: math.sin(2 * math.pi * 60 * t)),
            Wire(0, 2), Diode(4, 2, I_s, k), Diode(2, 5, I_s, k),
            Diode(4, 3, I_s, k), Diode(3, 5, I_s, k),
            Wire(1, 3), Ground(1), Wire(5, 6), Wire(6, 9),
            Capacitor(6, 8, C), Resistor(9, 10, R),
            Wire(8, 10), Wire(7, 8), Wire(4, 7)
        ]
    )

    simulation, lookup = state.compile()
    simulation.dt = 0.0001
    simulation.solver_iterations = 20
    simulation.solver_threshold = 1e-10

    sim_time = 1
    steps = int(sim_time / simulation.dt)
    history = np.zeros((steps, simulation.x.size))
    for index in range(steps):
        simulation.step(simulation.dt * index)
        history[index] = simulation.x

    # UI 초기화
    if t_index_slider: t_index_slider.delete()
    if slider_label: slider_label.delete()
    if play_button: play_button.delete()

    t_index_slider = slider(bind=on_slider_change, min=0, max=steps - 1, value=0, step=1, length=600)
    slider_label = wtext(text=f"  Time index: {t_index_slider.value} / {steps - 1}")
    play_button = button(text="Play", bind=lambda _: toggle_play())

    for b in bars: b.visible = False
    for l in voltage_labels: l.visible = False
    bars.clear(); voltage_labels.clear()

    for i in range(len(node_pos)):
        bar = box(pos=node_pos[i], size=vector(0.2, 0, 0))
        bars.append(bar)
        lab = label(pos=node_pos[i], text="0 V", height=10, color=color.black)
        voltage_labels.append(lab)

    if resistor_voltage_label: resistor_voltage_label.visible = False
    resistor_voltage_label = label(pos=(node_pos[9] + node_pos[10]) / 2 + vector(0, 0.5, 0), 
                                   text="ΔV: 0.00 V", height=12, color=color.red, box=False)

    global voltage_graph
    # 기존 그래프 객체 전부 지우기
    if voltage_graph:
        voltage_graph.delete()
    voltage_graph = graph(title="Node Voltages", xtitle="Time (s)", ytitle="Voltage (V)", width=800, height=300)

    # 새 그래프에 곡선 재등록
    voltage_curves.clear()
    for i in range(len(node_pos)):
        if lookup[i] == -1:
            voltage_curves.append(None)
        else:
            voltage_curves.append(gcurve(graph=voltage_graph, label=f"Node {i}", color=vector(np.random.rand(), np.random.rand(), np.random.rand())))

    if resistor_voltage_curve:
        resistor_voltage_curve.delete()
    resistor_voltage_curve = gcurve(graph=voltage_graph, label="Resistor V9 - V10", color=color.red)

    update_graphs(0)
    global playing
    playing = False

def update_graphs(t_index):
    for i in range(len(node_pos)):
        lookup_index = lookup[i]
        value = 0 if lookup_index == -1 else history[t_index][lookup_index]
        bars[i].pos = node_pos[i] + vector(-1, value, 0)
        bars[i].size = vector(0.2, 2 * value, 0)
        voltage_labels[i].text = f"{value:.2f} V"
    if lookup[9] != -1 and lookup[10] != -1:
        v_diff = history[t_index][lookup[9]] - history[t_index][lookup[10]]
        resistor_voltage_label.text = f"ΔV: {v_diff:.2f} V"

def on_slider_change(evt):
    t_index = int(evt.value)
    update_graphs(t_index)
    slider_label.text = f"  Time index: {t_index} / {steps - 1}"

def toggle_play():
    global playing
    playing = not playing
    play_button.text = "Pause" if playing else "Play"

# === 회로 구성 ===
vsource(1, 0)
wire(0, 2); diode(4, 2); diode(2, 5); diode(4, 3); diode(3, 5)
wire(1, 3); ground(1); wire(5, 6); wire(6, 9)
capacitor(6, 8); resistor(9, 10); wire(8, 10); wire(7, 8); wire(4, 7)
for i, pos in enumerate(node_pos):
    label(pos=pos + vector(0.2, 0.2, 0), text=str(i), height=10, color=color.black, box=False)

scene.append_to_caption("\n")
update_param_labels()
button(text="Run Simulation", bind=lambda _: run_simulation())

# === 시뮬레이션 루프 ===
run_simulation()
current_index = -1
while True:
    rate(60)
    if playing:
        if t_index_slider.value < steps - 1:
            t_index_slider.value += 1
        else:
            playing = False
            play_button.text = "Play"

    t_index = int(t_index_slider.value)
    if t_index != current_index:
        current_index = t_index
        update_graphs(t_index)
        slider_label.text = f"  Time index: {t_index} / {steps - 1}"
        if t_index % 5 == 0:
            t = t_index * simulation.dt
            for i in range(len(node_pos)):
                if voltage_curves[i] is not None:
                    voltage = history[t_index][lookup[i]]
                    voltage_curves[i].plot(t, voltage)
            if lookup[9] != -1 and lookup[10] != -1:
                v_diff = history[t_index][lookup[9]] - history[t_index][lookup[10]]
                resistor_voltage_curve.plot(t, v_diff)

