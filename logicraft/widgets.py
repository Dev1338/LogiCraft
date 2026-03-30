"""
Reusable custom widgets used across multiple tabs.
"""

from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QDrag, QIntValidator
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
    QLineEdit, QFrame, QSizePolicy,
)


# ── Bit Toggle Row ────────────────────────────────────────────────────────────

class BitToggleRow(QWidget):
    """Row of clickable bit-toggle buttons with synced decimal/hex fields."""

    value_changed = pyqtSignal(int)  # emits the unsigned int value

    def __init__(self, bit_width: int = 8, label: str = "Value",
                 parent: QWidget | None = None, read_only: bool = False):
        super().__init__(parent)
        self._bit_width = bit_width
        self._read_only = read_only
        self._buttons: list[QPushButton] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        # label
        lbl = QLabel(label)
        lbl.setProperty("class", "subheading")
        root.addWidget(lbl)

        # bit buttons
        self._bits_layout = QHBoxLayout()
        self._bits_layout.setSpacing(2)
        self._rebuild_buttons()
        root.addLayout(self._bits_layout)

        # decimal / hex entry row
        entry_row = QHBoxLayout()
        entry_row.setSpacing(8)

        dec_label = QLabel("DEC")
        dec_label.setProperty("class", "mono")
        dec_label.setFixedWidth(32)
        entry_row.addWidget(dec_label)
        self.dec_edit = QLineEdit("0")
        self.dec_edit.setFixedWidth(100)
        self.dec_edit.setReadOnly(read_only)
        self.dec_edit.setValidator(QIntValidator(0, (1 << bit_width) - 1))
        entry_row.addWidget(self.dec_edit)

        hex_label = QLabel("HEX")
        hex_label.setProperty("class", "mono")
        hex_label.setFixedWidth(32)
        entry_row.addWidget(hex_label)
        self.hex_edit = QLineEdit("0x0")
        self.hex_edit.setFixedWidth(100)
        self.hex_edit.setReadOnly(True)
        entry_row.addWidget(self.hex_edit)

        entry_row.addStretch()
        root.addLayout(entry_row)

        # signals
        if not read_only:
            self.dec_edit.editingFinished.connect(self._on_dec_edited)

        # drag support
        self.setAcceptDrops(True)

    # ── Public API ────────────────────────────────────────────────────────

    def value(self) -> int:
        v = 0
        for i, btn in enumerate(self._buttons):
            if btn.property("active") == "true":
                v |= 1 << (self._bit_width - 1 - i)
        return v

    def set_value(self, val: int) -> None:
        val = val & ((1 << self._bit_width) - 1)
        for i, btn in enumerate(self._buttons):
            bit = (val >> (self._bit_width - 1 - i)) & 1
            btn.setProperty("active", "true" if bit else "false")
            btn.setText(str(bit))
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._sync_fields()

    def set_bit_width(self, w: int) -> None:
        old_val = self.value()
        self._bit_width = w
        self.dec_edit.setValidator(QIntValidator(0, (1 << w) - 1))
        self._rebuild_buttons()
        self.set_value(old_val & ((1 << w) - 1))

    def bit_width(self) -> int:
        return self._bit_width

    # ── Internals ─────────────────────────────────────────────────────────

    def _rebuild_buttons(self) -> None:
        # clear
        for btn in self._buttons:
            self._bits_layout.removeWidget(btn)
            btn.deleteLater()
        self._buttons.clear()

        for i in range(self._bit_width):
            btn = QPushButton("0")
            btn.setProperty("class", "bit-toggle" if not self._read_only else "bit-toggle-result")
            btn.setProperty("active", "false")
            if not self._read_only:
                btn.clicked.connect(lambda _, idx=i: self._toggle_bit(idx))
            self._buttons.append(btn)
            self._bits_layout.addWidget(btn)

        self._bits_layout.addStretch()

    def _toggle_bit(self, idx: int) -> None:
        btn = self._buttons[idx]
        current = btn.property("active") == "true"
        btn.setProperty("active", "false" if current else "true")
        btn.setText("0" if current else "1")
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        self._sync_fields()
        self.value_changed.emit(self.value())

    def _sync_fields(self) -> None:
        v = self.value()
        self.dec_edit.blockSignals(True)
        self.dec_edit.setText(str(v))
        self.dec_edit.blockSignals(False)
        self.hex_edit.setText(f"0x{v:X}")

    def _on_dec_edited(self) -> None:
        try:
            v = int(self.dec_edit.text())
        except ValueError:
            v = 0
        self.set_value(v)
        self.value_changed.emit(v)

    # ── Drag and drop ─────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self._read_only:
            # let buttons handle their own clicks
            super().mousePressEvent(event)

    def start_drag(self) -> None:
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(str(self.value()))
        drag.setMimeData(mime)
        drag.exec(Qt.DropAction.CopyAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and not self._read_only:
            event.acceptProposedAction()
            self.setProperty("class", "drop-zone")
            self.style().unpolish(self)
            self.style().polish(self)

    def dragLeaveEvent(self, event):
        self.setProperty("class", "")
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event):
        if event.mimeData().hasText() and not self._read_only:
            try:
                val = int(event.mimeData().text())
                self.set_value(val)
                self.value_changed.emit(val)
            except ValueError:
                pass
        self.setProperty("class", "")
        self.style().unpolish(self)
        self.style().polish(self)


