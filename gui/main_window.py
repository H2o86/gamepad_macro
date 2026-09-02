import os
from datetime import datetime
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QFrame, QGridLayout, QInputDialog,
    QMessageBox, QSystemTrayIcon, QMenu, QTabWidget, QLineEdit,
    QFileDialog, QDialog, QFormLayout
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QIcon, QAction, QPixmap, QColor, QPainter

from core.profile_manager import ProfileManager
from core.gamepad_listener import GamepadListener
from core.macro_engine import MacroEngine
from core.input_simulator import InputSimulator
from core.game_detector import GameDetector
from gui.macro_editor_dialog import MacroEditorDialog, DPAD_NAMES

def create_tray_icon() -> QIcon:
    """Return high-res custom gamepad app icon for Taskbar & System Tray."""
    icon_path = os.path.join("resources", "app_icon.png")
    if os.path.exists(icon_path):
        return QIcon(icon_path)

    pix = QPixmap(64, 64)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)

    # Outer rounded background
    painter.setBrush(QColor("#0F172A"))
    painter.setPen(QColor("#0EA5E9"))
    painter.drawRoundedRect(2, 2, 60, 60, 14, 14)

    # Gamepad Body Shape
    painter.setBrush(QColor("#0284C7"))
    painter.setPen(QColor("#38BDF8"))
    painter.drawRoundedRect(10, 20, 44, 24, 8, 8)

    # D-Pad Cross (Left side)
    painter.setBrush(QColor("#FFFFFF"))
    painter.setPen(Qt.NoPen)
    painter.drawRect(16, 28, 10, 8)
    painter.drawRect(17, 27, 8, 10)

    # Action Buttons (Right side)
    painter.setBrush(QColor("#34D399"))
    painter.drawEllipse(40, 25, 5, 5)
    painter.drawEllipse(36, 29, 5, 5)
    painter.drawEllipse(44, 29, 5, 5)
    painter.drawEllipse(40, 33, 5, 5)

    # Center LED Status Light
    painter.setBrush(QColor("#38BDF8"))
    painter.drawEllipse(29, 29, 6, 6)

    painter.end()
    return QIcon(pix)

class CopyPlayerDialog(QDialog):
    """Dialog for copying macro configurations from ANY source player to ANY target player or ALL players."""
    def __init__(self, active_player_id: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📋 Sao chép Cấu hình Macro Giữa Các Player")
        self.setMinimumWidth(460)
        self.active_player_id = active_player_id
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        lbl_title = QLabel("📋 Sao chép cấu hình 4 nút D-Pad linh hoạt:")
        lbl_title.setStyleSheet("font-weight: bold; color: #38BDF8; font-size: 14px;")
        layout.addWidget(lbl_title)

        form = QFormLayout()

        # Source Player Selection
        self.combo_source = QComboBox()
        for p in range(1, 9):
            self.combo_source.addItem(f"🎮 Player {p}", p)

        src_idx = self.combo_source.findData(self.active_player_id)
        if src_idx >= 0:
            self.combo_source.setCurrentIndex(src_idx)
        form.addRow("Từ Player Nguồn:", self.combo_source)

        # Target Player Selection
        self.combo_target = QComboBox()
        self.combo_target.addItem("🌐 TẤT CẢ các Player còn lại (P1 - P8)", 0)
        for p in range(1, 9):
            self.combo_target.addItem(f"🎯 Chỉ sang Player {p}", p)

        form.addRow("Đến Player Đích:", self.combo_target)
        layout.addLayout(form)

        lbl_note = QLabel("💡 Ghi chú: Cấu hình 4 nút D-Pad của Player Đích sẽ được ghi đè bằng cấu hình từ Player Nguồn.")
        lbl_note.setStyleSheet("color: #94A3B8; font-size: 11px;")
        layout.addWidget(lbl_note)

        btn_box = QHBoxLayout()
        btn_confirm = QPushButton("📋 Thực hiện Sao chép")
        btn_confirm.clicked.connect(self.accept)
        btn_cancel = QPushButton("Hủy")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)

        btn_box.addStretch()
        btn_box.addWidget(btn_confirm)
        btn_box.addWidget(btn_cancel)
        layout.addLayout(btn_box)

    def get_source_and_target(self) -> tuple[int, int]:
        src = self.combo_source.currentData()
        target = self.combo_target.currentData()
        return (src, target)

