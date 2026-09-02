from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QDoubleSpinBox, QStackedWidget,
    QWidget, QFormLayout, QMessageBox, QListWidget, QListWidgetItem,
    QGroupBox, QTextBrowser
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent, QColor
from core.gamepad_listener import GamepadListener

DPAD_NAMES = {
    "dpad_up": "D-Pad Lên (Up)",
    "dpad_down": "D-Pad Xuống (Down)",
    "dpad_left": "D-Pad Trái (Left)",
    "dpad_right": "D-Pad Phải (Right)"
}

# Xbox Controller button presets mapped to EXACT PES6 Numpad Keyboard Layout (from Settings.exe)
XBOX_PRESETS = [
    {"name": "-- Chọn phím tay cầm Xbox / Flydigi --", "key": "", "macro_name": ""},
    {"name": "🎮 Nút A (Chuyền ngắn / Lấy bóng) ➔ Phím [Num Del]", "key": "numdel", "macro_name": "Nút A (Chuyền ngắn / Lấy bóng)"},
    {"name": "🎮 Nút B (Chuyền dài / Xoạc bóng) ➔ Phím [Num 3]", "key": "num3", "macro_name": "Nút B (Chuyền dài / Xoạc)"},
    {"name": "🎮 Nút X (Sút bóng / Gọi máy hỗ trợ) ➔ Phím [Num 2]", "key": "num2", "macro_name": "Nút X (Sút bóng / Máy hỗ trợ)"},
    {"name": "🎮 Nút Y (Chọc khe / Thủ môn dâng) ➔ Phím [Num 5]", "key": "num5", "macro_name": "Nút Y (Chọc khe / Thủ môn dâng)"},
    {"name": "🎮 Nút LB (Đổi người / Chạy chỗ) ➔ Phím [Right Ctrl]", "key": "rctrl", "macro_name": "Nút LB (Đổi người / Chạy chỗ)"},
    {"name": "🎮 Nút RB (Chạy nhanh - Sprint) ➔ Phím [Num 0]", "key": "num0", "macro_name": "Nút RB (Chạy nhanh)"},
    {"name": "🎮 Nút LT (Chiến thuật - Special) ➔ Phím [Right Shift]", "key": "rshift", "macro_name": "Nút LT (Chiến thuật)"},
    {"name": "🎮 Nút RT (Sút má trong / Kỹ thuật) ➔ Phím [Num 1]", "key": "num1", "macro_name": "Nút RT (Sút má trong)"},
    {"name": "🎮 Nút Start (Tạm dừng) ➔ Phím [G]", "key": "g", "macro_name": "Nút Start (Pause)"},
    {"name": "🎮 Nút Back/Select ➔ Phím [F]", "key": "f", "macro_name": "Nút Select"},
]

# PlayStation 4 & 5 (DualShock 4 / DualSense) Button Presets
PS4_PS5_PRESETS = [
    {"name": "-- Chọn phím tay cầm PS4 / PS5 (DualShock 4 / DualSense) --", "key": "", "macro_name": ""},
    {"name": "🎮 Nút ✕ (Cross - Chuyền ngắn / Lấy bóng) ➔ Phím [Num Del]", "key": "numdel", "macro_name": "Nút ✕ (Chuyền ngắn / Lấy bóng)"},
    {"name": "🎮 Nút ◯ (Circle - Chuyền dài / Xoạc bóng) ➔ Phím [Num 3]", "key": "num3", "macro_name": "Nút ◯ (Chuyền dài / Xoạc)"},
    {"name": "🎮 Nút ▢ (Square - Sút bóng / Máy hỗ trợ) ➔ Phím [Num 2]", "key": "num2", "macro_name": "Nút ▢ (Sút bóng / Máy hỗ trợ)"},
    {"name": "🎮 Nút △ (Triangle - Chọc khe / Thủ môn dâng) ➔ Phím [Num 5]", "key": "num5", "macro_name": "Nút △ (Chọc khe / Thủ môn dâng)"},
    {"name": "🎮 Nút L1 (Đổi người / Chạy chỗ) ➔ Phím [Right Ctrl]", "key": "rctrl", "macro_name": "Nút L1 (Đổi người / Chạy chỗ)"},
    {"name": "🎮 Nút R1 (Chạy nhanh - Sprint) ➔ Phím [Num 0]", "key": "num0", "macro_name": "Nút R1 (Chạy nhanh)"},
    {"name": "🎮 Nút L2 (Chiến thuật - Special) ➔ Phím [Right Shift]", "key": "rshift", "macro_name": "Nút L2 (Chiến thuật)"},
    {"name": "🎮 Nút R2 (Sút má trong / Kỹ thuật) ➔ Phím [Num 1]", "key": "num1", "macro_name": "Nút R2 (Sút má trong)"},
    {"name": "🎮 Nút Options (Tạm dừng) ➔ Phím [G]", "key": "g", "macro_name": "Nút Options (Pause)"},
    {"name": "🎮 Nút Share / Create ➔ Phím [F]", "key": "f", "macro_name": "Nút Share/Create"},
]

