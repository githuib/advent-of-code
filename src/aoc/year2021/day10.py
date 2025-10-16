from abc import ABC
from typing import TYPE_CHECKING, Literal, cast

from aoc.problems import MultiLineProblem

if TYPE_CHECKING:
    from collections.abc import Iterator

brackets = {"(": ")", "[": "]", "{": "}", "<": ">"}
broken_scores = {None: 0, ")": 3, "]": 57, "}": 1197, ">": 25137}
missing_scores = {"(": 1, "[": 2, "{": 3, "<": 4}

OpeningBracket = Literal["(", "[", "{", "<"]
ClosingBracket = Literal[")", "]", "}", ">"]
Bracket = OpeningBracket | ClosingBracket


def parse_char(
    line: list[Bracket],
    stack: list[OpeningBracket] | None = None,
) -> tuple[list[OpeningBracket], ClosingBracket | None]:
    stack = stack or []
    if not line:
        # all characters parsed, no broken closing bracket encountered
        return stack, None

    c, *line = line
    if c in brackets:
        # opening bracket, add to stack
        return parse_char(line, [cast("OpeningBracket", c), *stack])

    s, *stack = stack
    if c == brackets[s]:
        # closing bracket matching, pop from stack
        return parse_char(line, stack)

    # closing bracket bracket not matching:
    # return stack and broken closing bracket
    return stack, cast("ClosingBracket", c)


def calc_missing_score(stack, score):
    if not stack:
        return score
    c, *stack = stack
    return calc_missing_score(stack, score * 5 + missing_scores[c])


class _Problem(MultiLineProblem[int], ABC):
    def parsed_lines(self) -> Iterator[tuple[list[OpeningBracket], ClosingBracket | None]]:
        for line in self.lines:
            yield parse_char(cast("list[Bracket]", list(line)))


class Problem1(_Problem):
    test_solution = 26397
    my_solution = 216297

    def solution(self) -> int:
        return sum(broken_scores[broken] for _, broken in self.parsed_lines())


class Problem2(_Problem):
    test_solution = 288957
    my_solution = 2165057169

    def solution(self) -> int:
        scores = [
            calc_missing_score(stack, 0)
            for stack, broken in self.parsed_lines()
            if not broken
        ]
        return sorted(scores)[len(scores) // 2]


TEST_INPUT = """
[({(<(())[]>[[{[]{<()<>>
[(()[<>])]({[<{<<[]>>(
{([(<{}[<>[]}>{[]{[(<()>
(((({<>}<{<{<>}{[]{[]{}
[[<[([]))<([[{}[[()]]]
[{[{({}]{}}([{[{{{}}([]
{<[[]]>}<{[{[{[]{()[[[]
[<(<(<(<{}))><([]([]()
<{([([[(<>()){}]>(<<{{
<{([{{}}[<[[[<>{}]]]>[]]
"""