class ResetDefaultDialog(QDialog):
    """Dialog for resetting default macro configuration for an individual player or ALL players."""
    def __init__(self, active_player_id: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔄 Khôi Phục Cấu Hình Mặc Định")
        self.setMinimumWidth(440)
        self.active_player_id = active_player_id
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        lbl_title = QLabel("🔄 Khôi phục phím D-Pad về Preset Mặc Định PES6:")
        lbl_title.setStyleSheet("font-weight: bold; color: #F59E0B; font-size: 14px;")
        layout.addWidget(lbl_title)

        form = QFormLayout()
        self.combo_target = QComboBox()
        self.combo_target.addItem(f"🎯 Chỉ Player {self.active_player_id} (Hiện tại)", self.active_player_id)
        self.combo_target.addItem("🌐 TẤT CẢ 8 Player (P1 -> P8)", 0)
        for p in range(1, 9):
            if p != self.active_player_id:
                self.combo_target.addItem(f"Player {p}", p)

        form.addRow("Chọn đối tượng khôi phục:", self.combo_target)
        layout.addLayout(form)

        lbl_note = QLabel("💡 Mặc định PES6 gồm: D-Pad Lên (Giả Sút), D-Pad Xuống (Super Cancel), D-Pad Trái (Chip Shot), D-Pad Phải (Finesse Shot).")
        lbl_note.setStyleSheet("color: #94A3B8; font-size: 11px;")
        layout.addWidget(lbl_note)

        btn_box = QHBoxLayout()
        btn_confirm = QPushButton("🔄 Khôi phục Mặc định")
        btn_confirm.setStyleSheet("background-color: #F59E0B; color: #000000; font-weight: bold;")
        btn_confirm.clicked.connect(self.accept)
        btn_cancel = QPushButton("Hủy")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)

        btn_box.addStretch()
        btn_box.addWidget(btn_confirm)
        btn_box.addWidget(btn_cancel)
        layout.addLayout(btn_box)

    def get_target_player(self) -> int:
        return self.combo_target.currentData()

