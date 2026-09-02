import time
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QDoubleSpinBox, QSpinBox, QWidget,
    QFormLayout, QMessageBox, QListWidget, QListWidgetItem,
    QGroupBox, QTextBrowser, QFrame, QScrollArea, QSplitter
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor
from core.profile_manager import ProfileManager
from core.gamepad_listener import GamepadListener

# Controller Button Mappings for PES6 Numpad Layout
XBOX_BUTTON_MAP = [
    {"name": "-- Chọn phím Nút Tay cầm --", "key": ""},
    {"name": "🎮 Nút A / ✕ (Chuyền ngắn / Lấy bóng) ➔ [Num Del]", "key": "numdel"},
    {"name": "🎮 Nút B / ◯ (Chuyền dài / Xoạc bóng) ➔ [Num 3]", "key": "num3"},
    {"name": "🎮 Nút X / ▢ (Sút bóng / Gọi máy hỗ trợ) ➔ [Num 2]", "key": "num2"},
    {"name": "🎮 Nút Y / △ (Chọc khe / Thủ môn dâng) ➔ [Num 5]", "key": "num5"},
    {"name": "🎮 Nút LB / L1 (Đổi người / Chạy chỗ) ➔ [Right Ctrl]", "key": "rctrl"},
    {"name": "🎮 Nút RB / R1 (Chạy nhanh - Sprint) ➔ [Num 0]", "key": "num0"},
    {"name": "🎮 Nút LT / L2 (Chiến thuật - Special) ➔ [Right Shift]", "key": "rshift"},
    {"name": "🎮 Nút RT / R2 (Sút má trong / Kỹ thuật) ➔ [Num 1]", "key": "num1"},
    {"name": "🎮 Nút Start / Options ➔ [G]", "key": "g"},
    {"name": "🎮 Nút Back / Share / Select ➔ [F]", "key": "f"},
    {"name": "⌨️ Bàn phím: Phím W ➔ [W]", "key": "w"},
    {"name": "⌨️ Bàn phím: Phím A ➔ [A]", "key": "a"},
    {"name": "⌨️ Bàn phím: Phím S ➔ [S]", "key": "s"},
    {"name": "⌨️ Bàn phím: Phím D ➔ [D]", "key": "d"},
    {"name": "⌨️ Bàn phím: Phím Q ➔ [Q]", "key": "q"},
    {"name": "⌨️ Bàn phím: Phím E ➔ [E]", "key": "e"},
    {"name": "⌨️ Bàn phím: Phím C ➔ [C]", "key": "c"},
    {"name": "⌨️ Bàn phím: Phím Z ➔ [Z]", "key": "z"},
    {"name": "⌨️ Bàn phím: Phím X ➔ [X]", "key": "x"},
]


