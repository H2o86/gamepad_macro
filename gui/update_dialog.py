import os
import subprocess
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextBrowser, QProgressBar, QFrame,
    QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont, QColor
from core.update_checker import UpdateCheckerThread, UpdateDownloaderThread
from version import APP_VERSION

class UpdateDialog(QDialog):
    def __init__(self, parent=None, update_info: dict = None):
        super().__init__(parent)
        self.update_info = update_info or {}
        self.downloader_thread = None

        self.setWindowTitle("Tự Động Cập Nhật - PES6 Gamepad Macro Manager")
        self.setMinimumSize(560, 420)
        self.resize(600, 460)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header Frame
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #0F172A;
                border: 1px solid #1E293B;
                border-radius: 10px;
                padding: 12px;
            }
        """)
        h_layout = QHBoxLayout(header_frame)

        # Icon / Emoji
        icon_label = QLabel("🚀")
        icon_label.setFont(QFont("Segoe UI Emoji", 32))
        h_layout.addWidget(icon_label)

        # Header Text
        v_head = QVBoxLayout()
        lbl_title = QLabel("Đã có phiên bản mới!")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #38BDF8;")
        
        latest_ver = self.update_info.get("latest_version", "v1.0.0")
        current_ver = self.update_info.get("current_version", "v" + APP_VERSION)
        
        lbl_ver = QLabel(f"Phiên bản hiện tại: <b style='color:#94A3B8;'>{current_ver}</b> ➔ Phiên bản mới: <b style='color:#4ADE80;'>{latest_ver}</b>")
        lbl_ver.setStyleSheet("font-size: 13px; color: #CBD5E1;")

        v_head.addWidget(lbl_title)
        v_head.addWidget(lbl_ver)
        h_layout.addLayout(v_head)
        h_layout.addStretch()

        layout.addWidget(header_frame)

        # Release Notes Title
        lbl_notes_title = QLabel("📋 Thông tin cập nhật & Tính năng mới:")
        lbl_notes_title.setStyleSheet("font-weight: bold; color: #F8FAFC; font-size: 14px;")
        layout.addWidget(lbl_notes_title)

        # Release Notes Browser
        self.txt_notes = QTextBrowser()
        notes_text = self.update_info.get("release_notes", "Không có thông tin chi tiết.")
        self.txt_notes.setMarkdown(notes_text)
        self.txt_notes.setStyleSheet("""
            QTextBrowser {
                background-color: #1E293B;
                color: #F1F5F9;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.txt_notes, stretch=1)

        # Download Progress Area (Hidden by default)
        self.progress_frame = QFrame()
        self.progress_frame.setVisible(False)
        p_layout = QVBoxLayout(self.progress_frame)
        p_layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_progress_status = QLabel("Đang chuẩn bị tải xuống...")
        self.lbl_progress_status.setStyleSheet("color: #38BDF8; font-size: 12px; font-weight: bold;")
        p_layout.addWidget(self.lbl_progress_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #475569;
                border-radius: 6px;
                text-align: center;
                background-color: #0F172A;
                color: #FFFFFF;
                font-weight: bold;
                height: 22px;
            }
            QProgressBar::chunk {
                background-color: #0284C7;
                border-radius: 5px;
            }
        """)
        p_layout.addWidget(self.progress_bar)

        layout.addWidget(self.progress_frame)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_close = QPushButton("Để sau")
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #F8FAFC;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        self.btn_close.clicked.connect(self.reject)

        self.btn_download = QPushButton("⚡ Tải xuống & Cập nhật ngay")
        self.btn_download.setCursor(Qt.PointingHandCursor)
        self.btn_download.setStyleSheet("""
            QPushButton {
                background-color: #0284C7;
                color: #FFFFFF;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0369A1;
            }
            QPushButton:disabled {
                background-color: #475569;
                color: #94A3B8;
            }
        """)
        self.btn_download.clicked.connect(self._start_download)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)
        btn_layout.addWidget(self.btn_download)

        layout.addLayout(btn_layout)

    def _start_download(self):
        download_url = self.update_info.get("download_url", "")
        if not download_url:
            html_url = self.update_info.get("html_url", "")
            if html_url:
                import webbrowser
                webbrowser.open(html_url)
                QMessageBox.information(
                    self,
                    "Mở Trang Cập Nhật",
                    "Đã mở trang tải bản cập nhật trên trình duyệt web của bạn."
                )
            else:
                QMessageBox.warning(self, "Lỗi Tải Về", "Không tìm thấy liên kết tải bản cập nhật.")
            return

        self.btn_download.setEnabled(False)
        self.btn_close.setEnabled(False)
        self.progress_frame.setVisible(True)

        filename = "PES6_Gamepad_Macro_Manager_Setup.exe"
        if download_url.endswith(".zip"):
            filename = "PES6_Gamepad_Macro_Manager_Update.zip"

        self.downloader_thread = UpdateDownloaderThread(download_url, filename)
        self.downloader_thread.progress.connect(self._on_download_progress)
        self.downloader_thread.finished.connect(self._on_download_finished)
        self.downloader_thread.start()

    def _on_download_progress(self, downloaded: int, total: int, percent: float):
        mb_down = downloaded / (1024 * 1024)
        mb_total = total / (1024 * 1024)
        if total > 0:
            self.lbl_progress_status.setText(f"📥 Đang tải bản cập nhật: {mb_down:.1f} MB / {mb_total:.1f} MB ({percent:.0f}%)")
            self.progress_bar.setValue(int(percent))
        else:
            self.lbl_progress_status.setText(f"📥 Đang tải bản cập nhật: {mb_down:.1f} MB...")
            self.progress_bar.setValue(50)

    def _on_download_finished(self, file_path: str, success: bool, error_msg: str):
        if not success:
            self.btn_download.setEnabled(True)
            self.btn_close.setEnabled(True)
            self.lbl_progress_status.setText(f"❌ Lỗi tải về: {error_msg}")
            QMessageBox.critical(self, "Lỗi Tải Bản Cập Nhật", f"Không thể tải bản cập nhật:\n{error_msg}")
            return

        self.lbl_progress_status.setText("✅ Tải bản cập nhật hoàn tất!")
        self.progress_bar.setValue(100)

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Cập Nhật Hoàn Tất")
        msg_box.setText("Bản cập nhật mới đã sẵn sàng cài đặt.\nỨng dụng sẽ tự động chạy bộ cài và khởi động lại.")
        msg_box.setIcon(QMessageBox.Information)
        btn_run = msg_box.addButton("Cài Đặt Ngay", QMessageBox.AcceptRole)
        msg_box.exec()

        try:
            if file_path.endswith(".exe"):
                subprocess.Popen([file_path])
            elif file_path.endswith(".zip"):
                import os
                os.startfile(os.path.dirname(file_path))

            # Exit current running application so installer can overwrite
            from PySide6.QtWidgets import QApplication
            QApplication.quit()
        except Exception as e:
            QMessageBox.warning(self, "Lỗi Khởi Chạy Bộ Cài", f"Không thể tự khởi chạy bộ cài:\n{e}")
