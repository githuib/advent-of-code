from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING, NamedTuple

from based_utils.algo import AStarState, BFSState, DijkstraState, State
from based_utils.cli import Table, human_readable_duration, timed
from kleur import Colored, ColorStr, Highlighter

from advent_of_code import C, log
from advent_of_code.problems import NumGridProblem
from advent_of_code.utils import lower_to_num, num_to_lower
from advent_of_code.utils.geo2d import P2, NumGrid2

if TYPE_CHECKING:
    from collections.abc import Iterator

    from kleur import Color


@dataclass
class Constants:
    hill: NumGrid2
    goal: int
    reverse: bool


class Variables(NamedTuple):
    pos: P2


class _State[C: Constants](State[C, Variables], ABC):
    @property
    def is_end_state(self) -> bool:
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


class _Problem(NumGridProblem[int], ABC):
    def parse_value(self, c: str) -> int:
        return {"S": 0, "E": 27}.get(c, lower_to_num(c))

    def shortest_path(self, start: str, end: str) -> int:
        start_val, end_val = self.parse_value(start), self.parse_value(end)
        start_pos = self.grid.point_with_value(start_val)
        ep = self.grid.points_with_value(end_val)

        c = Constants(self.grid, end_val, reverse=end_val < start_val)
        p_bfs, t_bfs = timed(lambda: _BFSState.find_path(Variables(start_pos), c))

        def _debug_str() -> Iterator[str]:
            visited_points_bfs: set[P2] = {s.v.pos for s in p_bfs.visited_states}

            p_dijkstra, t_dijkstra = timed(
                lambda: _DijkstraState.find_path(Variables(start_pos), c)
            )
            visited_points_dijkstra: set[P2] = {
                s.v.pos for s in p_dijkstra.visited_states
            }

            if len(ep) == 1:
                reverse = end_val < start_val
                end_pos, *_ = ep
                ac = AStarConstants(self.grid, end_val, reverse, end_pos)
                p_a_star, t_a_star = timed(
                    lambda: _AStarState.find_path(Variables(start_pos), ac)
                )
                visited_points_a_star: set[P2] = {
                    s.v.pos for s in p_a_star.visited_states
                }
            else:
                p_a_star = None
                t_a_star = 0
                visited_points_a_star = set[P2]()

            p_points: set[P2] = {s.v.pos for s in p_bfs.states}
            hill_chars = {
                p: {0: "S", 27: "E"}.get(h, num_to_lower(h))
                for p, h in self.grid.items()
            }

            def cs(color: Color) -> Colored:
                return Colored(color.slightly_darker, color)

            hl_start = Highlighter(C.green.saturated(0.8))
            hl_end = Highlighter(C.blue.saturated(0.8))
            hl_path = Highlighter(C.pink.saturated(0.8))

            c_dijkstra = C.brown.slightly_darker.saturated(0.5)
            c_bfs = c_dijkstra.slightly_darker
            c_a_star = c_dijkstra.slightly_brighter

            def grid_cell_str(p: P2, default_val: int, _colored: ColorStr) -> ColorStr:
                v = hill_chars.get(p, default_val)
                return (
                    hl_end(v)
                    if (p == start_pos)
                    else hl_start(v)
                    if (p in ep)
                    else hl_path(v)
                    if (p in p_points)
                    else cs(c_a_star)(v)
                    if (p in visited_points_a_star)
                    else cs(c_dijkstra)(v)
                    if (p in visited_points_dijkstra)
                    else cs(c_bfs)(v)
                    if (p in visited_points_bfs)
                    else Colored(c_bfs)(v)
                )

            yield from self.grid.to_lines(format_value=grid_cell_str)
            yield ""
            yield from Table(column_splits=[1], style_table=Colored(c_dijkstra))(
                ("Legend", "Algorithm", "Visited", "Path found in"),
                (
                    f"{cs(c_bfs)('x')} visited by BFS",
                    "BFS",
                    len(visited_points_bfs),
                    human_readable_duration(t_bfs),
                ),
                (
                    f"{cs(c_dijkstra)('y')} visited by Dijkstra & BFS",
                    "Dijkstra",
                    len(visited_points_dijkstra),
                    human_readable_duration(t_dijkstra),
                ),
                (
                    f"{cs(c_a_star)('z')} visited by A*, Dijkstra & BFS",
                    "A*",
                    len(visited_points_a_star),
                    human_readable_duration(t_a_star),
                )
                if p_a_star
                else (),
                (f"{hl_start('S')} start",),
                (f"{hl_end('E')} end",),
                (f"{hl_path('p')} path",),
                (f"{Colored(c_dijkstra)('w')} wild, unexplored terrain",),
            )

        log.lazy_debug(_debug_str)

        return p_bfs.length


class Problem1(_Problem):
    test_solution = 31
    puzzle_solution = 490

    def solution(self) -> int:
        return self.shortest_path(start="E", end="S")


class Problem2(_Problem):
    test_solution = 29
    puzzle_solution = 488

    def solution(self) -> int:
        return self.shortest_path(start="E", end="a")


TEST_INPUT = """
Sabqponm
abcryxxl
accszExk
acctuvwj
abdefghi
"""
