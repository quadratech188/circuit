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

class VoltageSource(mna_visual.Element):
    def __init__(self, i: int, j: int, V: Callable[[float], float]) -> None:
        super().__init__()
        self.i = i
        self.j = j
        self.V = V

    def compile(self, state: 'mna_visual.State') -> List[mna.Element]:
        return [mna.VoltageSource(state.uf[self.i], state.uf[self.j], self.V)]

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
