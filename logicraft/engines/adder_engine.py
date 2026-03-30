"""
Adder architecture comparison engine — Ripple Carry, Carry Lookahead, Carry Select.
"""

from __future__ import annotations
from dataclasses import dataclass
import math


@dataclass
class AdderResult:
    name: str
    result: int
    carry_out: bool
    gate_count: int
    critical_path_delay: int    # in gate delays
    per_bit_delay: list[int]    # delay to compute each bit (index 0 = MSB)
    bit_width: int


# ── Ripple Carry Adder ───────────────────────────────────────────────────────

def ripple_carry(a: int, b: int, bit_width: int) -> AdderResult:
    """Model a ripple carry adder."""
    mask = (1 << bit_width) - 1
    a, b = a & mask, b & mask
    result = (a + b) & mask
    carry = bool((a + b) >> bit_width)

    # Each full adder: 2 gate delays for sum, 2 for carry
    # Carry must propagate through all bits
    per_bit = []
    for i in range(bit_width):
        bit_pos = bit_width - 1 - i  # MSB first
        delay = 2 * (bit_width - bit_pos)  # carry propagation
        per_bit.append(delay)

    gate_count = bit_width * 5  # XOR, AND, OR per full adder ≈ 5 gates

    return AdderResult(
        name="Ripple Carry",
        result=result,
        carry_out=carry,
        gate_count=gate_count,
        critical_path_delay=2 * bit_width,
        per_bit_delay=per_bit,
        bit_width=bit_width,
    )


# ── Carry Lookahead Adder ────────────────────────────────────────────────────

def carry_lookahead(a: int, b: int, bit_width: int) -> AdderResult:
    """Model a carry lookahead adder with 4-bit CLA blocks."""
    mask = (1 << bit_width) - 1
    a, b = a & mask, b & mask
    result = (a + b) & mask
    carry = bool((a + b) >> bit_width)

    block_size = 4
    n_blocks = math.ceil(bit_width / block_size)

    # Within a block: 3 gate delays (PG gen + CLA logic + sum)
    # Between blocks: 2 gate delays per level of CLA hierarchy
    # Total ~ 4 + 2*log4(n) gate delays for the carry
    levels = max(1, math.ceil(math.log(max(n_blocks, 1) + 0.001) / math.log(4)))
    base_delay = 4  # PG + first level CLA + sum

    per_bit = []
    for i in range(bit_width):
        bit_pos = bit_width - 1 - i
        block_idx = bit_pos // block_size
        intra_block = 3  # constant within a block
        inter_block = 2 * min(levels, max(1, math.ceil(math.log(max(block_idx + 1, 1) + 0.001) / math.log(4))))
        per_bit.append(intra_block + inter_block)

    critical = base_delay + 2 * levels
    gate_count = bit_width * 5 + n_blocks * 10  # extra gates for CLA logic

    return AdderResult(
        name="Carry Lookahead",
        result=result,
        carry_out=carry,
        gate_count=gate_count,
        critical_path_delay=critical,
        per_bit_delay=per_bit,
        bit_width=bit_width,
    )


# ── Carry Select Adder ──────────────────────────────────────────────────────

def carry_select(a: int, b: int, bit_width: int) -> AdderResult:
    """Model a carry select adder with 4-bit blocks."""
    mask = (1 << bit_width) - 1
    a, b = a & mask, b & mask
    result = (a + b) & mask
    carry = bool((a + b) >> bit_width)

    block_size = 4
    n_blocks = math.ceil(bit_width / block_size)

    # First block: ripple (2*block_size delays)
    # Subsequent blocks: compute both carry=0 and carry=1 in parallel
    # Then select with MUX (1 gate delay per block)
    first_block_delay = 2 * min(block_size, bit_width)

    per_bit = []
    for i in range(bit_width):
        bit_pos = bit_width - 1 - i
        block_idx = bit_pos // block_size
        if block_idx == n_blocks - 1:
            # LSB block: ripple
            intra = 2 * ((bit_pos % block_size) + 1)
            per_bit.append(intra)
        else:
            # Parallel block + MUX select chain
            intra = 2 * min(block_size, bit_width)  # ripple within block (parallel)
            mux_chain = n_blocks - 1 - block_idx  # MUX select propagation
            per_bit.append(intra + mux_chain)

    critical = first_block_delay + (n_blocks - 1)  # MUX chain
    gate_count = bit_width * 10 + n_blocks * 3  # dual ripple + MUX per block

    return AdderResult(
        name="Carry Select",
        result=result,
        carry_out=carry,
        gate_count=gate_count,
        critical_path_delay=critical,
        per_bit_delay=per_bit,
        bit_width=bit_width,
    )


# ── Comparison helper ────────────────────────────────────────────────────────

def compare_all(a: int, b: int, bit_width: int) -> list[AdderResult]:
    """Run all three adder architectures and return results."""
    return [
        ripple_carry(a, b, bit_width),
        carry_lookahead(a, b, bit_width),
        carry_select(a, b, bit_width),
    ]


def scaling_data(widths: list[int] | None = None) -> dict[str, list[tuple[int, int]]]:
    """Return critical-path delay vs bit-width for all architectures."""
    if widths is None:
        widths = [4, 8, 12, 16]
    data: dict[str, list[tuple[int, int]]] = {
        "Ripple Carry": [],
        "Carry Lookahead": [],
        "Carry Select": [],
    }
    for w in widths:
        data["Ripple Carry"].append((w, ripple_carry(0, 0, w).critical_path_delay))
        data["Carry Lookahead"].append((w, carry_lookahead(0, 0, w).critical_path_delay))
        data["Carry Select"].append((w, carry_select(0, 0, w).critical_path_delay))
    return data
