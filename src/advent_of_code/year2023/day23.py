from abc import ABC
from itertools import pairwise
from typing import TYPE_CHECKING

from igraph import EdgeSeq, Graph, Layout, plot  # type: ignore[import-untyped]
from matplotlib import pyplot as plt

from advent_of_code import AOC
from advent_of_code.geo2d import P2, Dir2, Grid2
from advent_of_code.problems import GridProblem

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from matplotlib.axes import Axes


def longest_path(graph: Graph, weighted_edges: bool) -> tuple[EdgeSeq, int]:
    def gen_paths() -> Iterator[tuple[EdgeSeq, int]]:
        start, end = graph.vs.select(_degree=1)
        for ids in graph.get_all_simple_paths(start, end):
            es = graph.es[graph.get_eids(pairwise(ids))]
            yield es, sum(es["weight"]) if weighted_edges else len(es)
    return max(gen_paths(), key=lambda p: p[1])


def plot_graph(plot_callback: Callable[[Axes], None]) -> None:
    fig, ax = plt.subplots()
    plot_callback(ax)
    plt.gca().invert_yaxis()
    fig.canvas.draw()
    plt.pause(0.001)
    input("Press [enter] to continue.")


class _Problem(GridProblem[int], ABC):
    def __init__(self) -> None:
        self.road = Grid2[str]({p: v for p, v in self.grid.items() if v != "#"})
        self.ps = list(self.road.keys())
        ids: dict[P2, int] = {p: i for i, p in enumerate(self.road)}
        self.start, *_, self.end = self.road.keys()
        self.graph_values = [
            (ids[p], ids[q], v == "." and p != self.start and q != self.end)
            for p in ids for q, v in self.road.neighbors(p, directions=[Dir2.right, Dir2.down])
        ]


class Problem1(_Problem):
    test_solution = 94
    my_solution = 2326

    def plot_callback(self, ax, graph: Graph, lp_edges: EdgeSeq) -> None:
        plot(
            graph,
            target=ax,
            vertex_size=6,
            edge_color=["tomato" if e in lp_edges else "grey" for e in graph.es],
            edge_width=2,  # [2 if e in longest_es else .5 for e in graph.es],
            layout=Layout(self.road.keys()),
        )

    def solution(self) -> int:
        graph = Graph(edges=[
            e for i, j, bidirectional in self.graph_values
            for e in [(i, j)] + ([(j, i)] if bidirectional else [])
        ], directed=True)
        lp_edges, lp_length = longest_path(graph, weighted_edges=False)
        if AOC.debugging:
            plot_graph(lambda ax: self.plot_callback(ax, graph, lp_edges))
        return lp_length


class Problem2(_Problem):
    test_solution = 154
    my_solution = 6574

    def plot_callback(self, ax, graph: Graph, lp_edges: EdgeSeq, g_weigths: Graph) -> None:
        longest_es = [e for pe in lp_edges for e in graph.es.select(_within=pe["chain"])]
        plot(
            graph,
            target=ax,
            vertex_size=0,
            edge_color="tomato",  # ['tomato' if e in longest_es else 'grey' for e in graph.es],
            edge_width=[2 if e in longest_es else .5 for e in graph.es],
            layout=Layout(self.ps),
        )
        plot(
            g_weigths,
            target=ax,
            vertex_size=0,
            edge_label=g_weigths.es["weight"],
            edge_background=["#0af" if e in lp_edges else None for e in g_weigths.es],
            edge_color="#0af",  # ['#0af' if e in lp_edges else 'grey' for e in g_weigths.es],
            edge_width=[5 if e in lp_edges else 1 for e in g_weigths.es],
            layout=Layout(g_weigths.vs["pos"]),
        )

    def solution(self) -> int:
        ids = list(range(len(self.road)))
        graph = Graph(edges=[(i, j) for i, j, _ in self.graph_values], vertex_attrs={"idx": ids})
        chain_ids = graph.vs.select(_degree=2)["idx"]
        g_chains = graph.subgraph_edges(graph.es.select(_within=chain_ids))
        w_ids = {o: n for n, o in enumerate(set(ids) - set(chain_ids))}
        chain_vs = [g_chains.vs[c] for c in g_chains.connected_components("weak")]
        g_weigths = Graph(
            edges=[[
                w_ids[i]
                for v in graph.vs.select(vs.select(_degree=1)["idx"])
                for n in v.neighbors() if (i := n.index) in w_ids
            ] for vs in chain_vs],
            edge_attrs={"weight": [len(c) + 1 for c in chain_vs], "chain": [c["idx"] for c in chain_vs]},
            vertex_attrs={"pos": [self.ps[i] for i in w_ids]},
        )
        lp_edges, lp_length = longest_path(g_weigths, weighted_edges=True)
        if AOC.debugging:
            plot_graph(lambda ax: self.plot_callback(ax, graph, lp_edges, g_weigths))
        return lp_length


TEST_INPUT = """
#.#####################
#.......#########...###
#######.#########.#.###
###.....#.>.>.###.#.###
###v#####.#v#.###.#.###
###.>...#.#.#.....#...#
###v###.#.#.#########.#
###...#.#.#.......#...#
#####.#.#.#######.#.###
#.....#.#.#.......#...#
#.#####.#.#.#########v#
#.#...#...#...###...>.#
#.#.#v#######v###.###v#
#...#.>.#...>.>.#.###.#
#####v#.#.###v#.#.###.#
#.....#...#...#.#.#...#
#.#########.###.#.#.###
#...###...#...#...#.###
###.###.#.###v#####v###
#...#...#.#.>.>.#.>.###
#.###.###.#.###.#.#v###
#.....###...###...#...#
#####################.#
"""
