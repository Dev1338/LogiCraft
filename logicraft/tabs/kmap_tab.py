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

        # View selector
        self._view_stack = QGroupBox("Visualization")
        v_lay = QVBoxLayout(self._view_stack)
        hdr = QHBoxLayout()
        self._view_combo = QComboBox()
        self._view_combo.addItems(["K-Map View", "Logic Circuit"])
        self._view_combo.currentIndexChanged.connect(self._on_view_changed)
        hdr.addWidget(self._view_combo)
        hdr.addStretch()
        v_lay.addLayout(hdr)

        self.canvas = MplCanvas(self, width=8, height=6, dark=self._dark)
        v_lay.addWidget(self.canvas)
        right_lay.addWidget(self._view_stack)
        splitter.addWidget(right)
        splitter.setSizes([400, 700])

        self._rebuild_table()
        self._last_res = None

    def apply_theme(self, dark):
        self._dark = dark
        self.canvas.apply_theme(dark)
        if self._last_res:
            self._on_view_changed()

    def _on_view_changed(self, idx=None):
        if not self._last_res:
            return
        mode = self._view_combo.currentText()
        if mode == "K-Map View":
            self._draw_kmap(self._last_res)
        else:
            self._draw_circuit(self._last_res)

    def _on_var_changed(self, idx):
        self._n_vars = idx + 2
        self._outputs = [0] * (1 << self._n_vars)
        self._last_res = None
        self._rebuild_table()
        self.canvas.axes.clear()
        self.canvas.draw()

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

        # Improve column sizing
        header = self._table.horizontalHeader()
        for i in range(n + 1):
            header.setMinimumSectionSize(50)
        self._table.resizeColumnsToContents()
        header.setStretchLastSection(True)

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
        self._last_res = res
        self._sop_label.setText(f"SOP: {res.sop_expression}")
        self._on_view_changed()

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

        # Draw groups with wrap-around support
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

            if not cells:
                continue

            ris = sorted(list(set(c[0] for c in cells)))
            cis = sorted(list(set(c[1] for c in cells)))

            def get_ranges(indices, total):
                if not indices:
                    return []
                if len(indices) == total:
                    return [(0, total - 1)]
                # Check for wrap-around (toroidal)
                if 0 in indices and (total - 1) in indices:
                    # Find the gap
                    gap_start = -1
                    for i in range(total):
                        if i not in indices:
                            gap_start = i
                            break
                    if gap_start != -1:
                        # Find the next segment start
                        last_part_start = -1
                        for i in range(gap_start, total):
                            if i in indices:
                                last_part_start = i
                                break
                        return [(0, gap_start - 1), (last_part_start, total - 1)]
                return [(min(indices), max(indices))]

            row_ranges = get_ranges(ris, rows)
            col_ranges = get_ranges(cis, cols)

            for rr_start, rr_end in row_ranges:
                for cr_start, cr_end in col_ranges:
                    x = cr_start * cell - 0.08
                    y = (rows - 1 - rr_end) * cell - 0.08
                    w = (cr_end - cr_start + 1) * cell + 0.16
                    h = (rr_end - rr_start + 1) * cell + 0.16
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

    def _draw_circuit(self, res):
        """Logic Gate Visualization for the SOP expression."""
        from logicraft.theme import get_palette
        import matplotlib.patches as mpatches
        import matplotlib.path as mpath
        import numpy as np

        p = get_palette(self._dark)
        ax = self.canvas.axes
        ax.clear()

        n = self._n_vars
        terms = res.essential_implicants
        if not terms:
            ax.text(0.5, 0.5, "OUTPUT (F) = 0", ha="center", va="center", fontsize=18, fontweight="bold", color=p.on_surface, transform=ax.transAxes)
            ax.set_axis_off()
            self.canvas.draw()
            return
        
        # If result is "1" (always high)
        if len(terms) == 1 and not (terms[0].mask ^ ((1 << n) - 1)):
             ax.text(0.5, 0.5, "OUTPUT (F) = 1 (VCC)", ha="center", va="center", fontsize=18, fontweight="bold", color=p.on_surface, transform=ax.transAxes)
             ax.set_axis_off()
             self.canvas.draw()
             return

        var_names = [chr(65 + i) for i in range(n)]
        
        # Layout constants
        x_start = 1.0
        x_and = 4.0
        x_or = 7.5
        x_end = 9.5
        
        y_step = 2.0
        total_height = max(len(terms), n) * y_step + 2.0
        
        # Draw Inputs (A, B, C, D)
        var_y = {}
        for i in range(n):
            y = total_height - (i + 1) * (total_height / (n + 1))
            var_y[i] = y
            ax.text(x_start - 0.5, y, var_names[i], ha="right", va="center", fontsize=14, fontweight="bold", color=p.on_surface)
            ax.plot([x_start - 0.2, x_start + 1.5], [y, y], color=p.outline, linewidth=2, zorder=1)

        # Helper to draw AND gate
        def draw_and(x, y, color=p.primary):
            w, h = 1.2, 1.4
            # Rectangle part
            rect = mpatches.Rectangle((x - w/2, y - h/2), w/2, h, facecolor=color+"30", edgecolor=color, linewidth=2, zorder=2)
            ax.add_patch(rect)
            # Semicircle part
            theta = np.linspace(-np.pi/2, np.pi/2, 20)
            arc_x = x + np.cos(theta) * (h/2) - 0.6
            arc_y = y + np.sin(theta) * (h/2)
            ax.plot(arc_x, arc_y, color=color, linewidth=2, zorder=2)
            ax.fill(arc_x, arc_y, color=color+"30", zorder=2)
            return x + h/2 - 0.6, y # output point

        # Helper to draw OR gate
        def draw_or(x, y, color=p.secondary):
            w, h = 1.4, 1.6
            # Curved triangle shape for OR
            t = np.linspace(-1, 1, 30)
            # Left curve
            lx = x - w/2 + 0.3 * (1 - t**2)
            ly = y + (h/2) * t
            # Right point curves
            rx = x - w/2 + 0.3 * (1 - t**2) + w * (1 - t**2) # This is wrong, let's simplify
            
            # Simple OR path
            path_data = [
                (mpath.Path.MOVETO, [x - w/2, y + h/2]),
                (mpath.Path.CURVE3, [x - w/4, y]),
                (mpath.Path.LINETO, [x - w/2, y - h/2]),
                (mpath.Path.CURVE3, [x + w/2, y]),
                (mpath.Path.CURVE3, [x - w/2, y + h/2]),
            ]
            codes, verts = zip(*path_data)
            path = mpath.Path(verts, codes)
            ax.add_patch(mpatches.PathPatch(path, facecolor=color+"30", edgecolor=color, linewidth=2, zorder=2))
            return x + w/2, y

        # Draw AND gates for each term
        and_outputs = []
        for j, imp in enumerate(terms):
            y_and = total_height - (j + 1) * (total_height / (len(terms) + 1))
            
            # Find literals
            literals = []
            for i in range(n):
                bit_pos = n - 1 - i
                if not (imp.mask >> bit_pos & 1):
                    is_true = (imp.value >> bit_pos) & 1
                    literals.append((i, is_true))
            
            if len(literals) > 1:
                out_x, out_y = draw_and(x_and, y_and)
                and_outputs.append((out_x, out_y))
                
                for k, (var_idx, is_true) in enumerate(literals):
                    in_y = y_and + (len(literals)/2 - k - 0.5) * 0.4
                    y_src = var_y[var_idx]
                    ax.plot([x_start + 1.5, x_and - 0.6], [y_src, in_y], color=p.outline, alpha=0.4, zorder=1)
                    if not is_true:
                        ax.add_patch(mpatches.Circle((x_and - 1.2, (y_src + in_y * 2)/3), 0.1, facecolor=p.surface, edgecolor=p.error, linewidth=1.5, zorder=3))
            elif len(literals) == 1:
                var_idx, is_true = literals[0]
                y_src = var_y[var_idx]
                ax.plot([x_start + 1.5, x_or - 0.7], [y_src, y_and], color=p.outline, zorder=1)
                if not is_true:
                     ax.add_patch(mpatches.Circle((x_start + 2.5, (y_src + y_and)/2), 0.1, facecolor=p.surface, edgecolor=p.error, linewidth=1.5, zorder=3))
                and_outputs.append((x_or - 0.7, y_and))
            else:
                # result = 1 case handled above
                pass

        # Draw OR gate
        if len(and_outputs) > 1:
            y_or = total_height / 2
            out_x, out_y = draw_or(x_or, y_or)
            for ox, oy in and_outputs:
                ax.plot([ox, x_or - 0.7], [oy, y_or], color=p.outline, alpha=0.6, zorder=1)
            ax.plot([out_x, x_end], [out_y, out_y], color=p.secondary, linewidth=3, zorder=1)
            ax.text(x_end + 0.2, out_y, "F", color=p.secondary, fontsize=16, fontweight="bold", va="center")
        elif len(and_outputs) == 1:
            ox, oy = and_outputs[0]
            ax.plot([ox, x_end], [oy, oy], color=p.secondary, linewidth=3, zorder=1)
            ax.text(x_end + 0.2, oy, "F", color=p.secondary, fontsize=16, fontweight="bold", va="center")

        ax.set_xlim(0, x_end + 1)
        ax.set_ylim(0, total_height)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(f"Logic Gate Diagram (SOP: {res.sop_expression})", fontsize=14, fontweight="bold", color=p.on_surface, pad=20)
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
