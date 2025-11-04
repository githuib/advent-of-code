from abc import ABC
from itertools import combinations

from advent_of_code import log
from advent_of_code.problems import NoSolutionFoundError, ParsedProblem
from advent_of_code.utils.geo2d import intersect_lines_2
from advent_of_code.utils.geo3d import P3D, Grid3D

Trajectory = tuple[P3D, P3D]


class _Problem(ParsedProblem[Trajectory, int], ABC):
    line_pattern = "{:p3} @ {:p3}"

    def __init__(self) -> None:
        self.hailstone_pairs = set(combinations(self.parsed_input, 2))


class Problem1(_Problem):
    test_solution = 2
    my_solution = 15593

    def check(self, h1: Trajectory, h2: Trajectory) -> bool:
        check_range = self.var(
            test=(7, 27), puzzle=(200_000_000_000_000, 400_000_000_000_000)
        )
        (x1, y1, _), (vx1, vy1, _) = h1
        (x2, y2, _), (vx2, vy2, _) = h2
        i = intersect_lines_2(
            ((x1, y1), (x1 + vx1, y1 + vy1)), ((x2, y2), (x2 + vx2, y2 + vy2))
        )
        if i is None:
            return False
        x, y = i
        r_min, r_max = check_range
        return (
            r_min <= x <= r_max
            and r_min <= y <= r_max
            and (x - x1) * vx1 >= 0
            and (y - y1) * vy1 >= 0
            and (x - x2) * vx2 >= 0
            and (y - y2) * vy2 >= 0
        )

    def solution(self) -> int:
        return sum(self.check(h1, h2) for h1, h2 in self.hailstone_pairs)


class Problem2(_Problem):
    test_solution = 47
    my_solution = 757031940316991

    def solution(self) -> int:
        velo_range = Grid3D(v for _, v in self.parsed_input).size
        potential_v = [set[int]()] * 3
        for (p1, v1), (p2, v2) in self.hailstone_pairs:
            for i in range(3):
                p_diff = p2[i] - p1[i]
                pot_v = (
                    {
                        v
                        for v in range(-velo_range[i], velo_range[i])
                        if v not in (0, v1[i]) and p_diff % (v - v1[i]) == 0
                    }
                    if v1[i] == v2[i]
                    else set()
                )
                if pot_v:
                    potential_v[i] = potential_v[i] & pot_v or pot_v
            if all(len(v) == 1 for v in potential_v):
                break  # only one possible velocity left
        if not any(potential_v):
            raise NoSolutionFoundError
        if not all(len(v) == 1 for v in potential_v):
            # For the test case, several possible velocities are found, although the first
            # values actually (coincidentally?) result in the correct answer.
            log.warning(
                f"Multiple possible velocity matches found:\n{
                    '\n'.join(
                        f'{c}: {v}' for c, v in zip('xyz', potential_v, strict=False)
                    )
                }"
            )

        # While other stations' listeners are at school... we're shoplifting!
        #  V-Rock - the home of the vulture.
        v_rock = P3D(*(v.pop() for v in potential_v))
        (p1, v1), (p2, v2) = self.hailstone_pairs.pop()
        m1, m2 = (
            (v1.y - v_rock.y) / (v1.x - v_rock.x),
            (v2.y - v_rock.y) / (v2.x - v_rock.x),
        )
        px = round(((p2.y - (m2 * p2.x)) - (p1.y - (m1 * p1.x))) / (m1 - m2))
        t = (px - p1.x) / (v1.x - v_rock.x)
        p_rock = P3D(
            px, round(p1.y + (v1.y - v_rock.y) * t), round(p1.z + (v1.z - v_rock.z) * t)
        )
        log.debug(f"Position: {p_rock}")
        log.debug(f"Velocity: {v_rock}")
        log.debug(f"Time: {t}")
        return p_rock.manhattan_length


TEST_INPUT = """
19, 13, 30 @ -2,  1, -2
18, 19, 22 @ -1, -1, -2
20, 25, 34 @ -2, -2, -4
12, 31, 28 @ -1, -2, -1
20, 19, 15 @  1, -5, -3
"""
