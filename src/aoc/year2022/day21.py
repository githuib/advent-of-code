from abc import ABC
from dataclasses import dataclass

from aoc import log
from aoc.problems import MultiLineProblem

SYMBOLS = {"humn": "😎"}


def parse_job(job: str) -> tuple[str, str, str] | int:
    return (job[:4], job[5], job[-4:]) if len(job) == 11 else int(job)


def calc(left: int, op: str, right: int) -> int:
    match op:
        case "+":
            return left + right
        case "-":
            return left - right
        case "*":
            return left * right
        case "/":
            return left // right
        case _:
            raise ValueError


class Node(ABC):
    value: int
    jobs: dict
    variable: str | None = None

    @classmethod
    def from_job(cls, monkey: str) -> Node:
        if monkey == cls.variable:
            return Variable(monkey)
        job = cls.jobs[monkey]
        if isinstance(job, int):
            return Number(job)
        return Operation.from_monkeys(*job).prune()

    def prune(self) -> Node:
        return self

    def merge(self, op: str, other: Node) -> Node:
        return Operation(self, op, other)

    def solve_equation(self, result: int) -> int:
        return result


@dataclass
class Variable(Node):
    name: str

    def __repr__(self) -> str:
        return SYMBOLS[self.name]


@dataclass
class Number(Node):
    value: int

    def __repr__(self) -> str:
        return str(self.value)

    def merge(self, op: str, other: Node) -> Node:
        if isinstance(other, Number):
            return Number(calc(self.value, op, other.value))
        return other.merge(op, self)


@dataclass
class Operation(Node):
    left: Node
    op: str
    right: Node

    @classmethod
    def from_monkeys(cls, left_monkey: str, op: str, right_monkey: str) -> Operation:
        return Operation(Node.from_job(left_monkey), op, Node.from_job(right_monkey))

    def __repr__(self) -> str:
        return f"({self.left} {self.op} {self.right})"

    def prune(self) -> Node:
        return self.left.prune().merge(self.op, self.right.prune())

    def _op_left(self, result: int):
        left = self.left.value
        match self.op:
            case "+":
                return result - left
            case "-":
                return left - result
            case "*":
                return result // left
            case "/":
                return left // result
            case _:
                raise ValueError

    def _op_right(self, result: int):
        right = self.right.value
        match self.op:
            case "+":
                return result - right
            case "-":
                return result + right
            case "*":
                return result // right
            case "/":
                return result * right
            case _:
                raise ValueError

    def solve_equation(self, result: int = 0) -> int:
        log.debug("%s = %d", self, result)
        if isinstance(self.right, Number):
            return self.left.solve_equation(self._op_right(result))
        if isinstance(self.left, Number):
            return self.right.solve_equation(self._op_left(result))
        raise ValueError


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self):
        Node.jobs = {line[:4]: parse_job(line[6:]) for line in self.lines}


class Problem1(_Problem):
    test_solution = 152
    my_solution = 62386792426088

    def solution(self) -> int:
        return Node.from_job("root").value


class Problem2(_Problem):
    test_solution = 301
    my_solution = 4945453364388

    def solution(self) -> int:
        left, _, right = Node.jobs["root"]
        Node.variable = "humn"
        result = Operation.from_monkeys(left, "-", right).solve_equation()
        log.debug("%s = %d", SYMBOLS[Node.variable], result)
        return result


TEST_INPUT = """
root: pppw + sjmn
dbpl: 5
cczh: sllz + lgvd
zczc: 2
ptdq: humn - dvpt
dvpt: 3
lfqf: 4
humn: 5
ljgn: 2
sjmn: drzm * dbpl
sllz: 4
pppw: cczh / lfqf
lgvd: ljgn * ptdq
drzm: hmdt - zczc
hmdt: 32
"""
