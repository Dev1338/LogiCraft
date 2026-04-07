"""
ALU computation engine — pure logic, no UI.
"""

from dataclasses import dataclass


@dataclass
class ALUResult:
    """Result of an ALU operation."""

    result: int  # unsigned result (masked to bit_width)
    carry: bool
    overflow: bool
    zero: bool
    sign: bool
    bit_width: int
    # per-bit detail for carry chain visualisation
    a_bits: list[int]
    b_bits: list[int]
    result_bits: list[int]
    carry_bits: list[int]  # carry into each stage (len = bit_width + 1)
    gate_labels: list[str]  # label per stage

    @property
    def signed_result(self) -> int:
        if self.result >> (self.bit_width - 1):
            return self.result - (1 << self.bit_width)
        return self.result

    @property
    def result_hex(self) -> str:
        return f"0x{self.result:0{self.bit_width // 4}X}"

    @property
    def result_bin(self) -> str:
        return format(self.result, f"0{self.bit_width}b")


def _to_signed(val: int, width: int) -> int:
    if val >> (width - 1):
        return val - (1 << width)
    return val


def _from_signed(val: int, width: int) -> int:
    return val & ((1 << width) - 1)


def compute(a: int, b: int, op: str, bit_width: int) -> ALUResult:
    """Execute an ALU operation and return full result with per-bit detail."""
    mask = (1 << bit_width) - 1
    a = a & mask
    b = b & mask

    a_bits = [(a >> (bit_width - 1 - i)) & 1 for i in range(bit_width)]
    b_bits = [(b >> (bit_width - 1 - i)) & 1 for i in range(bit_width)]

    carry_bits = [0] * (bit_width + 1)
    result_bits = [0] * bit_width
    gate_labels = [""] * bit_width
    raw_result = 0
    carry = False
    overflow = False

    if op == "ADD":
        carry_bits[bit_width] = 0  # carry-in
        for i in range(bit_width - 1, -1, -1):
            ab = a_bits[i]
            bb = b_bits[i]
            cin = carry_bits[i + 1] if i < bit_width - 1 else 0
            # for the rightmost bit, carry-in = 0; for others, use carry from
            # right
            if i == bit_width - 1:
                cin = 0
            else:
                cin = carry_bits[i + 1]
            s = ab ^ bb ^ cin
            cout = (ab & bb) | (ab & cin) | (bb & cin)
            result_bits[i] = s
            carry_bits[i] = cout
            gate_labels[i] = "FA"
        # fix carry chain: propagate from LSB to MSB
        carry_bits = _full_adder_chain(a_bits, b_bits, 0, bit_width)
        for i in range(bit_width):
            result_bits[i] = a_bits[i] ^ b_bits[i] ^ carry_bits[i + 1]
            gate_labels[i] = "FA"
        raw_result = sum(
            result_bits[i] << (bit_width - 1 - i) for i in range(bit_width)
        )
        carry = bool(carry_bits[0])
        # overflow: sign of a and b same, but result different
        sa = _to_signed(a, bit_width)
        sb = _to_signed(b, bit_width)
        sr = _to_signed(raw_result, bit_width)
        overflow = (sa >= 0 and sb >= 0 and sr < 0) or (sa < 0 and sb < 0 and sr >= 0)

    elif op == "SUB":
        b_comp = (~b) & mask
        b_bits_sub = [(b_comp >> (bit_width - 1 - i)) & 1 for i in range(bit_width)]
        carry_bits = _full_adder_chain(a_bits, b_bits_sub, 1, bit_width)
        for i in range(bit_width):
            result_bits[i] = a_bits[i] ^ b_bits_sub[i] ^ carry_bits[i + 1]
            gate_labels[i] = "FA"
        raw_result = sum(
            result_bits[i] << (bit_width - 1 - i) for i in range(bit_width)
        )
        carry = not bool(carry_bits[0])  # borrow
        sa = _to_signed(a, bit_width)
        sb = _to_signed(b, bit_width)
        sr = _to_signed(raw_result, bit_width)
        overflow = (sa >= 0 and sb < 0 and sr < 0) or (sa < 0 and sb >= 0 and sr >= 0)
        b_bits = b_bits_sub  # show complemented b in visualisation

    elif op == "MUL":
        sa = _to_signed(a, bit_width)
        sb = _to_signed(b, bit_width)
        product = sa * sb
        raw_result = _from_signed(product, bit_width)
        result_bits = [
            (raw_result >> (bit_width - 1 - i)) & 1 for i in range(bit_width)
        ]
        carry_bits = [0] * (bit_width + 1)
        gate_labels = ["MUL"] * bit_width
        carry = bool(product & ~mask)
        overflow = product != _to_signed(raw_result, bit_width)

    elif op in ("AND", "OR", "XOR", "XNOR", "NAND", "NOR"):
        for i in range(bit_width):
            ab, bb = a_bits[i], b_bits[i]
            if op == "AND":
                r = ab & bb
                gate_labels[i] = "AND"
            elif op == "OR":
                r = ab | bb
                gate_labels[i] = "OR"
            elif op == "XOR":
                r = ab ^ bb
                gate_labels[i] = "XOR"
            elif op == "XNOR":
                r = 1 - (ab ^ bb)
                gate_labels[i] = "XNOR"
            elif op == "NAND":
                r = 1 - (ab & bb)
                gate_labels[i] = "NAND"
            elif op == "NOR":
                r = 1 - (ab | bb)
                gate_labels[i] = "NOR"
            result_bits[i] = r
        raw_result = sum(
            result_bits[i] << (bit_width - 1 - i) for i in range(bit_width)
        )
        carry_bits = [0] * (bit_width + 1)

    elif op == "NOT":
        raw_result = (~a) & mask
        result_bits = [
            (raw_result >> (bit_width - 1 - i)) & 1 for i in range(bit_width)
        ]
        gate_labels = ["NOT"] * bit_width
        carry_bits = [0] * (bit_width + 1)

    elif op in ("SHL", "SHR", "ROL", "ROR"):
        if op == "SHL":
            raw_result = (a << 1) & mask
            carry = bool(a >> (bit_width - 1))
        elif op == "SHR":
            carry = bool(a & 1)
            raw_result = a >> 1
        elif op == "ROL":
            msb = (a >> (bit_width - 1)) & 1
            raw_result = ((a << 1) | msb) & mask
        elif op == "ROR":
            lsb = a & 1
            raw_result = (a >> 1) | (lsb << (bit_width - 1))
        result_bits = [
            (raw_result >> (bit_width - 1 - i)) & 1 for i in range(bit_width)
        ]
        gate_labels = [op] * bit_width
        carry_bits = [0] * (bit_width + 1)

    else:
        raw_result = 0
        result_bits = [0] * bit_width
        gate_labels = ["?"] * bit_width
        carry_bits = [0] * (bit_width + 1)

    zero = raw_result == 0
    sign = bool(raw_result >> (bit_width - 1))

    return ALUResult(
        result=raw_result,
        carry=carry,
        overflow=overflow,
        zero=zero,
        sign=sign,
        bit_width=bit_width,
        a_bits=a_bits,
        b_bits=b_bits,
        result_bits=result_bits,
        carry_bits=carry_bits,
        gate_labels=gate_labels,
    )


def _full_adder_chain(
    a_bits: list[int], b_bits: list[int], carry_in: int, width: int
) -> list[int]:
    """Compute carry chain from LSB (right) to MSB (left).

    Returns list of length (width+1).  Index 0 = carry-out of MSB,
    index width = carry-in to LSB.
    """
    carries = [0] * (width + 1)
    carries[width] = carry_in
    for i in range(width - 1, -1, -1):
        ab = a_bits[i]
        bb = b_bits[i]
        cin = carries[i + 1]
        carries[i] = (ab & bb) | (ab & cin) | (bb & cin)
    return carries


# ── Operation categories for the dropdown ────────────────────────────────────

OPERATIONS = {
    "Arithmetic": ["ADD", "SUB", "MUL"],
    "Logic": ["AND", "OR", "XOR", "XNOR", "NOT", "NAND", "NOR"],
    "Shift": ["SHL", "SHR", "ROL", "ROR"],
}
