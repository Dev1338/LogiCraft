"""
Design-system tokens and QSS stylesheets derived from the Stitch ALU Simulator
project.  Provides light/dark themes for PyQt6 and matching matplotlib rcParams.
"""

from dataclasses import dataclass


# ── Colour palette ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class Palette:
    primary: str
    primary_container: str
    on_primary: str
    secondary: str
    secondary_container: str
    on_secondary: str
    tertiary: str
    tertiary_container: str
    on_tertiary: str
    error: str
    error_container: str
    on_error: str
    surface: str
    surface_container: str
    surface_container_high: str
    surface_container_lowest: str
    surface_container_low: str
    surface_dim: str
    on_surface: str
    on_surface_variant: str
    outline: str
    outline_variant: str
    background: str
    on_background: str
    # extra
    primary_fixed: str
    primary_fixed_dim: str
    inverse_surface: str
    inverse_on_surface: str


LIGHT = Palette(
    primary="#004d99",
    primary_container="#1565C0",
    on_primary="#ffffff",
    secondary="#48626e",
    secondary_container="#cbe7f5",
    on_secondary="#ffffff",
    tertiary="#005c15",
    tertiary_container="#25752b",
    on_tertiary="#ffffff",
    error="#ba1a1a",
    error_container="#ffdad6",
    on_error="#ffffff",
    surface="#ffffff",
    surface_container="#eff3f8",
    surface_container_high="#e8e8e8",
    surface_container_lowest="#ffffff",
    surface_container_low="#f8fafc",
    surface_dim="#dadada",
    on_surface="#1a1c1c",
    on_surface_variant="#424752",
    outline="#727783",
    outline_variant="#c2c6d4",
    background="#f9f9f9",
    on_background="#1a1c1c",
    primary_fixed="#d6e3ff",
    primary_fixed_dim="#a9c7ff",
    inverse_surface="#2f3131",
    inverse_on_surface="#f1f1f1",
)

DARK = Palette(
    primary="#a9c7ff",
    primary_container="#00468c",
    on_primary="#003062",
    secondary="#afcbd8",
    secondary_container="#304a55",
    on_secondary="#1b3540",
    tertiary="#88d982",
    tertiary_container="#005312",
    on_tertiary="#003909",
    error="#ffb4ab",
    error_container="#93000a",
    on_error="#690005",
    surface="#1a1c1c",
    surface_container="#272929",
    surface_container_high="#323434",
    surface_container_lowest="#111313",
    surface_container_low="#222424",
    surface_dim="#1a1c1c",
    on_surface="#e2e2e2",
    on_surface_variant="#c2c6d4",
    outline="#8c919c",
    outline_variant="#424752",
    background="#1a1c1c",
    on_background="#e2e2e2",
    primary_fixed="#d6e3ff",
    primary_fixed_dim="#a9c7ff",
    inverse_surface="#e2e2e2",
    inverse_on_surface="#2f3131",
)


# ── QSS stylesheet generator ─────────────────────────────────────────────────


