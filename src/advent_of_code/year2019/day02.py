from abc import ABC

from advent_of_code.problems import NoSolutionFoundError

from .intcode import IntcodeProblem


class _Problem(IntcodeProblem[int], ABC):
    def run_program(self, noun: int, verb: int) -> int:
        self.computer.program[1] = noun
        self.computer.program[2] = verb
        self.computer.run()
        return self.computer.memory[0]


class Problem1(_Problem):
    test_solution = None
    puzzle_solution = 7210630

    def solution(self) -> int:
        return self.run_program(noun=12, verb=2)


class Problem2(_Problem):
    test_solution = None
    puzzle_solution = 3892

    def solution(self) -> int:
        for noun in range(100):
            for verb in range(100):
                if self.run_program(noun, verb) != 19690720:
                    continue
                return 100 * noun + verb
        raise NoSolutionFoundError


TEST_INPUT = """

"""
