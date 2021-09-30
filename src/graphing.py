from __future__ import annotations
from automata import *
from math import atan, ceil
import numpy as np

Point = Tuple[
    float,  # X-coordinate for the state to be drawn at
    float  # Y-coordinate for the state to be drawn at
]

# Only two control points are necessary since it connects
# to the two states
BezierCurve = Tuple[
    Point,
    Point,
]


class Graph:
    _min_x = 0
    _min_y = 0
    _max_x = 5
    _max_y = 5
    _state_radius = 0.5
    _state_fontsize = 14
    _symbol_fontsize = 12

    def dumps(self) -> str:
        return '\n'.join([
            "States:"
        ] + [
            f"{state}:{x},{y}" for state, (x, y) in self.state_pos.items()
        ] + [
            "Edges:"
        ] + [
            f"{x1},{y1},{x2},{y2}" for ((x1, y1), (x2, y2)) in self.edge_curve
        ])

    @classmethod
    def loads(cls, fsm: StateMachine, s: str) -> Graph:
        lines = iter(enumerate(s.split('\n')))
        num, line = next(lines)
        if line != "States:":
            raise ValueError(f"Could not parse graph file; unknown header `{line}` at line {num}")

        state_pos = {}
        num, line = next(lines)
        while line != "Edges:":
            lhs, rhs = line.split(':')

            if not lhs or not rhs:
                raise ValueError(f"Could not parse state position `{line}` at line {num}")

            state = StateMachine.parse_state(lhs)
            if state not in fsm.states:
                raise ValueError(f"Unknown state `{state}` found in graph file at line {num}")

            try:
                x, y = (float(n) for n in rhs.split(','))
            except ValueError:
                raise ValueError(f"Could not parse state position `{line}` at line {num}")

            state_pos[state] = (x, y)
            num, line = next(lines)

        edge_curve = []
        for edge, (num, line) in enumerate(lines):
            try:
                x1, y1, x2, y2 = (float(n) for n in line.split(','))
            except ValueError:
                raise ValueError(f"Could not parse edge Bezier curve `{line}` at line {num} (edge {edge})")

            edge_curve.append((
                (x1, y1),
                (x2, y2)
            ))

        return Graph(fsm, state_pos, tuple(edge_curve))

    @classmethod
    def newgraph(cls):
        return '\n'.join((
            "newgraph",
            "xaxis",
            ' '.join((
                "min", str(cls._min_x), "max", str(cls._max_x),
                "nodraw"
            )),
            "yaxis",
            ' '.join((
                "min", str(cls._min_y), "max", str(cls._max_y),
                "nodraw"
            ))
        ))

    @classmethod
    def state(cls, state: State, x: float, y: float, accept=False) -> str:
        return '\n'.join((
            ' '.join((
                "newcurve",
                "marktype", "circle",
                "marksize", str(cls._state_radius), str(cls._state_radius),
                "linetype", ("solid" if accept else "dotted"),
                "cfill", *('1' for _ in range(3))
            )),
            f"pts {x} {y}",
            ' '.join((
                "newstring",
                "hjc", "vjc",
                "x", str(x), "y", str(y)
            )),
            ' '.join((
                "fontsize", str(cls._state_fontsize),
                "font", "Helvetica",
                ":", str(state)
            ))
        ))

    @classmethod
    def _curve_tip_angle(cls, point2: Point, point3: Point) -> float:
        return (point3[1] - point2[1]) / (point3[0] - point2[0])

    @classmethod
    def edge(cls, from_state: Point, symbol: str, to_state: Point, curve: BezierCurve):
        symbol_x, symbol_y = (
            (curve[0][0] + curve[1][0]) / 2,
            (curve[0][1] + curve[1][1]) / 2
        )
        curve_angle = cls._curve_tip_angle(curve[-1], to_state)
        point_on_circle = (
            to_state[0] - cls._state_radius * np.cos(curve_angle) / 2,
            to_state[1] - cls._state_radius * np.sin(curve_angle) / 2
        )
        return '\n'.join((
            ' '.join((
                "newline", "bezier", "rarrow",
                "pts", *(f"{x} {y} " for x, y in (from_state,) + curve + (point_on_circle,))
            )),
            ' '.join((
                "newstring",
                "hjc", "vjc",
                "x", str(symbol_x), "y", str(symbol_y)
            )),
            ' '.join((
                "fontsize", str(cls._symbol_fontsize),
                "font", "Helvetica",
                ":", str(symbol)
            )),
        ))

    def __init__(
            self,
            fsm: StateMachine,
            state_pos: Dict[
                State,  # State to be drawn
                Point   # Position on the graph to draw this state
            ] = None,
            edge_curve: Tuple[BezierCurve, ...] = None
    ):
        if state_pos is None:
            state_pos = {
                state: (0, 0) for state in fsm.states
            }

        if edge_curve is None:
            edge_curve = tuple(
                (
                    (0, 0),
                    (0, 0)
                ) for _ in fsm.edges
            )

        for container1, container2, error_msg in (
                (fsm.states, state_pos, "Position for state `{state}' not given"),
                (state_pos, fsm.states, "Unknown state '{state}' given as position")
        ):
            for state in container1:
                if state not in container2:
                    raise ValueError(error_msg.format(state=state))

        fsm_edges = len(fsm.edges)
        curves = len(edge_curve)

        if fsm_edges < curves:
            raise ValueError(f"More curves given in the graph file than actual edges")
        elif fsm_edges > curves:
            raise ValueError(f"Not all edges have a curve in the graph file")

        self.fsm = fsm
        self.state_pos = state_pos
        self.edge_curve = edge_curve

    def __str__(self):
        return '\n'.join([
            self.newgraph()
        ] + [
            self.state(state, x, y, accept=(state in self.fsm.accept_states))

            for state, (x, y) in self.state_pos.items()
        ] + [
            self.edge(self.state_pos[from_state], symbol, self.state_pos[to_state], curve)

            for (from_state, symbol, to_state), curve in zip(self.fsm.edges, self.edge_curve)
        ])
