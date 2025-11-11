from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING, NamedTuple

from yachalk import chalk

from advent_of_code import log
from advent_of_code.problems import NumberGridProblem
from advent_of_code.utils.cli import table_lines, timed
from advent_of_code.utils.geo2d import P2, NumberGrid2
from advent_of_code.utils.search import AStarState, BFSState, DijkstraState, State
from advent_of_code.utils.strings import PRE_a

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass
class Constants:
    hill: NumberGrid2
    goal: int
    reverse: bool


class Variables(NamedTuple):
    pos: P2


class _State[C: Constants](State[C, Variables], ABC):
    @property
    def is_finished(self) -> bool:
        return self.c.hill[self.v.pos] == self.c.goal

    @property
    def next_states(self) -> Iterator[_State]:
        height = self.c.hill[self.v.pos]
        for new_pos, new_height in self.c.hill.neighbors(self.v.pos):
            if (
                (height <= new_height + 1)
                if self.c.reverse
                else (new_height <= height + 1)
            ):
                yield self.move(Variables(new_pos))


class _BFSState(_State, BFSState[Constants, Variables]):
    pass


class _DijkstraState(_State, DijkstraState[Constants, Variables]):
    pass


@dataclass
class AStarConstants(Constants):
    heuristic_end_pos: P2


class _AStarState(_State, AStarState[AStarConstants, Variables]):
    @property
    def heuristic(self) -> int:
        x, y = self.v.pos
        ex, ey = self.c.heuristic_end_pos
        horizontal_distance = abs(ex - x) + abs(ey - y)
        vertical_distance = abs(self.c.goal - self.c.hill[self.v.pos])
        return horizontal_distance + vertical_distance


class _Problem(NumberGridProblem[int], ABC):
    def convert_element(self, element: str) -> int:
        return {"S": 0, "E": 27}.get(element, ord(element) - PRE_a)

    def shortest_path(self, start: str, end: str) -> int:
        start_val, end_val = self.convert_element(start), self.convert_element(end)
        start_pos = self.grid.point_with_value(start_val)
        ep = self.grid.points_with_value(end_val)

        c = Constants(self.grid, end_val, reverse=end_val < start_val)
        p_bfs, _, t_bfs = timed(lambda: _BFSState.find_path(Variables(start_pos), c))

        def _debug_str() -> Iterator[str]:
            visited_points_bfs: set[P2] = {s.v.pos for s in p_bfs.visited}

            p_dijkstra, _, t_dijkstra = timed(
                lambda: _DijkstraState.find_path(Variables(start_pos), c)
            )
            visited_points_dijkstra: set[P2] = {s.v.pos for s in p_dijkstra.visited}

            if len(ep) == 1:
                reverse = end_val < start_val
                end_pos, *_ = ep
                ac = AStarConstants(self.grid, end_val, reverse, end_pos)
                p_a_star, _, t_a_star = timed(
                    lambda: _AStarState.find_path(Variables(start_pos), ac)
                )
                visited_points_a_star: set[P2] = {s.v.pos for s in p_a_star.visited}
            else:
                p_a_star = None
                t_a_star = ""
                visited_points_a_star = set[P2]()

            p_points: set[P2] = {s.v.pos for s in p_bfs.states}
            hill_chars = {
                p: {0: "S", 27: "E"}.get(h, chr(h + PRE_a))
                for p, h in self.grid.items()
            }

            class Styles:
                start_end = chalk.hex("034").bg_hex("bdf")
                a = chalk.hex("222").bg_hex("333")
                a_star = chalk.hex("535").bg_hex("848")
                path = chalk.hex("068").bg_hex("0af")
                dijkstra = chalk.hex("424").bg_hex("636")
                bfs = chalk.hex("212").bg_hex("424")
                none = chalk.hex("222").bg_hex("000")

            def grid_cell_str(p: P2, default_val: int | None) -> str:
                v = hill_chars.get(p, default_val)
                return (
                    Styles.start_end(v)
                    if (p in {start_pos, *ep})
                    else Styles.path(v)
                    if (p in p_points)
                    else Styles.a_star(v)
                    if (p in visited_points_a_star)
                    else Styles.dijkstra(v)
                    if (p in visited_points_dijkstra)
                    else Styles.bfs(v)
                    if (p in visited_points_bfs)
                    else Styles.a(v)
                    if (v == end_val)
                    else Styles.none(v)
                )

            yield from self.grid.to_lines(format_value=grid_cell_str)
            yield ""
            yield from table_lines(
                ("Legend", "Algorithm", "Visited", "Path found in"),
                ("",),
                (f"{Styles.bfs('x')} visited by BFS", "BFS", len(p_bfs.visited), t_bfs),
                (
                    f"{Styles.dijkstra('y')} visited by Dijkstra & BFS",
                    "Dijkstra",
                    len(p_dijkstra.visited),
                    t_dijkstra,
                ),
                (
                    f"{Styles.a_star('z')} visited by A*, Dijkstra & BFS",
                    "A*",
                    len(p_a_star.visited),
                    t_a_star,
                )
                if p_a_star
                else (),
                (f"{Styles.start_end('S')} start",),
                (f"{Styles.start_end('E')} end",),
                (f"{Styles.path('p')} path",),
                (f"{Styles.a('a')} possible starting points (including un-escapable)",),
                (f"{Styles.none('w')} wild, unexplored terrain",),
            )

        log.lazy_debug(_debug_str)

        return p_bfs.length


class Problem1(_Problem):
    test_solution = 31
    my_solution = 490

    def solution(self) -> int:
        return self.shortest_path(start="E", end="S")


class Problem2(_Problem):
    test_solution = 29
    my_solution = 488

    def solution(self) -> int:
        return self.shortest_path(start="E", end="a")


TEST_INPUT = """
Sabqponm
abcryxxl
accszExk
acctuvwj
abdefghi
"""
