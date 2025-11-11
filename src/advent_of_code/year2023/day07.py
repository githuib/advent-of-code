from collections import Counter
from typing import TYPE_CHECKING

from advent_of_code.problems import MultiLineProblem

if TYPE_CHECKING:
    from collections.abc import Iterator


class _Problem(MultiLineProblem[int]):
    def __init__(self) -> None:
        self.cards = {str(i): i for i in range(2, 10)} | {
            "T": 10,
            "Q": 12,
            "K": 13,
            "A": 14,
        }

    def hands(self) -> Iterator[tuple[list[int], int]]:
        for line in self.lines:
            yield [self.cards[c] for c in line[:5]], int(line[6:])

    def hand_type(self, hand: Counter[int]) -> list[int]:
        return sorted(hand.values(), reverse=True) + [0] * (5 - len(hand))
        # return [v for _, v in hand.most_common()] + [0] * (5 - len(hand))

    def solution(self) -> int:
        def sort_key(elem: tuple[list[int], int]) -> tuple[list[int], list[int], int]:
            hand, bid = elem
            return self.hand_type(Counter(hand)), hand, bid

        sorted_hands = sorted(self.hands(), key=sort_key)
        return sum(i * bid for i, (_, bid) in enumerate(sorted_hands, 1))


class Problem1(_Problem):
    test_solution = 6440
    puzzle_solution = 251121738

    def __init__(self) -> None:
        super().__init__()
        self.cards["J"] = 11


class Problem2(_Problem):
    test_solution = 5905
    puzzle_solution = 251421071

    def __init__(self) -> None:
        super().__init__()
        self.cards["J"] = 1

    def hand_type(self, hand: Counter[int]) -> list[int]:
        if hand[1] < 5:
            jokers = hand.pop(1, 0)
            hand[hand.most_common(1)[0][0]] += jokers
        return super().hand_type(hand)


TEST_INPUT = """
32T3K 765
T55J5 684
KK677 28
KTJJT 220
QQQJA 483
"""
