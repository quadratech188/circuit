from typing import List
import mna.Element
import mna_visual

class Element:
    def __init__(self):
        pass

    def hook(self, state: 'mna_visual.State'):
        pass

    def compile(self, state: 'mna_visual.State') -> List[mna.Element]:
        return []
