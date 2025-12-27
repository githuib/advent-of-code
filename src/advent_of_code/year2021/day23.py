from abc import ABC, abstractmethod
from collections.abc import Hashable
from copy import copy
from dataclasses import dataclass, field
from functools import cached_property
from typing import TYPE_CHECKING, NamedTuple

from based_utils.algo import DijkstraState
from kleur import Highlighter
from ternimator import AnimParams

from advent_of_code import C, log
from advent_of_code.problems import MultiLineProblem
from advent_of_code.utils import lowlighted, upper_to_num

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass
class Room(Hashable):
    _amphipod_type: int
    _size: int
    _content: list[int]

    def __repr__(self) -> str:
        return f"{self._content}"

    def __hash__(self) -> int:
        return hash((self._amphipod_type, self._size, *self._content))

    def __copy__(self) -> Room:
        return Room(self._amphipod_type, self._size, self._content[:])

    @property
    def first(self) -> int:
        return self._content[-1]

    def get(self, i: int) -> int:
        try:
            return self._content[i]
        except IndexError:
            return 0

    @property
    def is_clean(self) -> bool:
        return all(amphipod == self._amphipod_type for amphipod in self._content)

    @property
    def is_empty(self) -> bool:
        return not self._content

    @property
    def is_full(self) -> bool:
        return len(self._content) == self._size

    @property
    def spots_left(self) -> int:
        return self._size - len(self._content)

    def can_add(self, amphipod: int) -> bool:
        return amphipod == self._amphipod_type and not self.is_full and self.is_clean

    def add(self, amphipod: int) -> None:
        self._content.append(amphipod)

    def remove(self) -> int:
        return self._content.pop()


class Constants(NamedTuple):
    room_size: int


@dataclass
class Variables(Hashable):
    rooms: list[Room]
    hallway: list[int] = field(default_factory=lambda: [0] * 7)

    def __hash__(self) -> int:
        return hash((*[hash(r) for r in self.rooms], *self.hallway))


class AmphipodState(DijkstraState[Constants, Variables]):
    def __hash__(self) -> int:
        return hash(f"{self.v.rooms}{self.v.hallway}")

    @property
    def is_end_state(self) -> bool:
        return bool(self.cost and not sum(self.v.hallway))

    def _can_move(self, room: int, hall: int) -> bool:
        # Trust me, I'm an engineer
        return not (
            (hall < room + 1 and any(self.v.hallway[hall + 1 : room + 2]))
            or (hall > room + 2 and any(self.v.hallway[room + 2 : hall]))
        )

    def _move(self, amphipod: int, r: int, h: int, *, into_room: bool) -> AmphipodState:
        rooms = [copy(room) for room in self.v.rooms]
        room = rooms[r]
        hallway = self.v.hallway[:]

        if into_room:
            room.add(hallway[h])
            hallway[h] = 0
        else:
            hallway[h] = room.remove()

        is_on_hall_end = h in (0, 6)
        # Trust me, I'm an engineer
        steps = (
            abs(h * 2 - r * 2 - 3)
            + 1
            - int(is_on_hall_end)
            + room.spots_left
            - int(into_room)
        )
        return self.move(
            Variables(rooms, hallway), distance=steps * 10 ** (amphipod - 1)
        )

    @property
    def next_states(self) -> Iterator[AmphipodState]:
        # all states that move an amphipod out of a room
        for r, room in enumerate(self.v.rooms):
            if not room.is_clean and not room.is_empty:
                for h, amphipod in enumerate(self.v.hallway):
                    if not amphipod and self._can_move(r, h):
                        yield self._move(room.first, r, h, into_room=False)

        # all states that move an amphipod into a room
        for h, amphipod in enumerate(self.v.hallway):
            if amphipod:
                for r, room in enumerate(self.v.rooms):
                    if room.can_add(amphipod) and self._can_move(r, h):
                        yield self._move(amphipod, r, h, into_room=True)

    def to_lines(self) -> Iterator[str]:
        """
        Code is not meant to look readable, just to print the mushroom.

        #############
        #CA...B.C.BB#
        ###.#.#.#D###
          #D#.#.#A#
          #D#B#.#C#
          #A#D#C#A#
          #########
        """
        edge = C.indigo.dark
        dot = C.poison.very_dark
        amph = C.pink
        w = lowlighted(edge)("#")

        def colored_char(c: str) -> str:
            color = dot if c == "." else amph
            return Highlighter(color)(c)

        def colored(cs: str) -> str:
            return "".join(colored_char(c) for c in cs)

        def p(r: int) -> str:
            return "  " if r > 0 else w * 2

        s = ".ABCD"
        h = ".".join(s[a] for a in self.v.hallway)
        rs = self.c.room_size
        yield f"{w * 13}"
        yield f"{w + colored(h[0] + h[2:-2] + h[-1]) + w}"
        for i in range(rs):
            yield (
                p(i)
                + w
                + w.join(colored(s[r.get(rs - i - 1)]) for r in self.v.rooms)
                + w
                + p(i)
            )
        yield f"  {w * 9}  "


class _Problem(MultiLineProblem[int], ABC):
    @property
    @abstractmethod
    def _input_lines(self) -> list[str]:
        pass

    @property
    def _room_content(self) -> Iterator[list[int]]:
        room_input: Iterator[tuple[str, ...]] = zip(
            *(line[3:10:2] for line in self._input_lines), strict=True
        )
        for content in room_input:
            yield [upper_to_num(c) for c in content]

    def solution(self) -> int:
        room_size = len(self._input_lines)
        rooms = [
            Room(name, room_size, content)
            for name, content in enumerate(self._room_content, 1)
        ]
        path = AmphipodState.find_path(Variables(rooms), Constants(room_size))

        def fmt(item: tuple[int, AmphipodState]) -> Iterator[str]:
            i, state = item
            yield f"Step {i}, cost so far: {state.cost}" if i > 0 else ""
            yield ""
            yield from state.to_lines()
            yield ""

        log.debug_animated(
            enumerate(path.states), AnimParams(item_to_lines=fmt, fps=10)
        )
        return path.length


class Problem1(_Problem):
    test_solution = 12521
    puzzle_solution = 12530

    @cached_property
    def _input_lines(self) -> list[str]:
        return self.lines[5:1:-3]


class Problem2(_Problem):
    test_solution = 44169
    puzzle_solution = 50492

    @cached_property
    def _input_lines(self) -> list[str]:
        return self.lines[5:1:-1]


TEST_INPUT = """
#############
#...........#
###B#C#B#D###
  #D#C#B#A#
  #D#B#A#C#
  #A#D#C#A#
  #########
"""