class StepWidget(QFrame):
    """Widget representing one step in a sequence (up to 8 steps max)."""
    delete_requested = Signal(object)

    def __init__(self, step_number: int, step_data: dict = None):
        super().__init__()
        self.step_number = step_number
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            StepWidget {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 6px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)

        lbl_step = QLabel(f"Bước {step_number}:")
        lbl_step.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_step.setStyleSheet("color: #38BDF8;")
        layout.addWidget(lbl_step)

        # Key selector combo
        self.cmb_key = QComboBox()
        self.cmb_key.setStyleSheet("background-color: #0F172A; color: #F8FAFC; border: 1px solid #475569; border-radius: 4px; padding: 4px;")
        for item in XBOX_BUTTON_MAP:
            self.cmb_key.addItem(item["name"], item["key"])
        layout.addWidget(self.cmb_key, stretch=2)

        # Action mode
        self.cmb_mode = QComboBox()
        self.cmb_mode.setStyleSheet("background-color: #0F172A; color: #F8FAFC; border: 1px solid #475569; border-radius: 4px; padding: 4px;")
        self.cmb_mode.addItem("Nhấn nhả (Tap)", "tap")
        self.cmb_mode.addItem("Tổ hợp (Combo RB+RT)", "combo")
        self.cmb_mode.addItem("Giữ phím (Hold)", "hold")
        layout.addWidget(self.cmb_mode, stretch=1)

        # Hold time (ms)
        lbl_hold = QLabel("Hold (ms):")
        lbl_hold.setStyleSheet("color: #CBD5E1;")
        layout.addWidget(lbl_hold)
        self.spn_hold = QSpinBox()
        self.spn_hold.setRange(10, 5000)
        self.spn_hold.setSingleStep(10)
        self.spn_hold.setValue(50)
        self.spn_hold.setStyleSheet("background-color: #0F172A; color: #38BDF8; font-weight: bold;")
        layout.addWidget(self.spn_hold)

        # Delay time (ms)
        lbl_delay = QLabel("Delay (ms):")
        lbl_delay.setStyleSheet("color: #CBD5E1;")
        layout.addWidget(lbl_delay)
        self.spn_delay = QSpinBox()
        self.spn_delay.setRange(0, 5000)
        self.spn_delay.setSingleStep(10)
        self.spn_delay.setValue(50)
        self.spn_delay.setStyleSheet("background-color: #0F172A; color: #F8FAFC;")
        layout.addWidget(self.spn_delay)

        # Delete button
        btn_del = QPushButton("❌")
        btn_del.setToolTip("Xóa bước này")
        btn_del.setFixedWidth(32)
        btn_del.setStyleSheet("background-color: #EF4444; color: #FFFFFF; border-radius: 4px; font-weight: bold;")
        btn_del.clicked.connect(lambda: self.delete_requested.emit(self))
        layout.addWidget(btn_del)

        if step_data:
            self.set_step_data(step_data)

    def set_step_data(self, data: dict):
        key = data.get("key", "")
        if not key and data.get("keys"):
            key = data.get("keys")[0]
        
        idx = self.cmb_key.findData(key)
        if idx >= 0:
            self.cmb_key.setCurrentIndex(idx)

        act = data.get("action", "tap")
        mode_idx = self.cmb_mode.findData(act)
        if mode_idx >= 0:
            self.cmb_mode.setCurrentIndex(mode_idx)

        hold_sec = data.get("hold_duration", 0.05)
        delay_sec = data.get("post_delay", 0.05)
        self.spn_hold.setValue(int(hold_sec * 1000))
        self.spn_delay.setValue(int(delay_sec * 1000))

    def get_step_data(self) -> dict:
        key = self.cmb_key.currentData()
        action = self.cmb_mode.currentData()
        hold_sec = round(self.spn_hold.value() / 1000.0, 3)
        delay_sec = round(self.spn_delay.value() / 1000.0, 3)

        if action == "combo":
            return {
                "action": "combo",
                "keys": [key, "num1"] if key == "num0" else ["num0", key],
                "hold_duration": hold_sec,
                "post_delay": delay_sec
            }
        else:
            return {
                "action": action,
                "key": key,
                "hold_duration": hold_sec,
                "post_delay": delay_sec
            }