# Popular PES Skill Macro Presets (Mapped to PES6 Numpad Layout)
PES_SKILL_PRESETS = [
    {
        "name": "-- ⚽ TẢI MACRO KỸ THUẬT PES6 (Numpad Layout chuẩn) --",
        "macro_name": "",
        "data": None
    },
    {
        "name": "⚽ Sút Lắc Đổi Hướng (Knuckle Shot)",
        "macro_name": "Sút Lắc Đổi Hướng (Knuckle)",
        "data": {
            "name": "Sút Lắc Đổi Hướng (Knuckle)",
            "type": "sequence",
            "sequence": [
                {"action": "tap", "key": "num2", "hold_duration": 0.20, "post_delay": 0.35},
                {"action": "tap", "key": "num2", "hold_duration": 0.05, "post_delay": 0.05}
            ]
        }
    },
    {
        "name": "⚽ Giả Sút Nâng Cao (Tap X ➔ A)",
        "macro_name": "Giả Sút (Tap X ➔ A)",
        "data": {
            "name": "Giả Sút (Tap X ➔ A)",
            "type": "sequence",
            "sequence": [
                {"action": "tap", "key": "num2", "hold_duration": 0.04, "post_delay": 0.04},
                {"action": "tap", "key": "numdel", "hold_duration": 0.05, "post_delay": 0.05}
            ]
        }
    },
    {
        "name": "⚽ Super Cancel Nâng Cao (Tap X ➔ RB+RT)",
        "macro_name": "Super Cancel (Tap X ➔ RB+RT)",
        "data": {
            "name": "Super Cancel (Tap X ➔ RB+RT)",
            "type": "sequence",
            "sequence": [
                {"action": "tap", "key": "num2", "hold_duration": 0.04, "post_delay": 0.04},
                {"action": "combo", "keys": ["num0", "num1"], "hold_duration": 0.15, "post_delay": 0.05}
            ]
        }
    },
    {
        "name": "⚽ Sút Má Trong / Finesse Shot (Hold X 0.35s ➔ RT)",
        "macro_name": "Sút Má Trong (Hold X 0.35s ➔ RT)",
        "data": {
            "name": "Sút Má Trong (Hold X 0.35s ➔ RT)",
            "type": "sequence",
            "sequence": [
                {"action": "tap", "key": "num2", "hold_duration": 0.35, "post_delay": 0.03},
                {"action": "tap", "key": "num1", "hold_duration": 0.15, "post_delay": 0.05}
            ]
        }
    },
    {
        "name": "⚽ Chip Shot Nâng Cao / Tâng Bóng (Tap X ➔ RB)",
        "macro_name": "Chip Shot (Tap X ➔ RB)",
        "data": {
            "name": "Chip Shot (Tap X ➔ RB)",
            "type": "sequence",
            "sequence": [
                {"action": "tap", "key": "num2", "hold_duration": 0.05, "post_delay": 0.04},
                {"action": "tap", "key": "num0", "hold_duration": 0.15, "post_delay": 0.05}
            ]
        }
    },
    {
        "name": "⚽ Bật Tường Nhanh / One-Two Pass (LB + A ➔ Combo Right Ctrl + Num Del)",
        "macro_name": "Bật Tường (One-Two Pass)",
        "data": {
            "name": "Bật Tường (One-Two Pass)",
            "type": "combo",
            "keys": ["rctrl", "numdel"],
            "hold_duration": 0.10
        }
    },
    {
        "name": "⚽ Chọc Khe Bổng / Lofted Through Ball (LB + Y ➔ Combo Right Ctrl + Num 5)",
        "macro_name": "Chọc Khe Bổng (LB+Y)",
        "data": {
            "name": "Chọc Khe Bổng (LB+Y)",
            "type": "combo",
            "keys": ["rctrl", "num5"],
            "hold_duration": 0.22
        }
    }
]

