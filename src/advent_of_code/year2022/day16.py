from abc import ABC

from advent_of_code.problems import ParsedProblem


class _Problem(ParsedProblem[tuple[int, ...], int], ABC):
    # _line_pattern = 'Valve AA has flow rate=0; tunnel(s) lead(s) to valve(s) DD, II, BB'
    # _line_pattern = 'Valve {} has flow rate={:d}; tunnel(s) lead(s) to valve(s) DD, II, BB'
    # _regex_pattern = r'Valve (\w+) has flow rate=(\d+); tunnel[s]? lead[s]? to valve[s]? (?P<valves>.*)'
    # _regex_converters = [str, int, lambda s: s.split(', ')]

    def __init__(self) -> None:
        pass
        # print(self.parsed_regex)


class Problem1(_Problem):
    test_solution = 1651

    def solution(self) -> int:
        return 0


class Problem2(_Problem):
    def solution(self) -> int:
        return 0


TEST_INPUT = """
Valve AA has flow rate=0; tunnels lead to valves DD, II, BB
Valve BB has flow rate=13; tunnels lead to valves CC, AA
Valve CC has flow rate=2; tunnels lead to valves DD, BB
Valve DD has flow rate=20; tunnels lead to valves CC, AA, EE
Valve EE has flow rate=3; tunnels lead to valves FF, DD
Valve FF has flow rate=0; tunnels lead to valves EE, GG
Valve GG has flow rate=0; tunnels lead to valves FF, HH
Valve HH has flow rate=22; tunnel leads to valve GG
Valve II has flow rate=0; tunnels lead to valves AA, JJ
Valve JJ has flow rate=21; tunnel leads to valve II
"""
