from abc import ABC
from itertools import batched

from advent_of_code.geo2d import P2, Dir2
from advent_of_code.year2019.intcode import IntcodeProblem

DIRECTIONS = [Dir2.up, Dir2.right, Dir2.down, Dir2.left]


class _Problem[T](IntcodeProblem[T], ABC):
    def paint_panels(self, starting_color: int) -> dict[P2, int]:
        runner = self.computer.run_to_next_output(starting_color)
        x, y, direction = 0, 0, 0
        painted_panels = {}

        for color, turn in batched(runner, 2, strict=True):
            # Paint current panel.
            painted_panels[x, y] = color

            # Move robot to next panel.
            direction = (direction + [-1, 1][turn] + 4) % 4
            dx, dy = DIRECTIONS[direction]
            x, y = x + dx, y + dy

            # Feed color of next panel to computer.
            self.computer.inputs.append(painted_panels.get((x, y), 0))

        return painted_panels


class Problem1(_Problem[int]):
    my_solution = 2129

    def solution(self) -> int:
        return len(self.paint_panels(starting_color=0))


class Problem2(_Problem[str]):
    my_solution = """
░███░░████░░██░░█░░█░███░░░██░░████░█
░█░░█░█░░░░█░░█░█░█░░█░░█░█░░█░░░░█░█
░█░░█░███░░█░░░░██░░░█░░█░█░░░░░░█░░█
░███░░█░░░░█░░░░█░█░░███░░█░██░░█░░░█
░█░░░░█░░░░█░░█░█░█░░█░█░░█░░█░█░░░░█
░█░░░░████░░██░░█░░█░█░░█░░███░████░████
"""

    def solution(self) -> str:
        grouped_by_y: dict[int, list[int]] = {}
        for (x, y), color in self.paint_panels(starting_color=1).items():
            if color:
                grouped_by_y.setdefault(y, []).append(x)
        return "\n".join(
            "".join("█" if x in row else "░" for x in range(max(row) + 1))
            for _, row in sorted(grouped_by_y.items())
        )
