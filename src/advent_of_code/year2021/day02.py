from abc import ABC

from advent_of_code.problems import ParsedProblem


class _Problem(ParsedProblem[tuple[str, int], int], ABC):
    line_pattern = "{:w} {:d}"


class Problem1(_Problem):
    test_solution = 150
    puzzle_solution = 1480518

    def solution(self) -> int:
        pos, depth = 0, 0
        for command, value in self.parsed_input:
            match command:
                case "forward":
                    pos += value
                case "up":
                    depth -= value
                case "down":
                    depth += value
        return pos * depth


class Problem2(_Problem):
    test_solution = 900
    puzzle_solution = 1282809906

    def solution(self) -> int:
        pos, depth, aim = 0, 0, 0
        for command, value in self.parsed_input:
            match command:
                case "forward":
                    pos += value
                    depth += value * aim
                case "up":
                    aim -= value
                case "down":
                    aim += value
        return pos * depth


TEST_INPUT = """
forward 5
down 5
forward 8
up 3
down 8
forward 2
"""
