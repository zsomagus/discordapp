# main.py
import sys
import os

# GUI mappa hozzáadása a Python útvonalhoz
sys.path.append(os.path.join(os.path.dirname(__file__), "gui"))

from gui.gui_main import start_gui

if __name__ == "__main__":
    start_gui()
