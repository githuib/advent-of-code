from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING, NamedTuple

from yachalk import chalk

from advent_of_code import AOC, log
from advent_of_code.geo2d import P2, Grid2
from advent_of_code.problems import NumberGridProblem
from advent_of_code.search import AStarState, BFSState, DijkstraState, State
from advent_of_code.utils import debug_table, timed

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass
class Constants:
    hill: Grid2[int]
    goal: int
    reverse: bool


class Variables(NamedTuple):
    pos: P2


class _State[C: Constants, V: Variables](State[C, V], ABC):
    def __repr__(self) -> str:
        return f"{self.v.pos}"

    @property
    def is_finished(self) -> bool:
        return self.c.hill[self.v.pos] == self.c.goal

    @property
    def next_states(self) -> Iterator[_State]:
        height = self.c.hill[self.v.pos]
        for new_pos, new_height in self.c.hill.neighbors(self.v.pos):
            if ((
                height <= new_height + 1
            ) if self.c.reverse else (
                new_height <= height + 1
            )):
                yield self.move(pos=new_pos)


class _BFSState(_State[Constants, Variables], BFSState[Constants, Variables]):
    pass


class _DijkstraState(_State[Constants, Variables], DijkstraState[Constants, Variables]):
    pass


@dataclass
class AStarConstants(Constants):
    heuristic_end_pos: P2


class _AStarState(_State[AStarConstants, Variables], AStarState[AStarConstants, Variables]):
    @property
    def heuristic(self) -> int:
        x, y = self.v.pos
        ex, ey = self.c.heuristic_end_pos
        horizontal_distance = abs(ex - x) + abs(ey - y)
        vertical_distance = abs(self.c.goal - self.c.hill[self.v.pos])
        return horizontal_distance + vertical_distance


PRE_A = ord("a") - 1


class _Problem(NumberGridProblem[int], ABC):
    def convert_element(self, element: str) -> int:
        return {"S": 0, "E": 27}.get(element, ord(element) - PRE_A)

    def shortest_path(self, start: str, end: str) -> int:
        start_val, end_val = self.convert_element(start), self.convert_element(end)
        reverse = end_val < start_val
        start_pos = self.grid.point_with_value(start_val)
        ep = self.grid.points_with_value(end_val)
        end_pos = ep.pop() if len(ep) == 1 else None

        c = Constants(self.grid, end_val, reverse=end_val < start_val)
        p_bfs, _, t_bfs = timed(lambda: _BFSState.find_path(Variables(pos=start_pos), c))
        visited_points_bfs: set[P2] = {s.v.pos for s in p_bfs.visited}
        p_dijkstra, _, t_dijkstra = timed(lambda: _DijkstraState.find_path(Variables(pos=start_pos), c))
        visited_points_dijkstra: set[P2] = {s.v.pos for s in p_dijkstra.visited}
        if end_pos:
            ac = AStarConstants(self.grid, end_val, reverse, end_pos)
            p_a_star, _, t_a_star = timed(lambda: _AStarState.find_path(Variables(pos=start_pos), ac))
            visited_points_a_star: set[P2] = {s.v.pos for s in p_a_star.visited}
            a_star_result = [((f'{chalk.hex("034").bg_hex("bdf")("E")} end', 5), "A*", len(p_a_star.visited), t_a_star)]
        else:
            visited_points_a_star = set[P2]()
            a_star_result = []

        if AOC.debugging:
            p_points: set[P2] = {s.v.pos for s in p_bfs.states}
            hill_chars = {p: {0: "S", 27: "E"}.get(h, chr(h + PRE_A)) for p, h in self.grid.items()}
            log.debug(self.grid.to_str(lambda p, _: (
                chalk.hex("034").bg_hex("bdf")(hill_chars[p]) if (
                    p in {start_pos, end_pos} | ep
                ) else chalk.hex("068").bg_hex("0af")(hill_chars[p]) if (
                    p in p_points
                ) else chalk.hex("535").bg_hex("848")(hill_chars[p]) if (
                    p in visited_points_a_star
                ) else chalk.hex("424").bg_hex("636")(hill_chars[p]) if (
                    p in visited_points_dijkstra
                ) else chalk.hex("212").bg_hex("424")(hill_chars[p]) if (
                    p in visited_points_bfs
                ) else chalk.hex("222").bg_hex("333")(hill_chars[p]) if (
                    hill_chars[p] == end_val
                ) else chalk.hex("222").bg_hex("000")(hill_chars[p])
            )))
            log.debug(" ")
            debug_table([("Legend", "Algorithm", "Visited", "Path found in"), ("", "BFS", len(p_bfs.visited), t_bfs), ((f"{chalk.hex('034').bg_hex('bdf')('S')} start", 7), "Dijkstra", len(p_dijkstra.visited), t_dijkstra), *a_star_result, ((f"{chalk.hex('068').bg_hex('0af')('p')} path", 6), "", "", "", ""), ((f"{chalk.hex('535').bg_hex('848')('x')} visited by all algorithms (A*, Dijkstra & BFS)", 48), "", "", "", ""), ((f"{chalk.hex('424').bg_hex('636')('y')} only visited by Dijkstra & BFS", 32), "", "", "", ""), ((f"{chalk.hex('212').bg_hex('424')('z')} only visited by BFS", 21), "", "", "", ""), ((f"{chalk.hex('222').bg_hex('333')('a')} possible starting points (including un-escapable)", 51 + 68), "", "", "", ""), ((f"{chalk.hex('222').bg_hex('000')('w')} wild, unexplored terrain", 26), "", "", "", "")])
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
