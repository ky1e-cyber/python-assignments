from functools import reduce
from dataclasses import dataclass
from typing import List, Dict


class DisjointSets:
    def __init__(self, n: int):
        self._parents: List[int] = [i for i in range(n)]
        self._parents_cache: Dict[int, int] = {}
        self._ranks: List[int] = [0] * n
        self.sets_count: int = n

    def find_set(self, v: int) -> int:
        keys: List[int] = []
        while self._parents[v] != v:
            if v in self._parents_cache:
                v = self._parents_cache[v]
                continue
            keys.append(v)
            v = self._parents[v]
        
        self._parents_cache.update(dict.fromkeys(keys, v))
        return v

    def merge_sets(self, root1: int, root2: int):
        root1, root2 = (root2, root1) if self._ranks[root1] < self._ranks[root2] else (root1, root2)
        self._parents[root2] = root1
        if self._ranks[root1] == self._ranks[root2]:
            self._ranks[root1] += 1
        self.sets_count -= 1

@dataclass(frozen=True)
class Edge:
    from_vert: int
    to_vert: int
    weight: int

def solution(data: str) -> (int, int):
    def _insert_edge(w: int, e: Edge) -> int:
        root1: int = sets.find_set(e.from_vert)
        root2: int = sets.find_set(e.to_vert)

        if root1 != root2:
            sets.merge_sets(root1, root2)
            return w + e.weight
            
        return w

    data = (
        map(int, l.split(" ")) for l in 
        (d.strip() for d in data.splitlines() if d != "")
        )

    n, m = next(data)
    sets: DisjointSets = DisjointSets(n)
    edges: List[Edge] = sorted(
        (Edge(fv, tv, w) for fv, tv, w in data),
        key = lambda x: x.weight
    )

    weight: int = reduce(_insert_edge, edges, 0)

    return sets.sets_count, weight