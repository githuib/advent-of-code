from abc import ABC
from functools import reduce

from advent_of_code.problems import OneLineProblem


def hash_(s: str) -> int:
    """
    >>> hash_('HASH')
    52
    """
    return reduce(lambda i, c: ((i + ord(c)) * 17) % 256, s, 0)


class _Problem(OneLineProblem[int], ABC):
    def __init__(self):
        self.operations = self.input.split(",")


class Problem1(_Problem):
    test_solution = 1320
    my_solution = 507666

    def solution(self) -> int:
        return sum(hash_(s) for s in self.operations)


class Problem2(_Problem):
    test_solution = 145
    my_solution = 233537

    def solution(self) -> int:
        boxes: dict[int, dict[str, int]] = {}
        for op in self.operations:
            label, focal_length = (
                (op[:-1], 0) if op[-1] == "-" else (op[:-2], int(op[-1]))
            )
            lenses = boxes.setdefault(hash_(label) + 1, {})
            if focal_length:
                lenses[label] = focal_length
            else:
                lenses.pop(label, None)
        return sum(
            box * slot * focal_length
            for box, lenses in boxes.items()
            for slot, focal_length in enumerate(lenses.values(), 1)
        )


TEST_INPUT = "rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7"
