from itertools import takewhile

from more_itertools import all_unique, windowed

from advent_of_code.problems import OneLineProblem


class _Problem(OneLineProblem[int]):
    _window_size: int

    def solution(self) -> int:
        ws = self._window_size
        window = windowed(self.line, ws)
        return len(list(takewhile(lambda s: not all_unique(s), window))) + ws


class Problem1(_Problem):
    test_solution = 10
    puzzle_solution = 1356

    _window_size = 4


class Problem2(_Problem):
    test_solution = 29
    puzzle_solution = 2564

    _window_size = 14


TEST_INPUT = "nznrnfrfntjfmvfwmzdfjlvtqnbhcprsg"
