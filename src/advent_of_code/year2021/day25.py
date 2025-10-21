from yachalk import chalk

from advent_of_code import log
from advent_of_code.geo2d import P2, Grid2
from advent_of_code.problems import GridProblem, MultiLineProblem
from advent_of_code.utils import first_duplicate

SeaCucumbers = list[set[P2]]


def board_str(sea_cucumbers: SeaCucumbers) -> str:
    east, south = sea_cucumbers
    board = Grid2[str](dict.fromkeys(east, ">") | dict.fromkeys(south, "v"))
    return board.to_str(lambda _, v: {
        None: chalk.hex("0af").bg_hex("0af")("."),
        ">": chalk.hex("888").bg_hex("888")(">"),
        "v": chalk.hex("666").bg_hex("666")("v"),
    }[v])


class Problem1(GridProblem[int]):
    test_solution = 58
    my_solution = 389

    def __init__(self):
        self.width = self.grid.width
        self.height = self.grid.height
        self.sea_cucumbers = [self.grid.points_with_values(c) for c in ">v"]

    def __iter__(self):
        return self

    def __next__(self):
        old = east, south = self.sea_cucumbers
        east = {((x, y) if (
            (p := ((x + 1) % self.width, y)) in east or p in south
        ) else p) for (x, y) in east}
        self.sea_cucumbers = east, {((x, y) if (
            (p := (x, (y + 1) % self.height)) in east or p in south
        ) else p) for (x, y) in south}
        return old

    def solution(self) -> int:
        n, sea_cucumbers = first_duplicate(self)
        log.debug(board_str(sea_cucumbers))
        return n


class Problem2(MultiLineProblem[None]):
    def solution(self) -> None:
        print("""
         __  |__
       __L L_|L L__
 ...[+(____________)
        C_________/
""")


TEST_INPUT = """
v...>>.vv>
.vv>>.vv..
>>.>v>...v
>>v>>.>.v.
v>v.vv.v..
>.>>..v...
.vv..>.>v.
v.v..>>v.v
....v..v.>
"""
