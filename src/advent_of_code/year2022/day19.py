from abc import ABC

from advent_of_code.problems import ParsedProblem


class _Problem(ParsedProblem[tuple[int, ...], int], ABC):
    multi_line_pattern = (
        "Blueprint {:d}: "
        "Each ore robot costs {:d} ore. "
        "Each clay robot costs {:d} ore. "
        "Each obsidian robot costs {:d} ore and {:d} clay. "
        "Each geode robot costs {:d} ore and {:d} obsidian."
    )

    def __init__(self) -> None:
        pass


class Problem1(_Problem):
    test_solution = 33

    def solution(self) -> int:
        return 0


class Problem2(_Problem):
    def solution(self) -> int:
        return 0


TEST_INPUT = (
    "Blueprint 1:"
    " Each ore robot costs 4 ore."
    " Each clay robot costs 2 ore."
    " Each obsidian robot costs 3 ore and 14 clay."
    " Each geode robot costs 2 ore and 7 obsidian.\n"
    "Blueprint 2:"
    " Each ore robot costs 2 ore."
    " Each clay robot costs 3 ore."
    " Each obsidian robot costs 3 ore and 8 clay."
    " Each geode robot costs 3 ore and 12 obsidian.\n"
)
