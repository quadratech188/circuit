from typing import List, Callable
import mna
import mna_visual

class Resistor(mna_visual.Element):
    def __init__(self, i: int, j: int, R: float) -> None:
        super().__init__()
        self.i = i
        self.j = j
        self.R = R

    def compile(self, state: 'mna_visual.State') -> List[mna.Element]:
        return [mna.Resistor(state.uf[self.i], state.uf[self.j], self.R)]

class Inductor(mna_visual.Element):
    def __init__(self, i: int, j: int, L: float) -> None:
        super().__init__()
        self.i = i
        self.j = j
        self.L = L

    def compile(self, state: 'mna_visual.State') -> List[mna.Element]:
        return [mna.Inductor(state.uf[self.i], state.uf[self.j], self.L)]

class Capacitor(mna_visual.Element):
    def __init__(self, i: int, j: int, C: float) -> None:
        super().__init__()
        self.i = i
        self.j = j
        self.C = C

    def compile(self, state: 'mna_visual.State') -> List[mna.Element]:
        return [mna.Capacitor(state.uf[self.i], state.uf[self.j], self.C)]

class Diode(mna_visual.Element):
    def __init__(self, i: int, j: int, I_s: float, k: float) -> None:
        super().__init__()
        self.i = i
        self.j = j
        self.I_s = I_s
        self.k = k

    def compile(self, state: 'mna_visual.State') -> List[mna.Element]:
        return [mna.Diode(state.uf[self.i], state.uf[self.j], self.I_s, self.k)]

class VoltageSource(mna_visual.Element):
    def __init__(self, i: int, j: int, V: Callable[[float], float]) -> None:
        super().__init__()
        self.i = i
        self.j = j
        self.V = V

    def compile(self, state: 'mna_visual.State') -> List[mna.Element]:
        return [mna.VoltageSource(state.uf[self.i], state.uf[self.j], self.V)]

class CurrentSource(mna_visual.Element):
    def __init__(self, i: int, j: int, A: Callable[[float], float]) -> None:
        super().__init__()
        self.i = i
        self.j = j
        self.A = A

    def compile(self, state: 'mna_visual.State') -> List[mna.Element]:
        return [mna.CurrentSource(state.uf[self.i], state.uf[self.j], self.A)]

class Wire(mna_visual.Element):
    def __init__(self, i: int, j: int):
        super().__init__()
        self.i = i
        self.j = j

    def hook(self, state: 'mna_visual.State'):
        state.uf.connect(self.i, self.j)

class Ground(mna_visual.Element):
    def __init__(self, i: int):
        super().__init__()
        self.i = i

    def hook(self, state: 'mna_visual.State'):
        state.uf.connect(self.i, -1)

