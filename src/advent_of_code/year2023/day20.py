from abc import ABC, abstractmethod
from collections import Counter, deque
from math import lcm
from typing import TYPE_CHECKING

from more_itertools import consume

from advent_of_code.problems import MultiLineProblem

if TYPE_CHECKING:
    from collections.abc import Iterator


class Module(ABC):
    def __init__(self, destinations: list[str]) -> None:
        self.destinations = destinations

    @abstractmethod
    def on_pulse(self, value: bool, sender: str) -> bool | None:  # noqa: FBT001
        pass


class BroadcastModule(Module):
    def on_pulse(self, value: bool, _sender: str) -> bool | None:  # noqa: FBT001
        return value


class FlipFlopModule(Module):
    def __init__(self, destinations: list[str]) -> None:
        super().__init__(destinations)
        self.state = False

    def on_pulse(self, value: bool, _sender: str) -> bool | None:  # noqa: FBT001
        if value:
            return None
        self.state = not self.state
        return self.state


class ConjunctionModule(Module):
    def __init__(self, destinations: list[str]) -> None:
        super().__init__(destinations)
        self.input_pulses: dict[str, bool] = {}

    def on_pulse(self, value: bool, sender: str) -> bool | None:  # noqa: FBT001
        self.input_pulses[sender] = value
        return not all(self.input_pulses.values())


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self) -> None:
        self.modules: dict[str, Module] = {}
        for line in self.lines:
            name, mod_str = line.split(" -> ")
            destinations = mod_str.split(", ")
            if name[0] == "%":
                self.modules[name[1:]] = FlipFlopModule(destinations)
            elif name[0] == "&":
                self.modules[name[1:]] = ConjunctionModule(destinations)
            elif name == "broadcaster":
                self.modules[name] = BroadcastModule(destinations)
            else:
                raise ValueError
        for source, m_source in self.modules.items():
            for dest in m_source.destinations:
                m_dest = self.modules.get(dest)
                if isinstance(m_dest, ConjunctionModule):
                    m_dest.input_pulses[source] = False

    def press_button(self, src: str = "", dst: str = "broadcaster") -> Iterator[bool]:
        pulse_queue = deque([(src, dst, False)])
        while pulse_queue:
            source, destination, value = pulse_queue.popleft()
            yield value
            if destination in self.modules:
                m_dest = self.modules[destination]
                resp = m_dest.on_pulse(value, source)
                if resp is not None:
                    pulse_queue.extend(
                        (destination, d, resp) for d in m_dest.destinations
                    )


class Problem1(_Problem):
    test_solution = 11687500  # 32000000
    puzzle_solution = 791120136

    def solution(self) -> int:
        c = Counter(v for _ in range(1000) for v in self.press_button())
        return c[False] * c[True]


class Problem2(_Problem):
    test_solution = None
    puzzle_solution = 215252378794009

    def solution(self) -> int:
        def cycle_lengths() -> Iterator[int]:
            flip_flops = {
                m for m in self.modules.values() if isinstance(m, FlipFlopModule)
            }
            for dest in self.modules["broadcaster"].destinations:
                n, all_flip_flops_off = 0, False
                while not all_flip_flops_off:
                    n += 1
                    consume(self.press_button("broadcaster", dest))
                    all_flip_flops_off = not any(f.state for f in flip_flops)
                yield n

        return lcm(*cycle_lengths())


# TEST_INPUT = """
# broadcaster -> a, b, c
# %a -> b
# %b -> c
# %c -> inv
# &inv -> a
# """

TEST_INPUT = """
broadcaster -> a
%a -> inv, con
&inv -> b
%b -> con
&con -> output
"""
