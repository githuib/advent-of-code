from abc import ABC

from advent_of_code.problems import MultiLineProblem


class Board:
    def __init__(self, input_lines: list[str]):
        # parse 5 x 5 bingo board from input
        self.data = [
            [int(x) for x in line.split()]
            for line in input_lines
        ]
        # data with rows and columns swapped
        self.inverted_data = [list(col) for col in zip(*self.data, strict=False)]
        self.has_bingo = False

    def draw_number(self, n: int) -> None:
        for r, row in enumerate(self.data):
            try:
                # check if row contains drawn number
                c = row.index(n)
            except ValueError:
                continue
            else:
                # mark drawn number by setting it to zero
                col = self.inverted_data[c]
                row[c] = 0
                col[r] = 0
                # check for bingo (either current row or column only contains zeros)
                self.has_bingo = sum(row) == 0 or sum(col) == 0
                break


class _Problem(MultiLineProblem[int], ABC):
    squid_mode: bool

    def solution(self) -> int:
        numbers = [int(x) for x in self.lines[0].split(",")]
        boards = [
            Board(self.lines[b:b + 5])
            # every board takes up 5 lines + 1 newline = 6
            for b in range(2, len(self.lines), 6)
        ]

        for n in numbers:
            for board in boards:
                if board.has_bingo:
                    # skip already finished boards
                    continue

                board.draw_number(n)
                if (
                    board.has_bingo
                    and (not self.squid_mode or all(b.has_bingo for b in boards))
                ):
                    return sum(x for row in board.data for x in row) * n

        return 0


class Problem1(_Problem):
    test_solution = 4512
    my_solution = 8136

    squid_mode = False


class Problem2(_Problem):
    test_solution = 1924
    my_solution = 12738

    squid_mode = True


TEST_INPUT = """
7,4,9,5,11,17,23,2,0,14,21,24,10,16,13,6,15,25,12,22,18,20,8,19,3,26,1

22 13 17 11  0
 8  2 23  4 24
21  9 14 16  7
 6 10  3 18  5
 1 12 20 15 19

 3 15  0  2 22
 9 18 13 17  5
19  8  7 25 23
20 11 10 24  4
14 21 16 12  6

14 21 17 24  4
10 16 15  9 19
18  8 23 26 20
22 11 13  6  5
 2  0 12  3  7
"""
