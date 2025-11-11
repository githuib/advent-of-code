from abc import abstractmethod

from parse import with_pattern  # type: ignore[import-untyped]

from advent_of_code.problems import ParsedProblem


@with_pattern(r"\w")
def __parse_turn(turn: str) -> int:
    return 1 if turn in "AX" else 2 if turn in "BY" else 3


class _Problem(ParsedProblem[tuple[int, int], int]):
    line_pattern = "{:turn} {:turn}"

    def solution(self) -> int:
        return sum(self.play_round(o, m) for o, m in self.parsed_input)

    @abstractmethod
    def play_round(self, o: int, m: int) -> int:
        pass


class Problem1(_Problem):
    test_solution = 15
    puzzle_solution = 11906

    def play_round(self, o: int, m: int) -> int:
        return m + (m - o + 1) % 3 * 3


class Problem2(_Problem):
    test_solution = 12
    puzzle_solution = 11186

    def play_round(self, o: int, m: int) -> int:
        return (m + o) % 3 + m * 3 - 2


TEST_INPUT = """
A Y
B X
C Z
"""
