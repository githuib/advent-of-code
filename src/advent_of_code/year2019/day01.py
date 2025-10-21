from advent_of_code.problems import MultiLineProblem
from advent_of_code.utils import repeat_transform


def total_fuel(mass: int) -> int:
    return mass // 3 - 2


def total_fuel_advanced(mass: int) -> int:
    return sum(repeat_transform(mass, total_fuel, while_condition=lambda f: f > 0))


class Problem1(MultiLineProblem[int]):
    test_solution = 33583
    my_solution = 3372695

    def solution(self) -> int:
        return sum(total_fuel(int(line)) for line in self.lines)


class Problem2(Problem1):
    test_solution = 50346
    my_solution = 5056172

    def solution(self) -> int:
        return sum(total_fuel_advanced(int(line)) for line in self.lines)


TEST_INPUT = """
100756
"""