class PlayerTabWidget(QWidget):
    """Widget for each Player Tab (Player 1 .. Player 8)."""
    def __init__(self, player_id: int, main_window, parent=None):
        super().__init__(parent)
        self.player_id = player_id
        self.main_window = main_window
        self.btn_dpads = {}
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(10, 10, 10, 10)

        # Device Selection Bar
        dev_card = QFrame()
        dev_card.setObjectName("card")
        dev_layout = QHBoxLayout(dev_card)

        dev_layout.addWidget(QLabel(f"🎮 Thiết bị cho P{self.player_id}:"))
        self.combo_device = QComboBox()
        self.combo_device.setMinimumWidth(230)
        self.combo_device.currentIndexChanged.connect(self._on_device_selected)
        dev_layout.addWidget(self.combo_device)

        dev_layout.addStretch()

        btn_copy = QPushButton("📋 Sao chép...")
        btn_copy.setObjectName("btn_secondary")
        btn_copy.setToolTip("Sao chép cấu hình Macro từ Player bất kỳ sang Player khác hoặc cho tất cả Player")
        btn_copy.clicked.connect(lambda: self.main_window._open_copy_dialog(self.player_id))
        dev_layout.addWidget(btn_copy)

        btn_reset = QPushButton("🔄 Reset Mặc định")
        btn_reset.setObjectName("btn_secondary")
        btn_reset.setToolTip("Khôi phục 4 nút D-Pad của Player này hoặc cả 8 Player về cấu hình tuyệt chiêu mặc định PES6")
        btn_reset.clicked.connect(lambda: self.main_window._open_reset_dialog(self.player_id))
        dev_layout.addWidget(btn_reset)

        layout.addWidget(dev_card)

        # D-Pad Visualizer & Macro Map Card
        dpad_card = QFrame()
        dpad_card.setObjectName("card")
        dpad_layout = QVBoxLayout(dpad_card)

        lbl_dpad_header = QLabel(f"🎯 Cấu hình phím D-Pad cho Player {self.player_id} (Nhấp vào nút để gán Macro):")
        lbl_dpad_header.setStyleSheet("font-weight: bold; color: #38BDF8;")
        dpad_layout.addWidget(lbl_dpad_header)

        # Grid Layout for D-Pad Cross
        grid = QGridLayout()
        grid.setSpacing(10)

        for dpad_dir in ["dpad_up", "dpad_down", "dpad_left", "dpad_right"]:
            btn = QPushButton()
            btn.setObjectName("btn_dpad")
            btn.setMinimumHeight(65)
            btn.clicked.connect(lambda _, d=dpad_dir: self.main_window._open_macro_editor(self.player_id, d))
            self.btn_dpads[dpad_dir] = btn

        grid.addWidget(self.btn_dpads["dpad_up"], 0, 1)
        grid.addWidget(self.btn_dpads["dpad_left"], 1, 0)
        grid.addWidget(self.btn_dpads["dpad_right"], 1, 2)
        grid.addWidget(self.btn_dpads["dpad_down"], 2, 1)

        # Center indicator
        lbl_center = QLabel(f"🎮\nPlayer {self.player_id}")
        lbl_center.setAlignment(Qt.AlignCenter)
        lbl_center.setStyleSheet("color: #64748B; font-weight: bold;")
        grid.addWidget(lbl_center, 1, 1)

        dpad_layout.addLayout(grid)
        layout.addWidget(dpad_card)

    def _on_device_selected(self, index: int):
        joy_idx = self.combo_device.currentData()
        if joy_idx is not None:
            self.main_window.profile_manager.set_player_device_index(self.player_id, joy_idx)

    def update_devices_list(self, device_list: list[dict]):
        self.combo_device.blockSignals(True)
        self.combo_device.clear()

        # Add unassigned / automatic option
        self.combo_device.addItem(f"⚙️ Tự động (Tay cầm #{self.player_id})", self.player_id - 1)

        for dev in device_list:
            self.combo_device.addItem(dev["name"], dev["index"])

        # Select saved device_index
        saved_idx = self.main_window.profile_manager.get_player_device_index(self.player_id)
        idx = self.combo_device.findData(saved_idx)
        if idx >= 0:
            self.combo_device.setCurrentIndex(idx)

        self.combo_device.blockSignals(False)

    def update_dpad_buttons_text(self):
        pm = self.main_window.profile_manager
        for dpad_dir, btn in self.btn_dpads.items():
            mapping = pm.get_player_dpad_mapping(self.player_id, dpad_dir)
            title = DPAD_NAMES.get(dpad_dir, dpad_dir)

            if not mapping:
                text = f"⬆️ {title}\n(Chưa gán)"
            else:
                mname = mapping.get("name", "").strip()
                mtype = mapping.get("type", "single")

                if mtype == "single":
                    key = mapping.get("key", "?").upper()
                    mode = mapping.get("mode", "press_hold")
                    mode_str = "Hold" if mode == "press_hold" else ("Tap" if mode == "tap" else "AutoClick")
                    action_str = f"🎯 Phím [{key}] ({mode_str})"
                elif mtype == "combo":
                    keys = "+".join(mapping.get("keys", [])).upper()
                    action_str = f"⚡ Combo: [{keys}]"
                elif mtype == "sequence":
                    count = len(mapping.get("sequence", []))
                    action_str = f"🔄 Chuỗi ({count} bước)"
                else:
                    action_str = "🎯 Custom Action"

                if mname:
                    text = f"🎮 {title}\n⚽ {mname}\n[{action_str}]"
                else:
                    text = f"🎮 {title}\n[{action_str}]"

            btn.setText(text)

