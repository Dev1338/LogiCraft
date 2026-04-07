"""
FSM data model, simulation, and state minimisation (table-filling).
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class State:
    name: str
    output: str = ""
    is_start: bool = False
    is_accept: bool = False
    x: float = 0.0
    y: float = 0.0


@dataclass
class Transition:
    src: str
    dst: str
    input_symbol: str
    output: str = ""  # Mealy output


@dataclass
class FSMDef:
    mode: str  # "Moore" or "Mealy"
    states: list[State] = field(default_factory=list)
    transitions: list[Transition] = field(default_factory=list)
    alphabet: list[str] = field(default_factory=list)

    def start_state(self):
        for s in self.states:
            if s.is_start:
                return s
        return self.states[0] if self.states else None

    def get_state(self, name):
        for s in self.states:
            if s.name == name:
                return s
        return None

    def get_transitions_from(self, state_name):
        return [t for t in self.transitions if t.src == state_name]


@dataclass
class TraceStep:
    step: int
    current_state: str
    input_symbol: str
    next_state: str
    output: str


@dataclass
class SimResult:
    trace: list[TraceStep]
    final_state: str
    accepted: bool
    output_string: str


def simulate(fsm: FSMDef, input_string: str) -> SimResult:
    trace = []
    current = fsm.start_state()
    if not current:
        return SimResult([], "", False, "")
    outputs = []

    for i, sym in enumerate(input_string):
        transitions = fsm.get_transitions_from(current.name)
        matched = None
        for t in transitions:
            if t.input_symbol == sym:
                matched = t
                break

        if matched is None:
            trace.append(TraceStep(i, current.name, sym, "STUCK", ""))
            return SimResult(trace, current.name, False, "".join(outputs))

        next_st = fsm.get_state(matched.dst)
        if fsm.mode == "Mealy":
            out = matched.output
        else:
            out = next_st.output if next_st else ""
        outputs.append(out)

        trace.append(TraceStep(i, current.name, sym, matched.dst, out))
        current = next_st if next_st else current

    accepted = current.is_accept if current else False
    return SimResult(trace, current.name, accepted, "".join(outputs))


# ── Presets ──────────────────────────────────────────────────────────────


def preset_101_detector() -> FSMDef:
    fsm = FSMDef(mode="Moore", alphabet=["0", "1"])
    fsm.states = [
        State("S0", "0", is_start=True, x=0, y=0),
        State("S1", "0", x=1, y=-1),
        State("S2", "0", x=2, y=0),
        State("S3", "1", is_accept=True, x=3, y=-1),
    ]
    fsm.transitions = [
        Transition("S0", "S1", "1"),
        Transition("S0", "S0", "0"),
        Transition("S1", "S2", "0"),
        Transition("S1", "S1", "1"),
        Transition("S2", "S3", "1"),
        Transition("S2", "S0", "0"),
        Transition("S3", "S2", "0"),
        Transition("S3", "S1", "1"),
    ]
    return fsm


def preset_mod3_counter() -> FSMDef:
    fsm = FSMDef(mode="Moore", alphabet=["0", "1"])
    fsm.states = [
        State("S0", "0", is_start=True, is_accept=True, x=0, y=0),
        State("S1", "1", x=2, y=-1),
        State("S2", "2", x=2, y=1),
    ]
    fsm.transitions = [
        Transition("S0", "S0", "0"),
        Transition("S0", "S1", "1"),
        Transition("S1", "S2", "0"),
        Transition("S1", "S0", "1"),
        Transition("S2", "S1", "0"),
        Transition("S2", "S2", "1"),
    ]
    return fsm


def preset_even_zeros() -> FSMDef:
    fsm = FSMDef(mode="Moore", alphabet=["0", "1"])
    fsm.states = [
        State("Even", "Y", is_start=True, is_accept=True, x=0, y=0),
        State("Odd", "N", x=2, y=0),
    ]
    fsm.transitions = [
        Transition("Even", "Odd", "0"),
        Transition("Even", "Even", "1"),
        Transition("Odd", "Even", "0"),
        Transition("Odd", "Odd", "1"),
    ]
    return fsm


PRESETS = {
    "101 Sequence Detector": preset_101_detector,
    "Modulo-3 Counter": preset_mod3_counter,
    "Even Zeros Acceptor": preset_even_zeros,
}


# ── State Minimisation (table-filling) ───────────────────────────────────


def minimize_states(fsm: FSMDef) -> FSMDef:
    states = fsm.states
    n = len(states)
    if n <= 1:
        return fsm

    names = [s.name for s in states]
    idx = {s.name: i for i, s in enumerate(states)}

    # Build distinguishability table
    dist = [[False] * n for _ in range(n)]

    # Mark pairs with different outputs (Moore) or accept status
    for i in range(n):
        for j in range(i + 1, n):
            if fsm.mode == "Moore":
                if states[i].output != states[j].output:
                    dist[i][j] = dist[j][i] = True
            if states[i].is_accept != states[j].is_accept:
                dist[i][j] = dist[j][i] = True

    changed = True
    while changed:
        changed = False
        for i in range(n):
            for j in range(i + 1, n):
                if dist[i][j]:
                    continue
                for sym in fsm.alphabet:
                    ti = [
                        t
                        for t in fsm.transitions
                        if t.src == names[i] and t.input_symbol == sym
                    ]
                    tj = [
                        t
                        for t in fsm.transitions
                        if t.src == names[j] and t.input_symbol == sym
                    ]
                    if not ti or not tj:
                        if bool(ti) != bool(tj):
                            dist[i][j] = dist[j][i] = True
                            changed = True
                        continue
                    di = idx.get(ti[0].dst, i)
                    dj = idx.get(tj[0].dst, j)
                    if dist[di][dj]:
                        dist[i][j] = dist[j][i] = True
                        changed = True

    # Group equivalent states
    groups = []
    assigned = [False] * n
    for i in range(n):
        if assigned[i]:
            continue
        group = [i]
        assigned[i] = True
        for j in range(i + 1, n):
            if not assigned[j] and not dist[i][j]:
                group.append(j)
                assigned[j] = True
        groups.append(group)

    if len(groups) == n:
        return fsm  # already minimal

    # Build new FSM
    import math

    new_fsm = FSMDef(mode=fsm.mode, alphabet=list(fsm.alphabet))
    group_map = {}
    for gi, group in enumerate(groups):
        rep = states[group[0]]
        new_name = rep.name if len(group) == 1 else f"G{gi}"
        for si in group:
            group_map[names[si]] = new_name
        angle = 2 * math.pi * gi / len(groups)
        ns = State(
            new_name,
            rep.output,
            is_start=any(states[si].is_start for si in group),
            is_accept=any(states[si].is_accept for si in group),
            x=2 * math.cos(angle),
            y=2 * math.sin(angle),
        )
        new_fsm.states.append(ns)

    seen = set()
    for t in fsm.transitions:
        src = group_map.get(t.src, t.src)
        dst = group_map.get(t.dst, t.dst)
        key = (src, dst, t.input_symbol)
        if key not in seen:
            seen.add(key)
            new_fsm.transitions.append(Transition(src, dst, t.input_symbol, t.output))

    return new_fsm
