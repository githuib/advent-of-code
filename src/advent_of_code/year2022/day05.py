from parse import parse  # type: ignore[import-untyped]

from advent_of_code.problems import MultiLineProblem
from advent_of_code.utils import grouped, padded, split_at, transposed


class _Problem(MultiLineProblem[str]):
    _is_v9001: bool

    def __init__(self) -> None:
        input_blocks = grouped(self.lines)
        *rows, nums = (line[1::4] for line in next(input_blocks))
        self._stacks: dict[str, str] = dict(zip(nums, (
            s.strip() for s in transposed(padded(reversed(rows), len(nums)))
        ), strict=False))
        self._moves_input = next(input_blocks)

    def solution(self) -> str:
        for line in self._moves_input:
            amount, g, r = parse("move {:d} from {} to {}", line)
            self._stacks[g], gtfo = split_at(self._stacks[g], -amount)
            self._stacks[r] += gtfo if self._is_v9001 else gtfo[::-1]
        return "".join(stack[-1] for stack in self._stacks.values())


class Problem1(_Problem):
    test_solution = "CMZ"
    my_solution = "TWSGQHNHL"

    _is_v9001 = False


class Problem2(_Problem):
    test_solution = "MCD"
    my_solution = "JNRSCDWPP"

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
