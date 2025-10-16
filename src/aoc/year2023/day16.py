from abc import ABC
from collections import deque

from yachalk import chalk

from aoc import AOC, log
from aoc.geo2d import P2, Dir2
from aoc.problems import GridProblem


class _Problem(GridProblem[int], ABC):
    def energized(self, start: tuple[P2, P2]) -> int:
        beams = deque([start])
        visited = set()
        while beams:
            (x, y), d = beams.popleft()
            dx, dy = d
            p = x + dx, y + dy
            if p not in self.grid:
                continue
            v = self.grid[p]
            new_dirs = []
            if v == "/":
                new_dirs.append({
                    Dir2.left: Dir2.down,
                    Dir2.down: Dir2.left,
                    Dir2.right: Dir2.up,
                    Dir2.up: Dir2.right,
                }[d])
            elif v == "\\":
                new_dirs.append({
                    Dir2.left: Dir2.up,
                    Dir2.up: Dir2.left,
                    Dir2.right: Dir2.down,
                    Dir2.down: Dir2.right,
                }[d])
            elif v == "|" and d in (Dir2.left, Dir2.right):
                new_dirs.append(Dir2.up)
                new_dirs.append(Dir2.down)
            elif v == "-" and d in (Dir2.up, Dir2.down):
                new_dirs.append(Dir2.left)
                new_dirs.append(Dir2.right)
            else:
                new_dirs.append(d)
            new_beams = {(p, nd) for nd in new_dirs if (p, nd) not in visited}
            beams.extend(new_beams)
            visited |= new_beams
        points = {p for p, _ in visited}
        if AOC.debugging:
            log.debug(self.grid.to_str(
                lambda q, c: chalk.hex("034").bg_hex("bdf")(c) if q in points else chalk.hex("222").bg_hex("888")(c),
            ))
        return len(points)


class Problem1(_Problem):
    test_solution = 46
    my_solution = 6902

    def solution(self) -> int:
        return self.energized(((-1, 0), Dir2.right))


class Problem2(_Problem):
    test_solution = 51
    my_solution = 7697

    def solution(self) -> int:
        return max(self.energized((p, d)) for p, d in [
            ((x, y), d)
            for x in range(self.grid.width)
            for y, d in ((-1, Dir2.down), (self.grid.height, Dir2.up))
        ] + [
            ((x, y), d)
            for x, d in ((-1, Dir2.right), (self.grid.width, Dir2.left))
            for y in range(self.grid.height)
        ])


TEST_INPUT = r"""
.|...\....
|.-.\.....
.....|-...
........|.
..........
.........\
..../.\\..
.-.-/..|..
.|....-|.\
..//.|....
"""
