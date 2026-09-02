import ctypes
from ctypes import wintypes

# Windows API constants & types
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

COMMON_PES_PROCESSES = [
    "pes6.exe", "pes2007.exe", "pes6_online.exe", "pes5.exe", "settings.exe"
]

COMMON_PES_TITLES = [
    "pro evolution soccer", "pes6", "pes 6", "pes 2007", "settings"
]

class GameDetector:
    """Detects running PES6 / DirectX game windows and handles target window focus."""

    @staticmethod
    def get_foreground_hwnd() -> int:
        return user32.GetForegroundWindow()

    @staticmethod
    def get_window_title(hwnd: int) -> str:
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return ""
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value

    @staticmethod
    def get_window_process_name(hwnd: int) -> str:
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == 0:
            return ""
        
        # PROCESS_QUERY_INFORMATION (0x0400) | PROCESS_VM_READ (0x0010)
        h_process = kernel32.OpenProcess(0x0410, False, pid.value)
        if not h_process:
            return ""
        
        try:
            buff = ctypes.create_unicode_buffer(260)
            size = wintypes.DWORD(260)
            # QueryFullProcessImageNameW
            if kernel32.QueryFullProcessImageNameW(h_process, 0, buff, ctypes.byref(size)):
                full_path = buff.value
                return full_path.split("\\")[-1].lower()
        except Exception:
            pass
        finally:
            kernel32.CloseHandle(h_process)
        return ""

    @classmethod
    def find_game_window(cls, custom_target: str = "") -> dict:
        """
        Scan all top-level windows for PES6 / DirectX target.
        Returns info dict: {'is_running': bool, 'is_focused': bool, 'hwnd': int, 'title': str, 'proc_name': str}
        """
        found_info = {
            "is_running": False,
            "is_focused": False,
            "hwnd": 0,
            "title": "",
            "proc_name": ""
        }

        fg_hwnd = cls.get_foreground_hwnd()

        def enum_windows_callback(hwnd, lParam):
            if not user32.IsWindowVisible(hwnd):
                return True

            title = cls.get_window_title(hwnd)
            title_lower = title.lower()
            proc_name = cls.get_window_process_name(hwnd)

            is_match = False

            # If user specified a custom target
            if custom_target and custom_target.strip():
                t_lower = custom_target.strip().lower()
                if t_lower in proc_name or t_lower in title_lower:
                    is_match = True
            else:
                # Match default PES process or title
                if any(proc in proc_name for proc in COMMON_PES_PROCESSES):
                    is_match = True
                elif any(kw in title_lower for kw in COMMON_PES_TITLES):
                    # Exclude python main.py app window title
                    if "macro manager" not in title_lower:
                        is_match = True

            if is_match:
                found_info["is_running"] = True
                found_info["hwnd"] = hwnd
                found_info["title"] = title
                found_info["proc_name"] = proc_name
                found_info["is_focused"] = (hwnd == fg_hwnd)
                return False  # Stop enumeration

            return True

        user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)
        return found_info

    @staticmethod
    def focus_window(hwnd: int) -> bool:
        if hwnd and user32.IsWindow(hwnd):
            user32.ShowWindow(hwnd, 9)  # SW_RESTORE = 9
            return user32.SetForegroundWindow(hwnd) != 0
        return False