# ── Draggable Value Label ────────────────────────────────────────────────────

class DraggableValueLabel(QLabel):
    """A label whose text (integer value) can be dragged onto BitToggleRows."""

    def __init__(self, text: str = "0", parent: QWidget | None = None):
        super().__init__(text, parent)
        self._value = 0
        self.setProperty("class", "mono")
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setStyleSheet("padding: 4px 8px;")

    def set_drag_value(self, v: int) -> None:
        self._value = v

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(str(self._value))
            drag.setMimeData(mime)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            drag.exec(Qt.DropAction.CopyAction)
            self.setCursor(Qt.CursorShape.OpenHandCursor)


# ── Flag Pill ─────────────────────────────────────────────────────────────────

class FlagPill(QPushButton):
    """Coloured indicator pill for status flags (Zero, Carry, etc.)."""

    def __init__(self, label: str, parent: QWidget | None = None):
        super().__init__(label, parent)
        self.setProperty("class", "flag-pill")
        self.setProperty("active", "false")
        self.setCheckable(False)
        self.setEnabled(False)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def set_active(self, active: bool) -> None:
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)


# ── Segment Control ──────────────────────────────────────────────────────────

class SegmentControl(QWidget):
    """Horizontal segmented button bar for mode switching."""

    selection_changed = pyqtSignal(int)

    def __init__(self, options: list[str], parent: QWidget | None = None):
        super().__init__(parent)
        self._buttons: list[QPushButton] = []
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        for i, opt in enumerate(options):
            btn = QPushButton(opt)
            btn.setProperty("class", "segment")
            btn.setProperty("active", "true" if i == 0 else "false")
            btn.clicked.connect(lambda _, idx=i: self._select(idx))
            layout.addWidget(btn)
            self._buttons.append(btn)

        self._selected = 0

    def _select(self, idx: int) -> None:
        if idx == self._selected:
            return
        self._buttons[self._selected].setProperty("active", "false")
        self._buttons[self._selected].style().unpolish(self._buttons[self._selected])
        self._buttons[self._selected].style().polish(self._buttons[self._selected])
        self._selected = idx
        self._buttons[idx].setProperty("active", "true")
        self._buttons[idx].style().unpolish(self._buttons[idx])
        self._buttons[idx].style().polish(self._buttons[idx])
        self.selection_changed.emit(idx)

    def selected(self) -> int:
        return self._selected

    def set_selected(self, idx: int) -> None:
        self._select(idx)


# ── Separator ─────────────────────────────────────────────────────────────────

class TonalSeparator(QFrame):
    """Horizontal separator using tonal shift instead of a line."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedHeight(1)
        self.setStyleSheet("background-color: rgba(0,0,0,0.06);")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
