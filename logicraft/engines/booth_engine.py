"""
Radix-2 Booth's multiplication algorithm — cycle-by-cycle state computation.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class BoothCycleState:
    cycle: int
    a_reg: int
    q_reg: int
    q_minus_1: int
    action: str
    action_reason: str
    a_bits: list[int]
    q_bits: list[int]
    a_signed: int
    q_signed: int


@dataclass
class BoothResult:
    multiplicand: int
    multiplier: int
    bit_width: int
    cycles: list[BoothCycleState]
    final_product: int
    expected_product: int
    product_bits: str
    is_correct: bool


def _to_signed(val, width):
    val = val & ((1 << width) - 1)
    if val >> (width - 1):
        return val - (1 << width)
    return val


def _to_unsigned(val, width):
    return val & ((1 << width) - 1)


def _bits(val, width):
    u = _to_unsigned(val, width)
    return [(u >> (width - 1 - i)) & 1 for i in range(width)]


def run_booth(m, r, bit_width):
    mask = (1 << bit_width) - 1
    m_val = _to_unsigned(m, bit_width)
    r_val = _to_unsigned(r, bit_width)
    a = 0
    q = r_val
    q_minus_1 = 0
    n = bit_width
    m_signed = _to_signed(m, bit_width)
    expected = m_signed * _to_signed(r, bit_width)
    cycles = []

    cycles.append(
        BoothCycleState(
            cycle=0,
            a_reg=a,
            q_reg=q,
            q_minus_1=q_minus_1,
            action="INIT",
            action_reason="Initial state",
            a_bits=_bits(a, bit_width),
            q_bits=_bits(q, bit_width),
            a_signed=_to_signed(a, bit_width),
            q_signed=_to_signed(q, bit_width),
        )
    )

    for cycle in range(1, n + 1):
        q0 = q & 1
        if q0 == 0 and q_minus_1 == 1:
            action = "ADD M"
            reason = "Q0=0, Q-1=1 -> A = A + M"
            a = (a + m_val) & mask
        elif q0 == 1 and q_minus_1 == 0:
            action = "SUB M"
            reason = "Q0=1, Q-1=0 -> A = A - M"
            a = (a + ((~m_val + 1) & mask)) & mask
        else:
            action = "NOP"
            reason = f"Q0={q0}, Q-1={q_minus_1} -> No operation"

        old_a_lsb = a & 1
        old_q_lsb = q & 1
        a_msb = (a >> (bit_width - 1)) & 1
        a = ((a >> 1) | (a_msb << (bit_width - 1))) & mask
        q = ((q >> 1) | (old_a_lsb << (bit_width - 1))) & mask
        q_minus_1 = old_q_lsb

        cycles.append(
            BoothCycleState(
                cycle=cycle,
                a_reg=a,
                q_reg=q,
                q_minus_1=q_minus_1,
                action=action,
                action_reason=reason,
                a_bits=_bits(a, bit_width),
                q_bits=_bits(q, bit_width),
                a_signed=_to_signed(a, bit_width),
                q_signed=_to_signed(q, bit_width),
            )
        )

    product_unsigned = (a << bit_width) | q
    product_signed = _to_signed(product_unsigned, 2 * bit_width)
    product_bits_str = format(
        _to_unsigned(product_signed, 2 * bit_width), f"0{2 * bit_width}b"
    )

    return BoothResult(
        multiplicand=m_signed,
        multiplier=_to_signed(r, bit_width),
        bit_width=bit_width,
        cycles=cycles,
        final_product=product_signed,
        expected_product=expected,
        product_bits=product_bits_str,
        is_correct=(product_signed == expected),
    )
