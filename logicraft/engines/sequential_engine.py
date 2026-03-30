"""
Sequential logic engine — flip-flop simulation and timing diagram data.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class FlipFlopState:
    """State at one clock cycle."""
    cycle: int
    inputs: dict[str, int]    # e.g. {"D": 1} or {"J": 0, "K": 1}
    q_before: int
    q_after: int
    q_bar: int
    is_invalid: bool
    invalid_reason: str


@dataclass
class TimingResult:
    ff_type: str
    states: list[FlipFlopState]
    input_names: list[str]


# ── State tables ─────────────────────────────────────────────────────────────

def get_state_table(ff_type: str) -> list[dict]:
    """Return the characteristic table for the given flip-flop type."""
    if ff_type == "D":
        return [
            {"D": 0, "Q_next": 0},
            {"D": 1, "Q_next": 1},
        ]
    elif ff_type == "T":
        return [
            {"T": 0, "Q": 0, "Q_next": 0},
            {"T": 0, "Q": 1, "Q_next": 1},
            {"T": 1, "Q": 0, "Q_next": 1},
            {"T": 1, "Q": 1, "Q_next": 0},
        ]
    elif ff_type == "SR":
        return [
            {"S": 0, "R": 0, "Q_next": "Q"},
            {"S": 0, "R": 1, "Q_next": 0},
            {"S": 1, "R": 0, "Q_next": 1},
            {"S": 1, "R": 1, "Q_next": "INVALID"},
        ]
    elif ff_type == "JK":
        return [
            {"J": 0, "K": 0, "Q": 0, "Q_next": 0},
            {"J": 0, "K": 0, "Q": 1, "Q_next": 1},
            {"J": 0, "K": 1, "Q_next": 0},
            {"J": 1, "K": 0, "Q_next": 1},
            {"J": 1, "K": 1, "Q": 0, "Q_next": 1},
            {"J": 1, "K": 1, "Q": 1, "Q_next": 0},
        ]
    return []


# ── Simulation ───────────────────────────────────────────────────────────────

def simulate(ff_type: str, input_sequence: list[dict[str, int]],
             initial_q: int = 0) -> TimingResult:
    """
    Simulate a flip-flop through a sequence of input dictionaries.

    Each entry in input_sequence is e.g. {"D": 1}, {"S": 0, "R": 1}, etc.
    """
    states = []
    q = initial_q

    if ff_type == "D":
        input_names = ["D"]
    elif ff_type == "T":
        input_names = ["T"]
    elif ff_type == "SR":
        input_names = ["S", "R"]
    elif ff_type == "JK":
        input_names = ["J", "K"]
    else:
        input_names = []

    for cycle_idx, inputs in enumerate(input_sequence):
        q_before = q
        is_invalid = False
        invalid_reason = ""

        if ff_type == "D":
            d = inputs.get("D", 0)
            q_after = d
        elif ff_type == "T":
            t = inputs.get("T", 0)
            q_after = q ^ t
        elif ff_type == "SR":
            s = inputs.get("S", 0)
            r = inputs.get("R", 0)
            if s == 1 and r == 1:
                q_after = q  # undefined—keep previous
                is_invalid = True
                invalid_reason = "S=1, R=1 is invalid"
            elif s == 1:
                q_after = 1
            elif r == 1:
                q_after = 0
            else:
                q_after = q
        elif ff_type == "JK":
            j = inputs.get("J", 0)
            k = inputs.get("K", 0)
            if j == 1 and k == 1:
                q_after = 1 - q
            elif j == 1:
                q_after = 1
            elif k == 1:
                q_after = 0
            else:
                q_after = q
        else:
            q_after = q

        states.append(FlipFlopState(
            cycle=cycle_idx,
            inputs=dict(inputs),
            q_before=q_before,
            q_after=q_after,
            q_bar=1 - q_after,
            is_invalid=is_invalid,
            invalid_reason=invalid_reason,
        ))
        q = q_after

    return TimingResult(ff_type=ff_type, states=states, input_names=input_names)


def parse_input_string(ff_type: str, text: str) -> list[dict[str, int]]:
    """Parse a user-typed input string into a list of input dicts.

    For D and T: "0 1 1 0 1"
    For SR and JK: "00 01 10 11 01"  (pairs of bits)
    """
    tokens = text.strip().split()
    result = []
    if ff_type in ("D", "T"):
        name = "D" if ff_type == "D" else "T"
        for t in tokens:
            try:
                result.append({name: int(t) & 1})
            except ValueError:
                result.append({name: 0})
    elif ff_type == "SR":
        for t in tokens:
            if len(t) >= 2:
                s = int(t[0]) & 1
                r = int(t[1]) & 1
            elif len(t) == 1:
                s = int(t[0]) & 1
                r = 0
            else:
                s, r = 0, 0
            result.append({"S": s, "R": r})
    elif ff_type == "JK":
        for t in tokens:
            if len(t) >= 2:
                j = int(t[0]) & 1
                k = int(t[1]) & 1
            elif len(t) == 1:
                j = int(t[0]) & 1
                k = 0
            else:
                j, k = 0, 0
            result.append({"J": j, "K": k})
    return result
