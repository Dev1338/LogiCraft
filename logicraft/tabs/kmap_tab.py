"""
Tab 3 — Gates & K-Map UI.
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
    QTableWidget,
    QTableWidgetItem,
    QScrollArea,
    QFileDialog,
)
from logicraft.canvas import MplCanvas
from logicraft.engines.kmap_engine import solve


class KMapTab(QWidget):
    def __init__(self, dark=False):
        super().__init__()
        self._dark = dark
        self._n_vars = 3
        self._outputs = [0] * (1 << self._n_vars)
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

        # Variable selector
        var_group = QGroupBox("Variables")
        var_lay = QHBoxLayout(var_group)
        var_lay.addWidget(QLabel("Count:"))
        self._var_combo = QComboBox()
        self._var_combo.addItems(["2", "3", "4"])
        self._var_combo.setCurrentIndex(1)
        self._var_combo.currentIndexChanged.connect(self._on_var_changed)
        var_lay.addWidget(self._var_combo)
        var_lay.addStretch()
        left.addWidget(var_group)

        # Truth table
        tt_group = QGroupBox("Truth Table (click output to cycle 0→1→X)")
        tt_lay = QVBoxLayout(tt_group)
        self._table = QTableWidget()
        self._table.cellClicked.connect(self._on_cell_clicked)
        tt_lay.addWidget(self._table)
        left.addWidget(tt_group)

        # Buttons
        btn_row = QHBoxLayout()
        self._solve_btn = QPushButton("⚡ Solve")
        self._solve_btn.clicked.connect(self._solve)
        btn_row.addWidget(self._solve_btn)
        self._csv_btn = QPushButton("📋 Export CSV")
        self._csv_btn.setProperty("class", "secondary")
        self._csv_btn.clicked.connect(self._export_csv)
        btn_row.addWidget(self._csv_btn)
        btn_row.addStretch()
        left.addLayout(btn_row)

        # SOP result
        self._sop_label = QLabel("SOP: —")
        self._sop_label.setProperty("class", "mono")
        self._sop_label.setWordWrap(True)
        self._sop_label.setStyleSheet("font-size:14px; padding:8px; font-weight:bold;")
        left.addWidget(self._sop_label)

        left.addStretch()
        left_scroll.setWidget(left_w)
        splitter.addWidget(left_scroll)

        # Right
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(8, 8, 8, 8)
        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("Karnaugh Map"))
        hdr.addStretch()

        right_lay.addLayout(hdr)
        self.canvas = MplCanvas(self, width=8, height=6, dark=self._dark)
        right_lay.addWidget(self.canvas)
        splitter.addWidget(right)
        splitter.setSizes([400, 700])

        self._rebuild_table()

    def apply_theme(self, dark):
        self._dark = dark
        self.canvas.apply_theme(dark)

    def _on_var_changed(self, idx):
        self._n_vars = idx + 2
        self._outputs = [0] * (1 << self._n_vars)
        self._rebuild_table()

    def _rebuild_table(self):
        n = self._n_vars
        rows = 1 << n
        var_names = [chr(65 + i) for i in range(n)]
        self._table.setRowCount(rows)
        self._table.setColumnCount(n + 1)
        self._table.setHorizontalHeaderLabels(var_names + ["F"])

        for r in range(rows):
            for c in range(n):
                bit = (r >> (n - 1 - c)) & 1
                item = QTableWidgetItem(str(bit))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._table.setItem(r, c, item)
            out_item = QTableWidgetItem(self._out_text(self._outputs[r]))
            out_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            out_item.setFlags(out_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(r, n, out_item)

        self._table.resizeColumnsToContents()

    def _out_text(self, v):
        if v == -1:
            return "X"
        return str(v)

    def _on_cell_clicked(self, row, col):
        if col != self._n_vars:
            return
        cur = self._outputs[row]
        nxt = {0: 1, 1: -1, -1: 0}[cur]
        self._outputs[row] = nxt
        item = self._table.item(row, col)
        item.setText(self._out_text(nxt))

    def _solve(self):
        res = solve(self._n_vars, self._outputs)
        self._sop_label.setText(f"SOP: {res.sop_expression}")
        self._draw_kmap(res)

    def _draw_kmap(self, res):
        from logicraft.theme import get_palette
        import matplotlib.patches as mpatches

        p = get_palette(self._dark)
        ax = self.canvas.axes
        ax.clear()

        rows = len(res.kmap_grid)
        cols = len(res.kmap_grid[0]) if rows else 0
        cell = 1.2

        for r in range(rows):
            for c in range(cols):
                x, y = c * cell, (rows - 1 - r) * cell
                val = res.kmap_grid[r][c]
                fc = p.surface_container_lowest
                ax.add_patch(
                    mpatches.FancyBboxPatch(
                        (x, y),
                        cell,
                        cell,
                        boxstyle="round,pad=0.03",
                        facecolor=fc,
                        edgecolor=p.outline_variant,
                        linewidth=1,
                    )
                )
                color = p.on_surface if val != "X" else p.error
                ax.text(
                    x + cell / 2,
                    y + cell / 2,
                    val,
                    ha="center",
                    va="center",
                    fontsize=16,
                    fontweight="bold",
                    color=color,
                    fontfamily="monospace",
                )

        # Labels
        for c, lbl in enumerate(res.col_labels):
            ax.text(
                c * cell + cell / 2,
                rows * cell + 0.2,
                lbl,
                ha="center",
                fontsize=10,
                color=p.secondary,
                fontweight="bold",
                fontfamily="monospace",
            )
        for r, lbl in enumerate(res.row_labels):
            ax.text(
                -0.3,
                (rows - 1 - r) * cell + cell / 2,
                lbl,
                ha="right",
                va="center",
                fontsize=10,
                color=p.secondary,
                fontweight="bold",
                fontfamily="monospace",
            )

        # Draw groups
        for imp, color in res.groups:
            cells = []
            for mt in imp.minterms:
                bits = format(mt, f"0{self._n_vars}b")
                if self._n_vars == 2:
                    r_bits, c_bits = bits[0], bits[1]
                elif self._n_vars == 3:
                    r_bits, c_bits = bits[0], bits[1:]
                else:
                    r_bits, c_bits = bits[:2], bits[2:]
                ri = res.row_labels.index(r_bits) if r_bits in res.row_labels else 0
                ci = res.col_labels.index(c_bits) if c_bits in res.col_labels else 0
                cells.append((ri, ci))

            if cells:
                min_r = min(c[0] for c in cells)
                max_r = max(c[0] for c in cells)
                min_c = min(c[1] for c in cells)
                max_c = max(c[1] for c in cells)
                x = min_c * cell - 0.08
                y = (rows - 1 - max_r) * cell - 0.08
                w = (max_c - min_c + 1) * cell + 0.16
                h = (max_r - min_r + 1) * cell + 0.16
                ax.add_patch(
                    mpatches.FancyBboxPatch(
                        (x, y),
                        w,
                        h,
                        boxstyle="round,pad=0.08",
                        facecolor=color + "20",
                        edgecolor=color,
                        linewidth=2,
                    )
                )

        ax.set_xlim(-0.8, cols * cell + 0.5)
        ax.set_ylim(-0.5, rows * cell + 0.6)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(
            f"{self._n_vars}-Variable Karnaugh Map",
            fontsize=13,
            fontweight="bold",
            color=p.on_surface,
            pad=10,
        )

        # Legend
        for i, (imp, color) in enumerate(res.groups):
            var_names = [chr(65 + j) for j in range(self._n_vars)]
            expr = imp.to_expr(var_names)
            ax.text(
                cols * cell + 0.6,
                (rows - 1) * cell - i * 0.5,
                f"■ {expr}",
                fontsize=10,
                color=color,
                fontweight="bold",
            )

        self.canvas.fig.tight_layout()
        self.canvas.draw()

    def _export_csv(self):
        import csv

        path, _ = QFileDialog.getSaveFileName(
            self, "Export Truth Table", "truth_table.csv", "CSV (*.csv)"
        )
        if not path:
            return
        n = self._n_vars
        var_names = [chr(65 + i) for i in range(n)]
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(var_names + ["F"])
            for r in range(1 << n):
                row = [(r >> (n - 1 - c)) & 1 for c in range(n)]
                out = self._outputs[r]
                row.append("X" if out == -1 else str(out))
                writer.writerow(row)
