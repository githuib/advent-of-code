from abc import ABC, abstractmethod
from functools import cache
from typing import TYPE_CHECKING

from advent_of_code.problems import MultiLineProblem

if TYPE_CHECKING:
    from collections.abc import Iterator

Criteria = tuple[int, ...]  # tuple because @cache wants something hashable


@cache
def find(springs: str, criteria: Criteria) -> int:
    if not criteria:
        return "#" not in springs

    c = criteria[0]
    c_rest = criteria[1:]
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

    @abstractmethod
    def _find(self, s: str, c: Criteria) -> int:
        pass

    def solution(self) -> int:
        return sum(self._find(s, c) for s, c in self.records())


class Problem1(_Problem):
    test_solution = 21
    puzzle_solution = 7674

    def _find(self, s: str, c: Criteria) -> int:
        return find(s, c)


class Problem2(_Problem):
    test_solution = 525152
    puzzle_solution = 4443895258186

    def _find(self, s: str, c: Criteria) -> int:
        return find("?".join([s] * 5), c * 5)


TEST_INPUT = """
???.### 1,1,3
.??..??...?##. 1,1,3
?#?#?#?#?#?#?#? 1,3,1,6
????.#...#... 4,1,1
????.######..#####. 1,6,5
?###???????? 3,2,1
"""
