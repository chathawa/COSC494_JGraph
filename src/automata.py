from __future__ import annotations
from typing import Dict, Tuple, Union, List, Set

State = Union[int, str]
Edge = Tuple[
            State,  # State to transition from
            str,    # Symbol to transition on
            State   # State to transition to
        ]


class StateMachine:
    def dumps(self) -> str:
        return '\n'.join([
            f"Start:{self.start_state}",
            f"Accept:{self.format_states(self.accept_states)}",
            "Edges:"
        ] + [
            f"{from_state},{symbol}->{to_state}" for from_state, symbol, to_state in self.edges
        ])

    @classmethod
    def loads(cls, s: str, det: bool) -> StateMachine:
        lines = iter(enumerate(s.split('\n')))

        num, line = next(lines)
        lhs, rhs = line.split(':')
        if not lhs or not rhs or lhs != "Start":
            raise ValueError(f"Could not parse header `{line}` on line {num}")
        start_state = cls.parse_state(rhs)

        num, line = next(lines)
        lhs, rhs = line.split(':')
        if not lhs or not rhs or lhs != "Accept":
            raise ValueError(f"Could not parse header `{line}` on line {num}")
        accept_states = cls.parse_states(rhs)

        num, line = next(lines)
        if line != "Edges:":
            raise ValueError(f"Could not parse `{line}` on line {num}")

        edges = []
        for edge, (num, line) in enumerate(lines):
            lhs, rhs = line.split('->')
            if not lhs or not rhs:
                raise ValueError(f"Could not parse edge `{line}` on line {num} (edge {edge})")
            from_state, symbol = lhs.split(',')
            from_state = cls.parse_state(from_state)
            to_state = cls.parse_state(rhs)
            edges.append((from_state, symbol, to_state))

        return StateMachine(start_state, accept_states, tuple(edges), det=det)

    @staticmethod
    def format_states(states: Tuple) -> str:
        return '{' + ','.join((str(s) for s in states)) + '}'

    @staticmethod
    def parse_state(s: str) -> State:
        try:
            return int(s)
        except ValueError:
            return s

    @classmethod
    def parse_states(cls, states: str) -> Tuple[State]:
        return tuple(cls.parse_state(s) for s in states.strip('{}').split(','))

    def __init__(
            self,
            start_state,
            accept_states: Tuple,
            edges: Tuple[Edge, ...],
            det=True
    ):
        alphabet = set()
        trans: Dict[
            State,         # State to transition from
            Dict[
                str,       # Symbol to transition on
                Tuple[
                    int,   # Index for the edge that represents this transition
                    State  # State to transition to
                ]
            ]
        ] = {}
        states: Set[State] = set()

        for index, (from_state, symbol, to_state) in enumerate(edges):
            for new_state in (state for state in (from_state, to_state) if state not in states):
                states.add(new_state)

            if symbol not in alphabet:
                alphabet.add(symbol)

            try:
                state_trans = trans[from_state]
            except KeyError:
                state_trans = trans[from_state] = {}

            if det and symbol in state_trans:
                raise ValueError(
                    f"State machine is a DFA but has multiple transitions from `{from_state}` on `{symbol}`"
                )

            state_trans[symbol] = (index, to_state)

        self.start_state = start_state
        self.accept_states = accept_states
        self.alphabet = ''.join(alphabet)
        self.edges = edges
        self.trans = trans
        self.states: List[State] = sorted(list(states))
        self.det = det
