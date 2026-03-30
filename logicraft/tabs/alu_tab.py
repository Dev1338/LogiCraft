"""
Tab 1 — ALU Simulator UI.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QGroupBox,
    QComboBox, QPushButton, QLabel, QListWidget, QCheckBox,
    QLineEdit, QFrame, QScrollArea, QSizePolicy,
)
from logicraft.widgets import BitToggleRow, FlagPill, DraggableValueLabel, TonalSeparator
from logicraft.canvas import MplCanvas
from logicraft.engines.alu_engine import compute, OPERATIONS, ALUResult


class ALUTab(QWidget):
    def __init__(self, bit_width=8, dark=False):
        super().__init__()
        self._bw = bit_width
        self._dark = dark
        self._history = []
        self._last_result = None
        self._quiz_mode = False
        self._init_ui()

    def _init_ui(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)

        # ── Left Panel ──────────────────────────────────
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_widget = QWidget()
        left = QVBoxLayout(left_widget)
        left.setContentsMargins(24, 24, 24, 24)
        left.setSpacing(16)

        def create_input_frame(title_text, is_dashed=False):
            frame = QFrame()
            frame.setProperty("class", "input-box-dashed" if is_dashed else "input-box")
            lay = QVBoxLayout(frame)
            lay.setContentsMargins(12, 12, 12, 12)
            
            header = QHBoxLayout()
            icon = QLabel("⠿")
            icon.setStyleSheet("color: #727783; font-weight: bold; font-size: 16px;")
            title = QLabel(title_text)
            title.setStyleSheet("font-weight: 700; font-size: 11px; color: #48626e; letter-spacing: 0.5px;")
            header.addWidget(icon)
            header.addWidget(title)
            
            dec_lbl = QLabel("Dec:")
            dec_lbl.setStyleSheet("font-family: 'Courier New', monospace; font-size: 10px; font-weight: bold; color: #727783;")
            val_dec = QLabel("0")
            val_dec.setStyleSheet("font-family: 'Courier New', monospace; font-size: 11px; font-weight: bold; color: #1a1c1c;")
            
            hex_lbl = QLabel("Hex:")
            hex_lbl.setStyleSheet("font-family: 'Courier New', monospace; font-size: 10px; font-weight: bold; color: #ab47bc;")
            val_hex = QLabel("0x0")
            val_hex.setStyleSheet("font-family: 'Courier New', monospace; font-size: 11px; font-weight: bold; color: #ab47bc;")
            
            header.addStretch()
            for w in [dec_lbl, val_dec, hex_lbl, val_hex]:
                header.addWidget(w)
            
            lay.addLayout(header)
            return frame, lay, val_dec, val_hex

        # Input A
        self._input_a_group, a_lay, self._val_a_dec, self._val_a_hex = create_input_frame("INPUT A", is_dashed=True)
        self.input_a = BitToggleRow(self._bw, "")
        # hide internal labels in BitToggleRow to use our custom header
        self.input_a.layout().itemAt(0).widget().hide()
        self.input_a.dec_edit.hide()
        self.input_a.hex_edit.hide()
        self.input_a.layout().itemAt(2).layout().itemAt(0).widget().hide()
        self.input_a.layout().itemAt(2).layout().itemAt(2).widget().hide()
        
        self.input_a.value_changed.connect(lambda v: (self._val_a_dec.setText(str(v)), self._val_a_hex.setText(f"0x{v:X}")))
        a_lay.addWidget(self.input_a)
        left.addWidget(self._input_a_group)

        # Input B
        self._input_b_group, b_lay, self._val_b_dec, self._val_b_hex = create_input_frame("INPUT B", is_dashed=False)
        self.input_b = BitToggleRow(self._bw, "")
        self.input_b.layout().itemAt(0).widget().hide()
        self.input_b.dec_edit.hide()
        self.input_b.hex_edit.hide()
        self.input_b.layout().itemAt(2).layout().itemAt(0).widget().hide()
        self.input_b.layout().itemAt(2).layout().itemAt(2).widget().hide()
        
        self.input_b.value_changed.connect(lambda v: (self._val_b_dec.setText(str(v)), self._val_b_hex.setText(f"0x{v:X}")))
        b_lay.addWidget(self.input_b)
        left.addWidget(self._input_b_group)

        # Operation
        op_label = QLabel("OPERATION")
        op_label.setStyleSheet("font-weight: 700; font-size: 11px; color: #48626e; letter-spacing: 0.5px; margin-top: 8px;")
        left.addWidget(op_label)
        
        self.op_combo = QComboBox()
        self.op_combo.setFixedHeight(36)
        for cat, ops in OPERATIONS.items():
            for op in ops:
                self.op_combo.addItem(f"{cat}: {op}" if cat != "" else op, op) # Adjust to format nicely
        # Clean up combo box display
        self.op_combo.clear()
        self.op_combo.addItem("ADD (Addition)", "ADD")
        self.op_combo.addItem("SUB (Subtraction)", "SUB")
        self.op_combo.addItem("AND (Bitwise AND)", "AND")
        self.op_combo.addItem("OR (Bitwise OR)", "OR")
        self.op_combo.addItem("XOR (Bitwise XOR)", "XOR")
        left.addWidget(self.op_combo)

        # Compute
        self.compute_btn = QPushButton("COMPUTE")
        self.compute_btn.setProperty("class", "compute-btn")
        self.compute_btn.clicked.connect(self._compute)
        left.addWidget(self.compute_btn)

        # Status Flags
        flags_label = QLabel("STATUS FLAGS")
        flags_label.setStyleSheet("font-weight: 700; font-size: 11px; color: #48626e; letter-spacing: 0.5px; margin-top: 8px;")
        left.addWidget(flags_label)
        
        flags_lay = QHBoxLayout()
        self.flag_z = FlagPill("ZERO")
        self.flag_c = FlagPill("CARRY")
        self.flag_v = FlagPill("OVF")
        self.flag_s = FlagPill("SIGN")
        
        # specific hardcoded styles for exact mockup representation
        self.flag_c.setStyleSheet("background-color: #25752b; color: white;")
        self.flag_v.setStyleSheet("background-color: #ba1a1a; color: white;")
        
        for f in [self.flag_z, self.flag_c, self.flag_v, self.flag_s]:
            flags_lay.addWidget(f)
        flags_lay.addStretch()
        left.addLayout(flags_lay)

        # Result
        self._result_group = QFrame()
        self._result_group.setProperty("class", "result-box")
        res_lay = QVBoxLayout(self._result_group)
        res_lay.setContentsMargins(16, 16, 16, 16)
        
        res_header = QHBoxLayout()
        res_title = QLabel("RESULT OUTPUT")
        res_title.setStyleSheet("font-weight: 700; font-size: 11px; color: #48626e; letter-spacing: 0.5px;")
        res_header.addWidget(res_title)
        res_header.addStretch()
        move_icon = QLabel("☩") # Drag icon substitute
        move_icon.setStyleSheet("font-size: 18px; color: #727783;")
        res_header.addWidget(move_icon)
        res_lay.addLayout(res_header)

        # Hidden bit row for functionality
        self.result_bits = BitToggleRow(self._bw, "", read_only=True)
        self.result_bits.hide() 

        # Results grid mapping
        grid = QVBoxLayout()
        grid.setSpacing(8)
        
        def create_res_row(label):
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("font-family: 'Courier New', monospace; font-size: 11px; color: #1a1c1c; font-weight: normal;")
            val = DraggableValueLabel("—")
            val.setStyleSheet("font-family: 'Courier New', monospace; font-size: 11px; color: #1a1c1c; font-weight: bold;")
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val)
            grid.addLayout(row)
            return val
            
        self._res_bin = create_res_row("Binary")
        self._res_dec = create_res_row("Decimal")
        self._res_hex = create_res_row("Hex")
        self._res_signed = create_res_row("Signed")
        self._res_signed.setStyleSheet("font-family: 'Courier New', monospace; font-size: 11px; color: #ba1a1a; font-weight: bold;")

        res_lay.addLayout(grid)
        left.addWidget(self._result_group)

        left.addWidget(TonalSeparator())

        # History
        hist_label = QLabel("Operation History")
        hist_label.setProperty("class", "subheading")
        left.addWidget(hist_label)
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(180)
        left.addWidget(self.history_list)

        left.addStretch()
        left_scroll.setWidget(left_widget)
        splitter.addWidget(left_scroll)

        # ── Right Canvas ────────────────────────────────
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(8, 8, 8, 8)

        canvas_header = QHBoxLayout()
        canvas_header.addWidget(QLabel("Gate-Level Carry Chain"))
        canvas_header.addStretch()
        right_lay.addLayout(canvas_header)

        self.canvas = MplCanvas(self, width=9, height=5, dark=self._dark)
        right_lay.addWidget(self.canvas)
        splitter.addWidget(right)

        splitter.setSizes([420, 700])

    def set_bit_width(self, w):
        self._bw = w
        self.input_a.set_bit_width(w)
        self.input_b.set_bit_width(w)
        self.result_bits.set_bit_width(w)

    def apply_theme(self, dark):
        self._dark = dark
        self.canvas.apply_theme(dark)
        if self._last_result:
            self._draw_carry_chain(self._last_result)

    def _compute(self):
        a = self.input_a.value()
        b = self.input_b.value()
        op = self.op_combo.currentData()
        res = compute(a, b, op, self._bw)
        self._last_result = res

        # Update flags
        self.flag_z.set_active(res.zero)
        self.flag_c.set_active(res.carry)
        self.flag_v.set_active(res.overflow)
        self.flag_s.set_active(res.sign)

        if not self._quiz_mode:
            self._show_result(res)

        self._draw_carry_chain(res)

        # History
        entry = f"A={a} {op} B={b} = {res.result} [Z={int(res.zero)} C={int(res.carry)} V={int(res.overflow)} S={int(res.sign)}]"
        self._history.append(entry)
        if len(self._history) > 20:
            self._history.pop(0)
        self.history_list.clear()
        self.history_list.addItems(self._history)
        self.history_list.scrollToBottom()

    def _show_result(self, res):
        self.result_bits.set_value(res.result)
        self._res_bin.setText(f"BIN: {res.result_bin}")
        self._res_dec.setText(f"DEC: {res.result}")
        self._res_hex.setText(f"HEX: {res.result_hex}")
        self._res_signed.setText(f"SIGNED: {res.signed_result}")

        for w in [self._res_bin, self._res_dec, self._res_hex, self._res_signed]:
            w.set_drag_value(res.result)

    def _toggle_quiz(self, on):
        self._quiz_mode = on
        self._quiz_frame.setVisible(on)
        if on:
            self._result_group.hide()
        else:
            self._result_group.show()
            if self._last_result:
                self._show_result(self._last_result)

    def _check_quiz(self):
        if not self._last_result:
            return
        try:
            ans = int(self._quiz_input.text())
        except ValueError:
            self._quiz_feedback.setText("Enter a valid integer")
            return
        expected = self._last_result.signed_result
        if ans == expected or ans == self._last_result.result:
            self._quiz_feedback.setText("✅ Correct!")
            self._quiz_feedback.setStyleSheet("color: #25752b; font-weight: bold;")
        else:
            self._quiz_feedback.setText(f"❌ Wrong — correct: {expected}")
            self._quiz_feedback.setStyleSheet("color: #ba1a1a; font-weight: bold;")
            self._show_result(self._last_result)
            self._result_group.show()

    def _draw_carry_chain(self, res: ALUResult):
        from logicraft.theme import get_palette
        p = get_palette(self._dark)
        ax = self.canvas.axes
        ax.clear()

        n = res.bit_width
        cell_w, cell_h = 1.2, 1.6
        total_w = n * cell_w + (n - 1) * 0.3

        for i in range(n):
            x = i * (cell_w + 0.3)
            # Cell background
            ax.add_patch(__import__('matplotlib.patches', fromlist=['FancyBboxPatch']).FancyBboxPatch(
                (x, 0), cell_w, cell_h, boxstyle="round,pad=0.05",
                facecolor=p.surface_container_lowest, edgecolor=p.outline_variant, linewidth=1
            ))
            # Bit label
            bit_label = f"Bit {n - 1 - i}"
            ax.text(x + cell_w/2, cell_h + 0.15, bit_label, ha='center', va='bottom',
                    fontsize=8, color=p.secondary)
            # A bit
            ax.text(x + cell_w/2, cell_h - 0.25, f"A: {res.a_bits[i]}", ha='center',
                    fontsize=10, color=p.on_surface, fontfamily='monospace', fontweight='bold')
            # B bit
            ax.text(x + cell_w/2, cell_h - 0.55, f"B: {res.b_bits[i]}", ha='center',
                    fontsize=10, color=p.on_surface, fontfamily='monospace', fontweight='bold')
            # Gate
            ax.text(x + cell_w/2, cell_h/2, res.gate_labels[i], ha='center', va='center',
                    fontsize=11, color=p.primary, fontweight='bold')
            # Result
            ax.text(x + cell_w/2, 0.25, f"= {res.result_bits[i]}", ha='center',
                    fontsize=11, color=p.tertiary, fontweight='bold', fontfamily='monospace')

            # Carry annotation
            if i < n and res.carry_bits[i]:
                ax.annotate("", xy=(x - 0.1, cell_h/2), xytext=(x - 0.25, cell_h/2 + 0.3),
                            arrowprops=dict(arrowstyle="->", color=p.error, lw=1.5))
                ax.text(x - 0.18, cell_h/2 + 0.4, f"C{res.carry_bits[i]}", fontsize=7,
                        color=p.error, ha='center', fontweight='bold')

        ax.set_xlim(-0.5, total_w + 0.5)
        ax.set_ylim(-0.5, cell_h + 0.8)
        ax.set_aspect('equal')
        ax.axis('off')
        title = f"{self._bw}-Bit {res.gate_labels[0]} Chain" if res.gate_labels else "Result"
        ax.set_title(title, fontsize=13, fontweight='bold', color=p.on_surface, pad=10)
        self.canvas.fig.tight_layout()
        self.canvas.draw()
