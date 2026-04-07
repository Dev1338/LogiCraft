"""
Base matplotlib canvas with theme-aware styling and PNG export helper.
"""

from logicraft.theme import get_mpl_style
from PyQt6.QtWidgets import QFileDialog, QWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
import os
from pathlib import Path

import matplotlib

matplotlib.use("QtAgg")


class MplCanvas(FigureCanvasQTAgg):
    """Theme-aware matplotlib canvas embeddable in PyQt6 layouts."""

    def __init__(
        self,
        parent: QWidget | None = None,
        width: float = 8,
        height: float = 5,
        dpi: int = 100,
        dark: bool = False,
    ):
        style = get_mpl_style(dark)
        matplotlib.rcParams.update(style)

        self.fig = Figure(
            figsize=(width, height), dpi=dpi, facecolor=style["figure.facecolor"]
        )
        self.axes = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.08, right=0.96, top=0.92, bottom=0.12)
        super().__init__(self.fig)
        self.setParent(parent)
        self._dark = dark

    # ── Theme update ──────────────────────────────────────────────────────

    def apply_theme(self, dark: bool) -> None:
        """Re-apply theme colours to the canvas."""
        self._dark = dark
        style = get_mpl_style(dark)
        matplotlib.rcParams.update(style)
        self.fig.set_facecolor(style["figure.facecolor"])
        for ax in self.fig.get_axes():
            ax.set_facecolor(style["axes.facecolor"])
            ax.tick_params(colors=style["xtick.color"])
            ax.xaxis.label.set_color(style["axes.labelcolor"])
            ax.yaxis.label.set_color(style["axes.labelcolor"])
            ax.title.set_color(style["text.color"])
            for spine in ax.spines.values():
                spine.set_edgecolor(style["axes.edgecolor"])
        self.draw_idle()

    # ── Export ────────────────────────────────────────────────────────────

    def export_png(self, default_name: str = "logicraft_export.png") -> str | None:
        """Open a save dialog and export the current figure as PNG."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export as PNG",
            os.path.join(str(Path.home()), default_name),
            "PNG Image (*.png)",
        )
        if path:
            self.fig.savefig(
                path, dpi=150, bbox_inches="tight", facecolor=self.fig.get_facecolor()
            )
            return path
        return None