class MainWindow(QMainWindow):
    def __init__(self, profile_manager: ProfileManager, gamepad_listener: GamepadListener, macro_engine: MacroEngine):
        super().__init__()
        self.profile_manager = profile_manager
        self.gamepad_listener = gamepad_listener
        self.macro_engine = macro_engine
        self.current_game_hwnd = 0

        self.setWindowTitle("PES6 Gamepad Macro Manager - Hỗ trợ 8 Players & Config Backup")
        self.setMinimumSize(740, 660)

        self.player_tabs = {}  # {player_id: PlayerTabWidget}
        self._init_ui()
        self._setup_connections()
        self._setup_system_tray()
        self._refresh_profiles_list()
        self._start_game_timer()

    def _init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # Header Card
        header_card = QFrame()
        header_card.setObjectName("card")
        header_layout = QHBoxLayout(header_card)

        title_box = QVBoxLayout()
        lbl_title = QLabel("🎮 PES6 Gamepad Macro Manager (8 Players)")
        lbl_title.setObjectName("title")
        lbl_subtitle = QLabel("Quản lý & Gán Macro độc lập cho 8 Người chơi (Player 1 -> Player 8)")
        lbl_subtitle.setObjectName("subtitle")
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_subtitle)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        # Status badge
        self.status_frame = QFrame()
        self.status_frame.setObjectName("status_disconnected")
        status_layout = QHBoxLayout(self.status_frame)
        status_layout.setContentsMargins(10, 6, 10, 6)
        self.lbl_status = QLabel("❌ Chưa tìm thấy tay cầm nào")
        self.lbl_status.setObjectName("status_text_disconn")
        status_layout.addWidget(self.lbl_status)

        header_layout.addWidget(self.status_frame)
        main_layout.addWidget(header_card)

        # Game Detector Status Card
        game_card = QFrame()
        game_card.setObjectName("card")
        game_layout = QHBoxLayout(game_card)

        self.lbl_game_status = QLabel("⚽ Trạng thái Game: 🔴 Đang quét tiến trình pes6.exe...")
        self.lbl_game_status.setStyleSheet("font-weight: bold; font-size: 13px; color: #F87171;")
        game_layout.addWidget(self.lbl_game_status)

        game_layout.addStretch()

        self.btn_focus_game = QPushButton("🎯 Focus Cửa sổ Game")
        self.btn_focus_game.setObjectName("btn_secondary")
        self.btn_focus_game.setVisible(False)
        self.btn_focus_game.clicked.connect(self._focus_target_game_window)
        game_layout.addWidget(self.btn_focus_game)

        game_layout.addWidget(QLabel("Target EXE:"))
        self.txt_target_exe = QLineEdit()
        self.txt_target_exe.setPlaceholderText("pes6.exe")
        self.txt_target_exe.setMaximumWidth(130)
        game_layout.addWidget(self.txt_target_exe)

        main_layout.addWidget(game_card)

        # Profile Switcher & Backup / Restore Card
        profile_card = QFrame()
        profile_card.setObjectName("card")
        profile_layout = QHBoxLayout(profile_card)

        profile_layout.addWidget(QLabel("📂 Profile:"))
        self.combo_profile = QComboBox()
        self.combo_profile.setMinimumWidth(160)
        self.combo_profile.currentIndexChanged.connect(self._on_profile_selected)
        profile_layout.addWidget(self.combo_profile)

        btn_new_prof = QPushButton("+ Tạo mới")
        btn_new_prof.setObjectName("btn_secondary")
        btn_new_prof.clicked.connect(self._on_create_profile)
        profile_layout.addWidget(btn_new_prof)

        btn_save_as = QPushButton("💾 Lưu tên file...")
        btn_save_as.setObjectName("btn_secondary")
        btn_save_as.clicked.connect(self._on_save_profile_as)
        profile_layout.addWidget(btn_save_as)

        # Flexible Copy Button
        btn_copy_global = QPushButton("📋 Sao chép Macro...")
        btn_copy_global.setObjectName("btn_secondary")
        btn_copy_global.clicked.connect(lambda: self._open_copy_dialog(1))
        profile_layout.addWidget(btn_copy_global)

        # Backup & Restore Menu Button
        btn_backup_menu = QPushButton("⚙️ Backup / Restore")
        btn_backup_menu.setObjectName("btn_secondary")

        menu_backup = QMenu(self)
        act_export_prof = QAction("📤 Xuất (Export) Profile cá nhân...", self)
        act_export_prof.triggered.connect(self._on_export_profile)
        menu_backup.addAction(act_export_prof)

        act_import_prof = QAction("📥 Nhập (Import) Profile cá nhân...", self)
        act_import_prof.triggered.connect(self._on_import_profile)
        menu_backup.addAction(act_import_prof)

        menu_backup.addSeparator()

        act_reset_def = QAction("🔄 Khôi phục Cấu hình Mặc định (Reset Defaults)...", self)
        act_reset_def.triggered.connect(lambda: self._open_reset_dialog(0))
        menu_backup.addAction(act_reset_def)

        menu_backup.addSeparator()

        act_backup_all = QAction("📦 Sao lưu TỔNG THỂ (Backup All)...", self)
        act_backup_all.triggered.connect(self._on_backup_all)
        menu_backup.addAction(act_backup_all)

        act_restore_all = QAction("♻️ Phục hồi TỔNG THỂ (Restore All)...", self)
        act_restore_all.triggered.connect(self._on_restore_all)
        menu_backup.addAction(act_restore_all)

        btn_backup_menu.setMenu(menu_backup)
        profile_layout.addWidget(btn_backup_menu)

        profile_layout.addStretch()

        # Macro Enable Toggle
        self.btn_toggle_macro = QPushButton("🟢 Macro: ĐANG BẬT")
        self.btn_toggle_macro.setCheckable(True)
        self.btn_toggle_macro.setChecked(True)
        self.btn_toggle_macro.clicked.connect(self._on_toggle_macro)
        profile_layout.addWidget(self.btn_toggle_macro)

        main_layout.addWidget(profile_card)

        # -------------------------------------------------------------
        # 8 Player Tabs (PES6 Settings Style)
        # -------------------------------------------------------------
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #334155;
                background-color: #1E293B;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #0F172A;
                color: #94A3B8;
                border: 1px solid #334155;
                padding: 8px 14px;
                font-weight: bold;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #1E293B;
                color: #38BDF8;
                border-bottom-color: #1E293B;
            }
            QTabBar::tab:hover {
                color: #F8FAFC;
            }
        """)

        for p in range(1, 9):
            tab_item = PlayerTabWidget(p, self)
            self.player_tabs[p] = tab_item
            self.tab_widget.addTab(tab_item, f"Player {p}")

        main_layout.addWidget(self.tab_widget)

        # Footer Tips
        lbl_tips = QLabel("💡 Mẹo: Dùng nút '🔄 Reset Mặc định' để khôi phục nhanh cấu hình tuyệt chiêu PES6 cho từng Player hoặc cả 8 Player!")
        lbl_tips.setStyleSheet("color: #F59E0B; font-weight: bold; font-size: 11px;")
        main_layout.addWidget(lbl_tips)

    def _setup_connections(self):
        self.gamepad_listener.connection_changed.connect(self._on_connection_changed)
        self.gamepad_listener.devices_changed.connect(self._on_devices_changed)
        self.gamepad_listener.dpad_event.connect(self._on_dpad_event)

    def _start_game_timer(self):
        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self._check_game_status)
        self.game_timer.start(1000)

    def _check_game_status(self):
        custom_target = self.txt_target_exe.text().strip()
        info = GameDetector.find_game_window(custom_target)

        if info["is_running"]:
            self.current_game_hwnd = info["hwnd"]
            InputSimulator.set_target_hwnd(info["hwnd"])

            if info["is_focused"]:
                self.lbl_game_status.setText(f"⚽ Target Game: 🟢 Đã Hook & Focus [{info['proc_name']} - {info['title']}]")
                self.lbl_game_status.setStyleSheet("color: #34D399; font-weight: bold;")
                self.btn_focus_game.setVisible(False)
            else:
                self.lbl_game_status.setText(f"⚽ Target Game: 🟡 Đang chạy ngầm / Chưa Focus [{info['proc_name']}]")
                self.lbl_game_status.setStyleSheet("color: #FBBF24; font-weight: bold;")
                self.btn_focus_game.setVisible(True)
        else:
            self.current_game_hwnd = 0
            InputSimulator.set_target_hwnd(0)
            self.lbl_game_status.setText("⚽ Target Game: 🔴 Chưa bật game (Đang quét pes6.exe, pes2007.exe, settings.exe...)")
            self.lbl_game_status.setStyleSheet("color: #F87171; font-weight: bold;")
            self.btn_focus_game.setVisible(False)

    def _focus_target_game_window(self):
        if self.current_game_hwnd:
            GameDetector.focus_window(self.current_game_hwnd)

    def _setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(create_tray_icon())
        self.tray_icon.setToolTip("PES6 Gamepad Macro Manager (8 Players)")

        menu = QMenu()
        act_show = QAction("Hiện cửa sổ chính", self)
        act_show.triggered.connect(self.showNormal)
        menu.addAction(act_show)

        self.act_toggle = QAction("Tắt Macro", self)
        self.act_toggle.triggered.connect(self._on_toggle_macro)
        menu.addAction(self.act_toggle)

        menu.addSeparator()
        act_exit = QAction("Thoát ứng dụng", self)
        act_exit.triggered.connect(self._force_exit)
        menu.addAction(act_exit)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_connection_changed(self, is_conn: bool, summary: str):
        if is_conn:
            self.status_frame.setObjectName("status_connected")
            self.lbl_status.setText(summary)
            self.lbl_status.setObjectName("status_text_conn")
        else:
            self.status_frame.setObjectName("status_disconnected")
            self.lbl_status.setText(summary)
            self.lbl_status.setObjectName("status_text_disconn")

        self.status_frame.setStyle(self.status_frame.style())
        self.lbl_status.setStyle(self.lbl_status.style())

    def _on_devices_changed(self, device_list: list[dict]):
        for player_id, tab in self.player_tabs.items():
            tab.update_devices_list(device_list)

    def _on_dpad_event(self, joy_idx: int, dpad_dir: str, is_pressed: bool):
        for p in range(1, 9):
            if self.profile_manager.get_player_device_index(p) == joy_idx or (joy_idx == p - 1):
                tab = self.player_tabs[p]
                if dpad_dir in tab.btn_dpads:
                    btn = tab.btn_dpads[dpad_dir]
                    if is_pressed:
                        btn.setObjectName("btn_dpad_active")
                    else:
                        btn.setObjectName("btn_dpad")
                    btn.setStyle(btn.style())

        # Pass event to macro engine
        self.macro_engine.handle_dpad_event(joy_idx, dpad_dir, is_pressed)

    def _refresh_profiles_list(self):
        self.combo_profile.blockSignals(True)
        self.combo_profile.clear()
        profiles = self.profile_manager.list_profiles()
        self.combo_profile.addItems(profiles)
        
        curr = self.profile_manager.active_profile_name
        idx = self.combo_profile.findText(curr)
        if idx >= 0:
            self.combo_profile.setCurrentIndex(idx)
        self.combo_profile.blockSignals(False)

        self._update_all_player_tabs_text()

    def _on_profile_selected(self, index: int):
        prof_name = self.combo_profile.currentText()
        if prof_name:
            self.profile_manager.load_profile(prof_name)
            self._update_all_player_tabs_text()

    def _on_create_profile(self):
        name, ok = QInputDialog.getText(self, "Tạo Profile mới", "Nhập tên Profile (VD: pes6_tournament, fifa):")
        if ok and name.strip():
            clean_name = name.strip().lower()
            from core.profile_manager import create_default_8player_profile
            self.profile_manager.save_profile_file(f"{clean_name}.json", create_default_8player_profile(name, is_pes6=True))
            self.profile_manager.load_profile(clean_name)
            self._refresh_profiles_list()

    def _on_save_profile_as(self):
        name, ok = QInputDialog.getText(
            self,
            "Lưu Profile Thành File Mới",
            "Nhập tên Profile mới (VD: Profile_Giai_Dau_2026):",
            text=f"{self.profile_manager.active_profile_name}_copy"
        )
        if ok and name.strip():
            new_prof = self.profile_manager.save_profile_as(name.strip())
            self._refresh_profiles_list()
            QMessageBox.information(self, "Thành công", f"Đã lưu thành Profile mới: [{new_prof}]!")

    def _on_export_profile(self):
        curr = self.profile_manager.active_profile_name
        default_file = f"{curr}.json"
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            f"Xuất Profile [{curr}] ra File JSON",
            default_file,
            "JSON Profile Files (*.json)"
        )
        if filepath:
            if self.profile_manager.export_profile(curr, filepath):
                QMessageBox.information(self, "Thành công", f"Đã xuất Profile [{curr}] thành công ra file:\n{filepath}")
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể xuất file Profile!")

    def _on_import_profile(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Nhập Profile từ File JSON bên ngoài",
            "",
            "JSON Profile Files (*.json)"
        )
        if filepath:
            new_prof = self.profile_manager.import_profile(filepath)
            if new_prof:
                self._refresh_profiles_list()
                QMessageBox.information(self, "Thành công", f"Đã nạp Profile cá nhân mới: [{new_prof}]!")
            else:
                QMessageBox.critical(self, "Lỗi", "File Profile không hợp lệ hoặc bị lỗi!")

    def _on_backup_all(self):
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"gamepad_macro_backup_{date_str}.zip"
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Sao lưu TỔNG THỂ Toàn bộ Profile",
            default_name,
            "ZIP Backup Files (*.zip)"
        )
        if filepath:
            if self.profile_manager.export_full_backup(filepath):
                QMessageBox.information(self, "Thành công", f"Đã sao lưu TỔNG THỂ toàn bộ Profile thành công ra file:\n{filepath}")
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể tạo file sao lưu Tổng thể!")

    def _on_restore_all(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Phục hồi TỔNG THỂ từ File Backup",
            "",
            "ZIP Backup Files (*.zip)"
        )
        if filepath:
            reply = QMessageBox.question(
                self,
                "Xác nhận Phục hồi Tổng thể",
                "Phục hồi sẽ đè các Profile hiện tại bằng dữ liệu từ file Backup ZIP. Bạn có chắc muốn tiếp tục?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                if self.profile_manager.import_full_backup(filepath):
                    self._refresh_profiles_list()
                    QMessageBox.information(self, "Thành công", "Đã phục hồi TỔNG THỂ toàn bộ cấu hình Profile từ file Backup!")
                else:
                    QMessageBox.critical(self, "Lỗi", "File Backup ZIP không hợp lệ hoặc bị lỗi!")

    def _open_copy_dialog(self, default_source_player_id: int = 1):
        dialog = CopyPlayerDialog(default_source_player_id, self)
        if dialog.exec():
            src_p, target_p = dialog.get_source_and_target()
            if src_p == target_p:
                QMessageBox.warning(self, "Cảnh báo", "Player Nguồn và Player Đích trùng nhau! Vui lòng chọn Player Đích khác.")
                return

            if self.profile_manager.copy_player_mappings(src_p, target_p):
                self._update_all_player_tabs_text()
                if target_p == 0:
                    QMessageBox.information(self, "Thành công", f"Đã sao chép toàn bộ Macro từ Player {src_p} sang TẤT CẢ các Player còn lại!")
                else:
                    QMessageBox.information(self, "Thành công", f"Đã sao chép toàn bộ Macro từ Player {src_p} sang Player {target_p}!")
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể sao chép cấu hình Macro!")

    def _open_reset_dialog(self, default_player_id: int = 1):
        dialog = ResetDefaultDialog(default_player_id, self)
        if dialog.exec():
            target_p = dialog.get_target_player()
            reply = QMessageBox.question(
                self,
                "Xác nhận Khôi phục Mặc định",
                f"Bạn có chắc chắn muốn khôi phục phím D-Pad của {'TẤT CẢ 8 Player' if target_p == 0 else f'Player {target_p}'} về cấu hình tuyệt chiêu mặc định PES6?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                if self.profile_manager.reset_player_defaults(target_p, is_pes6=True):
                    self._update_all_player_tabs_text()
                    if target_p == 0:
                        QMessageBox.information(self, "Thành công", "Đã khôi phục phím D-Pad của TẤT CẢ 8 Player về mặc định tuyệt chiêu PES6!")
                    else:
                        QMessageBox.information(self, "Thành công", f"Đã khôi phục phím D-Pad của Player {target_p} về mặc định tuyệt chiêu PES6!")
                else:
                    QMessageBox.critical(self, "Lỗi", "Không thể khôi phục cấu hình mặc định!")

    def _update_all_player_tabs_text(self):
        for player_id, tab in self.player_tabs.items():
            tab.update_dpad_buttons_text()

    def _open_macro_editor(self, player_id: int, dpad_dir: str):
        mapping = self.profile_manager.get_player_dpad_mapping(player_id, dpad_dir)
        dialog = MacroEditorDialog(player_id, dpad_dir, mapping, self.gamepad_listener, self)
        if dialog.exec():
            new_map = dialog.get_result()
            self.profile_manager.update_player_dpad_mapping(player_id, dpad_dir, new_map)
            self.player_tabs[player_id].update_dpad_buttons_text()

    def _on_toggle_macro(self):
        enabled = self.btn_toggle_macro.isChecked()
        self.macro_engine.set_enabled(enabled)
        if enabled:
            self.btn_toggle_macro.setText("🟢 Macro: ĐANG BẬT")
            self.btn_toggle_macro.setStyleSheet("background-color: #0EA5E9;")
            self.act_toggle.setText("Tắt Macro")
        else:
            self.btn_toggle_macro.setText("🔴 Macro: ĐÃ TẮT")
            self.btn_toggle_macro.setStyleSheet("background-color: #DC2626;")
            self.act_toggle.setText("Bật Macro")

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.showNormal()
                self.activateWindow()

    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                "PES6 Gamepad Macro Manager",
                "Ứng dụng vẫn đang chạy ngầm 8-Player góc màn hình!",
                QSystemTrayIcon.Information,
                2000
            )
            event.ignore()
        else:
            event.accept()

    def _force_exit(self):
        self.gamepad_listener.stop()
        self.tray_icon.hide()
        self.close()
        os._exit(0)
