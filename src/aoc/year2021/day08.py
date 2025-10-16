from abc import ABC
from typing import TYPE_CHECKING

from more_itertools import partition

from aoc.problems import ParsedProblem
from aoc.utils import compose_number, contains, invert_dict

if TYPE_CHECKING:
    from collections.abc import Iterable


def __parse_codes(s: str) -> list[str]:
    return ["".join(sorted(code)) for code in s.split()]


class _Problem(ParsedProblem[tuple[list[str], list[str]], int], ABC):
    line_pattern = "{:codes} | {:codes}"


class Problem1(_Problem):
    test_solution = 26
    my_solution = 514

    def solution(self) -> int:
        return len([
            code
            for _, output in self.parsed_input
            for code in output
            if len(code) in (2, 3, 4, 7)
        ])


def decode_output(signal: Iterable[str], output: Iterable[str]) -> int:
    n = {}

    # numbers with unique length: (1, 4, 7, 8)
    signal, [n[1]] = partition(lambda s: len(s) == 2, signal)
    signal, [n[4]] = partition(lambda s: len(s) == 4, signal)
    signal, [n[7]] = partition(lambda s: len(s) == 3, signal)
    signal, [n[8]] = partition(lambda s: len(s) == 7, signal)

    # numbers with length 6: (0, 6, 9)
    signal_5, signal_6 = partition(lambda s: len(s) == 6, signal)
    # 7 doesn't fit completely in 6
    signal_6, [n[6]] = partition(lambda s: not contains(s, n[7]), signal_6)
    # 4 fits completely in 9, remaining number is 0
    [n[0]], [n[9]] = partition(lambda s: contains(s, n[4]), signal_6)

    # remaining numbers: (2, 3, 5)
    # 1 fits completely in 3
    signal_5, [n[3]] = partition(lambda s: contains(s, n[1]), signal_5)
    # 5 fits completely in 6, remaining number is 2
    [n[2]], [n[5]] = partition(lambda s: contains(n[6], s), signal_5)

    encoding = invert_dict(n)
    return compose_number(encoding[o] for o in output)


class Problem2(_Problem):
    test_solution = 61229
    my_solution = 1012272

    def solution(self) -> int:
        return sum(decode_output(signal, output) for signal, output in self.parsed_input)


TEST_INPUT = """
be cfbegad cbdgef fgaecd cgeb fdcge agebfd fecdb fabcd edb | fdgacbe cefdb cefbgd gcbe
edbfga begcd cbg gc gcadebf fbgde acbgfd abcde gfcbed gfec | fcgedb cgb dgebacf gc
fgaebd cg bdaec gdafb agbcfd gdcbef bgcad gfac gcb cdgabef | cg cg fdcagb cbg
fbegcd cbd adcefb dageb afcb bc aefdc ecdab fgdeca fcdbega | efabcd cedba gadfec cb
aecbfdg fbg gf bafeg dbefa fcge gcbea fcaegb dgceab fcbdga | gecf egdcabf bgf bfgea
fgeab ca afcebg bdacfeg cfaedg gcfdb baec bfadeg bafgc acf | gebdcfa ecba ca fadegcb
dbcfg fgd bdegcaf fgec aegbdf ecdfab fbedc dacgb gdcebf gf | cefg dcbef fcge gbcadfe
bdfegc cbegaf gecbf dfcage bdacg ed bedf ced adcbefg gebcd | ed bcgafe cdgba cbgef
egadfb cdbfeg cegd fecab cgb gbdefca cg fgcdab egfdb bfceg | gbdfcae bgc cg cgb
gcafb gcf dcaebfg ecagb gf abcdeg gaef cafbge fdbac fegbdc | fgae cfgab fg bagce
"""