def _build_stylesheet(p: Palette) -> str:
    return f"""
/* ── Global ────────────────────────────────────────────── */
QMainWindow, QWidget {{
    background-color: {p.surface};
    color: {p.on_surface};
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: 13px;
}}
QLabel {{
    color: {p.on_surface};
    background: transparent;
}}
QLabel[class="heading"] {{
    font-size: 18px;
    font-weight: 700;
}}
QLabel[class="subheading"] {{
    font-size: 14px;
    font-weight: 600;
    color: {p.secondary};
}}
QLabel[class="mono"] {{
    font-family: 'Courier New', 'Consolas', monospace;
    font-size: 14px;
}}

/* ── Toolbar & Sidebar ───────────────────────────────────── */
QToolBar {{
    background-color: {p.surface_container};
    border: none;
    spacing: 8px;
    padding: 8px 16px;
    border-bottom: 1px solid {p.outline_variant};
}}
QToolBar QLabel {{
    font-weight: 600;
    font-size: 15px;
    color: {p.on_surface};
    padding-right: 12px;
}}
QLabel[class="heading-app"] {{
    font-weight: 700;
    font-size: 18px;
    color: {p.on_surface};
}}
QPushButton[class="icon-btn"] {{
    background: transparent;
    color: {p.secondary};
    font-size: 20px;
    padding: 0;
    border: none;
}}
QPushButton[class="icon-btn"]:hover {{
    color: {p.primary};
    background-color: {p.surface_container_high};
    border-radius: 16px;
}}
QWidget[class="sidebar"] {{
    background-color: {p.surface_container};
    border-right: 1px solid {p.outline_variant};
}}
QLabel[class="project-explorer"] {{
    font-size: 13px;
    font-weight: 700;
    color: {p.secondary};
    padding: 0 16px;
    letter-spacing: 0.5px;
}}

/* ── Tab Bar (Document-Style) ──────────────────────────── */
QTabWidget::pane {{
    border: none;
    background-color: {p.surface_container_lowest};
}}
QTabBar {{
    background-color: {p.surface_container};
    border: none;
}}
QTabBar::tab {{
    background-color: {p.surface_dim};
    color: {p.on_surface_variant};
    padding: 8px 18px;
    margin: 0px;
    border: none;
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
    font-size: 13px;
    font-weight: 500;
    min-width: 100px;
}}
QTabBar::tab:selected {{
    background-color: {p.surface_container_lowest};
    color: {p.primary};
    font-weight: 600;
}}
QTabBar::tab:hover:!selected {{
    background-color: {p.surface_container_low};
}}

/* ── Buttons ───────────────────────────────────────────── */
QPushButton {{
    background-color: {p.primary};
    color: {p.on_primary};
    border: none;
    border-radius: 4px;
    padding: 6px 16px;
    font-weight: 600;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: {p.primary_container};
}}
QPushButton:pressed {{
    background-color: {p.primary};
    opacity: 0.85;
}}
QPushButton:disabled {{
    background-color: {p.surface_container_high};
    color: {p.outline};
}}
QPushButton[class="secondary"] {{
    background-color: {p.surface_container_high};
    color: {p.on_surface};
}}
QPushButton[class="secondary"]:hover {{
    background-color: {p.surface_dim};
}}
QPushButton[class="bit-toggle"] {{
    background-color: {p.surface_container_high};
    color: {p.on_surface};
    font-family: 'Courier New', monospace;
    font-size: 16px;
    font-weight: 700;
    min-width: 32px;
    min-height: 32px;
    max-width: 32px;
    max-height: 32px;
    padding: 0px;
    border-radius: 4px;
}}
QPushButton[class="bit-toggle"][active="true"] {{
    background-color: {p.primary};
    color: {p.on_primary};
}}
QPushButton[class="bit-toggle-result"] {{
    background-color: {p.tertiary_container};
    color: {p.on_tertiary};
    font-family: 'Courier New', monospace;
    font-size: 16px;
    font-weight: 700;
    min-width: 32px;
    min-height: 32px;
    max-width: 32px;
    max-height: 32px;
    padding: 0px;
    border-radius: 4px;
}}
QPushButton[class="flag-pill"] {{
    border-radius: 10px;
    padding: 3px 12px;
    font-size: 12px;
    font-weight: 600;
    min-height: 20px;
}}
QPushButton[class="flag-pill"][active="true"] {{
    background-color: {p.tertiary};
    color: {p.on_tertiary};
}}
QPushButton[class="flag-pill"][active="false"] {{
    background-color: {p.surface_container_high};
    color: {p.outline};
}}
QPushButton[class="flag-pill-error"] {{
    border-radius: 10px;
    padding: 3px 12px;
    font-size: 12px;
    font-weight: 600;
    min-height: 20px;
}}
QPushButton[class="flag-pill-error"][active="true"] {{
    background-color: {p.error};
    color: {p.on_error};
}}
QPushButton[class="flag-pill-error"][active="false"] {{
    background-color: {p.surface_container_high};
    color: {p.outline};
}}

/* ── Combo Box ─────────────────────────────────────────── */
QComboBox {{
    background-color: {p.surface_container_lowest};
    color: {p.on_surface};
    border: 1px solid {p.outline};
    border-radius: 4px;
    padding: 5px 10px;
    font-size: 13px;
    min-height: 26px;
}}
QComboBox:focus {{
    border: 2px solid {p.primary};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background-color: {p.surface_container_lowest};
    color: {p.on_surface};
    selection-background-color: {p.primary_fixed};
    selection-color: {p.primary};
    border: 1px solid {p.outline_variant};
    border-radius: 4px;
    outline: 0;
}}

/* ── Line Edit ─────────────────────────────────────────── */
QLineEdit {{
    background-color: {p.surface_container_lowest};
    color: {p.on_surface};
    border: 1px solid {p.outline};
    border-radius: 4px;
    padding: 5px 10px;
    font-size: 13px;
    font-family: 'Courier New', monospace;
}}
QLineEdit:focus {{
    border: 2px solid {p.primary};
}}

/* ── Spin Box ──────────────────────────────────────────── */
QSpinBox {{
    background-color: {p.surface_container_lowest};
    color: {p.on_surface};
    border: 1px solid {p.outline};
    border-radius: 4px;
    padding: 4px 8px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
}}
QSpinBox:focus {{
    border: 2px solid {p.primary};
}}

/* ── Group Box (Sectioned Border) ──────────────────────── */
QGroupBox {{
    background-color: {p.surface_container_lowest};
    border: 1px solid {p.outline_variant};
    border-radius: 4px;
    margin-top: 14px;
    padding-top: 18px;
    padding-left: 10px;
    padding-right: 10px;
    padding-bottom: 10px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 8px;
    color: {p.secondary};
    font-weight: 600;
    font-size: 12px;
}}

/* ── Scroll Area ───────────────────────────────────────── */
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollBar:vertical {{
    background: {p.surface_container};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {p.outline_variant};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* ── List Widget ───────────────────────────────────────── */
QListWidget {{
    background-color: {p.surface_container_lowest};
    color: {p.on_surface};
    border: 1px solid {p.outline_variant};
    border-radius: 4px;
    outline: 0;
    font-family: 'Courier New', monospace;
    font-size: 12px;
}}
QListWidget[class="nav-list"] {{
    background-color: transparent;
    border: none;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: 14px;
    font-weight: 500;
}}
QListWidget::item {{
    padding: 4px 8px;
}}
QListWidget[class="nav-list"]::item {{
    padding: 12px 20px;
    color: {p.on_surface_variant};
    border-left: 3px solid transparent;
}}
QListWidget::item:selected {{
    background-color: {p.primary_fixed};
    color: {p.primary};
}}
QListWidget[class="nav-list"]::item:selected {{
    background-color: {p.surface_container_lowest};
    color: {p.primary};
    font-weight: 600;
    border-left: 3px solid {p.primary};
}}
QListWidget::item:hover {{
    background-color: {p.surface_container_low};
}}
QListWidget[class="nav-list"]::item:hover:!selected {{
    background-color: rgba(0, 0, 0, 0.03);
    color: {p.on_surface};
}}

/* ── Table Widget ──────────────────────────────────────── */
QTableWidget {{
    background-color: {p.surface_container_lowest};
    color: {p.on_surface};
    gridline-color: {p.outline_variant};
    border: 1px solid {p.outline_variant};
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
}}
QTableWidget::item {{
    padding: 4px;
}}
QTableWidget::item:selected {{
    background-color: {p.primary_fixed};
    color: {p.primary};
}}
QHeaderView::section {{
    background-color: {p.surface_container};
    color: {p.secondary};
    border: none;
    padding: 4px 8px;
    font-weight: 600;
    font-size: 12px;
}}

/* ── Check Box ─────────────────────────────────────────── */
QCheckBox {{
    spacing: 6px;
    font-size: 13px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 2px solid {p.outline};
    border-radius: 3px;
    background: {p.surface_container_lowest};
}}
QCheckBox::indicator:checked {{
    background-color: {p.primary};
    border-color: {p.primary};
}}

/* ── Status Bar ────────────────────────────────────────── */
QStatusBar {{
    background-color: {p.surface_container};
    color: {p.on_surface_variant};
    font-size: 12px;
    border-top: 1px solid {p.outline_variant};
}}

/* ── Splitter ──────────────────────────────────────────── */
QSplitter::handle {{
    background-color: {p.outline_variant};
    width: 1px;
}}

/* ── Segment Controls ──────────────────────────────────── */
QPushButton[class="segment"] {{
    background-color: {p.surface_container_high};
    color: {p.on_surface_variant};
    border: none;
    border-radius: 4px;
    padding: 5px 14px;
    font-weight: 500;
    font-size: 12px;
}}
QPushButton[class="segment"][active="true"] {{
    background-color: {p.surface_container_lowest};
    color: {p.primary};
    font-weight: 600;
    border-bottom: 2px solid {p.primary};
}}

/* ── Drop Zone & Custom Frames ─────────────────────────── */
QFrame[class="drop-zone"] {{
    border: 2px dashed {p.primary};
    background-color: rgba(0, 77, 153, 0.05);
    border-radius: 4px;
}}
QFrame[class="input-box"] {{
    border: 1px solid {p.outline_variant};
    background-color: {p.surface_container_lowest};
    border-radius: 4px;
}}
QFrame[class="input-box-dashed"] {{
    border: 1px dashed {p.primary};
    background-color: {p.surface_container_lowest};
    border-radius: 4px;
}}
QFrame[class="result-box"] {{
    border: 1px solid {p.outline_variant};
    background-color: {p.surface_container};
    border-radius: 4px;
}}
QPushButton[class="compute-btn"] {{
    background-color: {p.primary_container};
    color: {p.on_primary};
    font-size: 14px;
    font-weight: 700;
    padding: 10px;
    border-radius: 4px;
    letter-spacing: 1px;
}}
QPushButton[class="compute-btn"]:hover {{
    background-color: {p.primary};
}}
"""


