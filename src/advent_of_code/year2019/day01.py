from based_utils.data.iterators import repeat_transform

from advent_of_code.problems import MultiLineProblem


def total_fuel(mass: int) -> int:
    return mass // 3 - 2


def total_fuel_advanced(mass: int) -> int:
    return sum(
        repeat_transform(mass, transform=total_fuel, while_condition=lambda f: f > 0)
    )


class Problem1(MultiLineProblem[int]):
    test_solution = 33583
    puzzle_solution = 3372695

    def solution(self) -> int:
        return sum(total_fuel(int(line)) for line in self.lines)


class Problem2(Problem1):
    test_solution = 50346
    puzzle_solution = 5056172

    def solution(self) -> int:
        return sum(total_fuel_advanced(int(line)) for line in self.lines)


TEST_INPUT = """
100756
"""
