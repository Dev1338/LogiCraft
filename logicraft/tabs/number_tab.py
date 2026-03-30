"""
Tab 2 — Number Systems UI.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QGroupBox,
    QLabel, QLineEdit, QComboBox, QPushButton, QTextEdit,
    QScrollArea, QFrame,
)
from logicraft.canvas import MplCanvas
from logicraft.widgets import TonalSeparator
from logicraft.engines.number_engine import (
    convert, parse_value, twos_complement_analysis,
    ieee754_encode, base_conversion_steps,
)


class NumberTab(QWidget):
    def __init__(self, bit_width=8, dark=False):
        super().__init__()
        self._bw = bit_width
        self._dark = dark
        self._init_ui()

    def _init_ui(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(splitter)

        # ── Left Panel ──
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_w = QWidget()
        left = QVBoxLayout(left_w)
        left.setContentsMargins(16, 16, 16, 16)
        left.setSpacing(10)

        # Input
        inp_group = QGroupBox("Value Input")
        inp_lay = QVBoxLayout(inp_group)
        base_row = QHBoxLayout()
        base_row.addWidget(QLabel("Base:"))
        self._base_combo = QComboBox()
        for b_name, b_val in [("Binary (2)", 2), ("Octal (8)", 8),
                               ("Decimal (10)", 10), ("Hex (16)", 16)]:
            self._base_combo.addItem(b_name, b_val)
        self._base_combo.setCurrentIndex(2)
        base_row.addWidget(self._base_combo)
        base_row.addStretch()
        inp_lay.addLayout(base_row)

        self._value_edit = QLineEdit("0")
        self._value_edit.textChanged.connect(self._on_value_changed)
        inp_lay.addWidget(self._value_edit)
        left.addWidget(inp_group)

        # Conversions
        conv_group = QGroupBox("All-Base Conversion")
        conv_lay = QVBoxLayout(conv_group)
        self._fields = {}
        for name in ["Binary", "Octal", "Decimal", "Signed Decimal", "Hexadecimal"]:
            row = QHBoxLayout()
            lbl = QLabel(f"{name}:")
            lbl.setFixedWidth(110)
            lbl.setStyleSheet("font-weight:600; color: #48626e;")
            row.addWidget(lbl)
            fld = QLineEdit("0")
            fld.setReadOnly(True)
            fld.setStyleSheet("font-family: 'Courier New', monospace;")
            row.addWidget(fld)
            self._fields[name] = fld
            conv_lay.addLayout(row)
        left.addWidget(conv_group)

        # Two's complement
        tc_group = QGroupBox("Two's Complement Analysis")
        tc_lay = QVBoxLayout(tc_group)
        self._tc_text = QTextEdit()
        self._tc_text.setReadOnly(True)
        self._tc_text.setMaximumHeight(140)
        self._tc_text.setStyleSheet("font-family:'Courier New',monospace; font-size:12px;")
        tc_lay.addWidget(self._tc_text)
        left.addWidget(tc_group)

        # Show steps
        self._steps_btn = QPushButton("📋 Show Conversion Steps")
        self._steps_btn.setProperty("class", "secondary")
        self._steps_btn.clicked.connect(self._show_steps)
        left.addWidget(self._steps_btn)
        self._steps_text = QTextEdit()
        self._steps_text.setReadOnly(True)
        self._steps_text.setMaximumHeight(120)
        self._steps_text.setStyleSheet("font-family:'Courier New',monospace; font-size:11px;")
        self._steps_text.hide()
        left.addWidget(self._steps_text)

        left.addWidget(TonalSeparator())

        # IEEE 754
        ieee_group = QGroupBox("IEEE 754 Float Analyser")
        ieee_lay = QVBoxLayout(ieee_group)
        ieee_row = QHBoxLayout()
        ieee_row.addWidget(QLabel("Decimal float:"))
        self._float_edit = QLineEdit("0.0")
        self._float_edit.setFixedWidth(140)
        ieee_row.addWidget(self._float_edit)
        self._float_btn = QPushButton("Analyse")
        self._float_btn.clicked.connect(self._analyse_float)
        ieee_row.addWidget(self._float_btn)
        ieee_row.addStretch()
        ieee_lay.addLayout(ieee_row)
        self._ieee_text = QTextEdit()
        self._ieee_text.setReadOnly(True)
        self._ieee_text.setMaximumHeight(100)
        self._ieee_text.setStyleSheet("font-family:'Courier New',monospace; font-size:11px;")
        ieee_lay.addWidget(self._ieee_text)
        left.addWidget(ieee_group)

        left.addStretch()
        left_scroll.setWidget(left_w)
        splitter.addWidget(left_scroll)

        # ── Right Canvas ──
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(8, 8, 8, 8)
        hdr = QHBoxLayout()
        self._canvas_title = QLabel("Bit Cell Visualization")
        self._canvas_title.setProperty("class", "subheading")
        hdr.addWidget(self._canvas_title)
        hdr.addStretch()

        right_lay.addLayout(hdr)

        self.canvas = MplCanvas(self, width=9, height=5, dark=self._dark)
        right_lay.addWidget(self.canvas)
        splitter.addWidget(right)
        splitter.setSizes([420, 700])

        self._on_value_changed()

    def set_bit_width(self, w):
        self._bw = w
        self._on_value_changed()

    def apply_theme(self, dark):
        self._dark = dark
        self.canvas.apply_theme(dark)
        self._on_value_changed()

    def _on_value_changed(self):
        base = self._base_combo.currentData() or 10
        val = parse_value(self._value_edit.text(), base)
        if val is None:
            return
        res = convert(val, self._bw)
        self._fields["Binary"].setText(res.binary)
        self._fields["Octal"].setText(res.octal)
        self._fields["Decimal"].setText(res.decimal)
        self._fields["Signed Decimal"].setText(res.signed_decimal)
        self._fields["Hexadecimal"].setText(res.hexadecimal)

        tc = twos_complement_analysis(val, self._bw)
        lines = [
            f"Unsigned:  {tc.unsigned_value}",
            f"Binary:    {tc.magnitude_binary}",
            f"Sign Bit:  {tc.sign_bit} ({'negative' if tc.sign_bit else 'positive'})",
            f"Inverted:  {tc.inverted_binary}",
            f"Add One:   {tc.after_add_one}",
            f"Signed:    {tc.signed_value}",
        ]
        self._tc_text.setPlainText("\n".join(lines))
        self._draw_bits(res)

    def _draw_bits(self, res):
        from logicraft.theme import get_palette
        p = get_palette(self._dark)
        ax = self.canvas.axes
        ax.clear()

        n = res.bit_width
        cell = 1.0
        gap = 0.15
        total = n * (cell + gap)

        for i, bit in enumerate(res.bits):
            x = i * (cell + gap)
            if i == 0:
                color = "#ba1a1a"
            elif bit:
                color = p.primary
            else:
                color = p.surface_container_high

            ax.add_patch(__import__('matplotlib.patches', fromlist=['FancyBboxPatch']).FancyBboxPatch(
                (x, 0), cell, cell, boxstyle="round,pad=0.04",
                facecolor=color, edgecolor=p.outline_variant, linewidth=1
            ))
            text_color = "#ffffff" if (bit or i == 0) else p.on_surface
            ax.text(x + cell/2, cell/2, str(bit), ha='center', va='center',
                    fontsize=16, fontweight='bold', color=text_color, fontfamily='monospace')

            if bit:
                power = n - 1 - i
                ax.text(x + cell/2, cell + 0.2, f"2^{power}={2**power}",
                        ha='center', fontsize=8, color=p.primary, fontweight='bold')

            ax.text(x + cell/2, -0.2, str(n - 1 - i), ha='center',
                    fontsize=8, color=p.secondary, fontfamily='monospace')

        ax.set_xlim(-0.3, total + 0.3)
        ax.set_ylim(-0.6, cell + 0.6)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f"{n}-Bit Register Visualization", fontsize=13,
                     fontweight='bold', color=p.on_surface, pad=10)
        self.canvas.fig.tight_layout()
        self.canvas.draw()

    def _show_steps(self):
        if self._steps_text.isVisible():
            self._steps_text.hide()
            return
        base = self._base_combo.currentData() or 10
        val = parse_value(self._value_edit.text(), base)
        if val is None:
            return
        steps = base_conversion_steps(val, base, 2)
        self._steps_text.setPlainText("\n".join(steps))
        self._steps_text.show()

    def _analyse_float(self):
        try:
            fval = float(self._float_edit.text())
        except ValueError:
            self._ieee_text.setPlainText("Invalid float value")
            return
        res = ieee754_encode(fval)
        lines = [
            f"Hex: {res.hex_repr}",
            f"Sign: {res.sign_bit}  Exponent: {''.join(map(str, res.exponent_bits))} ({res.biased_exponent}, bias={res.actual_exponent})",
            f"Mantissa: {''.join(map(str, res.mantissa_bits))}",
            f"Formula: {res.formula}",
        ]
        if res.is_special:
            lines.append(f"Special: {res.special_name}")
        self._ieee_text.setPlainText("\n".join(lines))
        self._draw_ieee(res)

    def _draw_ieee(self, res):
        from logicraft.theme import get_palette
        p = get_palette(self._dark)
        ax = self.canvas.axes
        ax.clear()
        self._canvas_title.setText("IEEE 754 Single Precision (32-Bit)")

        cell = 0.6
        for i, bit in enumerate(res.all_bits):
            x = i * cell
            if i == 0:
                c = "#ba1a1a"
            elif i < 9:
                c = p.primary
            else:
                c = p.tertiary
            ax.add_patch(__import__('matplotlib.patches', fromlist=['Rectangle']).Rectangle(
                (x, 0), cell, cell, facecolor=c, edgecolor=p.outline_variant, linewidth=0.5
            ))
            ax.text(x + cell/2, cell/2, str(bit), ha='center', va='center',
                    fontsize=8, color='#ffffff', fontweight='bold', fontfamily='monospace')

        ax.text(0.3, cell + 0.15, "S", ha='center', fontsize=9, color="#ba1a1a", fontweight='bold')
        ax.text(4.5 * cell, cell + 0.15, "Exponent (8 bits)", ha='center', fontsize=9, color=p.primary, fontweight='bold')
        ax.text(20 * cell, cell + 0.15, "Mantissa (23 bits)", ha='center', fontsize=9, color=p.tertiary, fontweight='bold')

        ax.text(16 * cell, -0.4, res.formula, ha='center', fontsize=10, color=p.on_surface, fontfamily='monospace')

        ax.set_xlim(-0.3, 32 * cell + 0.3)
        ax.set_ylim(-0.8, cell + 0.5)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title("IEEE 754 Single Precision", fontsize=13, fontweight='bold', color=p.on_surface, pad=10)
        self.canvas.fig.tight_layout()
        self.canvas.draw()