LIGHT_STYLESHEET = _build_stylesheet(LIGHT)
DARK_STYLESHEET = _build_stylesheet(DARK)


def get_mpl_style(dark: bool = False) -> dict:
    """Return matplotlib rcParams matching the current theme."""
    p = DARK if dark else LIGHT
    return {
        "figure.facecolor": p.surface_container_lowest,
        "axes.facecolor": p.surface_container_lowest,
        "axes.edgecolor": p.outline_variant,
        "axes.labelcolor": p.on_surface,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "text.color": p.on_surface,
        "xtick.color": p.on_surface_variant,
        "ytick.color": p.on_surface_variant,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "grid.color": p.outline_variant,
        "grid.alpha": 0.35,
        "grid.linewidth": 0.5,
        "legend.facecolor": p.surface_container,
        "legend.edgecolor": p.outline_variant,
        "legend.fontsize": 10,
        "font.family": ["sans-serif"],
        "font.size": 11,
        "lines.linewidth": 1.8,
        "patch.edgecolor": p.outline_variant,
        "figure.dpi": 100,
        "savefig.dpi": 150,
        "savefig.facecolor": p.surface_container_lowest,
    }


def get_palette(dark: bool = False) -> Palette:
    """Return the active colour palette."""
    return DARK if dark else LIGHT
