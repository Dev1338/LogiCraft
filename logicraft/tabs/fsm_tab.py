"""
Tab 7 — FSM Designer UI.
"""

import math
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QGroupBox,
    QLabel, QPushButton, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QScrollArea, QCheckBox, QFormLayout,
)
from logicraft.canvas import MplCanvas
from logicraft.widgets import TonalSeparator
from logicraft.engines.fsm_engine import (
    FSMDef, State, Transition, simulate, PRESETS, minimize_states, SimResult,
)


class FSMTab(QWidget):
    def __init__(self, dark=False):
        super().__init__()
        self._dark = dark
        self._fsm = FSMDef(mode="Moore", alphabet=["0", "1"])
        self._sim_result = None
        self._dragging = None
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
        left.setSpacing(8)

        # Mode
        mode_group = QGroupBox("Machine Type")
        mode_lay = QHBoxLayout(mode_group)
        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["Moore", "Mealy"])
        self._mode_combo.currentTextChanged.connect(self._on_mode_changed)
        mode_lay.addWidget(self._mode_combo)
        mode_lay.addStretch()
        left.addWidget(mode_group)

        # Presets
        preset_group = QGroupBox("Presets")
        preset_lay = QHBoxLayout(preset_group)
        self._preset_combo = QComboBox()
        self._preset_combo.addItems(["(Custom)"] + list(PRESETS.keys()))
        preset_lay.addWidget(self._preset_combo)
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self._load_preset)
        preset_lay.addWidget(load_btn)
        preset_lay.addStretch()
        left.addWidget(preset_group)

        # Add state
        st_group = QGroupBox("Add State")
        st_form = QFormLayout(st_group)
        self._st_name = QLineEdit()
        self._st_name.setPlaceholderText("e.g. S0")
        st_form.addRow("Name:", self._st_name)
        self._st_output = QLineEdit()
        self._st_output.setPlaceholderText("Output (Moore)")
        st_form.addRow("Output:", self._st_output)
        st_flags = QHBoxLayout()
        self._st_start = QCheckBox("Start")
        self._st_accept = QCheckBox("Accept")
        st_flags.addWidget(self._st_start)
        st_flags.addWidget(self._st_accept)
        st_form.addRow("Flags:", st_flags)
        add_st_btn = QPushButton("+ Add State")
        add_st_btn.clicked.connect(self._add_state)
        st_form.addRow(add_st_btn)
        left.addWidget(st_group)

        # Add transition
        tr_group = QGroupBox("Add Transition")
        tr_form = QFormLayout(tr_group)
        self._tr_src = QLineEdit()
        self._tr_src.setPlaceholderText("Source state")
        tr_form.addRow("From:", self._tr_src)
        self._tr_dst = QLineEdit()
        self._tr_dst.setPlaceholderText("Dest state")
        tr_form.addRow("To:", self._tr_dst)
        self._tr_inp = QLineEdit()
        self._tr_inp.setPlaceholderText("Input symbol")
        tr_form.addRow("Input:", self._tr_inp)
        self._tr_out = QLineEdit()
        self._tr_out.setPlaceholderText("Output (Mealy)")
        tr_form.addRow("Output:", self._tr_out)
        add_tr_btn = QPushButton("+ Add Transition")
        add_tr_btn.clicked.connect(self._add_transition)
        tr_form.addRow(add_tr_btn)
        left.addWidget(tr_group)

        # States list
        self._states_label = QLabel("States: (none)")
        self._states_label.setWordWrap(True)
        self._states_label.setStyleSheet("font-size:11px;")
        left.addWidget(self._states_label)

        left.addWidget(TonalSeparator())

        # Simulation
        sim_group = QGroupBox("Simulate")
        sim_lay = QVBoxLayout(sim_group)
        sim_row = QHBoxLayout()
        sim_row.addWidget(QLabel("Input:"))
        self._sim_input = QLineEdit()
        self._sim_input.setPlaceholderText("e.g. 10110")
        sim_row.addWidget(self._sim_input)
        sim_btn = QPushButton("▶ Run")
        sim_btn.clicked.connect(self._simulate)
        sim_row.addWidget(sim_btn)
        sim_lay.addLayout(sim_row)
        self._verdict_label = QLabel("")
        self._verdict_label.setStyleSheet("font-size:14px; font-weight:bold; padding:4px;")
        sim_lay.addWidget(self._verdict_label)
        left.addWidget(sim_group)

        # Trace table
        self._trace_table = QTableWidget()
        self._trace_table.setMaximumHeight(160)
        left.addWidget(self._trace_table)

        # Minimize
        min_row = QHBoxLayout()
        self._min_btn = QPushButton("🔧 Minimize States")
        self._min_btn.setProperty("class", "secondary")
        self._min_btn.clicked.connect(self._minimize)
        min_row.addWidget(self._min_btn)
        min_row.addStretch()
        left.addLayout(min_row)

        left.addStretch()
        left_scroll.setWidget(left_w)
        splitter.addWidget(left_scroll)

        # Right
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(8, 8, 8, 8)
        hdr = QHBoxLayout()
        hdr.addWidget(QLabel("State Diagram"))
        hdr.addStretch()

        right_lay.addLayout(hdr)
        self.canvas = MplCanvas(self, width=9, height=7, dark=self._dark)
        right_lay.addWidget(self.canvas)
        splitter.addWidget(right)
        splitter.setSizes([400, 700])

        # Canvas mouse events for dragging
        self.canvas.mpl_connect('button_press_event', self._on_press)
        self.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.canvas.mpl_connect('button_release_event', self._on_release)

    def apply_theme(self, dark):
        self._dark = dark
        self.canvas.apply_theme(dark)
        self._draw_fsm()

    def _on_mode_changed(self, mode):
        self._fsm.mode = mode

    def _load_preset(self):
        name = self._preset_combo.currentText()
        if name in PRESETS:
            self._fsm = PRESETS[name]()
            self._mode_combo.setCurrentText(self._fsm.mode)
            self._update_states_label()
            self._draw_fsm()

    def _add_state(self):
        name = self._st_name.text().strip()
        if not name:
            return
        output = self._st_output.text().strip()
        n = len(self._fsm.states)
        angle = 2 * math.pi * n / max(n + 1, 3)
        s = State(name, output, self._st_start.isChecked(),
                  self._st_accept.isChecked(),
                  x=2 * math.cos(angle), y=2 * math.sin(angle))
        if not any(inp.name == name for inp in self._fsm.states):
            self._fsm.states.append(s)
        self._st_name.clear()
        self._st_output.clear()
        self._st_start.setChecked(False)
        self._st_accept.setChecked(False)
        self._update_states_label()
        self._draw_fsm()

    def _add_transition(self):
        src = self._tr_src.text().strip()
        dst = self._tr_dst.text().strip()
        inp = self._tr_inp.text().strip()
        out = self._tr_out.text().strip()
        if not src or not dst or not inp:
            return
        self._fsm.transitions.append(Transition(src, dst, inp, out))
        if inp not in self._fsm.alphabet:
            self._fsm.alphabet.append(inp)
        self._tr_src.clear()
        self._tr_dst.clear()
        self._tr_inp.clear()
        self._tr_out.clear()
        self._draw_fsm()

    def _update_states_label(self):
        names = [s.name for s in self._fsm.states]
        self._states_label.setText(f"States: {', '.join(names) if names else '(none)'}")

    def _simulate(self):
        inp_str = self._sim_input.text().strip()
        if not inp_str or not self._fsm.states:
            return
        result = simulate(self._fsm, inp_str)
        self._sim_result = result

        # Verdict
        if result.accepted:
            self._verdict_label.setText(f"✅ ACCEPTED — Final state: {result.final_state}")
            self._verdict_label.setStyleSheet("font-size:14px; font-weight:bold; color:#25752b; padding:4px;")
        else:
            self._verdict_label.setText(f"❌ REJECTED — Final state: {result.final_state}")
            self._verdict_label.setStyleSheet("font-size:14px; font-weight:bold; color:#ba1a1a; padding:4px;")

        # Trace table
        self._trace_table.setRowCount(len(result.trace))
        cols = ["Step", "State", "Input", "Next", "Output"]
        self._trace_table.setColumnCount(len(cols))
        self._trace_table.setHorizontalHeaderLabels(cols)
        for r, tr in enumerate(result.trace):
            for c, val in enumerate([tr.step, tr.current_state, tr.input_symbol, tr.next_state, tr.output]):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._trace_table.setItem(r, c, item)
        self._trace_table.resizeColumnsToContents()

        self._draw_fsm()

    def _minimize(self):
        self._fsm = minimize_states(self._fsm)
        self._update_states_label()
        self._draw_fsm()

    def _draw_fsm(self):
        from logicraft.theme import get_palette
        import matplotlib.patches as mpatches
        import numpy as np
        p = get_palette(self._dark)
        ax = self.canvas.axes
        ax.clear()

        states = self._fsm.states
        if not states:
            ax.text(0.5, 0.5, "Add states to begin", ha='center', va='center',
                    fontsize=14, color=p.outline, transform=ax.transAxes)
            self.canvas.draw()
            return

        # Arrange in circle if no positions set
        n = len(states)
        for i, s in enumerate(states):
            if s.x == 0 and s.y == 0 and n > 1:
                angle = 2 * math.pi * i / n
                s.x = 3 * math.cos(angle)
                s.y = 3 * math.sin(angle)

        state_map = {s.name: s for s in states}
        radius = 0.5

        # Highlighted states from trace
        traced = set()
        if self._sim_result:
            for tr in self._sim_result.trace:
                traced.add(tr.current_state)
                traced.add(tr.next_state)

        # Draw states
        for s in states:
            fc = p.surface_container_lowest
            ec = p.primary

            # Glow for traced
            if s.name in traced:
                glow = mpatches.Circle((s.x, s.y), radius + 0.15,
                                        facecolor='#FFD60033', edgecolor='#FFD600', linewidth=2)
                ax.add_patch(glow)

            circle = mpatches.Circle((s.x, s.y), radius,
                                      facecolor=fc, edgecolor=ec, linewidth=2)
            ax.add_patch(circle)

            # Double ring for accept
            if s.is_accept:
                inner = mpatches.Circle((s.x, s.y), radius - 0.08,
                                         facecolor='none', edgecolor=ec, linewidth=1.5)
                ax.add_patch(inner)

            # Label
            label = s.name
            if self._fsm.mode == "Moore" and s.output:
                label += f"\n/{s.output}"
            ax.text(s.x, s.y, label, ha='center', va='center',
                    fontsize=10, fontweight='bold', color=p.on_surface)

        # Start arrow
        start = self._fsm.start_state()
        if start:
            ax.annotate("", xy=(start.x - radius, start.y),
                        xytext=(start.x - radius - 0.8, start.y),
                        arrowprops=dict(arrowstyle='->', color=p.primary, lw=2))

        # Draw transitions
        drawn_pairs = {}
        for t in self._fsm.transitions:
            src_s = state_map.get(t.src)
            dst_s = state_map.get(t.dst)
            if not src_s or not dst_s:
                continue

            key = (min(t.src, t.dst), max(t.src, t.dst))
            pair_count = drawn_pairs.get(key, 0)
            drawn_pairs[key] = pair_count + 1

            label = t.input_symbol
            if self._fsm.mode == "Mealy" and t.output:
                label += f"/{t.output}"

            if t.src == t.dst:
                # Self-loop
                angle = math.atan2(src_s.y, src_s.x) if (src_s.x or src_s.y) else math.pi/2
                loop_x = src_s.x + 0.7 * math.cos(angle)
                loop_y = src_s.y + 0.7 * math.sin(angle)
                arc = mpatches.FancyArrowPatch(
                    (src_s.x + radius * math.cos(angle + 0.3), src_s.y + radius * math.sin(angle + 0.3)),
                    (src_s.x + radius * math.cos(angle - 0.3), src_s.y + radius * math.sin(angle - 0.3)),
                    connectionstyle=f"arc3,rad=1.5",
                    arrowstyle='->', color=p.secondary, linewidth=1.5,
                    mutation_scale=15,
                )
                ax.add_patch(arc)
                ax.text(loop_x, loop_y, label, ha='center', va='center',
                        fontsize=9, color=p.secondary, fontweight='bold',
                        bbox=dict(facecolor=p.surface_container_lowest, edgecolor='none', pad=1))
            else:
                # Curved arrow
                curve = 0.2 if pair_count == 0 else -0.3
                dx = dst_s.x - src_s.x
                dy = dst_s.y - src_s.y
                dist = math.sqrt(dx**2 + dy**2) or 1
                ux, uy = dx / dist, dy / dist

                sx = src_s.x + ux * radius
                sy = src_s.y + uy * radius
                ex = dst_s.x - ux * radius
                ey = dst_s.y - uy * radius

                arrow = mpatches.FancyArrowPatch(
                    (sx, sy), (ex, ey),
                    connectionstyle=f"arc3,rad={curve}",
                    arrowstyle='->', color=p.on_surface_variant, linewidth=1.5,
                    mutation_scale=15,
                )
                ax.add_patch(arrow)

                mx = (sx + ex) / 2 + curve * (-(ey - sy))
                my = (sy + ey) / 2 + curve * (ex - sx)
                ax.text(mx, my, label, ha='center', va='center',
                        fontsize=9, color=p.on_surface, fontweight='bold',
                        bbox=dict(facecolor=p.surface_container_lowest, edgecolor='none', pad=1))

        # Auto-scale
        if states:
            xs = [s.x for s in states]
            ys = [s.y for s in states]
            margin = 2
            ax.set_xlim(min(xs) - margin, max(xs) + margin)
            ax.set_ylim(min(ys) - margin, max(ys) + margin)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f"{self._fsm.mode} FSM", fontsize=13, fontweight='bold', color=p.on_surface, pad=10)
        self.canvas.fig.tight_layout()
        self.canvas.draw()

    # ── Draggable states ──────────────────────────────────
    def _on_press(self, event):
        if event.inaxes is None or event.button != 1:
            return
        for s in self._fsm.states:
            if math.hypot(event.xdata - s.x, event.ydata - s.y) < 0.5:
                self._dragging = s
                return

    def _on_motion(self, event):
        if self._dragging and event.inaxes and event.xdata and event.ydata:
            self._dragging.x = event.xdata
            self._dragging.y = event.ydata
            self._draw_fsm()

    def _on_release(self, event):
        self._dragging = None
