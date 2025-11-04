from abc import ABC
from math import prod
from operator import gt, lt

from more_itertools import split_at

from advent_of_code.problems import MultiLineProblem

Check = tuple[str, str, int]
Rule = tuple[Check, str]
Workflow = tuple[list[Rule], str]


def parse_rule(rule: str) -> Rule:
    check, next_step = rule.split(":")
    return (check[0], check[1], int(check[2:])), next_step


def parse_workflow(line: str) -> tuple[str, Workflow]:
    name, rules_str = line[:-1].split("{")
    *rules, final_step = rules_str.split(",")
    return name, ([parse_rule(r) for r in rules], final_step)


def parse_rating(line: str) -> dict[str, int]:
    d = {}
    for s in line[1:-1].split(","):
        c, r = s.split("=")
        d[c] = int(r)
    return d


def check_rule(rating: int, comp_op: str, value: int) -> bool:
    return {"<": lt, ">": gt}[comp_op](rating, value)


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self) -> None:
        workflows, ratings = split_at(self.lines, lambda s: s == "")
        self.workflows = dict(parse_workflow(line) for line in workflows)
        self.ratings = [parse_rating(line) for line in ratings]

    def next_state(self, state: str) -> bool | Workflow:
        return (
            True if state == "A" else False if state == "R" else self.workflows[state]
        )


class Problem1(_Problem):
    test_solution = 19114
    my_solution = 331208

    def process_ratings(self, ratings: dict[str, int], label: str) -> bool:
        state = self.next_state(label)
        if isinstance(state, bool):
            return state
        rules, final_step = state
        for (r, op, v), next_step in rules:
            if check_rule(ratings[r], op, v):
                return self.process_ratings(ratings, next_step)
        return self.process_ratings(ratings, final_step)

    def solution(self) -> int:
        return sum(
            sum(rat.values()) for rat in self.ratings if self.process_ratings(rat, "in")
        )


def inverse_check(check: Check) -> Check:
    r, op, v = check
    return (r, ">", v - 1) if op == "<" else (r, "<", v + 1)


class Problem2(_Problem):
    test_solution = 167409079868000
    my_solution = 121464316215623

    def solution(self) -> int:
        accepted_paths = []

        def traverse(state: bool | Workflow, checks: list[Check]) -> None:  # noqa: FBT001
            if isinstance(state, bool):
                if state:
                    accepted_paths.append(checks)
            elif isinstance(state, tuple):
                rules, final_step = state
                if rules:
                    rule, *rest = rules
                    check, next_state = rule
                    traverse(self.next_state(next_state), [*checks, check])
                    traverse((rest, final_step), [*checks, inverse_check(check)])
                else:
                    traverse(self.next_state(final_step), checks)

        traverse(self.workflows["in"], [])

        def combinations(checks: list[Check]) -> int:
            d = {c: [1, 4000] for c in "xmas"}
            for r, op, v in checks:
                if op == "<":
                    d[r][1] = min(d[r][1], v - 1)
                else:
                    d[r][0] = max(d[r][0], v + 1)
            return prod(v_max - v_min + 1 for v_min, v_max in d.values())

        return sum(combinations(acc) for acc in accepted_paths)


TEST_INPUT = """
px{a<2006:qkq,m>2090:A,rfg}
pv{a>1716:R,A}
lnx{m>1548:A,A}
rfg{s<537:gd,x>2440:R,A}
qs{s>3448:A,lnx}
qkq{x<1416:A,crn}
crn{x>2662:A,R}
in{s<1351:px,qqz}
qqz{s>2770:qs,m<1801:hdj,R}
gd{a>3333:R,R}
hdj{m>838:A,pv}

{x=787,m=2655,a=1222,s=2876}
{x=1679,m=44,a=2067,s=496}
{x=2036,m=264,a=79,s=2244}
{x=2461,m=1339,a=466,s=291}
{x=2127,m=1623,a=2188,s=1013}
"""
