from more_itertools import last

from advent_of_code import log
from advent_of_code.geo2d import Grid2
from advent_of_code.year2019.intcode import IntcodeProblem

# ORDER = [0, 3, 1, 2]  # UP, RIGHT, DOWN, LEFT


class Problem1(IntcodeProblem[int]):
    my_solution = 2804

    def solution(self) -> int:
        grid = "".join(
            chr(output) for output in self.computer.run_to_next_output()
        ).splitlines()

        return sum(
            row * col
            for row in range(2, len(grid) - 2, 2)
            for col in range(2, len(grid[0]) - 2, 2)
            if (
                grid[row][col] == "#"
                and grid[row - 1][col] == "#"
                and grid[row + 1][col] == "#"
                and grid[row][col - 1] == "#"
                and grid[row][col + 1] == "#"
            )
        )


# E = Literal['L', 'R'] | int


# def to_path(grid: Mat2[int], position: P2) -> list[E]:
#     path: list[E] = []
#     direction = 0
#
#     while True:
#         for i in [0, -1, 2]:
#             direction = (direction + i + 4) % 4
#             x, y = position
#             dx, dy = Dir2.direct_neighbors[ORDER[direction]]
#             new_pos = x + dx, y + dy
#             if not grid.get(new_pos):
#                 continue
#             position = new_pos
#             if i == -1:
#                 path += ['L', 0]
#             elif i == 2:
#                 path += ['R', 0]
#             path[-1] += 1
#             break
#         else:
#             return path


# def find_patterns(path):
#     n = 4
#     c = n
#     segment = path[0:n]
#     res = [[]]
#     for i in range(len(path)):
#         if c > 0:
#             c -= 1
#             continue
#         test = path[i:i + n]
#         if test == segment:
#             # print(i, '--------------------- found')
#             res.append([])
#             c = n - 1
#         else:
#             # print(i, test[0])
#             res[-1].append(test[0])
#             # if res[-1]:
#             #     res[-1].append(test[-1])
#             # else:
#             #     res[-1] += test
#             # print(path[i:i + n])
#     print(res)


class Problem2(Problem1):
    my_solution = 833429

    def solution(self) -> int:
        self.computer.program[0] = 2

        runner = self.computer.run_to_next_output()

        # stage 1: Constructed path from first output
        # grid = Matrix2D[int]()
        grid = Grid2[int]()
        start_pos = None
        x = 0
        y = 0
        char_values = {".": 0, "#": 1, "^": 2}
        for output in runner:
            c = chr(output)
            if c == "\n":
                if x == 0:
                    break
                x = 0
                y += 1
            else:
                grid[x, y] = char_values[c]
                if c == "^":
                    start_pos = (x, y)
                x += 1
        assert start_pos is not None
        log.debug(grid)
        # for a, b in batched(to_path(grid, start_pos), 2, strict=True):
        #     print(a, b)

        # it: Iterator[tuple[str, int]] = batched(to_path(grid, start_pos), 2, strict=True)
        # logging.debug(f'path: {[
        #     f'{d}{str(n) if n < 10 else f"{n // 2}{n // 2}"}'
        #     for d, n in it
        # ]}')

        # find_patterns(path)
        # for d, n in chunked(path, 2):
        #     print(d, str(n) if n < 10 else f'{n // 2}{n // 2}')

        # Stage 2: Patterns derived manually after looking at path
        self.computer.inputs = [
            ord(c)
            for s in [
                "ABACABCCAB",
                "R8L55R8",
                "R66R8L8L66",
                "L66L55L8",
                "n",
            ]
            for c in ",".join(s) + "\n"
        ]
        return last(runner)


TEST_INPUT = ""
