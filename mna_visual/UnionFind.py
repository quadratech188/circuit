class UnionFind:
    def __init__(self, n: int) -> None:
        self._mapping = {i: i for i in range(-1, n)}
        self._canonical_mapping = {}
        self.size = 0

    def find(self, x: int) -> int:
        if (self._mapping[x] == x):
            return x;

        self._mapping[x] = self.find(self._mapping[x])
        return self._mapping[x]

    def connect(self, x: int, y: int) -> None:
        self._mapping[self.find(x)] = self.find(y)

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)

    def __getitem__(self, key: int):
        return self._canonical_mapping[key]

    def generate_canonical(self):
        counter = 0
        canonical = {}

        # Flatten
        for node, _ in self._mapping.items():
            self.find(node)

        # Ground maps to Ground
        canonical[self._mapping[-1]] = -1

        for node, mapping in self._mapping.items():
            if mapping not in canonical:
                canonical[mapping] = counter
                counter += 1

            self._canonical_mapping[node] = canonical[mapping]

        self.size = counter
