from abc import ABC

from advent_of_code.problems import OneLineProblem
from advent_of_code.utils.conversion import compose_number

BASE_PATTERN = [0, 1, 0, -1]


class _Problem(OneLineProblem[int], ABC):
    pass


class Problem1(_Problem):
    test_solution = 24176176
    puzzle_solution = 10189359

    def solution(self) -> int:
        input_str = [int(c) for c in self.line]
        input_length = len(input_str)
        for _ in range(100):
            input_str = [
                abs(
                    sum(
                        c * BASE_PATTERN[(i // n) % 4]
                        for i, c in enumerate(input_str, 1)
                    )
                )
                % 10
                for n in range(1, input_length + 1)
            ]
        return compose_number(input_str[:8])


class Problem2(_Problem):
    test_solution = 84462026
    puzzle_solution = None

    def solution(self) -> int:
        return 0


TEST_INPUT_1 = "80871224585914546619083218645595"
# 80871224585914546619083218645595 becomes 24176176.
# 19617804207202209144916044189917 becomes 73745418.
# 69317163492948606335995924319873 becomes 52432133.

TEST_INPUT_2 = "03036732577212944063491565474664"
# 03036732577212944063491565474664 becomes 84462026.
# 02935109699940807407585447034323 becomes 78725270.
# 03081770884921959731165446850517 becomes 53553731.
