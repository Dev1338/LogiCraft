"""
Tab 5 — Adder Types UI.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QGroupBox,
    QLabel,
    QPushButton,
    QLineEdit,
    QScrollArea,
)
from logicraft.canvas import MplCanvas

from logicraft.engines.adder_engine import compare_all, scaling_data


class AdderTab(QWidget):
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
        r1.addWidget(QLabel("A (decimal):"))
        self._a_edit = QLineEdit("42")
        self._a_edit.setFixedWidth(120)
        r1.addWidget(self._a_edit)
        r1.addStretch()
        inp_lay.addLayout(r1)
        r2 = QHBoxLayout()
        r2.addWidget(QLabel("B (decimal):"))
        self._b_edit = QLineEdit("27")
        self._b_edit.setFixedWidth(120)
        r2.addWidget(self._b_edit)
        r2.addStretch()
        inp_lay.addLayout(r2)
        left.addWidget(inp_group)

        btn_row = QHBoxLayout()
        self._cmp_btn = QPushButton("⚡ Compare Adders")
        self._cmp_btn.clicked.connect(self._compare)
        btn_row.addWidget(self._cmp_btn)
        btn_row.addStretch()
        left.addLayout(btn_row)

        # Stats
        self._stats_group = QGroupBox("Statistics")
        stats_lay = QVBoxLayout(self._stats_group)
        self._stats_labels = []
        for name in ["Ripple Carry", "Carry Lookahead", "Carry Select"]:
            lbl = QLabel(f"{name}: —")
            lbl.setStyleSheet("font-family:'Courier New',monospace; font-size:12px;")
            stats_lay.addWidget(lbl)
            self._stats_labels.append(lbl)
        left.addWidget(self._stats_group)

        # Scaling view
        self._scale_btn = QPushButton("📊 Show Scaling View")
        self._scale_btn.setProperty("class", "secondary")
        self._scale_btn.clicked.connect(self._show_scaling)
        left.addWidget(self._scale_btn)

        left.addStretch()
        left_scroll.setWidget(left_w)
        splitter.addWidget(left_scroll)

        # Right
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(8, 8, 8, 8)
        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("Per-Bit Delay Comparison"))
        hdr.addStretch()

        right_lay.addLayout(hdr)
        self.canvas = MplCanvas(self, width=10, height=6, dark=self._dark)
        right_lay.addWidget(self.canvas)
        splitter.addWidget(right)
        splitter.setSizes([350, 750])

    def set_bit_width(self, w):
        self._bw = w

    def apply_theme(self, dark):
        self._dark = dark
        self.canvas.apply_theme(dark)

    def _compare(self):
        try:
            a = int(self._a_edit.text())
            b = int(self._b_edit.text())
        except ValueError:
            return
        results = compare_all(a, b, self._bw)

        for i, res in enumerate(results):
            self._stats_labels[i].setText(
                f"{res.name}: Result={res.result} | Gates={res.gate_count} | Delay={
                    res.critical_path_delay
                }"
            )

        self._draw_bars(results)

    def _draw_bars(self, results):
        from logicraft.theme import get_palette

        p = get_palette(self._dark)
        self.canvas.fig.clear()
        axes = self.canvas.fig.subplots(1, 3, sharey=True)
        colors = [p.primary, p.tertiary, p.secondary]

        for idx, (res, ax) in enumerate(zip(results, axes)):
            bits = list(range(res.bit_width))
            delays = list(reversed(res.per_bit_delay))
            ax.bar(bits, delays, color=colors[idx], alpha=0.85, width=0.7)
            ax.axhline(
                res.critical_path_delay,
                color=p.error,
                linestyle="--",
                linewidth=1.5,
                label="Critical Path",
            )
            ax.set_title(res.name, fontsize=11, fontweight="bold", color=p.on_surface)
            ax.set_xlabel("Bit Position", fontsize=9, color=p.on_surface_variant)
            if idx == 0:
                ax.set_ylabel(
                    "Delay (gate delays)", fontsize=9, color=p.on_surface_variant
                )
            ax.set_facecolor(self.canvas.fig.get_facecolor())
            ax.tick_params(colors=p.on_surface_variant, labelsize=8)
            for spine in ax.spines.values():
                spine.set_color(p.outline_variant)
            ax.legend(fontsize=8, loc="upper left")

        self.canvas.fig.suptitle(
            f"{self._bw}-Bit Adder Comparison",
            fontsize=13,
            fontweight="bold",
            color=p.on_surface,
        )
        self.canvas.fig.subplots_adjust(
            wspace=0.15, left=0.08, right=0.96, top=0.88, bottom=0.12
        )
        self.canvas.draw()

    def _show_scaling(self):
        from logicraft.theme import get_palette

        p = get_palette(self._dark)
        data = scaling_data([4, 8, 12, 16])
        self.canvas.fig.clear()
        ax = self.canvas.fig.add_subplot(111)

        colors = {
            "Ripple Carry": p.primary,
            "Carry Lookahead": p.tertiary,
            "Carry Select": p.secondary,
        }
        markers = {"Ripple Carry": "o", "Carry Lookahead": "s", "Carry Select": "^"}

        for name, pts in data.items():
            ws = [pt[0] for pt in pts]
            ds = [pt[1] for pt in pts]
            ax.plot(
                ws,
                ds,
                marker=markers[name],
                color=colors[name],
                linewidth=2,
                markersize=8,
                label=name,
            )

        ax.set_xlabel("Bit Width", fontsize=11, color=p.on_surface)
        ax.set_ylabel(
            "Critical Path Delay (gate delays)", fontsize=11, color=p.on_surface
        )
        ax.set_title(
            "Adder Scaling: Delay vs Bit Width",
            fontsize=13,
            fontweight="bold",
            color=p.on_surface,
        )
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_facecolor(self.canvas.fig.get_facecolor())
        for spine in ax.spines.values():
            spine.set_color(p.outline_variant)
        ax.tick_params(colors=p.on_surface_variant)
        self.canvas.fig.tight_layout()
        self.canvas.draw()
