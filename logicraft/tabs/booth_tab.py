"""
Tab 6 — Booth's Algorithm UI.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QGroupBox,
    QLabel, QPushButton, QSpinBox, QComboBox, QTableWidget,
    QTableWidgetItem, QScrollArea, QFileDialog,
)
from logicraft.canvas import MplCanvas
from logicraft.widgets import TonalSeparator
from logicraft.engines.booth_engine import run_booth, BoothResult


class BoothTab(QWidget):
    def __init__(self, dark=False):
        super().__init__()
        self._dark = dark
        self._result = None
        self._step = 0
        self._init_ui()

    def _init_ui(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(splitter)

        # Left
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_w = QWidget()
        left = QVBoxLayout(left_w)
        left.setContentsMargins(16, 16, 16, 16)
        left.setSpacing(10)

        inp_group = QGroupBox("Inputs")
        inp_lay = QVBoxLayout(inp_group)
        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Multiplicand M:"))
        self._m_spin = QSpinBox()
        self._m_spin.setRange(-128, 127)
        self._m_spin.setValue(5)
        r1.addWidget(self._m_spin)
        r1.addStretch()
        inp_lay.addLayout(r1)
        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Multiplier R:"))
        self._r_spin = QSpinBox()
        self._r_spin.setRange(-128, 127)
        self._r_spin.setValue(-3)
        r2.addWidget(self._r_spin)
        r2.addStretch()
        inp_lay.addLayout(r2)
        r3 = QHBoxLayout()
        r3.addWidget(QLabel("Bit Width:"))
        self._bw_combo = QComboBox()
        self._bw_combo.addItems(["4", "6", "8"])
        self._bw_combo.setCurrentIndex(2)
        r3.addWidget(self._bw_combo)
        r3.addStretch()
        inp_lay.addLayout(r3)
        left.addWidget(inp_group)

        btn_row = QHBoxLayout()
        self._run_btn = QPushButton("▶ Run Booth's")
        self._run_btn.clicked.connect(self._run)
        btn_row.addWidget(self._run_btn)
        btn_row.addStretch()
        left.addLayout(btn_row)

        # Nav
        nav_row = QHBoxLayout()
        self._prev_btn = QPushButton("◀ Prev")
        self._prev_btn.setProperty("class", "secondary")
        self._prev_btn.clicked.connect(self._prev_step)
        self._prev_btn.setEnabled(False)
        nav_row.addWidget(self._prev_btn)
        self._step_label = QLabel("Step: —")
        self._step_label.setStyleSheet("font-weight:bold; font-size:14px;")
        nav_row.addWidget(self._step_label)
        self._next_btn = QPushButton("Next ▶")
        self._next_btn.setProperty("class", "secondary")
        self._next_btn.clicked.connect(self._next_step)
        self._next_btn.setEnabled(False)
        nav_row.addWidget(self._next_btn)
        nav_row.addStretch()
        left.addLayout(nav_row)

        # Step table
        st_group = QGroupBox("Step Table (click to jump)")
        st_lay = QVBoxLayout(st_group)
        self._step_table = QTableWidget()
        self._step_table.setMaximumHeight(260)
        self._step_table.cellClicked.connect(self._on_table_click)
        st_lay.addWidget(self._step_table)
        left.addWidget(st_group)

        # Result
        self._result_label = QLabel("Result: —")
        self._result_label.setProperty("class", "mono")
        self._result_label.setWordWrap(True)
        self._result_label.setStyleSheet("font-size:13px; padding:6px; font-weight:bold;")
        left.addWidget(self._result_label)

        # Export
        self._csv_btn = QPushButton("📋 Export CSV")
        self._csv_btn.setProperty("class", "secondary")
        self._csv_btn.clicked.connect(self._export_csv)
        left.addWidget(self._csv_btn)

        left.addStretch()
        left_scroll.setWidget(left_w)
        splitter.addWidget(left_scroll)

        # Right
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(8, 8, 8, 8)
        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("Register Visualization"))
        hdr.addStretch()

        right_lay.addLayout(hdr)
        self.canvas = MplCanvas(self, width=10, height=7, dark=self._dark)
        right_lay.addWidget(self.canvas)
        splitter.addWidget(right)
        splitter.setSizes([380, 720])

    def apply_theme(self, dark):
        self._dark = dark
        self.canvas.apply_theme(dark)
        if self._result:
            self._draw_step()

    def _run(self):
        m = self._m_spin.value()
        r = self._r_spin.value()
        bw = int(self._bw_combo.currentText())
        self._result = run_booth(m, r, bw)
        self._step = 0
        self._update_table()
        self._draw_step()
        self._update_nav()

        status = "✅ Correct" if self._result.is_correct else "❌ Mismatch"
        self._result_label.setText(
            f"Product: {self._result.final_product} (expected {self._result.expected_product}) {status}\n"
            f"Binary: {self._result.product_bits}"
        )

    def _update_table(self):
        res = self._result
        if not res:
            return
        cols = ["Cycle", "Action", "A", "Q", "Q-1"]
        self._step_table.setRowCount(len(res.cycles))
        self._step_table.setColumnCount(len(cols))
        self._step_table.setHorizontalHeaderLabels(cols)
        for r, st in enumerate(res.cycles):
            self._step_table.setItem(r, 0, QTableWidgetItem(str(st.cycle)))
            self._step_table.setItem(r, 1, QTableWidgetItem(st.action))
            a_str = ''.join(map(str, st.a_bits))
            q_str = ''.join(map(str, st.q_bits))
            self._step_table.setItem(r, 2, QTableWidgetItem(a_str))
            self._step_table.setItem(r, 3, QTableWidgetItem(q_str))
            self._step_table.setItem(r, 4, QTableWidgetItem(str(st.q_minus_1)))
            for c in range(len(cols)):
                item = self._step_table.item(r, c)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self._step_table.resizeColumnsToContents()

    def _update_nav(self):
        if not self._result:
            return
        n = len(self._result.cycles)
        self._prev_btn.setEnabled(self._step > 0)
        self._next_btn.setEnabled(self._step < n - 1)
        self._step_label.setText(f"Step: {self._step} / {n - 1}")
        self._step_table.selectRow(self._step)

    def _prev_step(self):
        if self._step > 0:
            self._step -= 1
            self._draw_step()
            self._update_nav()

    def _next_step(self):
        if self._result and self._step < len(self._result.cycles) - 1:
            self._step += 1
            self._draw_step()
            self._update_nav()

    def _on_table_click(self, row, _col):
        if self._result and 0 <= row < len(self._result.cycles):
            self._step = row
            self._draw_step()
            self._update_nav()

    def _draw_step(self):
        if not self._result:
            return
        from logicraft.theme import get_palette
        import matplotlib.patches as mpatches
        p = get_palette(self._dark)
        st = self._result.cycles[self._step]
        bw = self._result.bit_width

        self.canvas.fig.clear()
        gs = self.canvas.fig.add_gridspec(2, 1, height_ratios=[2, 1], hspace=0.4)
        ax_reg = self.canvas.fig.add_subplot(gs[0])
        ax_hist = self.canvas.fig.add_subplot(gs[1])

        # Register vis
        cell = 0.8
        y_a = 2.0
        y_q = 0.8
        y_q1 = 0.8

        # Action label
        action_colors = {"ADD M": p.tertiary, "SUB M": "#ba1a1a", "NOP": p.outline, "INIT": p.secondary}
        ac = action_colors.get(st.action, p.outline)
        ax_reg.text((bw * cell) / 2, y_a + cell + 0.6, st.action,
                    ha='center', fontsize=16, fontweight='bold', color=ac)
        ax_reg.text((bw * cell) / 2, y_a + cell + 0.25, st.action_reason,
                    ha='center', fontsize=10, color=p.on_surface_variant)

        # A register
        ax_reg.text(-0.5, y_a + cell / 2, "A", ha='right', va='center',
                    fontsize=13, fontweight='bold', color=p.primary)
        for i, bit in enumerate(st.a_bits):
            x = i * cell
            ax_reg.add_patch(mpatches.FancyBboxPatch(
                (x, y_a), cell, cell, boxstyle="round,pad=0.03",
                facecolor=p.primary if bit else p.surface_container_high,
                edgecolor=p.outline_variant, linewidth=1
            ))
            tc = p.on_primary if bit else p.on_surface
            ax_reg.text(x + cell/2, y_a + cell/2, str(bit), ha='center', va='center',
                        fontsize=14, fontweight='bold', color=tc, fontfamily='monospace')

        # Q register
        ax_reg.text(-0.5, y_q + cell / 2, "Q", ha='right', va='center',
                    fontsize=13, fontweight='bold', color=p.tertiary)
        for i, bit in enumerate(st.q_bits):
            x = i * cell
            ax_reg.add_patch(mpatches.FancyBboxPatch(
                (x, y_q), cell, cell, boxstyle="round,pad=0.03",
                facecolor=p.tertiary if bit else p.surface_container_high,
                edgecolor=p.outline_variant, linewidth=1
            ))
            tc = p.on_tertiary if bit else p.on_surface
            ax_reg.text(x + cell/2, y_q + cell/2, str(bit), ha='center', va='center',
                        fontsize=14, fontweight='bold', color=tc, fontfamily='monospace')

        # Q-1
        q1_x = bw * cell + 0.4
        ax_reg.add_patch(mpatches.FancyBboxPatch(
            (q1_x, y_q), cell, cell, boxstyle="round,pad=0.03",
            facecolor=p.secondary if st.q_minus_1 else p.surface_container_high,
            edgecolor=p.outline_variant, linewidth=1
        ))
        tc = p.on_secondary if st.q_minus_1 else p.on_surface
        ax_reg.text(q1_x + cell/2, y_q + cell/2, str(st.q_minus_1), ha='center', va='center',
                    fontsize=14, fontweight='bold', color=tc, fontfamily='monospace')
        ax_reg.text(q1_x + cell/2, y_q - 0.2, "Q₋₁", ha='center', fontsize=9, color=p.secondary)

        ax_reg.set_xlim(-1, (bw + 2) * cell)
        ax_reg.set_ylim(0, y_a + cell + 1.0)
        ax_reg.set_aspect('equal')
        ax_reg.axis('off')
        ax_reg.set_title(f"Booth's Algorithm — Cycle {st.cycle}", fontsize=13,
                         fontweight='bold', color=p.on_surface, pad=8)

        # History chart
        steps = self._result.cycles[:self._step + 1]
        xs = [s.cycle for s in steps]
        a_vals = [s.a_signed for s in steps]
        q_vals = [s.q_signed for s in steps]
        ax_hist.plot(xs, a_vals, 'o-', color=p.primary, label="A (signed)", linewidth=2, markersize=5)
        ax_hist.plot(xs, q_vals, 's-', color=p.tertiary, label="Q (signed)", linewidth=2, markersize=5)
        ax_hist.set_xlabel("Cycle", fontsize=10, color=p.on_surface_variant)
        ax_hist.set_ylabel("Signed Value", fontsize=10, color=p.on_surface_variant)
        ax_hist.legend(fontsize=9)
        ax_hist.grid(True, alpha=0.3)
        ax_hist.set_facecolor(self.canvas.fig.get_facecolor())
        for spine in ax_hist.spines.values():
            spine.set_color(p.outline_variant)
        ax_hist.tick_params(colors=p.on_surface_variant, labelsize=9)

        self.canvas.fig.subplots_adjust(left=0.1, right=0.95, top=0.92, bottom=0.08)
        self.canvas.draw()

    def _export_csv(self):
        if not self._result:
            return
        import csv
        path, _ = QFileDialog.getSaveFileName(self, "Export Log", "booth_log.csv", "CSV (*.csv)")
        if not path:
            return
        with open(path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(["Cycle", "Action", "A_bits", "Q_bits", "Q-1", "A_signed", "Q_signed"])
            for st in self._result.cycles:
                w.writerow([st.cycle, st.action, ''.join(map(str, st.a_bits)),
                            ''.join(map(str, st.q_bits)), st.q_minus_1, st.a_signed, st.q_signed])
