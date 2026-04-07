"""
Quine-McCluskey minimisation engine and K-map data generation.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Implicant:
    minterms: frozenset[int]
    mask: int  # bits that are "don't-care" in the implicant
    value: int  # the common bit pattern (with don't-care bits zeroed)
    n_vars: int
    is_essential: bool = False

    def covers(self, minterm: int) -> bool:
        return (minterm & ~self.mask) == (self.value & ~self.mask)

    def to_expr(self, var_names: list[str]) -> str:
        parts = []
        for i in range(self.n_vars):
            bit_pos = self.n_vars - 1 - i
            if not (self.mask >> bit_pos & 1):
                if (self.value >> bit_pos) & 1:
                    parts.append(var_names[i])
                else:
                    parts.append(f"{var_names[i]}'")
        return "".join(parts) if parts else "1"


@dataclass
class KMapResult:
    n_vars: int
    minterms: list[int]
    dont_cares: list[int]
    prime_implicants: list[Implicant]
    essential_implicants: list[Implicant]
    sop_expression: str
    kmap_grid: list[list[str]]  # 2D grid of "0", "1", "X"
    row_labels: list[str]
    col_labels: list[str]
    groups: list[tuple[Implicant, str]]  # (implicant, colour)


# ── Grey code ordering ───────────────────────────────────────────────────────

GREY_2 = ["00", "01", "11", "10"]
GREY_1 = ["0", "1"]

VAR_NAMES = {
    2: ["A", "B"],
    3: ["A", "B", "C"],
    4: ["A", "B", "C", "D"],
}


def _grey_labels(n: int) -> list[str]:
    if n == 1:
        return GREY_1
    if n == 2:
        return GREY_2
    # recursive grey code
    prev = _grey_labels(n - 1)
    return ["0" + g for g in prev] + ["1" + g for g in reversed(prev)]


# ── Quine-McCluskey ──────────────────────────────────────────────────────────


def _count_ones(n: int) -> int:
    return bin(n).count("1")


def _combine(a: Implicant, b: Implicant) -> Implicant | None:
    """Try to combine two implicants differing in exactly one bit."""
    if a.mask != b.mask:
        return None
    diff = a.value ^ b.value
    if diff & a.mask:
        return None
    if _count_ones(diff) != 1:
        return None
    return Implicant(
        minterms=a.minterms | b.minterms,
        mask=a.mask | diff,
        value=a.value & ~diff,
        n_vars=a.n_vars,
    )


def quine_mccluskey(
    n_vars: int, minterms: list[int], dont_cares: list[int] | None = None
) -> list[Implicant]:
    """Find all prime implicants using Quine-McCluskey."""
    if dont_cares is None:
        dont_cares = []

    all_terms = set(minterms) | set(dont_cares)
    if not all_terms:
        return []

    # initial implicants
    current: set[tuple[int, int, frozenset[int]]] = set()
    for t in all_terms:
        current.add((t, 0, frozenset([t])))

    prime_set: set[tuple[int, int, frozenset[int]]] = set()

    while current:
        used = set()
        next_level: set[tuple[int, int, frozenset[int]]] = set()
        items = list(current)
        for i, (v1, m1, mt1) in enumerate(items):
            for j, (v2, m2, mt2) in enumerate(items):
                if i >= j:
                    continue
                if m1 != m2:
                    continue
                diff = v1 ^ v2
                if diff & m1:
                    continue
                if _count_ones(diff) != 1:
                    continue
                new_val = v1 & ~diff
                new_mask = m1 | diff
                new_mt = mt1 | mt2
                next_level.add((new_val, new_mask, new_mt))
                used.add(i)
                used.add(j)

        for i, item in enumerate(items):
            if i not in used:
                prime_set.add(item)

        current = next_level

    # Convert to Implicant objects
    primes = []
    for val, mask, mts in prime_set:
        primes.append(
            Implicant(
                minterms=mts,
                mask=mask,
                value=val,
                n_vars=n_vars,
            )
        )

    return primes


def find_essential(primes: list[Implicant], minterms: list[int]) -> list[Implicant]:
    """Identify essential prime implicants using the prime implicant chart."""
    mt_set = set(minterms)
    essential = []
    covered = set()

    for mt in minterms:
        covering = [p for p in primes if mt in p.minterms]
        if len(covering) == 1:
            p = covering[0]
            if p not in essential:
                p.is_essential = True
                essential.append(p)
                covered |= p.minterms & mt_set

    # Greedy cover for remaining
    remaining = mt_set - covered
    remaining_primes = [p for p in primes if p not in essential]

    while remaining:
        best = max(
            remaining_primes, key=lambda p: len(p.minterms & remaining), default=None
        )
        if best is None or not (best.minterms & remaining):
            break
        essential.append(best)
        covered |= best.minterms & mt_set
        remaining = mt_set - covered
        remaining_primes.remove(best)

    return essential


# ── K-Map grid generation ────────────────────────────────────────────────────

GROUP_COLOURS = [
    "#1565C0",
    "#25752b",
    "#ba1a1a",
    "#9C27B0",
    "#FF9800",
    "#00897B",
    "#5C6BC0",
    "#F06292",
    "#8D6E63",
    "#78909C",
    "#E91E63",
    "#4CAF50",
]


def solve(n_vars: int, outputs: list[int]) -> KMapResult:
    """
    Solve a truth table.

    outputs: list of length 2^n_vars, each element is 0, 1, or -1 (don't-care).
    """
    assert len(outputs) == (1 << n_vars)
    minterms = [i for i, v in enumerate(outputs) if v == 1]
    dont_cares = [i for i, v in enumerate(outputs) if v == -1]

    primes = quine_mccluskey(n_vars, minterms, dont_cares)
    essential = find_essential(primes, minterms) if minterms else []

    var_names = VAR_NAMES.get(n_vars, [chr(65 + i) for i in range(n_vars)])

    # SOP expression
    if not essential:
        sop = "0"
    else:
        terms = [imp.to_expr(var_names) for imp in essential]
        sop = " + ".join(terms)

    # Build K-map grid
    if n_vars == 2:
        row_vars, col_vars = 1, 1
    elif n_vars == 3:
        row_vars, col_vars = 1, 2
    else:  # 4
        row_vars, col_vars = 2, 2

    row_labels = _grey_labels(row_vars)
    col_labels = _grey_labels(col_vars)

    grid = []
    for r_label in row_labels:
        row = []
        for c_label in col_labels:
            bits = r_label + c_label
            idx = int(bits, 2)
            if outputs[idx] == 1:
                row.append("1")
            elif outputs[idx] == -1:
                row.append("X")
            else:
                row.append("0")
        grid.append(row)

    # Assign colours to groups
    groups = []
    for i, imp in enumerate(essential):
        colour = GROUP_COLOURS[i % len(GROUP_COLOURS)]
        groups.append((imp, colour))

    return KMapResult(
        n_vars=n_vars,
        minterms=minterms,
        dont_cares=dont_cares,
        prime_implicants=primes,
        essential_implicants=essential,
        sop_expression=sop,
        kmap_grid=grid,
        row_labels=row_labels,
        col_labels=col_labels,
        groups=groups,
    )
