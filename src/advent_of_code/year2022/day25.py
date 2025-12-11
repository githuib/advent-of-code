from ternimator import AnimParams, animate, animated_lines
from ternimator.animations import changing_colors, fuck_me_sideways

from advent_of_code.problems import MultiLineProblem

FUBAR = {"=": -2, "-": -1, "0": 0, "1": 1, "2": 2}
SNAFU = [("0", 0), ("1", 0), ("2", 0), ("=", 1), ("-", 1), ("0", 1)]


def situation_normal(all_fucked_up: str) -> int:
    return sum(FUBAR[c] * 5**i for i, c in enumerate(all_fucked_up[::-1]))


def fuck_all_up_beyond_repair(normal_situation: int) -> str:
    digits = []
    while normal_situation:
        digits.append(normal_situation % 5)
        normal_situation //= 5
    fucked_up, carry = "", 0
    for d in digits:
        c, carry = SNAFU[d + carry]
        fucked_up = c + fucked_up
    return fucked_up


class Problem1(MultiLineProblem[str]):
    test_solution = "2=-1=0"
    puzzle_solution = "20=022=21--=2--12=-2"

    def solution(self) -> str:
        return fuck_all_up_beyond_repair(
            sum(situation_normal(line) for line in self.lines)
        )


GNOME = r"""
             ___,@
            /  <
       ,_  /    \  _,
   ?    \`/______\`/     \8/
,_(_).  |; (e  e) ;|   #######
 \___ \ \/\   7  /\/   #..#..#
     \/\   \'=='/      #######
      \ \___)--(_______#..#..#
       \___  ()  _____/#######
          /  ()  \    `----'
         /   ()   \
        '-.______.-'
      _    |_||_|    _
     (@____) || (____@)
      \______||______/

"""


class Problem2(MultiLineProblem[None]):
    def solution(self) -> None:
        """Day 25 didn't have a part 2."""
        animations = fuck_me_sideways(), changing_colors()
        animate(animated_lines(GNOME.splitlines(), *animations), AnimParams(fps=30))


TEST_INPUT = """
1=-0-2
12111
2=0=
21
2=01
111
20012
112
1=-1=
1-12
12
1=
122
"""
