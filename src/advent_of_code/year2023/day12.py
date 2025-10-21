from abc import ABC
from functools import cache
from typing import TYPE_CHECKING

from advent_of_code.problems import MultiLineProblem

if TYPE_CHECKING:
    from collections.abc import Iterator


@cache
def find(springs: str, criteria: tuple[int, ...]) -> int:
    if not criteria:
        return "#" not in springs

    c, c_rest = criteria[0], criteria[1:]
    result: int = 0
    for i in range(len(springs) - sum(criteria) - len(criteria) + 2):
        if "#" in springs[:i]:
            break
        nxt = i + c
        if "." not in springs[i:nxt] and springs[nxt : nxt + 1] != "#":
            result += find(springs[nxt + 1 :], c_rest)
    return result


class _Problem(MultiLineProblem[int], ABC):
    def records(self) -> Iterator[tuple[str, tuple[int, ...]]]:
        for line in self.lines:
            springs, criteria = line.split()
            yield springs, tuple(int(c) for c in criteria.split(","))


class Problem1(_Problem):
    test_solution = 21
    my_solution = 7674

    def solution(self) -> int:
        return sum(find(s, c) for s, c in self.records())


class Problem2(_Problem):
    test_solution = 525152
    my_solution = 4443895258186

    def solution(self) -> int:
        return sum(find("?".join([s] * 5), c * 5) for s, c in self.records())


TEST_INPUT = """
???.### 1,1,3
.??..??...?##. 1,1,3
?#?#?#?#?#?#?#? 1,3,1,6
????.#...#... 4,1,1
????.######..#####. 1,6,5
?###???????? 3,2,1
"""
