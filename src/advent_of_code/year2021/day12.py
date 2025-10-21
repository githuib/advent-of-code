from abc import ABC
from collections import defaultdict

from advent_of_code.problems import MultiLineProblem


class _Problem(MultiLineProblem[int], ABC):
    visit_small_caves_once: bool

    def __init__(self) -> None:
        self._graph: dict[str, list[str]] = defaultdict(list)
        for node1, node2 in [line.split("-") for line in self.lines]:
            if node1 != "end" and node2 != "start":
                self._graph[node1].append(node2)
            if node1 != "start" and node2 != "end":
                self._graph[node2].append(node1)

    def find_paths(self, node: str = "start", visited: set[str] | None = None) -> list[list[str]]:
        if node == "end":
            return [["end"]]

        visited = visited or set()
        paths = []
        for neighbor in self._graph[node]:
            new_visited = set()
            if neighbor in visited:
                if self.visit_small_caves_once:
                    # small cave already visited: skip
                    continue
                if "💩" in visited:
                    # extra small cave 💩 bonus already used: skip
                    continue
                # made use of bonus visit
                new_visited.add("💩")
            elif neighbor.islower():
                # keep track of visited small caves
                new_visited.add(neighbor)

            # explore all paths from the neighbor node
            paths += [
                [node, *path]
                for path in self.find_paths(neighbor, visited | new_visited)
            ]
        return paths

    def solution(self) -> int:
        return len(self.find_paths())


class Problem1(_Problem):
    test_solution = 19
    my_solution = 4495

    visit_small_caves_once = True


class Problem2(_Problem):
    test_solution = 103
    my_solution = 131254

    visit_small_caves_once = False


TEST_INPUT = """
dc-end
HN-start
start-kj
dc-start
dc-HN
LN-dc
HN-end
kj-sa
kj-HN
kj-dc
"""
