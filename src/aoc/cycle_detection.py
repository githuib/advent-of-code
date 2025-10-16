from dataclasses import dataclass
from itertools import islice, tee
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator


class CycleNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class Cycle:
    start: int
    length: int


def floyd[T](it: Iterator[T]) -> Cycle:
    """
    https://en.wikipedia.org/wiki/Cycle_detection#Floyd's_tortoise_and_hare
    """
    it_tortoise, it_cousin, it_hare = tee(it, 3)
    for tortoise, hare in zip(it_tortoise, islice(it_hare, 1, None, 2), strict=False):
        # 🐇 goes like a complete maniac, twice as fast as 🐢. When they meet again,
        # this means 🐇 has walked a full cycle more and 🐢 has walked exactly one cycle length from the start.
        if tortoise == hare:
            break
    for cycle_start, (tortoise, cousin) in enumerate(zip(it_tortoise, it_cousin, strict=False)):
        # 🐢's cousin leaves from the beginning as well, while the other 🐢 keeps on going.
        # They should meet as soon as the cycle starts, since the part of the cycle 🐢 didn't
        # walk yet is what he wasted while walking towards the cycle start.
        if tortoise == cousin:
            for cycle_length, tortwice in enumerate(it_tortoise, 1):
                # Cousin 🐢 stopped to role a spliff, other 🐢 didn't notice and walks another
                # round until they can light it up together.
                if tortwice == cousin:
                    return Cycle(cycle_start, cycle_length)
    raise CycleNotFoundError


def brent[T](it: Iterator[T]) -> Cycle:
    """
    https://en.wikipedia.org/wiki/Cycle_detection#Brent's_algorithm
    """
    it_tortoise, it_cousin, it_hare = tee(it, 3)
    power = cycle_length = 1
    tortoise = None
    for hare in it_hare:
        # 🐇 keeps sprinting until he meets 🐢 again.
        if hare == tortoise:
            break
        if power == cycle_length:
            tortoise = hare
            power *= 2
            cycle_length = 0
        cycle_length += 1
    # 🐢's cousin leaves from the beginning as well, walking exactly the length of one cycle.
    # After that, they both move at same speed until they meet exactly at the start of the cycle.
    for cycle_start, (tortoise, cousin) in enumerate(zip(it_tortoise, islice(it_cousin, cycle_length, None), strict=False)):
        if tortoise == cousin:
            return Cycle(cycle_start, cycle_length)
    raise CycleNotFoundError
