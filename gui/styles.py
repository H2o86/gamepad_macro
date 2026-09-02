DARK_STYLESHEET = """
QMainWindow, QDialog {
    background-color: #121824;
    color: #E2E8F0;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QWidget {
    color: #E2E8F0;
    font-size: 13px;
}

/* Header & Cards */
QFrame#card {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 12px;
}

QFrame#status_connected {
    background-color: rgba(16, 185, 129, 0.15);
    border: 1px solid #10B981;
    border-radius: 8px;
}

QFrame#status_disconnected {
    background-color: rgba(239, 68, 68, 0.15);
    border: 1px solid #EF4444;
    border-radius: 8px;
}

QLabel#title {
    font-size: 18px;
    font-weight: bold;
    color: #38BDF8;
}

QLabel#subtitle {
    font-size: 12px;
    color: #94A3B8;
}

QLabel#status_text_conn {
    color: #34D399;
    font-weight: bold;
}

QLabel#status_text_disconn {
    color: #F87171;
    font-weight: bold;
}

/* Buttons */
QPushButton {
    background-color: #0EA5E9;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #0284C7;
}

QPushButton:pressed {
    background-color: #0369A1;
}

QPushButton#btn_secondary {
    background-color: #334155;
    color: #F1F5F9;
}

QPushButton#btn_secondary:hover {
    background-color: #475569;
}

QPushButton#btn_danger {
    background-color: #DC2626;
    color: #FFFFFF;
}

QPushButton#btn_danger:hover {
    background-color: #B91C1C;
}

QPushButton#btn_dpad {
    background-color: #1E293B;
    border: 2px solid #38BDF8;
    border-radius: 8px;
    padding: 10px;
    text-align: center;
}

QPushButton#btn_dpad:hover {
    background-color: #334155;
    border-color: #0EA5E9;
}

QPushButton#btn_dpad_active {
    background-color: #0284C7;
    border: 2px solid #38BDF8;
    color: #FFFFFF;
}

/* Input, ComboBox, Lists */
QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox, QListWidget, QListView, QTextEdit {
    background-color: #0F172A;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 10px;
    color: #F8FAFC;
    selection-background-color: #0284C7;
    selection-color: #FFFFFF;
}

QListWidget::item {
    background-color: #0F172A;
    color: #F8FAFC;
    padding: 8px;
    border-bottom: 1px solid #1E293B;
    border-radius: 4px;
}

QListWidget::item:hover {
    background-color: #1E293B;
    color: #38BDF8;
}

QListWidget::item:selected {
    background-color: #0284C7;
    color: #FFFFFF;
    font-weight: bold;
}

QComboBox:hover, QLineEdit:hover, QListWidget:hover {
    border-color: #38BDF8;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #1E293B;
    color: #F8FAFC;
    selection-background-color: #0284C7;
    selection-color: #FFFFFF;
    border: 1px solid #334155;
}

/* Menus (Backup/Restore Popup & Tray Menu) */
QMenu {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 6px;
    color: #F8FAFC;
    padding: 6px;
}

QMenu::item {
    background-color: transparent;
    color: #F8FAFC;
    padding: 8px 24px 8px 12px;
    border-radius: 4px;
    font-weight: 500;
}

QMenu::item:hover, QMenu::item:selected {
    background-color: #0284C7;
    color: #FFFFFF;
    font-weight: bold;
}

QMenu::separator {
    height: 1px;
    background-color: #334155;
    margin: 6px 2px;
}

/* ScrollBar */
QScrollBar:vertical {
    background: #0F172A;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #334155;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}
"""