class MacroGuideDialog(QDialog):
    """Independent non-modal floating window guide for Macro Types & PES Power Control."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📖 Hướng Dẫn Chi Tiết Căn Lực & Chọn Loại Macro PES6")
        self.setMinimumSize(660, 520)

        # Set window flags so it displays as an independent non-modal window on top
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setModal(False)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        lbl_title = QLabel("📖 HƯỚNG DẪN CHI TIẾT (Vừa đọc vừa thao tác cài đặt bên dưới)")
        lbl_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #38BDF8;")
        layout.addWidget(lbl_title)

        browser = QTextBrowser()
        browser.setStyleSheet("""
            QTextBrowser {
                background-color: #0F172A;
                border: 1px solid #334155;
                color: #F1F5F9;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                padding: 10px;
            }
        """)
        browser.setHtml("""
        <h3 style="color:#38BDF8; margin-bottom:4px;">1. Phím Đơn (Single Key):</h3>
        <ul>
            <li><b>Giữ phím chủ động (Press & Hold):</b> Khi bạn giữ D-Pad thì máy giữ phím, nhả D-Pad out là nhả phím. Dùng cho phím Di chuyển hoặc Chạy nhanh.</li>
            <li><b>Nhấn Nhả (Tap) + Hold Duration (Căn lực):</b> Máy tự động đè phím trong thời gian <code>Hold Duration</code> chính xác.
                <br/><b>⚡ Căn lực PES:</b>
                <ul>
                    <li><code>0.10s - 0.18s</code>: Chuyền ngắn sệt nhẹ / Sút nhẹ góc hẹp.</li>
                    <li><code>0.20s - 0.35s</code>: Tâng bóng Chip Shot / Sút căn lực 50% thanh lực.</li>
                </ul>
            </li>
            <li><b>Auto Click (Rapid Fire):</b> Tự động nhấp phím liên tục với tốc độ cài đặt (dùng cướp bóng / spam nút).</li>
        </ul>

        <h3 style="color:#34D399; margin-bottom:4px;">2. Tổ Hợp Phím (Combo Keys):</h3>
        <p>Bấm đồng thời 2 hoặc nhiều phím cùng lúc. Chỉnh <code>Hold Duration</code> để giữ tổ hợp phím này trong bao lâu (VD: <code>0.20s</code> để bóng bổng vừa qua đầu thủ môn).</p>
        <p><i>Ví dụ PES:</i> Bấm bóng Chip Shot <code>Right Ctrl + Num 2</code> (LB + Sút).</p>

        <h3 style="color:#FBBF24; margin-bottom:4px;">3. Chuỗi Phím (Sequence):</h3>
        <p>Thực hiện chuỗi kỹ thuật nhiều bước nối tiếp nhau. Bạn có thể nhấp chọn trực tiếp từng bước trong danh sách để điều chỉnh riêng:</p>
        <ul>
            <li><b>⏱️ s Giữ (Hold Duration):</b> Thời gian đè nút để tăng thanh lực cho riêng bước đó.</li>
            <li><b>⏳ s Chờ (Post Delay):</b> Thời gian nghỉ trước khi chuyển sang bước kỹ thuật tiếp theo.</li>
        </ul>
        <p><i>Ví dụ tuyệt chiêu PES6:</i></p>
        <ul>
            <li><b>Giả Sút Nâng Cao (Tap X ➔ A):</b> Bước 1: Sút <code>Num 2</code> (Hold <code>0.04s</code>, Delay <code>0.04s</code>) ➔ Bước 2: Hủy <code>Num Del</code> (Hold <code>0.05s</code>).</li>
            <li><b>Sút Má Trong Finesse (Hold X 0.35s ➔ RT):</b> Bước 1: Sút <code>Num 2</code> (Hold <code>0.35s</code> lấy 50% thanh lực) ➔ Bước 2: Kỹ thuật <code>Num 1</code> (Hold <code>0.15s</code>).</li>
            <li><b>Sút Lắc Đổi Hướng (Knuckle Shot):</b> Bước 1: Sút <code>Num 2</code> (Hold <code>0.20s</code>, Delay <code>0.35s</code> chạy đà) ➔ Bước 2: Sút <code>Num 2</code> (Hold <code>0.05s</code> lắc bóng).</li>
        </ul>

        <h3 style="color:#F472B6; margin-bottom:4px;">4. Bảng Ký Hiệu Phím Tay Cầm:</h3>
        <table border="1" cellspacing="0" cellpadding="5" style="border-color:#334155; color:#F8FAFC; width:100%;">
            <tr style="background-color:#1E293B;">
                <th>Chức năng PES6</th><th>Tay cầm Xbox / Flydigi</th><th>Tay cầm PS4 / PS5</th><th>Phím Bàn Phím (PES6 Numpad)</th>
            </tr>
            <tr><td>Sút bóng</td><td>Nút X</td><td>Nút ▢ (Square)</td><td><code>Num 2</code></td></tr>
            <tr><td>Chuyền ngắn / Hủy</td><td>Nút A</td><td>Nút ✕ (Cross)</td><td><code>Num Del</code></td></tr>
            <tr><td>Chuyền dài / Xoạc</td><td>Nút B</td><td>Nút ◯ (Circle)</td><td><code>Num 3</code></td></tr>
            <tr><td>Chọc khe</td><td>Nút Y</td><td>Nút △ (Triangle)</td><td><code>Num 5</code></td></tr>
            <tr><td>Đổi người / L1</td><td>Nút LB</td><td>Nút L1</td><td><code>Right Ctrl</code></td></tr>
            <tr><td>Chạy nhanh / R1</td><td>Nút RB</td><td>Nút R1</td><td><code>Num 0</code></td></tr>
            <tr><td>Chiến thuật / L2</td><td>Nút LT</td><td>Nút L2</td><td><code>Right Shift</code></td></tr>
            <tr><td>Sút xoáy / R2</td><td>Nút RT</td><td>Nút R2</td><td><code>Num 1</code></td></tr>
        </table>
        """)
        layout.addWidget(browser)

        btn_box = QHBoxLayout()
        btn_close = QPushButton("📌 Đóng cửa sổ hướng dẫn")
        btn_close.clicked.connect(self.close)
        btn_box.addStretch()
        btn_box.addWidget(btn_close)
        layout.addLayout(btn_box)

class KeyRecorderLineEdit(QLineEdit):
    """QLineEdit that records keyboard keys or custom input."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Bấm phím bàn phím hoặc chọn phím bên dưới...")
        self.setReadOnly(True)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        text = event.text()

        key_name = self._qt_key_to_str(key, text)
        if key_name:
            self.setText(key_name)
        event.accept()

    def _qt_key_to_str(self, key: int, text: str) -> str:
        special_keys = {
            Qt.Key_Space: "space",
            Qt.Key_Return: "enter",
            Qt.Key_Enter: "enter",
            Qt.Key_Escape: "escape",
            Qt.Key_Backspace: "backspace",
            Qt.Key_Tab: "tab",
            Qt.Key_Shift: "rshift",
            Qt.Key_Control: "rctrl",
            Qt.Key_Alt: "lalt",
            Qt.Key_Up: "up",
            Qt.Key_Down: "down",
            Qt.Key_Left: "left",
            Qt.Key_Right: "right",
            Qt.Key_F1: "f1", Qt.Key_F2: "f2", Qt.Key_F3: "f3", Qt.Key_F4: "f4",
            Qt.Key_F5: "f5", Qt.Key_F6: "f6", Qt.Key_F7: "f7", Qt.Key_F8: "f8",
            Qt.Key_F9: "f9", Qt.Key_F10: "f10", Qt.Key_F11: "f11", Qt.Key_F12: "f12",
        }
        if key in special_keys:
            return special_keys[key]
        if text and text.isalnum():
            return text.lower()
        return ""

