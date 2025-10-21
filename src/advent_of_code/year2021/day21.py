from abc import ABC
from functools import cache
from itertools import product

from advent_of_code.problems import ParsedProblem
from advent_of_code.utils import mods


def update_score(pos: int, score: int, roll: int) -> tuple[int, int]:
    return (pos := mods(pos + roll, 10, 1)), score + pos


def move_pawn(
    pawns: tuple[int, int],
    sums: tuple[int, int],
    is_turn1: bool,
    roll: int,
):
    p1, p2 = pawns
    s1, s2 = sums
    if is_turn1:
        p1, s1 = update_score(p1, s1, roll)
    else:
        p2, s2 = update_score(p2, s2, roll)
    return (p1, p2), (s1, s2), not is_turn1


def turn(
    pawns: tuple[int, int],
    sums: tuple[int, int] = (0, 0),
    is_turn1: bool = True,
    total_rolls: int = 0,
) -> tuple[int, int, int]:
    s1, s2 = sums
    if s1 >= 1000 or s2 >= 1000:
        return s1, s2, total_rolls
    p, s, t = move_pawn(
        pawns,
        sums,
        is_turn1,
        roll=sum(mods(total_rolls + die, 100, 1) for die in range(1, 4)),
    )
    return turn(p, s, t, total_rolls + 3)


@cache
def quantum_turn(
    pawns: tuple[int, int],
    sums: tuple[int, int] = (0, 0),
    is_turn1: bool = True,
) -> list[int]:
    s1, s2 = sums
    if s1 >= 21:
        return [1, 0]
    if s2 >= 21:
        return [0, 1]
    return [
        sum(games_won)
        for games_won in zip(
            *[
                quantum_turn(*move_pawn(pawns, sums, is_turn1, sum(rolls)))
                for rolls in product(range(1, 4), repeat=3)
            ],
            strict=False,
        )
    ]


class _Problem(ParsedProblem[tuple[int], int], ABC):
    line_pattern = "position: {:d}"

    def __init__(self):
        [self.start_1], [self.start_2] = self.parsed_input


class Problem1(_Problem):
    test_solution = 739785
    my_solution = 432450

    def solution(self) -> int:
        *scores, rolls = turn(self.start_1, self.start_2)
        return min(scores) * rolls


class Problem2(_Problem):
    test_solution = 444356092776315
    my_solution = 138508043837521

    def solution(self) -> int:
        return max(quantum_turn(self.start_1, self.start_2))


TEST_INPUT = """
Player 1 starting position: 4
Player 2 starting position: 8
"""
