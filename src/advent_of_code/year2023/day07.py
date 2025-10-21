from collections import Counter

from advent_of_code.problems import MultiLineProblem


class Problem1(MultiLineProblem[int]):
    test_solution = 6440
    my_solution = 251121738

    cards = {str(i): i for i in range(2, 10)} | {
        "T": 10,
        "J": 11,
        "Q": 12,
        "K": 13,
        "A": 14,
    }

    def hand_type(self, hand: Counter[int]) -> list[int]:
        return sorted(hand.values(), reverse=True) + [0] * (5 - len(hand))
        # return [v for _, v in hand.most_common()] + [0] * (5 - len(hand))

    def solution(self) -> int:
        hands = [
            ([self.cards[c] for c in line[:5]], int(line[6:])) for line in self.lines
        ]
        return sum(
            i * bid
            for i, (_, _, bid) in enumerate(
                sorted(
                    (self.hand_type(Counter(hand)), hand, bid) for hand, bid in hands
                ),
                1,
            )
        )


class Problem2(Problem1):
    test_solution = 5905
    my_solution = 251421071

    def __init__(self):
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
