from math import prod

from based_utils.cli import animated
from based_utils.cli.animation import AnimParams, flashing
from igraph import Graph  # type: ignore[import-untyped]

from advent_of_code import log
from advent_of_code.problems import MultiLineProblem


class Problem1(MultiLineProblem[int]):
    test_solution = 54
    puzzle_solution = 582590

    def solution(self) -> int:
        # graph = Graph.ListDict({line[:3]: line[5:].split() for line in self.lines})
        # vs, *_ = graph.mincut().partition
        # plot(
        #     graph,
        #     target='kut.pdf',
        #     vertex_color=['blue' if i in vs else 'red' for i in range(len(graph.vs))],
        #     vertex_size=6,
        #     layout=graph.layout_fruchterman_reingold(),
        # )
        return prod(
            len(c)
            for c in Graph.ListDict({line[:3]: line[5:].split() for line in self.lines})
            .mincut()
            .partition
        )


HOCKEY = r"""
        _----_    _________       /\
       /      \  /         \/\ __///
      (        \/          / > /   \
       \        |      --/_>_/    /
         \_ ____|          \ /\ _/
           /               ///        __\
          (               // \       /  \\
           \      \     ///    \    /    \\
            (      \   //       \  /\  _  \\
             \   ___|///    _    \/  \/ \__)\
              ( / _ //\    ( \       /
               /_ /// /     \ \ _   /
               (__)  ) \_    \   --~
               ///--/    \____\
              //        __)    \
            ///        (________)
 _________///          ===========
//|_____|///

"""


class Problem2(MultiLineProblem[None]):
    def solution(self) -> None:
        anim = animated(HOCKEY.splitlines(), flashing())
        log.debug_animated(anim, params=AnimParams(fps=30))


TEST_INPUT = """
jqt: rhn xhk nvd
rsh: frs pzl lsr
xhk: hfx
cmg: qnr nvd lhk bvb
rhn: xhk bvb hfx
bvb: xhk hfx
pzl: lsr hfx nvd
qnr: nvd
ntq: jqt hfx bvb xhk
nvd: lhk
lsr: lhk
rzs: qnr cmg lsr rsh
frs: qnr lhk lsr
"""
