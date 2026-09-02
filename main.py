import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from core.profile_manager import ProfileManager
from core.gamepad_listener import GamepadListener
from core.macro_engine import MacroEngine
from gui.main_window import MainWindow, create_tray_icon
from gui.styles import DARK_STYLESHEET

def main():
    # Enable High DPI Scaling
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running in system tray
    app.setStyleSheet(DARK_STYLESHEET)
    app.setWindowIcon(create_tray_icon())

    # Core Managers
    profile_manager = ProfileManager(profiles_dir="profiles")
    macro_engine = MacroEngine(profile_manager)
    gamepad_listener = GamepadListener()

    # Main Window
    window = MainWindow(profile_manager, gamepad_listener, macro_engine)
    window.show()

    # Start Gamepad Polling Thread
    gamepad_listener.start()

    # Execute Qt Loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
