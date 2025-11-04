from abc import ABC
from collections import Counter
from math import ceil
from typing import TYPE_CHECKING

from advent_of_code.problems import MultiLineProblem

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


class _Problem(MultiLineProblem[int], ABC):
    def __init__(self) -> None:
        def parsed() -> Iterator[list[str]]:
            for line in self.lines:
                yield line.split(" => ")

        def parse_chemical(chemical_str: str) -> tuple[str, int]:
            amount_str, chemical = chemical_str.split()
            return chemical, int(amount_str)

        def parse_line(
            output: str, inputs: Iterable[str]
        ) -> tuple[str, tuple[int, list[tuple[str, int]]]]:
            chemical, amount = parse_chemical(output)
            return chemical, (amount, [parse_chemical(i) for i in inputs])

        self.reactions = dict(
            parse_line(output, inputs.split(", ")) for inputs, output in parsed()
        )
        self.scores = self.score_chemicals(["FUEL"])

    def score_chemicals(
        self, required: Iterable[str], score: int = 0
    ) -> dict[str, int]:
        scores = {}
        required_ = []
        for chemical in required:
            scores[chemical] = score
            if chemical in self.reactions:
                _, required_chemicals = self.reactions[chemical]
                required_ += [rc for rc, _ in required_chemicals]

        if not required_:
            return scores

        return {**scores, **self.score_chemicals(required_, score + 1)}

    def required_ore(self, fuel: int = 1) -> int:
        required = Counter({"FUEL": fuel})
        while True:
            yield_chemical, desired_amount = sorted(
                required.items(), key=lambda x: self.scores[x[0]]
            )[0]
            if yield_chemical in self.reactions:
                yield_amount, required_chemicals = self.reactions[yield_chemical]

                if desired_amount < yield_amount:
                    used, remaining = 1, 0
                else:
                    used, remaining = divmod(desired_amount, yield_amount)

                for required_chemical, required_amount in required_chemicals:
                    required[required_chemical] += used * required_amount

                if remaining:
                    required[yield_chemical] = remaining
                else:
                    del required[yield_chemical]

            if list(required.keys()) == [
                "ORE"
            ]:  # [k for k, v in required.items() if v]
                break

        return required["ORE"]


class Problem1(_Problem):
    test_solution = 2210736  # 13312 180697
    my_solution = 1065255

    def solution(self) -> int:
        return self.required_ore()


class Problem2(_Problem):
    test_solution = 460664  # 82892753 5586022
    my_solution = 1766154

    def solution(self) -> int:
        available_ore = 1000000000000
        fuel = 1
        ore = available_ore - 1
        while ore < available_ore:
            fuel = ceil(fuel * available_ore / ore)
            ore = self.required_ore(fuel)
        return fuel - 1


# TEST_INPUT = """
# 157 ORE => 5 NZVS
# 165 ORE => 6 DCFZ
# 44 XJWVT, 5 KHKGT, 1 QDVJ, 29 NZVS, 9 GPVTF, 48 HKGWZ => 1 FUEL
# 12 HKGWZ, 1 GPVTF, 8 PSHF => 9 QDVJ
# 179 ORE => 7 PSHF
# 177 ORE => 5 HKGWZ
# 7 DCFZ, 7 PSHF => 2 XJWVT
# 165 ORE => 2 GPVTF
# 3 DCFZ, 7 NZVS, 5 HKGWZ, 10 PSHF => 8 KHKGT
# """
#
# TEST_INPUT = """
# 2 VPVL, 7 FWMGM, 2 CXFTF, 11 MNCFX => 1 STKFG
# 17 NVRVD, 3 JNWZP => 8 VPVL
# 53 STKFG, 6 MNCFX, 46 VJHF, 81 HVMC, 68 CXFTF, 25 GNMV => 1 FUEL
# 22 VJHF, 37 MNCFX => 5 FWMGM
# 139 ORE => 4 NVRVD
# 144 ORE => 7 JNWZP
# 5 MNCFX, 7 RFSQX, 2 FWMGM, 2 VPVL, 19 CXFTF => 3 HVMC
# 5 VJHF, 7 MNCFX, 9 VPVL, 37 CXFTF => 6 GNMV
# 145 ORE => 6 MNCFX
# 1 NVRVD => 8 CXFTF
# 1 VJHF, 6 MNCFX => 4 RFSQX
# 176 ORE => 6 VJHF
# """

TEST_INPUT = """
171 ORE => 8 CNZTR
7 ZLQW, 3 BMBT, 9 XCVML, 26 XMNCP, 1 WPTQ, 2 MZWV, 1 RJRHP => 4 PLWSL
114 ORE => 4 BHXH
14 VRPVC => 6 BMBT
6 BHXH, 18 KTJDG, 12 WPTQ, 7 PLWSL, 31 FHTLT, 37 ZDVW => 1 FUEL
6 WPTQ, 2 BMBT, 8 ZLQW, 18 KTJDG, 1 XMNCP, 6 MZWV, 1 RJRHP => 6 FHTLT
15 XDBXC, 2 LTCX, 1 VRPVC => 6 ZLQW
13 WPTQ, 10 LTCX, 3 RJRHP, 14 XMNCP, 2 MZWV, 1 ZLQW => 1 ZDVW
5 BMBT => 4 WPTQ
189 ORE => 9 KTJDG
1 MZWV, 17 XDBXC, 3 XCVML => 2 XMNCP
12 VRPVC, 27 CNZTR => 2 XDBXC
15 KTJDG, 12 BHXH => 5 XCVML
3 BHXH, 2 VRPVC => 7 MZWV
121 ORE => 7 VRPVC
7 XCVML => 6 RJRHP
5 BHXH, 4 VRPVC => 5 LTCX
"""

# The 13312 ORE-per-FUEL example could produce 82892753 FUEL.
# The 180697 ORE-per-FUEL example could produce 5586022 FUEL.
# The 2210736 ORE-per-FUEL example could produce 460664 FUEL.
