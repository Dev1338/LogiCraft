#!/usr/bin/env python3
"""
LogiCraft — Digital Design & Computer Organisation Simulator.

Entry point: creates the QApplication and launches the main window.
"""

from logicraft.main_window import MainWindow
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication
import sys
import os

# Ensure we can import logicraft from the project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    # High-DPI support
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("LogiCraft")
    app.setOrganizationName("LogiCraft")

    # Load Inter font if available, else fallback
    font = QFont("Inter", 11)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
