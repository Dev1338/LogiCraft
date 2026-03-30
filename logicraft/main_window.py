"""
MainWindow — application shell with toolbar, sidebar navigation, and status bar.
"""

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import (
    QMainWindow, QToolBar, QStatusBar,
    QLabel, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QListWidget, QPushButton
)

from logicraft.theme import LIGHT_STYLESHEET, DARK_STYLESHEET
from logicraft.widgets import SegmentControl
from logicraft.tabs.alu_tab import ALUTab
from logicraft.tabs.number_tab import NumberTab
from logicraft.tabs.kmap_tab import KMapTab
from logicraft.tabs.sequential_tab import SequentialTab
from logicraft.tabs.adder_tab import AdderTab
from logicraft.tabs.booth_tab import BoothTab
from logicraft.tabs.fsm_tab import FSMTab

BIT_WIDTHS = [4, 8, 16]


class MainWindow(QMainWindow):
    bit_width_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LogiCraft — Digital Design Studio")
        self.setMinimumSize(1280, 800)
        self.resize(1366, 900)
        self._dark = False
        self._bit_width = 8

        # ── Toolbar ──────────────────────────────────────────
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        logo = QLabel("Digital Design Studio")
        logo.setProperty("class", "heading-app")
        toolbar.addWidget(logo)

        # Space before bit width
        spacer1 = QWidget()
        spacer1.setFixedWidth(20)
        toolbar.addWidget(spacer1)

        self._bw_segment = SegmentControl(["4-bit", "8-bit", "16-bit"])
        self._bw_segment.set_selected(1)  # default 8-bit
        self._bw_segment.selection_changed.connect(self._on_bw_changed)
        toolbar.addWidget(self._bw_segment)

        spacer_stretch = QWidget()
        spacer_stretch.setSizePolicy(spacer_stretch.sizePolicy().Policy.Expanding, spacer_stretch.sizePolicy().Policy.Preferred)
        toolbar.addWidget(spacer_stretch)

        self._dark_btn = QPushButton("⚙")
        self._dark_btn.setProperty("class", "icon-btn")
        self._dark_btn.setFixedSize(32, 32)
        self._dark_btn.setToolTip("Toggle Dark Mode")
        self._dark_btn.clicked.connect(self._toggle_dark)
        toolbar.addWidget(self._dark_btn)

        # ── Central Layout ───────────────────────────────────
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────────
        sidebar = QWidget()
        sidebar.setFixedWidth(260)
        sidebar.setProperty("class", "sidebar")
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(0, 24, 0, 0)
        side_layout.setSpacing(16)

        proj_label = QLabel("PROJECT EXPLORER\n<span style='color:#727783; font-weight:normal; font-size:12px;'>Precision Engineering</span>")
        proj_label.setProperty("class", "project-explorer")
        side_layout.addWidget(proj_label)

        self._nav_list = QListWidget()
        self._nav_list.setProperty("class", "nav-list")
        
        nav_items = [
            "⚙   ALU Simulator",
            "🔢   Number Systems",
            "🔲   Gates & K-Map",
            "≡   Sequential Logic",
            "➕   Adder Types",
            "✖   Booth's Algorithm",
            "🔄   FSM Designer"
        ]
        self._nav_list.addItems(nav_items)
        self._nav_list.setCurrentRow(0)
        self._nav_list.currentRowChanged.connect(self._on_nav_changed)
        side_layout.addWidget(self._nav_list)
        
        main_layout.addWidget(sidebar)

        # ── Stacked Content ──────────────────────────────────
        self._stack = QStackedWidget()
        self._stack.setProperty("class", "content-area")
        main_layout.addWidget(self._stack)

        self._alu_tab = ALUTab(self._bit_width, self._dark)
        self._number_tab = NumberTab(self._bit_width, self._dark)
        self._kmap_tab = KMapTab(self._dark)
        self._sequential_tab = SequentialTab(self._dark)
        self._adder_tab = AdderTab(self._bit_width, self._dark)
        self._booth_tab = BoothTab(self._dark)
        self._fsm_tab = FSMTab(self._dark)

        self._stack.addWidget(self._alu_tab)
        self._stack.addWidget(self._number_tab)
        self._stack.addWidget(self._kmap_tab)
        self._stack.addWidget(self._sequential_tab)
        self._stack.addWidget(self._adder_tab)
        self._stack.addWidget(self._booth_tab)
        self._stack.addWidget(self._fsm_tab)

        # ── Status Bar ───────────────────────────────────────
        status = QStatusBar()
        self.setStatusBar(status)
        
        self._status_left = QLabel("MODE: SIMULATION ACTIVE   CYCLE: 0.004MS")
        self._status_left.setProperty("class", "status-label")
        status.addWidget(self._status_left)
        
        spacer_status = QWidget()
        status.addPermanentWidget(spacer_status, 1)
        
        self._status_right = QLabel("V1.0.4   DOCUMENTATION   READY")
        self._status_right.setProperty("class", "status-label")
        status.addPermanentWidget(self._status_right)

        # Apply initial theme
        self._apply_theme()

    def _on_bw_changed(self, idx: int):
        self._bit_width = BIT_WIDTHS[idx]
        self._alu_tab.set_bit_width(self._bit_width)
        self._number_tab.set_bit_width(self._bit_width)
        self._adder_tab.set_bit_width(self._bit_width)
        self.bit_width_changed.emit(self._bit_width)

    def _on_nav_changed(self, idx: int):
        self._stack.setCurrentIndex(idx)

    def _toggle_dark(self):
        self._dark = not self._dark
        self._apply_theme()

    def _apply_theme(self):
        self.setStyleSheet(DARK_STYLESHEET if self._dark else LIGHT_STYLESHEET)
        for i in range(self._stack.count()):
            tab = self._stack.widget(i)
            if hasattr(tab, 'apply_theme'):
                tab.apply_theme(self._dark)
