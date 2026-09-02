import os
import sys
import json
import urllib.request
import urllib.error
from PySide6.QtCore import QThread, Signal
from version import APP_VERSION, GITHUB_RELEASES_URL

def parse_version_tuple(ver_str: str) -> tuple:
    """Parse version string like 'v1.0.1' or '1.2.0' into numeric tuple (1, 0, 1)."""
    clean_str = ver_str.strip().lstrip("vV")
    parts = []
    for p in clean_str.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])

class UpdateCheckerThread(QThread):
    """Background thread to query GitHub Releases API for latest app release."""
    update_result = Signal(dict)

    def __init__(self, silent: bool = False):
        super().__init__()
        self.silent = silent

    def run(self):
        try:
            req = urllib.request.Request(
                GITHUB_RELEASES_URL,
                headers={"User-Agent": "PES6-Gamepad-Macro-Manager-Updater"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status != 200:
                    self.update_result.emit({
                        "has_update": False,
                        "error": f"HTTP Error {resp.status}",
                        "silent": self.silent
                    })
                    return

                data = json.loads(resp.read().decode("utf-8"))
                tag_name = data.get("tag_name", "")
                release_notes = data.get("body", "Không có thông tin chi tiết phiên bản.")
                assets = data.get("assets", [])

                download_url = ""
                # Priority: PES6_Gamepad_Macro_Manager_Setup.exe -> PES6_Gamepad_Macro_Manager.exe -> .zip
                for asset in assets:
                    url = asset.get("browser_download_url", "")
                    name = asset.get("name", "").lower()
                    if "setup" in name and name.endswith(".exe"):
                        download_url = url
                        break
                    elif name.endswith(".exe") and not download_url:
                        download_url = url
                    elif name.endswith(".zip") and not download_url:
                        download_url = url

                if not download_url and data.get("zipball_url"):
                    download_url = data.get("zipball_url")

                latest_ver_tuple = parse_version_tuple(tag_name)
                current_ver_tuple = parse_version_tuple(APP_VERSION)

                has_update = latest_ver_tuple > current_ver_tuple

                self.update_result.emit({
                    "has_update": has_update,
                    "latest_version": tag_name if tag_name else "v" + APP_VERSION,
                    "current_version": "v" + APP_VERSION,
                    "release_notes": release_notes,
                    "download_url": download_url,
                    "html_url": data.get("html_url", ""),
                    "error": None,
                    "silent": self.silent
                })
        except Exception as e:
            self.update_result.emit({
                "has_update": False,
                "error": str(e),
                "silent": self.silent
            })


class UpdateDownloaderThread(QThread):
    """Background thread to download release file with byte progress monitoring."""
    progress = Signal(int, int, float)  # downloaded_bytes, total_bytes, percentage
    finished = Signal(str, bool, str)   # file_path, success, error_message

    def __init__(self, download_url: str, save_filename: str = "PES6_Gamepad_Macro_Manager_Update.exe"):
        super().__init__()
        self.download_url = download_url
        self.save_filename = save_filename

    def run(self):
        try:
            dest_dir = os.path.join(os.environ.get("TEMP", os.getcwd()), "PES6_Macro_Update")
            os.makedirs(dest_dir, exist_ok=True)
            target_path = os.path.join(dest_dir, self.save_filename)

            req = urllib.request.Request(
                self.download_url,
                headers={"User-Agent": "PES6-Gamepad-Macro-Manager-Updater"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                total_bytes = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 64 * 1024

                with open(target_path, "wb") as f:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        percent = (downloaded / total_bytes * 100.0) if total_bytes > 0 else 0.0
                        self.progress.emit(downloaded, total_bytes, percent)

            self.finished.emit(target_path, True, "")
        except Exception as e:
            self.finished.emit("", False, str(e))