class MacroLibraryDialog(QDialog):
    """Dedicated Macro Library Manager & 8-Step Creator Dialog."""
    def __init__(self, profile_manager: ProfileManager, gamepad_listener: GamepadListener = None, parent=None):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.gamepad_listener = gamepad_listener
        self.current_editing_index = -1
        self.recording_gamepad = False
        self.recorded_steps_temp = []
        self.last_press_time = 0

        self.setWindowTitle("📚 Thư Viện Macro & Trình Tạo Tuyệt Chiêu (Tối Đa 8 Phím)")
        self.resize(950, 680)
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
            QLineEdit, QTextBrowser {
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton {
                background-color: #0284C7;
                color: #FFFFFF;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #0369A1;
            }
            QPushButton:disabled {
                background-color: #334155;
                color: #94A3B8;
            }
        """)

        self._init_ui()
        self._load_library_list()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)

        splitter = QSplitter(Qt.Horizontal)

        # -------------------------------------------------------------
        # Left Side: Library List & Action Controls
        # -------------------------------------------------------------
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 8, 0)

        lbl_lib_title = QLabel("📚 Thư Viện Macro Đã Định Nghĩa")
        lbl_lib_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_lib_title.setStyleSheet("color: #38BDF8;")
        left_layout.addWidget(lbl_lib_title)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Tìm kiếm macro trong thư viện...")
        self.txt_search.textChanged.connect(self._filter_library_list)
        left_layout.addWidget(self.txt_search)

        self.lst_library = QListWidget()
        self.lst_library.currentRowChanged.connect(self._on_library_selection_changed)
        left_layout.addWidget(self.lst_library)

        btn_box = QHBoxLayout()
        btn_add_new = QPushButton("➕ Tạo Macro Mới")
        btn_add_new.setStyleSheet("background-color: #10B981; color: #FFFFFF;")
        btn_add_new.clicked.connect(self._on_click_new_macro)

        btn_dup = QPushButton("📋 Nhân bản")
        btn_dup.setStyleSheet("background-color: #3B82F6;")
        btn_dup.clicked.connect(self._on_click_duplicate)

        btn_del = QPushButton("🗑️ Xóa")
        btn_del.setStyleSheet("background-color: #EF4444;")
        btn_del.clicked.connect(self._on_click_delete)

        btn_box.addWidget(btn_add_new)
        btn_box.addWidget(btn_dup)
        btn_box.addWidget(btn_del)
        left_layout.addLayout(btn_box)

        splitter.addWidget(left_widget)

        # -------------------------------------------------------------
        # Right Side: Macro Step Creator (Up to 8 Steps)
        # -------------------------------------------------------------
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(8, 0, 0, 0)

        self.lbl_editor_title = QLabel("✏️ Trình Biên Soạn Tuyệt Chiêu Macro (Tối đa 8 Phím)")
        self.lbl_editor_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.lbl_editor_title.setStyleSheet("color: #F8FAFC;")
        right_layout.addWidget(self.lbl_editor_title)

        form_layout = QFormLayout()
        self.txt_macro_name = QLineEdit()
        self.txt_macro_name.setPlaceholderText("Ví dụ: Sút Lắc Knuckle Shot, Super Cancel...")
        form_layout.addRow("Tên Macro:", self.txt_macro_name)

        self.txt_macro_desc = QLineEdit()
        self.txt_macro_desc.setPlaceholderText("Mô tả tuyệt chiêu hoặc hướng dẫn bấm...")
        form_layout.addRow("Mô tả tuyệt chiêu:", self.txt_macro_desc)
        right_layout.addLayout(form_layout)

        # Live Gamepad Recording Bar
        rec_box = QHBoxLayout()
        self.btn_rec_gamepad = QPushButton("🎮 Ghi phím Live bằng Tay cầm")
        self.btn_rec_gamepad.setStyleSheet("background-color: #8B5CF6; color: #FFFFFF; font-weight: bold;")
        self.btn_rec_gamepad.clicked.connect(self._toggle_gamepad_recording)

        self.lbl_rec_status = QLabel("Trạng thái: Sẵn sàng")
        self.lbl_rec_status.setStyleSheet("color: #94A3B8; font-size: 12px;")

        rec_box.addWidget(self.btn_rec_gamepad)
        rec_box.addWidget(self.lbl_rec_status, stretch=1)
        right_layout.addLayout(rec_box)

        # Scrollable Steps Area (Max 8 Steps)
        lbl_steps_hdr = QLabel("Trình Tự Bước Phím (Max 8 phím):")
        lbl_steps_hdr.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_steps_hdr.setStyleSheet("color: #38BDF8; margin-top: 8px;")
        right_layout.addWidget(lbl_steps_hdr)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: 1px solid #334155; border-radius: 8px; background-color: #0F172A; }")

        self.steps_container = QWidget()
        self.steps_layout = QVBoxLayout(self.steps_container)
        self.steps_layout.setContentsMargins(8, 8, 8, 8)
        self.steps_layout.addStretch()
        self.scroll_area.setWidget(self.steps_container)
        right_layout.addWidget(self.scroll_area)

        # Steps Toolbar
        steps_tool_bar = QHBoxLayout()
        self.btn_add_step = QPushButton("➕ Thêm bước phím (Tối đa 8 phím)")
        self.btn_add_step.setStyleSheet("background-color: #0284C7;")
        self.btn_add_step.clicked.connect(self._on_add_step_clicked)

        btn_clear_steps = QPushButton("🧹 Xóa hết bước")
        btn_clear_steps.setStyleSheet("background-color: #475569;")
        btn_clear_steps.clicked.connect(self._clear_all_step_widgets)

        steps_tool_bar.addWidget(self.btn_add_step)
        steps_tool_bar.addWidget(btn_clear_steps)
        right_layout.addLayout(steps_tool_bar)

        # Save Button
        right_layout.addSpacing(10)
        self.btn_save_macro = QPushButton("💾 Lưu vào Thư Viện Macro")
        self.btn_save_macro.setFixedHeight(42)
        self.btn_save_macro.setStyleSheet("background-color: #10B981; color: #FFFFFF; font-size: 14px; font-weight: bold;")
        self.btn_save_macro.clicked.connect(self._save_current_editing_macro)
        right_layout.addWidget(self.btn_save_macro)

        splitter.addWidget(right_widget)
        splitter.setSizes([320, 630])
        main_layout.addWidget(splitter)

        # Connect Gamepad listener signals if available
        if self.gamepad_listener:
            self.gamepad_listener.button_pressed.connect(self._on_gamepad_button_pressed)

    def _load_library_list(self):
        self.lst_library.clear()
        lib = self.profile_manager.get_macro_library()
        for idx, item in enumerate(lib):
            name = item.get("name", f"Macro #{idx+1}")
            desc = item.get("description", "")
            seq_len = len(item.get("sequence", []))
            
            list_item = QListWidgetItem(f"⚽ {name} ({seq_len} phím)")
            list_item.setData(Qt.UserRole, idx)
            if desc:
                list_item.setToolTip(desc)
            self.lst_library.addItem(list_item)

        if self.lst_library.count() > 0:
            self.lst_library.setCurrentRow(0)
        else:
            self._on_click_new_macro()

    def _filter_library_list(self, text: str):
        query = text.strip().lower()
        for i in range(self.lst_library.count()):
            item = self.lst_library.item(i)
            item.setHidden(query not in item.text().lower())

    def _on_library_selection_changed(self, row: int):
        if row < 0:
            return
        item = self.lst_library.item(row)
        if not item:
            return
        lib_idx = item.data(Qt.UserRole)
        self.current_editing_index = lib_idx

        lib = self.profile_manager.get_macro_library()
        if 0 <= lib_idx < len(lib):
            macro_data = lib[lib_idx]
            self._populate_editor_form(macro_data)

    def _populate_editor_form(self, data: dict):
        self.txt_macro_name.setText(data.get("name", ""))
        self.txt_macro_desc.setText(data.get("description", ""))
        self._clear_all_step_widgets()

        seq = data.get("sequence", [])
        for step in seq:
            if self._get_step_count() < 8:
                self._add_step_widget(step)

    def _clear_all_step_widgets(self):
        while self.steps_layout.count() > 1:
            item = self.steps_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._update_add_step_button_state()

    def _get_step_count(self) -> int:
        return self.steps_layout.count() - 1  # Subtract stretch

    def _add_step_widget(self, step_data: dict = None):
        if self._get_step_count() >= 8:
            QMessageBox.warning(self, "Giới Hạn Bước Phím", "Mỗi Macro tối đa hỗ trợ 8 bước phím!")
            return

        step_num = self._get_step_count() + 1
        widget = StepWidget(step_num, step_data)
        widget.delete_requested.connect(self._on_step_deleted)

        self.steps_layout.insertWidget(self._get_step_count(), widget)
        self._update_add_step_button_state()

    def _on_step_deleted(self, widget: QWidget):
        self.steps_layout.removeWidget(widget)
        widget.deleteLater()
        QTimer.singleShot(50, self._renumber_steps)

    def _renumber_steps(self):
        count = self._get_step_count()
        for i in range(count):
            item = self.steps_layout.itemAt(i)
            if item and item.widget():
                w = item.widget()
                if isinstance(w, StepWidget):
                    w.step_number = i + 1
                    lbl = w.findChild(QLabel)
                    if lbl:
                        lbl.setText(f"Bước {i + 1}:")
        self._update_add_step_button_state()

    def _update_add_step_button_state(self):
        count = self._get_step_count()
        if count >= 8:
            self.btn_add_step.setEnabled(False)
            self.btn_add_step.setText("⛔ Đã đạt giới hạn tối đa 8 phím")
        else:
            self.btn_add_step.setEnabled(True)
            self.btn_add_step.setText(f"➕ Thêm bước phím ({count}/8 phím)")

    def _on_add_step_clicked(self):
        default_step = {"action": "tap", "key": "num2", "hold_duration": 0.05, "post_delay": 0.05}
        self._add_step_widget(default_step)

    def _on_click_new_macro(self):
        self.current_editing_index = -1
        self.txt_macro_name.setText("Macro Tuyệt Chiêu Mới")
        self.txt_macro_desc.setText("Mô tả kỹ thuật macro mới...")
        self._clear_all_step_widgets()
        # Add 2 default steps
        self._add_step_widget({"action": "tap", "key": "num2", "hold_duration": 0.05, "post_delay": 0.05})
        self._add_step_widget({"action": "tap", "key": "numdel", "hold_duration": 0.05, "post_delay": 0.05})

    def _on_click_duplicate(self):
        if self.current_editing_index < 0:
            return
        lib = self.profile_manager.get_macro_library()
        if 0 <= self.current_editing_index < len(lib):
            macro_data = dict(lib[self.current_editing_index])
            macro_data["name"] = f"{macro_data.get('name', 'Macro')} (Bản sao)"
            self.profile_manager.add_macro_to_library(macro_data)
            self._load_library_list()

    def _on_click_delete(self):
        if self.current_editing_index < 0:
            return
        lib = self.profile_manager.get_macro_library()
        if 0 <= self.current_editing_index < len(lib):
            macro_name = lib[self.current_editing_index].get("name", "Macro này")
            reply = QMessageBox.question(
                self, "Xác Nhận Xóa",
                f"Bạn có chắc chắn muốn xóa Macro '{macro_name}' khỏi Thư viện?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.profile_manager.delete_macro_from_library(self.current_editing_index)
                self._load_library_list()

    def _toggle_gamepad_recording(self):
        self.recording_gamepad = not self.recording_gamepad
        if self.recording_gamepad:
            self.btn_rec_gamepad.setText("⏹️ Dừng Ghi Tay Cầm")
            self.btn_rec_gamepad.setStyleSheet("background-color: #EF4444; color: #FFFFFF; font-weight: bold;")
            self.lbl_rec_status.setText("🔴 Đang lắng nghe phím tay cầm thực tế... (Hãy bấm tuyệt chiêu!)")
            self.lbl_rec_status.setStyleSheet("color: #EF4444; font-weight: bold;")
            self._clear_all_step_widgets()
            self.last_press_time = time.time()
        else:
            self.btn_rec_gamepad.setText("🎮 Ghi phím Live bằng Tay cầm")
            self.btn_rec_gamepad.setStyleSheet("background-color: #8B5CF6; color: #FFFFFF; font-weight: bold;")
            self.lbl_rec_status.setText("Trạng thái: Đã dừng ghi tay cầm.")
            self.lbl_rec_status.setStyleSheet("color: #10B981; font-weight: bold;")

    def _on_gamepad_button_pressed(self, device_idx: int, button_idx: int):
        if not self.recording_gamepad:
            return
        if self._get_step_count() >= 8:
            self._toggle_gamepad_recording()
            QMessageBox.information(self, "Hoàn Tất Ghi", "Đã ghi đủ tối đa 8 phím tuyệt chiêu từ tay cầm!")
            return

        now = time.time()
        elapsed = round(now - self.last_press_time, 2) if self.last_press_time > 0 else 0.05
        self.last_press_time = now

        # Map button_idx to standard PES key
        btn_key_map = {
            0: "numdel", # A / Cross
            1: "num3",   # B / Circle
            2: "num2",   # X / Square
            3: "num5",   # Y / Triangle
            4: "rctrl",  # LB / L1
            5: "num0",   # RB / R1
            6: "rshift", # LT / L2
            7: "num1",   # RT / R2
        }
        key_code = btn_key_map.get(button_idx, "num2")
        step_data = {
            "action": "tap",
            "key": key_code,
            "hold_duration": 0.05,
            "post_delay": max(0.04, elapsed)
        }
        self._add_step_widget(step_data)

    def _save_current_editing_macro(self):
        name = self.txt_macro_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Thiếu Thông Tin", "Vui lòng nhập tên cho Macro!")
            return

        steps_count = self._get_step_count()
        if steps_count == 0:
            QMessageBox.warning(self, "Chưa Có Bước Phím", "Macro cần có ít nhất 1 bước phím!")
            return

        sequence = []
        for i in range(steps_count):
            item = self.steps_layout.itemAt(i)
            if item and item.widget():
                w = item.widget()
                if isinstance(w, StepWidget):
                    sequence.append(w.get_step_data())

        macro_data = {
            "name": name,
            "description": self.txt_macro_desc.text().strip(),
            "type": "sequence",
            "sequence": sequence
        }

        if self.current_editing_index >= 0:
            self.profile_manager.update_macro_in_library(self.current_editing_index, macro_data)
        else:
            self.profile_manager.add_macro_to_library(macro_data)

        QMessageBox.information(self, "Lưu Thành Công", f"Đã lưu Macro '{name}' vào Thư viện Macro thành công!")
        self._load_library_list()
