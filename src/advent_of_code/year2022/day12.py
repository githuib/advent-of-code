from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING, NamedTuple

from based_utils.algo import AStarState, BFSState, DijkstraState
from based_utils.algo.paths import State
from based_utils.cli import Colored, format_table, human_readable_duration, timed
from based_utils.colors import Color
from based_utils.data.strings import PRE_a

from advent_of_code import log
from advent_of_code.problems import NumberGridProblem
from advent_of_code.utils.geo2d import P2, NumberGrid2

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


class _Problem(NumberGridProblem[int], ABC):
    def convert_element(self, element: str) -> int:
        return {"S": 0, "E": 27}.get(element, ord(element) - PRE_a)

    def shortest_path(self, start: str, end: str) -> int:
        start_val, end_val = self.convert_element(start), self.convert_element(end)
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
                p: {0: "S", 27: "E"}.get(h, chr(h + PRE_a))
                for p, h in self.grid.items()
            }

            c_path = Color.from_name("pink", lightness=0.35)
            c_start = Color.from_name("blue", lightness=0.4)
            c_end = Color.from_name("poison")
            c_searched = Color.from_name("orange", saturation=0.35)

            class Styles:
                start = c_start, c_start.with_changed(lightness=1.75)
                end = c_end, c_end.with_changed(lightness=1.75)
                path = c_path, c_path.with_changed(lightness=1.75)
                a = Color.grey(0.15), Color.grey(0.25)
                a_star = (
                    c_searched.with_changed(lightness=0.65),
                    c_searched.with_changed(lightness=0.9),
                )
                dijkstra = (
                    c_searched.with_changed(lightness=0.45),
                    c_searched.with_changed(lightness=0.7),
                )
                bfs = (
                    c_searched.with_changed(lightness=0.25),
                    c_searched.with_changed(lightness=0.5),
                )
                none = Color.grey(0.15), Color.grey(0)

            def grid_cell_str(p: P2, default_val: int, _colored: Colored) -> Colored:
                v = hill_chars.get(p, default_val)
                return (
                    Colored(v, *Styles.end)
                    if (p == start_pos)
                    else Colored(v, *Styles.start)
                    if (p in ep)
                    else Colored(v, *Styles.path)
                    if (p in p_points)
                    else Colored(v, *Styles.a_star)
                    if (p in visited_points_a_star)
                    else Colored(v, *Styles.dijkstra)
                    if (p in visited_points_dijkstra)
                    else Colored(v, *Styles.bfs)
                    if (p in visited_points_bfs)
                    else Colored(v, *Styles.a)
                    if (v == end_val)
                    else Colored(v, *Styles.none)
                )

            yield from self.grid.to_lines(format_value=grid_cell_str)
            yield ""
            yield from format_table(
                ("Legend", "Algorithm", "Visited", "Path found in"),
                (
                    f"{Colored('x', *Styles.bfs).formatted} visited by BFS",
                    "BFS",
                    len(visited_points_bfs),
                    human_readable_duration(t_bfs),
                ),
                (
                    f"{Colored('y', *Styles.dijkstra).formatted} visited by Dijkstra & BFS",
                    "Dijkstra",
                    len(visited_points_dijkstra),
                    human_readable_duration(t_dijkstra),
                ),
                (
                    f"{Colored('z', *Styles.a_star).formatted} visited by A*, Dijkstra & BFS",
                    "A*",
                    len(visited_points_a_star),
                    human_readable_duration(t_a_star),
                )
                if p_a_star
                else (),
                (f"{Colored('S', *Styles.start).formatted} start",),
                (f"{Colored('E', *Styles.end).formatted} end",),
                (f"{Colored('p', *Styles.path).formatted} path",),
                (
                    f"{Colored('a', *Styles.a).formatted} possible starting points (including un-escapable)",
                ),
                (f"{Colored('w', *Styles.none).formatted} wild, unexplored terrain",),
                column_splits=[1],
                color=c_searched.with_changed(lightness=0.75),
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
