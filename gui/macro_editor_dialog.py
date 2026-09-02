from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QWidget, QMessageBox, QListWidget,
    QListWidgetItem, QGroupBox, QTextBrowser, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from core.profile_manager import ProfileManager
from core.gamepad_listener import GamepadListener
from gui.macro_library_dialog import MacroLibraryDialog

DPAD_NAMES = {
    "dpad_up": "D-Pad Lên (Up)",
    "dpad_down": "D-Pad Xuống (Down)",
    "dpad_left": "D-Pad Trái (Left)",
    "dpad_right": "D-Pad Phải (Right)",
    "up": "D-Pad Lên (Up)",
    "down": "D-Pad Xuống (Down)",
    "left": "D-Pad Trái (Left)",
    "right": "D-Pad Phải (Right)"
}


class MacroEditorDialog(QDialog):
    """
    GUI Gán Macro cho Nút D-Pad.
    Chỉ cho phép gán những Macro đã được định nghĩa đầy đủ trong Thư viện Macro.
    Có nút mở Thư viện Macro để tạo/biên soạn tuyệt chiêu mới (lên đến 8 phím).
    """
    def __init__(self, player_id: int, dpad_dir: str, current_mapping: dict,
                 gamepad_listener: GamepadListener = None, parent=None):
        super().__init__(parent)
        self.player_id = player_id
        self.dpad_dir = dpad_dir
        self.current_mapping = current_mapping or {}
        self.gamepad_listener = gamepad_listener
        self.selected_macro_data = None

        # Access profile_manager from parent (MainWindow) if available
        if hasattr(parent, 'profile_manager'):
            self.profile_manager = parent.profile_manager
        else:
            self.profile_manager = ProfileManager()

        dir_name = DPAD_NAMES.get(dpad_dir, dpad_dir)
        self.setWindowTitle(f"🎯 Gán Macro - Player {player_id} [{dir_name}]")
        self.resize(680, 520)
        self.setStyleSheet("""
            QDialog {
                background-color: #0F172A;
                color: #F8FAFC;
            }
            QLabel {
                color: #F8FAFC;
            }
            QListWidget {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 8px;
                color: #F8FAFC;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #334155;
            }
            QListWidget::item:selected {
                background-color: #0284C7;
                color: #FFFFFF;
                font-weight: bold;
                border-radius: 6px;
            }
            QTextBrowser {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #0284C7;
                color: #FFFFFF;
                border-radius: 6px;
                padding: 8px 18px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #0369A1;
            }
        """)

        self._init_ui()
        self._load_macro_library()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # Header Info Banner
        dir_name = DPAD_NAMES.get(self.dpad_dir, self.dpad_dir)
        hdr_frame = QFrame()
        hdr_frame.setStyleSheet("background-color: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 12px;")
        hdr_layout = QHBoxLayout(hdr_frame)

        lbl_icon = QLabel("🎮")
        lbl_icon.setFont(QFont("Segoe UI Emoji", 26))
        hdr_layout.addWidget(lbl_icon)

        v_hdr = QVBoxLayout()
        lbl_target = QLabel(f"Gán Tuyệt Chiêu Macro Cho: Player {self.player_id} ➔ {dir_name}")
        lbl_target.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_target.setStyleSheet("color: #38BDF8;")
        
        lbl_sub = QLabel("Chỉ các Macro đã được định nghĩa đầy đủ trong Thư viện mới được phép chọn gán.")
        lbl_sub.setStyleSheet("color: #94A3B8; font-size: 12px;")
        v_hdr.addWidget(lbl_target)
        v_hdr.addWidget(lbl_sub)
        hdr_layout.addLayout(v_hdr)
        main_layout.addWidget(hdr_frame)

        main_layout.addSpacing(10)

        # Selection Split View
        content_layout = QHBoxLayout()

        # Left Column: Macro Library Selection List
        left_vbox = QVBoxLayout()
        lbl_list_hdr = QLabel("📚 Thư Viện Macro Có Sẵn:")
        lbl_list_hdr.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_list_hdr.setStyleSheet("color: #F8FAFC;")
        left_vbox.addWidget(lbl_list_hdr)

        self.lst_macros = QListWidget()
        self.lst_macros.currentRowChanged.connect(self._on_macro_selected)
        left_vbox.addWidget(self.lst_macros)

        # Open Library Manager Button
        btn_open_lib = QPushButton("📚 Quản Lý / Tạo Macro Mới (Up to 8 phím)...")
        btn_open_lib.setStyleSheet("background-color: #8B5CF6; color: #FFFFFF; font-weight: bold; padding: 8px;")
        btn_open_lib.clicked.connect(self._open_library_manager)
        left_vbox.addWidget(btn_open_lib)

        content_layout.addLayout(left_vbox, stretch=1)

        # Right Column: Preview Selected Macro
        right_vbox = QVBoxLayout()
        lbl_prev_hdr = QLabel("🔍 Chi Tiết Bước Thực Thi Macro:")
        lbl_prev_hdr.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_prev_hdr.setStyleSheet("color: #F8FAFC;")
        right_vbox.addWidget(lbl_prev_hdr)

        self.txt_preview = QTextBrowser()
        right_vbox.addWidget(self.txt_preview)

        content_layout.addLayout(right_vbox, stretch=1)
        main_layout.addLayout(content_layout)

        # Bottom Dialog Actions
        main_layout.addSpacing(12)
        bottom_layout = QHBoxLayout()

        btn_cancel = QPushButton("Hủy bỏ")
        btn_cancel.setStyleSheet("background-color: #475569; color: #FFFFFF;")
        btn_cancel.clicked.connect(self.reject)

        self.btn_assign = QPushButton("✅ Gán Macro Này Vào Phím D-Pad")
        self.btn_assign.setFixedHeight(40)
        self.btn_assign.setStyleSheet("background-color: #10B981; color: #FFFFFF; font-size: 13px; font-weight: bold;")
        self.btn_assign.clicked.connect(self._assign_macro)

        bottom_layout.addWidget(btn_cancel)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_assign)
        main_layout.addLayout(bottom_layout)

    def _load_macro_library(self):
        self.lst_macros.clear()
        library = self.profile_manager.get_macro_library()
        
        curr_name = self.current_mapping.get("name", "")
        select_row = 0

        for idx, macro in enumerate(library):
            name = macro.get("name", f"Macro #{idx+1}")
            seq_len = len(macro.get("sequence", []))
            
            item = QListWidgetItem(f"⚽ {name} ({seq_len} phím)")
            item.setData(Qt.UserRole, macro)
            self.lst_macros.addItem(item)

            if curr_name and name.lower() == curr_name.lower():
                select_row = idx

        if self.lst_macros.count() > 0:
            self.lst_macros.setCurrentRow(select_row)

    def _on_macro_selected(self, row: int):
        if row < 0:
            self.selected_macro_data = None
            self.txt_preview.setHtml("<p style='color:#94A3B8;'>Chưa chọn Macro nào.</p>")
            return

        item = self.lst_macros.item(row)
        if not item:
            return

        macro = item.data(Qt.UserRole)
        self.selected_macro_data = macro
        self._render_macro_preview(macro)

    def _render_macro_preview(self, macro: dict):
        name = macro.get("name", "Tuyệt Chiêu Macro")
        desc = macro.get("description", "Không có mô tả.")
        seq = macro.get("sequence", [])

        html = f"""
        <h3 style='color:#38BDF8; margin-bottom:4px;'>⚽ {name}</h3>
        <p style='color:#CBD5E1; font-size:12px; margin-top:0px;'><i>{desc}</i></p>
        <hr style='border: 1px solid #334155;'>
        <h4 style='color:#F8FAFC;'>Trình tự {len(seq)} bước phím:</h4>
        <ol style='color:#F8FAFC; line-height: 1.6;'>
        """

        key_label_map = {
            "numdel": "Nút A / ✕ (Chuyền ngắn) ➔ [Num Del]",
            "num3": "Nút B / ◯ (Chuyền dài) ➔ [Num 3]",
            "num2": "Nút X / ▢ (Sút bóng) ➔ [Num 2]",
            "num5": "Nút Y / △ (Chọc khe) ➔ [Num 5]",
            "rctrl": "Nút LB / L1 (Đổi người) ➔ [Right Ctrl]",
            "num0": "Nút RB / R1 (Sprint) ➔ [Num 0]",
            "rshift": "Nút LT / L2 (Chiến thuật) ➔ [Right Shift]",
            "num1": "Nút RT / R2 (Cứa lòng) ➔ [Num 1]",
            "r": "Nút L3 / LS (Nhấn cần gạt trái) ➔ [Phím R]",
            "t": "Nút R3 / RS (Nhấn cần gạt phải) ➔ [Phím T]",
            "g": "Nút Start / Pause ➔ [G]",
            "f": "Nút Select ➔ [F]"
        }

        for idx, step in enumerate(seq):
            action = step.get("action", "tap")
            key = step.get("key", "")
            keys = step.get("keys", [])
            hold_sec = step.get("hold_duration", 0.05)
            delay_sec = step.get("post_delay", 0.05)

            hold_ms = int(hold_sec * 1000)
            delay_ms = int(delay_sec * 1000)

            if action == "combo":
                key_str = " + ".join([key_label_map.get(k, k.upper()) for k in keys])
                act_str = f"<b style='color:#8B5CF6;'>[Tổ hợp COMBO]</b> {key_str}"
            elif action == "hold":
                key_str = key_label_map.get(key, key.upper())
                act_str = f"<b style='color:#EAB308;'>[GIỮ PHÍM]</b> {key_str}"
            else:
                key_str = key_label_map.get(key, key.upper())
                act_str = f"<b style='color:#38BDF8;'>[NHẤN NHẢ]</b> {key_str}"

            html += f"<li>{act_str} <span style='color:#94A3B8;'>(Hold: {hold_ms}ms, Delay: {delay_ms}ms)</span></li>"

        html += "</ol>"
        self.txt_preview.setHtml(html)

    def _open_library_manager(self):
        dialog = MacroLibraryDialog(self.profile_manager, self.gamepad_listener, self)
        dialog.exec()
        # Reload library list after editing
        self._load_macro_library()

    def _assign_macro(self):
        if not self.selected_macro_data:
            QMessageBox.warning(self, "Chưa Chọn Macro", "Vui lòng chọn một Macro trong Thư viện để gán!")
            return

        self.accept()

    def get_result_mapping(self) -> dict:
        if self.selected_macro_data:
            return dict(self.selected_macro_data)
        return self.current_mapping
