import numpy as np

from typing import List, Optional
import mna
import mna_visual

class State:
    def __init__(self, n, elements: List[mna_visual.Element] = []) -> None:
        self.elements = elements
        self.n = n
        self.voltages = {}

    def add_element(self, element: mna_visual.Element):
        self.elements.append(element)

    def compile(self) -> mna.Simulation:
        self.uf = mna_visual.UnionFind(self.n)
        for element in self.elements:
            element.hook(self)

        self.uf.generate_canonical()
        result = []
        for element in self.elements:
            result += element.compile(self)

        state = np.zeros(self.uf.size)
        for index, voltage in self.voltages.items():
            state[self.uf[index]] = voltage

        return mna.Simulation(
                self.uf.size,
                result,
                state
                )
