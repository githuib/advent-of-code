from abc import ABC
from collections import deque

from yachalk import chalk

from advent_of_code import log
from advent_of_code.problems import StringGridProblem
from advent_of_code.utils.geo2d import DOWN, LEFT, P2, RIGHT, UP


class _Problem(StringGridProblem[int], ABC):
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
                new_dirs.append({LEFT: DOWN, DOWN: LEFT, RIGHT: UP, UP: RIGHT}[d])
            elif v == "\\":
                new_dirs.append({LEFT: UP, UP: LEFT, RIGHT: DOWN, DOWN: RIGHT}[d])
            elif v == "|" and d in (LEFT, RIGHT):
                new_dirs.append(UP)
                new_dirs.append(DOWN)
            elif v == "-" and d in (UP, DOWN):
                new_dirs.append(LEFT)
                new_dirs.append(RIGHT)
            else:
                new_dirs.append(d)
            new_beams = {(p, nd) for nd in new_dirs if (p, nd) not in visited}
            beams.extend(new_beams)
            visited |= new_beams
        points = {p for p, _ in visited}

        log.lazy_debug(
            lambda: self.grid.to_lines(
                format_value=lambda q, c: chalk.hex("034").bg_hex("bdf")(c)
                if q in points
                else chalk.hex("222").bg_hex("888")(c)
            )
        )

        return len(points)


class Problem1(_Problem):
    test_solution = 46
    puzzle_solution = 6902

    def solution(self) -> int:
        return self.energized(((-1, 0), RIGHT))


class Problem2(_Problem):
    test_solution = 51
    puzzle_solution = 7697

    def solution(self) -> int:
        return max(
            self.energized((p, d))
            for p, d in [
                ((x, y), d)
                for x in range(self.grid.width)
                for y, d in ((-1, DOWN), (self.grid.height, UP))
            ]
            + [
                ((x, y), d)
                for x, d in ((-1, RIGHT), (self.grid.width, LEFT))
                for y in range(self.grid.height)
            ]
        )


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
