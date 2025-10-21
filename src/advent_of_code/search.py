from abc import ABC, abstractmethod
from collections import deque
from functools import cached_property
from queue import PriorityQueue, Queue
from typing import TYPE_CHECKING, Self

from advent_of_code import log

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


class ShortestPath[S: State](ABC):
    def __init__(self, initial_state: S):
        self.end_state = self._initial_state = initial_state
        self.visited = set[S]()

    @abstractmethod
    def from_queue(self) -> Iterator[S]:
        pass

    @abstractmethod
    def to_queue(self, state: S) -> None:
        pass

    def find(self: Self) -> Self:
        state = self._initial_state
        self.to_queue(state)
        for state in self.from_queue():
            if state.is_finished:
                break
            for next_state in state.next_states:
                if next_state not in self.visited and self._handle_state(next_state):
                    self.to_queue(next_state)
            self._on_state_processed(state)
        else:
            log.warning(
                "Queue empty before reaching the end criteria at state:\n%s", state
            )
        self.end_state = state
        return self

    @abstractmethod
    def _on_state_processed(self, state: S) -> None:
        pass

    @abstractmethod
    def _handle_state(self, state: S) -> bool:
        pass

    @property
    def states(self) -> list[S]:
        """Get the complete path by traversing back to the start."""
        return list(reversed(list(self.end_state.prev_states)))

    @property
    def length(self) -> int:
        return self.end_state.cost


class ShortestPathBFS[B: BFSState](ShortestPath[B]):
    def __init__(self, initial_state: B) -> None:
        super().__init__(initial_state)
        self._queue: deque[B] = deque()

    def from_queue(self) -> Iterator[B]:
        while self._queue:
            yield self._queue.popleft()

    def to_queue(self, state: B) -> None:
        self._queue.append(state)

    def _on_state_processed(self, state: B) -> None:
        pass

    def _handle_state(self, state: B) -> bool:
        self.visited.add(state)
        return True


class ShortestPathDijkstra[D: DijkstraState](ShortestPath[D]):
    def __init__(self, initial_state: D) -> None:
        super().__init__(initial_state)
        self._queue: Queue[D] = PriorityQueue()
        self._costs: dict[D, int] = {}

    def from_queue(self) -> Iterator[D]:
        while not self._queue.empty():
            yield self._queue.get_nowait()

    def to_queue(self, state: D) -> None:
        self._queue.put_nowait(state)

    def _on_state_processed(self, state: D) -> None:
        self.visited.add(state)

    def _handle_state(self, state: D) -> bool:
        if (old_cost := self._costs.get(state)) and state.cost >= old_cost:
            # you can do better than that
            return False
        # most efficient route to this state so far: update cost
        self._costs[state] = state.cost
        return True


class State[C, V](ABC):
    path_finder_cls: type[ShortestPath]
    c: C

    v: V
    prev: Self | None
    cost: int

    def __init__(self: Self, variables: V, prev: Self | None = None, cost: int = 0):
        self.v = variables
        self.prev = prev
        self.cost = cost

    @classmethod
    def find_path(cls: type[Self], variables: V, constants: C) -> ShortestPath[Self]:
        cls.c = constants
        return cls(variables).find_path_from_current_state()

    def find_path_from_current_state(self: Self) -> ShortestPath[Self]:
        return self.path_finder_cls(self).find()

    @property
    @abstractmethod
    def is_finished(self) -> bool:
        pass

    @property
    @abstractmethod
    def next_states(self: Self) -> Iterable[Self]:
        pass

    @property
    def prev_states(self) -> Iterator[Self]:
        state: Self | None = self
        assert state is not None
        while state:
            yield state
            state = state.prev

    def move(self: Self, distance: int = 1, **kwargs) -> Self:
        return self.__class__(self.v.__class__(**kwargs), self, self.cost + distance)

    def __hash__(self) -> int:
        return hash(self.v)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, State):
            return self.v == other.v
        return NotImplemented


class BFSState[C, V](State[C, V], ABC):
    path_finder_cls = ShortestPathBFS


class DijkstraState[C, V](State[C, V], ABC):
    path_finder_cls = ShortestPathDijkstra

    def __lt__(self, other: object) -> bool:
        """By defining this, states with a lower cost will have priority in the queue."""
        if isinstance(other, DijkstraState):
            return self.cost < other.cost
        return NotImplemented


class AStarState[C, V](DijkstraState[C, V], ABC):
    def __init__(self: Self, variables: V, prev: Self | None = None, cost: int = 0):
        super().__init__(variables, prev, cost)

    def __lt__(self, other: object) -> bool:
        """By defining this, states with a lower score (cost + heuristic) will have priority in the queue."""
        if isinstance(other, AStarState):
            return self.score < other.score
        return NotImplemented

    @cached_property
    def score(self) -> int:
        return self.cost + self.heuristic

    @property
    @abstractmethod
    def heuristic(self) -> int:
        """Basically turns the Dijkstra algo into A*"""
