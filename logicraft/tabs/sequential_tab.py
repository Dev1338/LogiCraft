"""
Tab 4 — Sequential Logic UI.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QGroupBox,
    QLabel,
    QComboBox,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QScrollArea,
    QFileDialog,
    QSpinBox,
)
from logicraft.canvas import MplCanvas
from logicraft.engines.sequential_engine import (
    get_state_table,
    simulate,
    parse_input_string,
    TimingResult,
)


class SequentialTab(QWidget):
    def __init__(self, dark=False):
        super().__init__()
        self._dark = dark
        self._last_result = None
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

        # FF type
        ff_group = QGroupBox("Flip-Flop Type")
        ff_lay = QHBoxLayout(ff_group)
        self._ff_combo = QComboBox()
        self._ff_combo.addItems(["D", "T", "SR", "JK"])
        self._ff_combo.currentTextChanged.connect(self._on_ff_changed)
        ff_lay.addWidget(self._ff_combo)
        ff_lay.addStretch()
        left.addWidget(ff_group)

        # State table
        st_group = QGroupBox("Characteristic Table")
        st_lay = QVBoxLayout(st_group)
        self._state_table = QTableWidget()
        self._state_table.setMaximumHeight(200)
        st_lay.addWidget(self._state_table)
        left.addWidget(st_group)

        # Input sequence
        inp_group = QGroupBox("Simulation Input")
        inp_lay = QVBoxLayout(inp_group)
        inp_lay.addWidget(QLabel("Input sequence (space-separated):"))
        self._input_edit = QLineEdit("0 1 1 0 1 0 1 1")
        inp_lay.addWidget(self._input_edit)
        q_row = QHBoxLayout()
        q_row.addWidget(QLabel("Initial Q:"))
        self._q_spin = QSpinBox()
        self._q_spin.setRange(0, 1)
        self._q_spin.setValue(0)
        q_row.addWidget(self._q_spin)
        q_row.addStretch()
        inp_lay.addLayout(q_row)
        left.addWidget(inp_group)

        # Buttons
        btn_row = QHBoxLayout()
        self._run_btn = QPushButton("▶ Run Simulation")
        self._run_btn.clicked.connect(self._run)
        btn_row.addWidget(self._run_btn)
        self._csv_btn = QPushButton("📋 Export CSV")
        self._csv_btn.setProperty("class", "secondary")
        self._csv_btn.clicked.connect(self._export_csv)
        btn_row.addWidget(self._csv_btn)
        btn_row.addStretch()
        left.addLayout(btn_row)

        left.addStretch()
        left_scroll.setWidget(left_w)
        splitter.addWidget(left_scroll)

        # Right
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(8, 8, 8, 8)
        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("Timing Diagram"))
        hdr.addStretch()

        right_lay.addLayout(hdr)
        self.canvas = MplCanvas(self, width=9, height=6, dark=self._dark)
        right_lay.addWidget(self.canvas)
        splitter.addWidget(right)
        splitter.setSizes([380, 720])

        self._on_ff_changed("D")

    def apply_theme(self, dark):
        self._dark = dark
        self.canvas.apply_theme(dark)
        if self._last_result:
            self._draw_timing(self._last_result)

    def _on_ff_changed(self, ff_type):
        table = get_state_table(ff_type)
        if not table:
            return
        cols = list(table[0].keys())
        self._state_table.setRowCount(len(table))
        self._state_table.setColumnCount(len(cols))
        self._state_table.setHorizontalHeaderLabels(cols)
        for r, row in enumerate(table):
            for c, key in enumerate(cols):
                val = str(row[key])
                item = QTableWidgetItem(val)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if val == "INVALID":
                    item.setForeground(Qt.GlobalColor.red)
                self._state_table.setItem(r, c, item)
        # Improve column sizing
        header = self._state_table.horizontalHeader()
        header.setMinimumSectionSize(50)
        self._state_table.resizeColumnsToContents()
        header.setStretchLastSection(True)

        # hint
        if ff_type in ("D", "T"):
            self._input_edit.setPlaceholderText("e.g. 0 1 1 0 1")
        else:
            self._input_edit.setPlaceholderText("e.g. 00 01 10 11 (bit pairs)")

    def _run(self):
        ff_type = self._ff_combo.currentText()
        seq = parse_input_string(ff_type, self._input_edit.text())
        if not seq:
            return
        result = simulate(ff_type, seq, self._q_spin.value())
        self._last_result = result
        self._draw_timing(result)

    def _draw_timing(self, result: TimingResult):
        from logicraft.theme import get_palette

        p = get_palette(self._dark)
        ax = self.canvas.axes
        ax.clear()

        n = len(result.states)
        if n == 0:
            return

        signals = {}
        # Clock
        clk = []
        for i in range(n):
            clk.extend([0, 1])
        signals["CLK"] = clk

        # Input signals
        for inp_name in result.input_names:
            sig = []
            for st in result.states:
                v = st.inputs.get(inp_name, 0)
                sig.extend([v, v])
            signals[inp_name] = sig

        # Q
        q_sig = []
        for st in result.states:
            q_sig.extend([st.q_before, st.q_after])
        signals["Q"] = q_sig

        # Q̄
        qb_sig = []
        for st in result.states:
            qb_sig.extend([1 - st.q_before, 1 - st.q_after])
        signals["Q̄"] = qb_sig

        n_signals = len(signals)
        t = [i * 0.5 for i in range(len(clk))]

        colors = {
            "CLK": p.outline,
            "Q": p.primary,
            "Q̄": p.secondary,
        }
        for inp_name in result.input_names:
            colors[inp_name] = p.tertiary

        self.canvas.fig.clear()
        axes = self.canvas.fig.subplots(n_signals, 1, sharex=True)
        if n_signals == 1:
            axes = [axes]

        for idx, (name, sig) in enumerate(signals.items()):
            a = axes[idx]
            color = colors.get(name, p.on_surface)
            a.step(t, sig, where="post", color=color, linewidth=2)
            if name == "Q":
                a.fill_between(t, sig, step="post", alpha=0.15, color=color)
            a.set_ylabel(
                name,
                fontsize=11,
                fontweight="bold",
                color=color,
                rotation=0,
                labelpad=30,
            )
            a.set_ylim(-0.2, 1.4)
            a.set_yticks([0, 1])
            a.set_yticklabels(["0", "1"], fontsize=9)
            a.spines["top"].set_visible(False)
            a.spines["right"].set_visible(False)
            a.spines["left"].set_color(p.outline_variant)
            a.spines["bottom"].set_color(p.outline_variant)
            a.tick_params(colors=p.on_surface_variant, labelsize=9)
            a.set_facecolor(self.canvas.fig.get_facecolor())

            # Invalid SR cycles
            for st in result.states:
                if st.is_invalid:
                    x_start = st.cycle
                    a.axvspan(x_start, x_start + 1, color="#ba1a1a", alpha=0.12)

        axes[-1].set_xlabel("Clock Cycle", fontsize=11, color=p.on_surface)
        axes[0].set_title(
            f"{result.ff_type} Flip-Flop Timing Diagram",
            fontsize=13,
            fontweight="bold",
            color=p.on_surface,
            pad=8,
        )
        self.canvas.fig.subplots_adjust(
            hspace=0.15, left=0.12, right=0.96, top=0.92, bottom=0.08
        )
        self.canvas.draw()

    def _export_csv(self):
        if not self._last_result:
            return
        import csv

        path, _ = QFileDialog.getSaveFileName(
            self, "Export Log", "timing_log.csv", "CSV (*.csv)"
        )
        if not path:
            return
        res = self._last_result
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            headers = ["Cycle"] + res.input_names + ["Q_before", "Q_after", "Invalid"]
            w.writerow(headers)
            for st in res.states:
                row = [st.cycle] + [st.inputs.get(n, 0) for n in res.input_names]
                row += [st.q_before, st.q_after, st.is_invalid]
                w.writerow(row)
