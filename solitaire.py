import numpy as np
import sympy as sp
import networkx as nx
from collections import Counter
import itertools
import tqdm
import time
import datetime
import functools
import matplotlib.pyplot
import numba


class Solitaire:
    """
    A class for creating various solitaire games. The board is represented as a graph where each node is a hole.
    The edges connecting the nodes are the valid neighbors.
    The different types of boards are called through their respective classmethods
    """

    def __init__(self, board, starting_hole, name):
        """
        Initializer for the game board, should not need to be called. Instead call one of the classmethods
        that create a specific board layout.
        Args:
            board: the graph nodes each with a x and y attribute of as a sympy.Number describing its position in
            cartesian coordinate system. Neighboring nodes are a distance of 1 (one) away from each other.
            starting_hole: which hole has a peg missing at the beginning
            name: the name of the type of board, used in when naming output files
        """
        board.node[starting_hole]['peg'] = False

        self.name = name
        self.board = board

        self.total_holes = board.number_of_nodes()
        self.max_steps = board.number_of_nodes() - 1

        self._calc_edges()
        self._calc_pos()
        self._find_neighbor_jumper_pairs()

    @classmethod
    def triangle(cls, starting_hole=4, name='triangle'):
        board = nx.Graph()

        ang = sp.rad(60)

        count = itertools.count()
        for i in range(5):
            y = -i * sp.sin(ang)
            x = -i * sp.cos(ang)
            for j in range(i + 1):
                board.add_node(next(count), peg=True, x=x, y=y)
                x += 1

        return cls(board, starting_hole, name)

    @classmethod
    def cross(cls, starting_hole=16, name='cross'):
        def add_holes(g, count, ys, xs):
            for y in ys:
                y = sp.Number(y)
                for x in xs:
                    x = sp.Number(x)
                    g.add_node(next(count), peg=True, x=x, y=y)

        board = nx.Graph()
        count = itertools.count()
        add_holes(board, count, (0, 1), (2, 3, 4))
        add_holes(board, count, (2, 3, 4), range(7))
        add_holes(board, count, (5, 6), (2, 3, 4))

        return cls(board, starting_hole, name)

    @classmethod
    def rhombus(cls, starting_hole=20, name='rhombus'):
        board = nx.Graph()
        count = itertools.count()

        ang = sp.rad(60)
        for yi in range(5):
            y = yi * sp.sin(ang)
            for x in range(5):
                x = x + yi * sp.cos(ang)
                board.add_node(next(count), peg=True, x=x, y=y)

        return cls(board, starting_hole, name)

    def _calc_edges(self):
        """
        Calculate which nodes are neighbors by finding which ones are a distance of 1 (one) away from each other.
        Creates an edge between neighboring nodes with an angle attribute describing the directionality of the neighbor.
        The angle is between 0 and 180. This needs to be run before _calc_pos to keep the sympy numbers and
        avoid floating point errors.
        """
        for n0, n1 in itertools.combinations(self.board.node, 2):

            x = self.board.node[n0]['x'] - self.board.node[n1]['x']
            y = self.board.node[n0]['y'] - self.board.node[n1]['y']
            if x ** 2 + y ** 2 == 1:
                angle = (sp.deg(sp.atan2(y, x)) + 360) % 180
                self.board.add_edge(n0, n1, angle=angle)

    def _calc_pos(self):
        """
        Evaluates the `x` and `y` coordinate attributes of each node to
        floating point numbers and creates a `pos` dictionary containing said coordinates for ease of use. This is so
        the positions can be plotted and the graph can also be saved.
        """
        self.pos = {}
        for key in self.board.node.keys():
            x, y = list(map(lambda z: self.board.node[key][z].evalf(), 'xy'))
            self.board.node[key]['x'] = x
            self.board.node[key]['y'] = y
            self.pos[key] = (x, y)

    def _find_neighbor_jumper_pairs(self):
        """
        For each hole, find their neighbors and which one of their neighbors could be used to jump. Essentially,
        for each jump you need three holes, this makes a tuple for each hole where the first element is the
        direct neighbor and the second element is its neighbor that is in line with the other two holes.
        This is stored in another tuple, indexed by the hole index.
        """
        neighbors = [None] * len(self.board)

        for n0 in self.board.nodes:
            temp = []
            for n1, v1 in self.board[n0].items():
                a1 = v1['angle']
                for n2, v2 in self.board[n1].items():
                    a2 = v2['angle']
                    if n2 is not n0 and a1 == a2:
                        temp.append((n1, n2))
            neighbors[n0] = tuple(temp)

        self.neighbor_jumper_pairs = tuple(neighbors)

    def draw_board(self, show_labels=True, **kwargs):
        """
        Plots the board showing the connections between the holes.

        Args:
            show_labels: show number of each node
            kwargs: keyword arguments, same as `networkx.draw_network`

        """
        colors = ['r' if val['peg'] else 'b' for val in self.board.node.values()]
        labels = {x: x if show_labels else '' for x in self.pos.keys()}

        nx.draw(self.board, pos=self.pos, node_color=colors, labels=labels, **kwargs)


if __name__ == '__main__':
    Solitaire.cross()
    Solitaire.triangle()
    test = Solitaire.cross(starting_hole=20)
    test.draw_board(show_labels=True)
    matplotlib.pyplot.show()


