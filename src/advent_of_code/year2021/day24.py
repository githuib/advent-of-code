from abc import ABC
from collections import deque

from advent_of_code import log
from advent_of_code.problems import MultiLineProblem


class ALU:
    def __init__(self):
        self.vars = {}
        self.inputs = None

    def run_program(self, lines, inputs):
        self.vars = {"w": 0, "x": 0, "y": 0, "z": 0}
        self.inputs = deque(inputs)
        for line in lines:
            self.process(*line.split())

    def process(self, instruction, var, *args):
        if args:
            arg = args[0]
            try:
                arg = int(arg)
            except ValueError:
                arg = self.vars[arg]
        else:
            arg = None
        match instruction:
            case "inp":
                self.vars[var] = self.inputs.popleft()
            case "add":
                self.vars[var] += arg
            case "mul":
                self.vars[var] *= arg
            case "div":
                self.vars[var] //= arg
            case "mod":
                self.vars[var] %= arg
            case "eql":
                self.vars[var] = int(self.vars[var] == arg)


class _Problem(MultiLineProblem[int], ABC):
    def solution(self) -> int:
        n = self.my_solution
        alu = ALU()
        alu.run_program(self.lines, [int(d) for d in str(n)])
        log.debug(alu.vars)
        return n or 0


class Problem1(_Problem):
    test_solution = None
    my_solution = 99691891979938


class Problem2(_Problem):
    test_solution = None
    my_solution = 27141191213911


notes = """
inp w   mul x 0  add x z  mod x 26  div z 1   add x 13  eql x w  eql x 0  mul y 0  add y 25  mul y x  add y 1  mul z y  mul y 0  add y w  add y 0  mul y x  add z y
inp w   mul x 0  add x z  mod x 26  div z 1   add x 11  eql x w  eql x 0  mul y 0  add y 25  mul y x  add y 1  mul z y  mul y 0  add y w  add y 3  mul y x  add z y
inp w   mul x 0  add x z  mod x 26  div z 1   add x 14  eql x w  eql x 0  mul y 0  add y 25  mul y x  add y 1  mul z y  mul y 0  add y w  add y 8  mul y x  add z y
inp w   mul x 0  add x z  mod x 26  div z 26  add x -5  eql x w  eql x 0  mul y 0  add y 25  mul y x  add y 1  mul z y  mul y 0  add y w  add y 5  mul y x  add z y
inp w   mul x 0  add x z  mod x 26  div z 1   add x 14  eql x w  eql x 0  mul y 0  add y 25  mul y x  add y 1  mul z y  mul y 0  add y w  add y 13 mul y x  add z y
inp w   mul x 0  add x z  mod x 26  div z 1   add x 10  eql x w  eql x 0  mul y 0  add y 25  mul y x  add y 1  mul z y  mul y 0  add y w  add y 9  mul y x  add z y
inp w   mul x 0  add x z  mod x 26  div z 1   add x 12  eql x w  eql x 0  mul y 0  add y 25  mul y x  add y 1  mul z y  mul y 0  add y w  add y 6  mul y x  add z y
inp w   mul x 0  add x z  mod x 26  div z 26  add x -14 eql x w  eql x 0  mul y 0  add y 25  mul y x  add y 1  mul z y  mul y 0  add y w  add y 1  mul y x  add z y
inp w   mul x 0  add x z  mod x 26  div z 26  add x -8  eql x w  eql x 0  mul y 0  add y 25  mul y x  add y 1  mul z y  mul y 0  add y w  add y 1  mul y x  add z y
inp w   mul x 0  add x z  mod x 26  div z 1   add x 13  eql x w  eql x 0  mul y 0  add y 25  mul y x  add y 1  mul z y  mul y 0  add y w  add y 2  mul y x  add z y
inp w   mul x 0  add x z  mod x 26  div z 26  add x  0  eql x w  eql x 0  mul y 0  add y 25  mul y x  add y 1  mul z y  mul y 0  add y w  add y 7  mul y x  add z y
inp w   mul x 0  add x z  mod x 26  div z 26  add x -5  eql x w  eql x 0  mul y 0  add y 25  mul y x  add y 1  mul z y  mul y 0  add y w  add y 5  mul y x  add z y
inp w   mul x 0  add x z  mod x 26  div z 26  add x -9  eql x w  eql x 0  mul y 0  add y 25  mul y x  add y 1  mul z y  mul y 0  add y w  add y 8  mul y x  add z y
inp w   mul x 0  add x z  mod x 26  div z 26  add x -1  eql x w  eql x 0  mul y 0  add y 25  mul y x  add y 1  mul z y  mul y 0  add y w  add y 15 mul y x  add z y

if (z % 26 + ??) != digit
    z = z (* 26) + (digit + ??)

    z = z (or z / 26)
1    13  0
1    11  3
1    14  8
26   -5  5
1    14  13
1    10  9
1    12  6
26   -14 1
26   -8  1
1    13  2
26    0  7
26   -5  5
26   -9  8
26   -1  15


    PUSH input[0] + 0
    PUSH input[1] + 3
    PUSH input[2] + 8
    POP. Must have input[3] == popped_value - 5
    PUSH input[4] + 13
    PUSH input[5] + 9
    PUSH input[6] + 6
    POP. Must have input[7] == popped_value - 14
    POP. Must have input[8] == popped_value - 8
    PUSH input[9] + 2
    POP. Must have input[10] == popped_value - 0
    POP. Must have input[11] == popped_value - 5
    POP. Must have input[12] == popped_value - 9
    POP. Must have input[13] == popped_value - 1


i3 = i2 + 3
i7 = i6 - 8
i8 = i5 + 1
i10 = i9 + 2
i11 = i4 + 8
i12 = i1 - 6
i13 = i0 - 1

99691891979938
27141191213911
"""
