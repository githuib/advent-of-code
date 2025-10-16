from abc import ABC
from copy import copy
from dataclasses import dataclass
from typing import NamedTuple

from yachalk import chalk

from aoc import log
from aoc.problems import MultiLineProblem
from aoc.search import DijkstraState


@dataclass
class Room:
    _amphipod_type: int
    _size: int
    _content: list[int]

    def __repr__(self) -> str:
        return f"{self._content}"

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


class Variables(NamedTuple):
    rooms: list[Room]
    hallway: list[int]


class AmphipodState(DijkstraState[Constants, Variables]):
    def __hash__(self) -> int:
        return hash(f"{self.v.rooms}{self.v.hallway}")

    @property
    def is_finished(self) -> bool:
        return bool(self.cost and not sum(self.v.hallway))

    def _can_move(self, room: int, hall: int) -> bool:
        # Trust me, I'm an engineer
        return not (
            (hall < room + 1 and any(self.v.hallway[hall + 1:room + 2])) or
            (hall > room + 2 and any(self.v.hallway[room + 2:hall]))
        )

    def _move(self, amphipod: int, r: int, h: int, into_room: bool) -> AmphipodState:
        rooms = [copy(room) for room in self.v.rooms]
        hallway = self.v.hallway[:]
        if into_room:
            rooms[r].add(hallway[h])
            hallway[h] = 0
        else:
            hallway[h] = rooms[r].remove()
        # Trust me, I'm an engineer
        steps = abs(h * 2 - r * 2 - 3) + 1 - int(h in (0, 6)) + rooms[r].spots_left - int(into_room)
        return self.move(steps * 10 ** (amphipod - 1), rooms=rooms, hallway=hallway)

    @property
    def next_states(self) -> list[AmphipodState]:
        return [
            # all states that move an amphipod out of a room
            self._move(room.first, r, h, into_room=False)
            for r, room in enumerate(self.v.rooms) if not room.is_clean and not room.is_empty
            for h, amphipod in enumerate(self.v.hallway) if not amphipod and self._can_move(r, h)
        ] + [
            # all states that move an amphipod into a room
            self._move(amphipod, r, h, into_room=True)
            for h, amphipod in enumerate(self.v.hallway) if amphipod
            for r, room in enumerate(self.v.rooms) if room.can_add(amphipod) and self._can_move(r, h)
        ]

    def __repr__(self) -> str:
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
        w: str = chalk.hex("eee").bg_hex("848")("#")
        e: str = chalk.hex("332").bg_hex("111")(".")

        def q(cs: str) -> str:
            return "".join(e if c == "." else chalk.hex("111").bg_hex("0af")(c) for c in cs)

        def p(i):  # ik zat in tram 5 en m'n lul stond stijf
            return "  " if i else w * 2
        s = ".ABCD"
        h = ".".join(s[a] for a in self.v.hallway)
        rs = self.c.room_size
        return (
            w * 13 + "\n" + w + q(h[0] + h[2:-2] + h[-1]) + w + "\n" + "\n".join(p(i) + w + w.join(
                q(s[r.get(rs - i - 1)]) for r in self.v.rooms
            ) + w + p(i) for i in range(rs)) + "\n  " + w * 9 + "  "
        )


class _Problem(MultiLineProblem[int], ABC):
    def shortest_path(self, is_part_1: bool) -> int:
        lines = self.lines[5:1:-3] if is_part_1 else self.lines[5:1:-1]
        room_size = len(lines)
        path = AmphipodState.find_path(
            Variables(rooms=[
                Room(name, room_size, [{"A": 1, "B": 2, "C": 3, "D": 4}[c] for c in content])
                for name, content in enumerate(zip(*[line[3:10:2] for line in lines], strict=False), 1)
            ], hallway=[0] * 7),
            Constants(room_size),
        )

        for i, state in enumerate(path.states):
            if i:
                log.debug("Step %d, cost so far: %d", i, state.cost)
                log.debug(" ")
            log.debug(state)
            log.debug(" ")

        return path.length


class Problem1(_Problem):
    test_solution = 12521
    my_solution = 12530

    def solution(self) -> int:
        return self.shortest_path(True)


class Problem2(_Problem):
    test_solution = 44169
    my_solution = 50492

    def solution(self) -> int:
        return self.shortest_path(False)


TEST_INPUT = """
#############
#...........#
###B#C#B#D###
  #D#C#B#A#
  #D#B#A#C#
  #A#D#C#A#
  #########
"""
