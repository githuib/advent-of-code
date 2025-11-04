from abc import ABC
from copy import copy
from itertools import permutations
from typing import TYPE_CHECKING

from .intcode import IntcodeProblem

if TYPE_CHECKING:
    from collections.abc import Iterable


class _Problem(IntcodeProblem[int], ABC):
    pass


class Problem1(_Problem):
    test_solution = None
    my_solution = 34686

    def output_for(self, phase_settings: Iterable[int], input_: int = 0) -> int:
        if not phase_settings:
            return input_
        phase_setting, *remaining_phase_settings = phase_settings
        return self.output_for(
            remaining_phase_settings, input_=self.computer.run(phase_setting, input_)
        )

    def solution(self) -> int:
        return max(
            self.output_for(phase_settings)
            for phase_settings in permutations(range(5), 5)
        )


class Problem2(_Problem):
    test_solution = None
    my_solution = 36384144

    def feedback_output_for(self, phase_settings: Iterable[int]) -> int:
        computers = [copy(self.computer) for _ in range(5)]
        output = 0
        states = {}
        is_running = True
        while is_running:
            for computer, phase_setting in zip(computers, phase_settings, strict=False):
                if computer in states:
                    computer.inputs += [output]
                else:
                    states[computer] = computer.run_to_next_output(
                        phase_setting, output
                    )
                try:
                    output = next(states[computer])
                except StopIteration:
                    is_running = False
        return output

    def solution(self) -> int:
        return max(
            self.feedback_output_for(phase_settings)
            for phase_settings in permutations(range(5, 10), 5)
        )


TEST_INPUT = (
    "3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,-5,54,1105,1,12,1,53,"
    "54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10"
)
