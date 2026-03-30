"""
Number system conversions, two's complement analysis, and IEEE 754 encoding.
"""

from __future__ import annotations
import struct
from dataclasses import dataclass


@dataclass
class ConversionResult:
    """All-base representation of a value."""
    value: int
    bit_width: int
    binary: str
    octal: str
    decimal: str
    signed_decimal: str
    hexadecimal: str
    bits: list[int]        # MSB-first
    set_positions: list[int]  # indices (from MSB=0) that are 1

    @property
    def unsigned(self) -> int:
        return self.value

    @property
    def signed(self) -> int:
        if self.value >> (self.bit_width - 1):
            return self.value - (1 << self.bit_width)
        return self.value


def convert(value: int, bit_width: int) -> ConversionResult:
    mask = (1 << bit_width) - 1
    v = value & mask
    bits = [(v >> (bit_width - 1 - i)) & 1 for i in range(bit_width)]
    signed_val = v - (1 << bit_width) if v >> (bit_width - 1) else v
    set_pos = [i for i, b in enumerate(bits) if b == 1]
    return ConversionResult(
        value=v,
        bit_width=bit_width,
        binary=format(v, f"0{bit_width}b"),
        octal=format(v, "o"),
        decimal=str(v),
        signed_decimal=str(signed_val),
        hexadecimal=format(v, f"0{bit_width // 4}X") if bit_width % 4 == 0 else format(v, "X"),
        bits=bits,
        set_positions=set_pos,
    )


def parse_value(text: str, base: int) -> int | None:
    """Parse a string in the given base (2/8/10/16).  Returns None on failure."""
    text = text.strip()
    if not text:
        return None
    try:
        if base == 16 and text.lower().startswith("0x"):
            return int(text, 16)
        return int(text, base)
    except ValueError:
        return None


# ── Two's complement walk-through ────────────────────────────────────────────

@dataclass
class TwosComplementSteps:
    unsigned_value: int
    sign_bit: int
    magnitude_binary: str
    inverted_binary: str
    after_add_one: str
    signed_value: int
    bit_width: int


def twos_complement_analysis(value: int, bit_width: int) -> TwosComplementSteps:
    mask = (1 << bit_width) - 1
    v = value & mask
    sign = (v >> (bit_width - 1)) & 1
    if sign:
        inv = (~v) & mask
        result = (inv + 1) & mask
        signed_val = -result
    else:
        inv = v
        result = v
        signed_val = v

    return TwosComplementSteps(
        unsigned_value=v,
        sign_bit=sign,
        magnitude_binary=format(v, f"0{bit_width}b"),
        inverted_binary=format((~v) & mask, f"0{bit_width}b"),
        after_add_one=format(((~v) & mask) + 1 & mask, f"0{bit_width}b") if sign else format(v, f"0{bit_width}b"),
        signed_value=signed_val,
        bit_width=bit_width,
    )


# ── IEEE 754 single-precision ────────────────────────────────────────────────

@dataclass
class IEEE754Result:
    sign_bit: int
    exponent_bits: list[int]     # 8 bits
    mantissa_bits: list[int]     # 23 bits
    all_bits: list[int]          # 32 bits
    biased_exponent: int
    actual_exponent: int
    mantissa_fraction: float
    formula: str
    decimal_value: float
    hex_repr: str
    is_special: bool
    special_name: str            # "NaN", "Inf", "-Inf", "Zero", etc.


def ieee754_encode(value: float) -> IEEE754Result:
    """Encode a decimal float into IEEE 754 single-precision breakdown."""
    packed = struct.pack(">f", value)
    int_val = struct.unpack(">I", packed)[0]

    bits = [(int_val >> (31 - i)) & 1 for i in range(32)]
    sign = bits[0]
    exp_bits = bits[1:9]
    mant_bits = bits[9:32]

    biased_exp = sum(b << (7 - i) for i, b in enumerate(exp_bits))
    actual_exp = biased_exp - 127

    # Compute mantissa fraction
    mant_frac = sum(b * (2 ** -(i + 1)) for i, b in enumerate(mant_bits))

    # Detect special values
    is_special = False
    special_name = ""
    if biased_exp == 255:
        is_special = True
        if any(mant_bits):
            special_name = "NaN"
            formula = "NaN"
        else:
            special_name = "-Inf" if sign else "+Inf"
            formula = special_name
    elif biased_exp == 0:
        if not any(mant_bits):
            is_special = True
            special_name = "-0" if sign else "+0"
            formula = special_name
        else:
            # denormalized
            formula = f"(-1)^{sign} × 0.{''.join(map(str, mant_bits))} × 2^(-126)"
    else:
        formula = f"(-1)^{sign} × 1.{''.join(map(str, mant_bits[:8]))}... × 2^({actual_exp})"

    return IEEE754Result(
        sign_bit=sign,
        exponent_bits=exp_bits,
        mantissa_bits=mant_bits,
        all_bits=bits,
        biased_exponent=biased_exp,
        actual_exponent=actual_exp,
        mantissa_fraction=mant_frac,
        formula=formula,
        decimal_value=value,
        hex_repr=f"0x{int_val:08X}",
        is_special=is_special,
        special_name=special_name,
    )


# ── Base conversion step-by-step explainer ────────────────────────────────────

def base_conversion_steps(value: int, from_base: int, to_base: int) -> list[str]:
    """Return human-readable step-by-step conversion from one base to another."""
    steps: list[str] = []
    if value < 0:
        steps.append(f"Note: working with magnitude |{value}| = {abs(value)}")
        value = abs(value)

    if from_base != 10:
        # First convert to decimal
        steps.append(f"Step 1: Convert from base-{from_base} to decimal")
        repr_str = _int_to_base_str(value, from_base)
        digits = list(reversed(repr_str))
        parts = []
        for i, d in enumerate(digits):
            dv = int(d, 36)
            parts.append(f"{d}×{from_base}^{i} = {dv * (from_base ** i)}")
        steps.append("  " + " + ".join(reversed(parts)))
        steps.append(f"  = {value} (decimal)")
    else:
        steps.append(f"Starting value: {value} (decimal)")

    if to_base != 10:
        steps.append(f"Step 2: Convert decimal {value} to base-{to_base} (repeated division)")
        v = value
        remainders = []
        if v == 0:
            remainders.append("0")
        while v > 0:
            q, r = divmod(v, to_base)
            r_str = _digit_char(r)
            steps.append(f"  {v} ÷ {to_base} = {q} remainder {r_str}")
            remainders.append(r_str)
            v = q
        remainders.reverse()
        result_str = "".join(remainders)
        steps.append(f"  Reading remainders bottom-to-top: {result_str}")

    return steps


def _int_to_base_str(val: int, base: int) -> str:
    if val == 0:
        return "0"
    digits = []
    while val > 0:
        digits.append(_digit_char(val % base))
        val //= base
    return "".join(reversed(digits))


def _digit_char(d: int) -> str:
    if d < 10:
        return str(d)
    return chr(ord('A') + d - 10)
