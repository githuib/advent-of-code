from based_utils.data.iterators import (
    equalized_lines,
    split_at,
    split_items,
    transposed_lines,
)
from parse import parse  # type: ignore[import-untyped]

from advent_of_code.problems import MultiLineProblem


class _Problem(MultiLineProblem[str]):
    _is_v9001: bool

    def __init__(self) -> None:
        stacks, self._moves_input = split_items(self.lines, delimiter="")
        *rows, nums = (line[1::4] for line in stacks)
        cols = transposed_lines(equalized_lines(reversed(rows), max_length=len(nums)))
        self._stacks: dict[str, str] = dict(
            zip(nums, (c.strip() for c in cols), strict=True)
        )

    def solution(self) -> str:
        for line in self._moves_input:
            amount, g, r = parse("move {:d} from {} to {}", line)
            self._stacks[g], gtfo = split_at(self._stacks[g], -amount)
            self._stacks[r] += gtfo if self._is_v9001 else gtfo[::-1]
        return "".join(stack[-1] for stack in self._stacks.values())


class Problem1(_Problem):
    test_solution = "CMZ"
    puzzle_solution = "TWSGQHNHL"

    _is_v9001 = False


class Problem2(_Problem):
    test_solution = "MCD"
    puzzle_solution = "JNRSCDWPP"

    _is_v9001 = True


TEST_INPUT = """
    [D]
[N] [C]
[Z] [M] [P]
 1   2   3

move 1 from 2 to 1
move 3 from 1 to 3
move 2 from 2 to 1
move 1 from 1 to 2
"""
