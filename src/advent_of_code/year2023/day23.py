from abc import ABC, abstractmethod
from functools import cached_property
from itertools import pairwise
from typing import TYPE_CHECKING

from igraph import EdgeSeq, Graph, Layout, plot  # type: ignore[import-untyped]
from matplotlib import pyplot as plt

from advent_of_code.geo2d import DOWN, P2, RIGHT, Grid2
from advent_of_code.problems import GridProblem

if TYPE_CHECKING:
    from matplotlib.axes import Axes


class _Problem(GridProblem[int], ABC):
    def __init__(self) -> None:
        self.road = Grid2[str]({p: v for p, v in self.grid.items() if v != "#"})
        self.ps = list(self.road.keys())
        ids: dict[P2, int] = {p: i for i, p in enumerate(self.road)}
        self.start, *_, self.end = self.road.keys()
        self.graph_values = [
            (ids[p], ids[q], v == "." and p != self.start and q != self.end)
            for p in ids
            for q, v in self.road.neighbors(p, directions=[RIGHT, DOWN])
        ]

    @property
    @abstractmethod
    def _initial_graph(self) -> Graph:
        pass

    @property
    @abstractmethod
    def _graph(self) -> Graph:
        pass

    @abstractmethod
    def _path_length(self, edges: EdgeSeq) -> int:
        pass

    @abstractmethod
    def _plot_graph(self, ax: Axes, edges: EdgeSeq) -> None:
        pass

    def _plot(self, edges: EdgeSeq) -> None:
        fig, ax = plt.subplots()
        self._plot_graph(ax, edges)
        plt.gca().invert_yaxis()
        fig.canvas.draw()
        plt.pause(0.001)
        input("Press [enter] to continue.")

    def solution(self) -> int:
        start, end = self._graph.vs.select(_degree=1)
        paths = (
            self._graph.es[self._graph.get_eids(pairwise(ids))]
            for ids in self._graph.get_all_simple_paths(start, end)
        )
        edges, length = max(
            ((es, self._path_length(es)) for es in paths), key=lambda p: p[1]
        )

        if self.is_debugged_run:
            self._plot(edges)

        return length


class Problem1(_Problem):
    test_solution = 94
    my_solution = 2326

    @cached_property
    def _initial_graph(self) -> Graph:
        return Graph(
            edges=[
                e
                for i, j, bidirectional in self.graph_values
                for e in [(i, j)] + ([(j, i)] if bidirectional else [])
            ],
            directed=True,
        )

    @cached_property
    def _graph(self) -> Graph:
        return self._initial_graph

    def _path_length(self, edges: EdgeSeq) -> int:
        return len(edges)

    def _plot_graph(self, ax: Axes, edges: EdgeSeq) -> None:
        plot(
            self._graph,
            target=ax,
            vertex_size=6,
            edge_color=["tomato" if e in edges else "grey" for e in self._graph.es],
            edge_width=2,  # [2 if e in longest_es else .5 for e in graph.es],
            layout=Layout(self.road.keys()),
        )


class Problem2(_Problem):
    test_solution = 154
    my_solution = 6574

    def __init__(self) -> None:
        super().__init__()
        self._ids = list(range(len(self.road)))

    @cached_property
    def _initial_graph(self) -> Graph:
        return Graph(
            edges=[(i, j) for i, j, _ in self.graph_values],
            vertex_attrs={"idx": self._ids},
        )

    @cached_property
    def _graph(self) -> Graph:
        chain_ids = self._initial_graph.vs.select(_degree=2)["idx"]
        g_chains = self._initial_graph.subgraph_edges(
            self._initial_graph.es.select(_within=chain_ids)
        )
        w_ids = {o: n for n, o in enumerate(set(self._ids) - set(chain_ids))}
        chain_vs = [g_chains.vs[c] for c in g_chains.connected_components("weak")]
        return Graph(
            edges=[
                [
                    w_ids[i]
                    for v in self._initial_graph.vs.select(vs.select(_degree=1)["idx"])
                    for n in v.neighbors()
                    if (i := n.index) in w_ids
                ]
                for vs in chain_vs
            ],
            edge_attrs={
                "weight": [len(c) + 1 for c in chain_vs],
                "chain": [c["idx"] for c in chain_vs],
            },
            vertex_attrs={"pos": [self.ps[i] for i in w_ids]},
        )

    def _path_length(self, edges: EdgeSeq) -> int:
        return sum(edges["weight"])

    def _plot_graph(self, ax: Axes, edges: EdgeSeq) -> None:
        longest_es = [
            e
            for pe in edges
            for e in self._initial_graph.es.select(_within=pe["chain"])
        ]
        plot(
            self._initial_graph,
            target=ax,
            vertex_size=0,
            edge_color="tomato",  # ['tomato' if e in longest_es else 'grey' for e in graph.es],
            edge_width=[2 if e in longest_es else 0.5 for e in self._initial_graph.es],
            layout=Layout(self.ps),
        )
        plot(
            self._graph,
            target=ax,
            vertex_size=0,
            edge_label=self._graph.es["weight"],
            edge_background=["#0af" if e in edges else None for e in self._graph.es],
            edge_color="#0af",  # ['#0af' if e in edges else 'grey' for e in self._graph.es],
            edge_width=[5 if e in edges else 1 for e in self._graph.es],
            layout=Layout(self._graph.vs["pos"]),
        )


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