class MacroEditorDialog(QDialog):
    def __init__(self, player_id: int, dpad_dir: str, current_mapping: dict, gamepad_listener: GamepadListener = None, parent=None):
        super().__init__(parent)
        self.player_id = player_id
        self.dpad_dir = dpad_dir
        self.mapping = current_mapping or {}
        self.gamepad_listener = gamepad_listener
        self.is_recording_gamepad = False
        self._block_seq_signals = False
        self.guide_window = None
        
        self.setWindowTitle(f"Player {player_id} - Chỉnh sửa Macro {DPAD_NAMES.get(dpad_dir, dpad_dir)}")
        self.setMinimumWidth(640)
        self._init_ui()
        self._load_current_mapping()
        self._connect_gamepad()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Header Title
        lbl_title = QLabel(f"⚙️ Player {self.player_id}: Gán Macro cho nút {DPAD_NAMES.get(self.dpad_dir, self.dpad_dir)}")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #38BDF8;")
        layout.addWidget(lbl_title)

        # Custom Macro Name Field
        form_name = QFormLayout()
        self.txt_macro_name = QLineEdit()
        self.txt_macro_name.setPlaceholderText("VD: Giả Sút, Super Cancel, Chip Shot, Auto Sút...")
        form_name.addRow("🏷️ Tên gợi nhớ Macro:", self.txt_macro_name)
        layout.addLayout(form_name)

        # Open Separate Non-Modal Guide Window Button
        btn_open_guide = QPushButton("📖 Mở Cửa Sổ Hướng Dẫn Chi Tiết (Mở song song vừa đọc vừa cài)")
        btn_open_guide.setObjectName("btn_secondary")
        btn_open_guide.clicked.connect(self._show_guide_window)
        layout.addWidget(btn_open_guide)

        # PES Skill Preset Selector Bar
        group_pes = QGroupBox("⚽ Thư viện Macro Kỹ Thuật PES6 (Numpad Layout chuẩn Settings.exe):")
        group_pes.setStyleSheet("QGroupBox { font-weight: bold; color: #34D399; border: 1px solid #10B981; border-radius: 6px; margin-top: 4px; padding-top: 8px; }")
        pes_layout = QVBoxLayout(group_pes)

        self.combo_pes_preset = QComboBox()
        for p in PES_SKILL_PRESETS:
            self.combo_pes_preset.addItem(p["name"], p)
        self.combo_pes_preset.currentIndexChanged.connect(self._on_pes_preset_selected)
        pes_layout.addWidget(self.combo_pes_preset)
        layout.addWidget(group_pes)

        # Macro Type Selection
        form = QFormLayout()
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Phím Đơn / Nút Tay Cầm", "Tổ hợp phím (Combo Keys)", "Chuỗi phím (Sequence)"])
        self.combo_type.currentIndexChanged.connect(self._on_type_changed)
        form.addRow("Loại Macro:", self.combo_type)
        layout.addLayout(form)

        # Stacked Pages for Types
        self.stacked_pages = QStackedWidget()

        # -------------------------------------------------------------
        # Page 1: Single Key / Xbox Gamepad Button
        # -------------------------------------------------------------
        page_single = QWidget()
        layout_single = QVBoxLayout(page_single)
        layout_single.setSpacing(10)

        group_xbox = QGroupBox("🎮 Chọn phím từ Tay cầm Xbox / PS4 / PS5 / PES6:")
        group_xbox.setStyleSheet("QGroupBox { font-weight: bold; color: #38BDF8; border: 1px solid #334155; border-radius: 6px; margin-top: 4px; padding-top: 8px; }")
        xbox_layout = QVBoxLayout(group_xbox)

        xbox_layout.addWidget(QLabel("🎮 Tay cầm Xbox / Flydigi:"))
        self.combo_xbox_preset = QComboBox()
        for item in XBOX_PRESETS:
            self.combo_xbox_preset.addItem(item["name"], item)
        self.combo_xbox_preset.currentIndexChanged.connect(self._on_xbox_preset_selected)
        xbox_layout.addWidget(self.combo_xbox_preset)

        xbox_layout.addWidget(QLabel("🎮 Tay cầm PlayStation 4 & 5 (DualShock 4 / DualSense):"))
        self.combo_ps_preset = QComboBox()
        for item in PS4_PS5_PRESETS:
            self.combo_ps_preset.addItem(item["name"], item)
        self.combo_ps_preset.currentIndexChanged.connect(self._on_ps_preset_selected)
        xbox_layout.addWidget(self.combo_ps_preset)

        self.btn_rec_gamepad = QPushButton("📡 Bấm nút trên tay cầm P" + str(self.player_id) + " để đọc...")
        self.btn_rec_gamepad.setObjectName("btn_secondary")
        self.btn_rec_gamepad.setCheckable(True)
        self.btn_rec_gamepad.clicked.connect(self._toggle_gamepad_recording)
        xbox_layout.addWidget(self.btn_rec_gamepad)
        layout_single.addWidget(group_xbox)

        form_single = QFormLayout()
        self.rec_key = KeyRecorderLineEdit()
        form_single.addRow("Mã phím gán:", self.rec_key)

        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["Giữ phím chủ động (Press & Hold)", "Nhấn nhả theo thời gian (Tap)", "Auto Click (Rapid Fire)"])
        self.combo_mode.currentIndexChanged.connect(self._on_mode_changed)
        form_single.addRow("Chế độ kích hoạt:", self.combo_mode)

        # Single Key Hold Duration (for Tap Mode)
        self.spin_single_hold = QDoubleSpinBox()
        self.spin_single_hold.setRange(0.02, 3.0)
        self.spin_single_hold.setSingleStep(0.05)
        self.spin_single_hold.setValue(0.15)
        self.spin_single_hold.setSuffix(" giây")
        self.lbl_single_hold = QLabel("⏱️ Thời gian giữ phím (Căn lực):")
        form_single.addRow(self.lbl_single_hold, self.spin_single_hold)

        # Rapid Fire Interval
        self.spin_rapid = QDoubleSpinBox()
        self.spin_rapid.setRange(0.02, 2.0)
        self.spin_rapid.setSingleStep(0.05)
        self.spin_rapid.setValue(0.10)
        self.spin_rapid.setSuffix(" giây")
        self.lbl_rapid = QLabel("Tốc độ Auto Click:")
        form_single.addRow(self.lbl_rapid, self.spin_rapid)

        layout_single.addLayout(form_single)
        self.stacked_pages.addWidget(page_single)

        # -------------------------------------------------------------
        # Page 2: Combo Keys (Tổ hợp phím)
        # -------------------------------------------------------------
        page_combo = QWidget()
        layout_combo = QVBoxLayout(page_combo)
        layout_combo.setSpacing(10)

        group_combo_gp = QGroupBox("🎮 Chọn nhanh phím PES6 Numpad cho Combo P" + str(self.player_id) + ":")
        group_combo_gp.setStyleSheet("QGroupBox { font-weight: bold; color: #38BDF8; border: 1px solid #334155; border-radius: 6px; margin-top: 4px; padding-top: 8px; }")
        combo_gp_layout = QVBoxLayout(group_combo_gp)

        self.btn_rec_combo = QPushButton("📡 Bấm phím trên tay cầm để tạo Combo...")
        self.btn_rec_combo.setObjectName("btn_secondary")
        self.btn_rec_combo.setCheckable(True)
        self.btn_rec_combo.clicked.connect(self._toggle_gamepad_recording_combo)
        combo_gp_layout.addWidget(self.btn_rec_combo)

        # Quick Xbox buttons add bar (Numpad Layout)
        quick_btn_box = QHBoxLayout()
        quick_btn_box.setSpacing(4)
        for label, k in [("Nút A (NumDel)", "numdel"), ("Nút B (Num3)", "num3"), ("Nút X (Num2)", "num2"), ("Nút Y (Num5)", "num5"), ("LB (RCtrl)", "rctrl"), ("RB (Num0)", "num0"), ("RT (Num1)", "num1")]:
            b = QPushButton(label)
            b.setObjectName("btn_secondary")
            b.setFixedHeight(28)
            b.clicked.connect(lambda _, key=k: self._add_key_to_combo(key))
            quick_btn_box.addWidget(b)
        combo_gp_layout.addLayout(quick_btn_box)

        layout_combo.addWidget(group_combo_gp)

        form_combo = QFormLayout()
        self.txt_combo = QLineEdit()
        self.txt_combo.setPlaceholderText("VD: rctrl+num2 (LB+Sút)")
        form_combo.addRow("Tổ hợp phím (+):", self.txt_combo)

        self.spin_combo_hold = QDoubleSpinBox()
        self.spin_combo_hold.setRange(0.02, 3.0)
        self.spin_combo_hold.setSingleStep(0.05)
        self.spin_combo_hold.setValue(0.15)
        self.spin_combo_hold.setSuffix(" giây")
        form_combo.addRow("⏱️ Thời gian giữ Combo (Căn lực):", self.spin_combo_hold)

        layout_combo.addLayout(form_combo)
        self.stacked_pages.addWidget(page_combo)

        # -------------------------------------------------------------
        # Page 3: Sequence (Chuỗi phím với Tính Năng Chỉnh Thời Gian Trực Tiếp)
        # -------------------------------------------------------------
        page_seq = QWidget()
        layout_seq = QVBoxLayout(page_seq)
        layout_seq.setSpacing(8)

        group_seq_gp = QGroupBox("🎮 Thêm phím vào Chuỗi bằng Tay Cầm P" + str(self.player_id) + ":")
        group_seq_gp.setStyleSheet("QGroupBox { font-weight: bold; color: #38BDF8; border: 1px solid #334155; border-radius: 6px; margin-top: 4px; padding-top: 8px; }")
        seq_gp_layout = QVBoxLayout(group_seq_gp)

        self.btn_rec_seq = QPushButton("📡 Bấm nút trên tay cầm để THÊM PHÍM vào chuỗi...")
        self.btn_rec_seq.setObjectName("btn_secondary")
        self.btn_rec_seq.setCheckable(True)
        self.btn_rec_seq.clicked.connect(self._toggle_gamepad_recording_seq)
        seq_gp_layout.addWidget(self.btn_rec_seq)
        layout_seq.addWidget(group_seq_gp)

        lbl_seq_hint = QLabel("Danh sách phím theo thứ tự (Nhấp vào dòng để chỉnh sửa trực tiếp thời gian Giữ/Chờ):")
        lbl_seq_hint.setStyleSheet("color: #38BDF8; font-weight: bold;")
        layout_seq.addWidget(lbl_seq_hint)
        
        self.list_seq = QListWidget()
        self.list_seq.setStyleSheet("""
            QListWidget {
                background-color: #0F172A;
                border: 1px solid #334155;
                border-radius: 6px;
                color: #F8FAFC;
            }
            QListWidget::item {
                background-color: #1E293B;
                color: #F8FAFC;
                padding: 6px 10px;
                margin-bottom: 4px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #0284C7;
                color: #FFFFFF;
                font-weight: bold;
            }
        """)
        self.list_seq.currentItemChanged.connect(self._on_seq_item_selected)
        layout_seq.addWidget(self.list_seq)

        # Sequence Editing Toolbar
        btn_seq_box = QHBoxLayout()
        self.txt_seq_key = QLineEdit()
        self.txt_seq_key.setPlaceholderText("Mã phím (num2, numdel...)")
        self.txt_seq_key.textChanged.connect(self._on_seq_spin_value_changed)

        self.spin_seq_hold = QDoubleSpinBox()
        self.spin_seq_hold.setRange(0.01, 3.0)
        self.spin_seq_hold.setSingleStep(0.01)
        self.spin_seq_hold.setValue(0.05)
        self.spin_seq_hold.setSuffix("s Giữ")
        self.spin_seq_hold.setToolTip("Thời gian giữ phím này để lấy lực sút/chuyền trong bước")
        self.spin_seq_hold.valueChanged.connect(self._on_seq_spin_value_changed)

        self.spin_seq_delay = QDoubleSpinBox()
        self.spin_seq_delay.setRange(0.01, 5.0)
        self.spin_seq_delay.setSingleStep(0.01)
        self.spin_seq_delay.setValue(0.05)
        self.spin_seq_delay.setSuffix("s Chờ")
        self.spin_seq_delay.setToolTip("Thời gian chờ trước khi sang bước tiếp theo")
        self.spin_seq_delay.valueChanged.connect(self._on_seq_spin_value_changed)

        btn_add_seq = QPushButton("+ Thêm")
        btn_add_seq.setObjectName("btn_secondary")
        btn_add_seq.clicked.connect(self._add_seq_step)

        btn_update_seq = QPushButton("✏️ Cập nhật")
        btn_update_seq.clicked.connect(self._update_selected_seq_step)

        btn_up_seq = QPushButton("⬆️")
        btn_up_seq.setObjectName("btn_secondary")
        btn_up_seq.setFixedWidth(36)
        btn_up_seq.setToolTip("Di chuyển bước chọn LÊN")
        btn_up_seq.clicked.connect(self._move_seq_up)

        btn_down_seq = QPushButton("⬇️")
        btn_down_seq.setObjectName("btn_secondary")
        btn_down_seq.setFixedWidth(36)
        btn_down_seq.setToolTip("Di chuyển bước chọn XUỐNG")
        btn_down_seq.clicked.connect(self._move_seq_down)

        btn_del_seq = QPushButton("🗑️ Xóa")
        btn_del_seq.setObjectName("btn_danger")
        btn_del_seq.clicked.connect(self._del_seq_step)

        btn_seq_box.addWidget(self.txt_seq_key)
        btn_seq_box.addWidget(self.spin_seq_hold)
        btn_seq_box.addWidget(self.spin_seq_delay)
        btn_seq_box.addWidget(btn_add_seq)
        btn_seq_box.addWidget(btn_update_seq)
        btn_seq_box.addWidget(btn_up_seq)
        btn_seq_box.addWidget(btn_down_seq)
        btn_seq_box.addWidget(btn_del_seq)
        layout_seq.addLayout(btn_seq_box)

        self.stacked_pages.addWidget(page_seq)

        layout.addWidget(self.stacked_pages)

        # Dialog Action Buttons
        btn_box = QHBoxLayout()
        btn_save = QPushButton("💾 Lưu cấu hình")
        btn_save.clicked.connect(self._save_and_close)
        btn_cancel = QPushButton("Hủy")
        btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)

        btn_box.addStretch()
        btn_box.addWidget(btn_save)
        btn_box.addWidget(btn_cancel)
        layout.addLayout(btn_box)

    def _show_guide_window(self):
        if self.guide_window is None or not self.guide_window.isVisible():
            self.guide_window = MacroGuideDialog(self)
            self.guide_window.show()
        else:
            self.guide_window.raise_()
            self.guide_window.activateWindow()

    def _connect_gamepad(self):
        if self.gamepad_listener:
            self.gamepad_listener.button_pressed.connect(self._on_gamepad_button_pressed)

    def disconnect_gamepad(self):
        if self.guide_window and self.guide_window.isVisible():
            self.guide_window.close()
        if self.gamepad_listener:
            try:
                self.gamepad_listener.button_pressed.disconnect(self._on_gamepad_button_pressed)
            except Exception:
                pass

    def _on_pes_preset_selected(self, index: int):
        preset_info = self.combo_pes_preset.currentData()
        if not preset_info or not preset_info.get("data"):
            return
        data = preset_info["data"]
        macro_name = preset_info.get("macro_name", "")
        if macro_name:
            self.txt_macro_name.setText(macro_name)
        self.mapping = data
        self._load_current_mapping()

    def _on_xbox_preset_selected(self, index: int):
        preset_info = self.combo_xbox_preset.currentData()
        if not preset_info:
            return
        key = preset_info.get("key", "")
        macro_name = preset_info.get("macro_name", "")
        if key:
            self.rec_key.setText(key)
        if macro_name and not self.txt_macro_name.text().strip():
            self.txt_macro_name.setText(macro_name)

    def _on_ps_preset_selected(self, index: int):
        preset_info = self.combo_ps_preset.currentData()
        if not preset_info:
            return
        key = preset_info.get("key", "")
        macro_name = preset_info.get("macro_name", "")
        if key:
            self.rec_key.setText(key)
        if macro_name and not self.txt_macro_name.text().strip():
            self.txt_macro_name.setText(macro_name)

    def _add_key_to_combo(self, key: str):
        curr = self.txt_combo.text().strip()
        if not curr:
            self.txt_combo.setText(key)
        else:
            keys = [k.strip() for k in curr.split("+") if k.strip()]
            if key not in keys:
                keys.append(key)
            self.txt_combo.setText("+".join(keys))

    def _toggle_gamepad_recording(self):
        self.is_recording_gamepad = self.btn_rec_gamepad.isChecked()
        if self.is_recording_gamepad:
            self.btn_rec_gamepad.setText("🟡 Hãy BẤM NÚT BẤT KỲ trên tay cầm...")
            self.btn_rec_gamepad.setStyleSheet("background-color: #EAB308; color: #000000; font-weight: bold;")
        else:
            self.btn_rec_gamepad.setText("📡 Bấm nút trên tay cầm Xbox để đọc...")
            self.btn_rec_gamepad.setStyleSheet("")

    def _toggle_gamepad_recording_combo(self):
        self.is_recording_gamepad_combo = self.btn_rec_combo.isChecked()
        if self.is_recording_gamepad_combo:
            self.btn_rec_combo.setText("🟡 Hãy BẤM CÁC NÚT trên tay cầm...")
            self.btn_rec_combo.setStyleSheet("background-color: #EAB308; color: #000000; font-weight: bold;")
        else:
            self.btn_rec_combo.setText("📡 Bấm các nút trên tay cầm để tự tạo Combo...")
            self.btn_rec_combo.setStyleSheet("")

    def _toggle_gamepad_recording_seq(self):
        self.is_recording_gamepad_seq = self.btn_rec_seq.isChecked()
        if self.is_recording_gamepad_seq:
            self.btn_rec_seq.setText("🟡 Hãy BẤM NÚT trên tay cầm để THÊM...")
            self.btn_rec_seq.setStyleSheet("background-color: #EAB308; color: #000000; font-weight: bold;")
        else:
            self.btn_rec_seq.setText("📡 Bấm nút trên tay cầm để THÊM PHÍM vào chuỗi...")
            self.btn_rec_seq.setStyleSheet("")

    def _on_gamepad_button_pressed(self, joy_idx: int, btn_id: str, friendly_name: str, default_key: str):
        pes_key_map = {
            'btn_a': 'numdel',
            'btn_b': 'num3',
            'btn_x': 'num2',
            'btn_y': 'num5',
            'btn_lb': 'rctrl',
            'btn_rb': 'num0',
            'btn_lt': 'rshift',
            'btn_rt': 'num1',
            'btn_select': 'f',
            'btn_start': 'g',
        }
        target_key = pes_key_map.get(btn_id, default_key)

        # 1. Single Key Mode
        if getattr(self, "is_recording_gamepad", False):
            self.rec_key.setText(target_key)
            if not self.txt_macro_name.text().strip():
                self.txt_macro_name.setText(friendly_name)
            self.btn_rec_gamepad.setChecked(False)
            self.btn_rec_gamepad.setText(f"✅ Đã chọn: {friendly_name}")
            self.btn_rec_gamepad.setStyleSheet("background-color: #10B981; color: #FFFFFF; font-weight: bold;")
            self.is_recording_gamepad = False

        # 2. Combo Keys Mode
        elif getattr(self, "is_recording_gamepad_combo", False):
            self._add_key_to_combo(target_key)
            self.btn_rec_combo.setText(f"✅ Đã thêm: {friendly_name} (Bấm tiếp hoặc tắt)")
            self.btn_rec_combo.setStyleSheet("background-color: #10B981; color: #FFFFFF; font-weight: bold;")

        # 3. Sequence Mode
        elif getattr(self, "is_recording_gamepad_seq", False):
            hold_d = self.spin_seq_hold.value()
            delay_d = self.spin_seq_delay.value()
            item = QListWidgetItem(f"🔑 Nhấn phím: '{target_key.upper()}'  ⏱️ (Giữ: {hold_d}s)  ⏳ (Chờ: {delay_d}s)")
            item.setData(Qt.UserRole, {"action": "tap", "key": target_key, "hold_duration": hold_d, "post_delay": delay_d})
            self.list_seq.addItem(item)
            self.btn_rec_seq.setText(f"✅ Đã thêm vào chuỗi: {friendly_name}")
            self.btn_rec_seq.setStyleSheet("background-color: #10B981; color: #FFFFFF; font-weight: bold;")

    def _on_type_changed(self, index: int):
        self.stacked_pages.setCurrentIndex(index)

    def _on_mode_changed(self, index: int):
        is_tap = (index == 1)
        is_rapid = (index == 2)
        
        self.lbl_single_hold.setVisible(is_tap)
        self.spin_single_hold.setVisible(is_tap)
        
        self.lbl_rapid.setVisible(is_rapid)
        self.spin_rapid.setVisible(is_rapid)

    def _on_seq_item_selected(self, current: QListWidgetItem, previous: QListWidgetItem):
        if not current:
            return
        step_data = current.data(Qt.UserRole)
        if not step_data:
            return
        
        self._block_seq_signals = True
        key = step_data.get('key', '')
        hold = step_data.get('hold_duration', step_data.get('delay', 0.05))
        delay = step_data.get('post_delay', 0.05)

        self.txt_seq_key.setText(key)
        self.spin_seq_hold.setValue(hold)
        self.spin_seq_delay.setValue(delay)
        self._block_seq_signals = False

    def _on_seq_spin_value_changed(self):
        if getattr(self, "_block_seq_signals", False):
            return
        curr_item = self.list_seq.currentItem()
        if not curr_item:
            return
        key = self.txt_seq_key.text().strip().lower()
        if not key:
            return
        hold = self.spin_seq_hold.value()
        delay = self.spin_seq_delay.value()
        step_data = curr_item.data(Qt.UserRole) or {}
        step_data["key"] = key
        step_data["hold_duration"] = hold
        step_data["post_delay"] = delay

        curr_item.setData(Qt.UserRole, step_data)
        curr_item.setText(f"🔑 Nhấn phím: '{key.upper()}'  ⏱️ (Giữ: {hold}s)  ⏳ (Chờ: {delay}s)")

    def _update_selected_seq_step(self):
        curr_item = self.list_seq.currentItem()
        if not curr_item:
            QMessageBox.information(self, "Thông báo", "Vui lòng nhấp chọn một bước trong danh sách để cập nhật!")
            return
        key = self.txt_seq_key.text().strip().lower()
        if not key:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập mã phím!")
            return

        hold = self.spin_seq_hold.value()
        delay = self.spin_seq_delay.value()
        step_data = curr_item.data(Qt.UserRole) or {}
        step_data["key"] = key
        step_data["hold_duration"] = hold
        step_data["post_delay"] = delay

        curr_item.setData(Qt.UserRole, step_data)
        curr_item.setText(f"🔑 Nhấn phím: '{key.upper()}'  ⏱️ (Giữ: {hold}s)  ⏳ (Chờ: {delay}s)")

    def _move_seq_up(self):
        row = self.list_seq.currentRow()
        if row > 0:
            item = self.list_seq.takeItem(row)
            self.list_seq.insertItem(row - 1, item)
            self.list_seq.setCurrentRow(row - 1)

    def _move_seq_down(self):
        row = self.list_seq.currentRow()
        if 0 <= row < self.list_seq.count() - 1:
            item = self.list_seq.takeItem(row)
            self.list_seq.insertItem(row + 1, item)
            self.list_seq.setCurrentRow(row + 1)

    def _add_seq_step(self):
        key = self.txt_seq_key.text().strip().lower()
        if not key:
            return
        hold_d = self.spin_seq_hold.value()
        delay_d = self.spin_seq_delay.value()
        
        item = QListWidgetItem(f"🔑 Nhấn phím: '{key.upper()}'  ⏱️ (Giữ: {hold_d}s)  ⏳ (Chờ: {delay_d}s)")
        item.setData(Qt.UserRole, {"action": "tap", "key": key, "hold_duration": hold_d, "post_delay": delay_d})
        self.list_seq.addItem(item)
        self.txt_seq_key.clear()

    def _del_seq_step(self):
        curr = self.list_seq.currentRow()
        if curr >= 0:
            self.list_seq.takeItem(curr)

    def _load_current_mapping(self):
        macro_name = self.mapping.get("name", "")
        if macro_name:
            self.txt_macro_name.setText(macro_name)

        macro_type = self.mapping.get("type", "single")
        if macro_type == "single":
            self.combo_type.setCurrentIndex(0)
            key = self.mapping.get("key", "")
            self.rec_key.setText(key)
            
            for idx in range(self.combo_xbox_preset.count()):
                preset_data = self.combo_xbox_preset.itemData(idx)
                if preset_data and preset_data.get("key") == key:
                    self.combo_xbox_preset.setCurrentIndex(idx)
                    break

            mode = self.mapping.get("mode", "press_hold")
            if mode == "press_hold":
                self.combo_mode.setCurrentIndex(0)
            elif mode == "tap":
                self.combo_mode.setCurrentIndex(1)
            elif mode == "rapid_fire":
                self.combo_mode.setCurrentIndex(2)

            self.spin_single_hold.setValue(self.mapping.get("hold_duration", 0.15))
            self.spin_rapid.setValue(self.mapping.get("rapid_interval", 0.10))
            self._on_mode_changed(self.combo_mode.currentIndex())

        elif macro_type == "combo":
            self.combo_type.setCurrentIndex(1)
            keys = self.mapping.get("keys", [])
            self.txt_combo.setText("+".join(keys))
            self.spin_combo_hold.setValue(self.mapping.get("hold_duration", 0.15))

        elif macro_type == "sequence":
            self.combo_type.setCurrentIndex(2)
            self.list_seq.clear()
            seq = self.mapping.get("sequence", [])
            for step in seq:
                key = step.get("key", "")
                hold_d = step.get("hold_duration", step.get("delay", 0.05))
                delay_d = step.get("post_delay", 0.05)
                item = QListWidgetItem(f"🔑 Nhấn phím: '{key.upper()}'  ⏱️ (Giữ: {hold_d}s)  ⏳ (Chờ: {delay_d}s)")
                item.setData(Qt.UserRole, step)
                self.list_seq.addItem(item)

    def _save_and_close(self):
        custom_name = self.txt_macro_name.text().strip()
        idx = self.combo_type.currentIndex()

        if idx == 0:
            key = self.rec_key.text().strip().lower()
            if not key:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn nút tay cầm hoặc nhập phím gán!")
                return
            mode_map = {0: "press_hold", 1: "tap", 2: "rapid_fire"}
            self.result_mapping = {
                "name": custom_name or f"Phím [{key.upper()}]",
                "type": "single",
                "key": key,
                "mode": mode_map.get(self.combo_mode.currentIndex(), "press_hold"),
                "hold_duration": self.spin_single_hold.value(),
                "rapid_interval": self.spin_rapid.value()
            }
        elif idx == 1:
            raw_combo = self.txt_combo.text().strip()
            if not raw_combo:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập tổ hợp phím!")
                return
            keys = [k.strip().lower() for k in raw_combo.split("+") if k.strip()]
            self.result_mapping = {
                "name": custom_name or f"Combo [{'+'.join(keys).upper()}]",
                "type": "combo",
                "keys": keys,
                "hold_duration": self.spin_combo_hold.value()
            }
        elif idx == 2:
            seq = []
            for i in range(self.list_seq.count()):
                item = self.list_seq.item(i)
                seq.append(item.data(Qt.UserRole))
            if not seq:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng thêm ít nhất 1 phím vào chuỗi!")
                return
            self.result_mapping = {
                "name": custom_name or f"Chuỗi ({len(seq)} bước)",
                "type": "sequence",
                "sequence": seq
            }

        self.disconnect_gamepad()
        self.accept()

    def closeEvent(self, event):
        self.disconnect_gamepad()
        super().closeEvent(event)

    def get_result(self) -> dict:
        return getattr(self, "result_mapping", {})
