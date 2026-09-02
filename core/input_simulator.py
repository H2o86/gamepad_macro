import ctypes
import time
import sys
from ctypes import wintypes

# Windows API constants
INPUT_KEYBOARD = 1
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101

# C-struct definitions for SendInput
ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]

class _INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", _INPUT_UNION),
    ]

# Dictionary of key name -> (scan_code, is_extended)
SCAN_CODES = {
    # Alphabet
    'a': (0x1E, False), 'b': (0x30, False), 'c': (0x2E, False), 'd': (0x20, False),
    'e': (0x12, False), 'f': (0x21, False), 'g': (0x22, False), 'h': (0x23, False),
    'i': (0x17, False), 'j': (0x24, False), 'k': (0x25, False), 'l': (0x26, False),
    'm': (0x32, False), 'n': (0x31, False), 'o': (0x18, False), 'p': (0x19, False),
    'q': (0x10, False), 'r': (0x13, False), 's': (0x1F, False), 't': (0x14, False),
    'u': (0x16, False), 'v': (0x2F, False), 'w': (0x11, False), 'x': (0x2D, False),
    'y': (0x15, False), 'z': (0x2C, False),
    
    # Numbers
    '0': (0x0B, False), '1': (0x02, False), '2': (0x03, False), '3': (0x04, False),
    '4': (0x05, False), '5': (0x06, False), '6': (0x07, False), '7': (0x08, False),
    '8': (0x09, False), '9': (0x0A, False),
    
    # Special & Modifiers
    'space': (0x39, False), 'enter': (0x1C, False), 'escape': (0x01, False),
    'backspace': (0x0E, False), 'tab': (0x0F, False),
    'shift': (0x2A, False), 'lshift': (0x2A, False), 'rshift': (0x36, False),
    'ctrl': (0x1D, False), 'lctrl': (0x1D, False), 'rctrl': (0x1D, True),
    'alt': (0x38, False), 'lalt': (0x38, False), 'ralt': (0x38, True),
    
    # Arrows
    'up': (0x48, True), 'down': (0x50, True), 'left': (0x4B, True), 'right': (0x4D, True),
    
    # Function Keys
    'f1': (0x3B, False), 'f2': (0x3C, False), 'f3': (0x3D, False), 'f4': (0x3E, False),
    'f5': (0x3F, False), 'f6': (0x40, False), 'f7': (0x41, False), 'f8': (0x42, False),
    'f9': (0x43, False), 'f10': (0x44, False), 'f11': (0x57, False), 'f12': (0x58, False),

    # Numpad (Direct Mapping for PES6 Keyboard Layout)
    'num0': (0x52, False), 'num1': (0x4F, False), 'num2': (0x50, False), 'num3': (0x51, False),
    'num4': (0x4B, False), 'num5': (0x4C, False), 'num6': (0x4D, False), 'num7': (0x47, False),
    'num8': (0x48, False), 'num9': (0x49, False),
    'numdel': (0x53, False), 'numperiod': (0x53, False), 'num.': (0x53, False),
}



class InputSimulator:
    """Windows SendInput & PostMessage simulator optimized for DirectX / DirectInput / PES6."""
    
    target_hwnd = 0  # Global target window handle if set

    @classmethod
    def set_target_hwnd(cls, hwnd: int):
        cls.target_hwnd = hwnd

    @staticmethod
    def _get_code_info(key_name: str):
        key = key_name.lower().strip()
        if key in SCAN_CODES:
            return SCAN_CODES[key]
        if len(key) == 1:
            vk = ord(key.upper())
            scan = ctypes.windll.user32.MapVirtualKeyW(vk, 0)
            return (scan, False)
        return (0, False)

    @classmethod
    def press_key(cls, key_name: str):
        scan_code, is_extended = cls._get_code_info(key_name)
        if scan_code == 0:
            return
        
        vk_code = ctypes.windll.user32.MapVirtualKeyW(scan_code, 1)

        # 1. Global SendInput (Hardware scancode)
        flags = KEYEVENTF_SCANCODE
        if is_extended:
            flags |= KEYEVENTF_EXTENDEDKEY

        ii_ = _INPUT_UNION()
        ii_.ki = KEYBDINPUT(
            wVk=vk_code,
            wScan=scan_code,
            dwFlags=flags,
            time=0,
            dwExtraInfo=0
        )
        x = INPUT(ctypes.c_ulong(INPUT_KEYBOARD), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

        # 2. Direct Window PostMessage if target HWND exists
        if cls.target_hwnd and ctypes.windll.user32.IsWindow(cls.target_hwnd):
            lparam_down = 1 | (scan_code << 16)
            ctypes.windll.user32.PostMessageW(cls.target_hwnd, WM_KEYDOWN, vk_code, lparam_down)

    @classmethod
    def release_key(cls, key_name: str):
        scan_code, is_extended = cls._get_code_info(key_name)
        if scan_code == 0:
            return

        vk_code = ctypes.windll.user32.MapVirtualKeyW(scan_code, 1)

        # 1. Global SendInput Release
        flags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP
        if is_extended:
            flags |= KEYEVENTF_EXTENDEDKEY

        ii_ = _INPUT_UNION()
        ii_.ki = KEYBDINPUT(
            wVk=vk_code,
            wScan=scan_code,
            dwFlags=flags,
            time=0,
            dwExtraInfo=0
        )
        x = INPUT(ctypes.c_ulong(INPUT_KEYBOARD), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

        # 2. Direct Window PostMessage Release
        if cls.target_hwnd and ctypes.windll.user32.IsWindow(cls.target_hwnd):
            lparam_up = 1 | (scan_code << 16) | (1 << 30) | (1 << 31)
            ctypes.windll.user32.PostMessageW(cls.target_hwnd, WM_KEYUP, vk_code, lparam_up)

    @classmethod
    def tap_key(cls, key_name: str, duration: float = 0.06):
        hold_time = max(0.02, duration)
        cls.press_key(key_name)
        time.sleep(hold_time)
        cls.release_key(key_name)

    @classmethod
    def send_combo(cls, keys: list[str], hold_time: float = 0.06):
        pressed = []
        for k in keys:
            cls.press_key(k)
            pressed.append(k)
            time.sleep(0.03)
        time.sleep(max(0.02, hold_time))
        for k in reversed(pressed):
            cls.release_key(k)
            time.sleep(0.03)

    @classmethod
    def send_sequence(cls, steps: list[dict]):
        for step in steps:
            action = step.get('action', 'tap')
            hold_dur = step.get('hold_duration', step.get('delay', 0.06))

            if action == 'tap':
                key = step.get('key', '')
                cls.tap_key(key, hold_dur)
            elif action == 'combo':
                keys = step.get('keys', [])
                cls.send_combo(keys, hold_dur)
            
            post_delay = step.get('post_delay', 0.06)
            if post_delay > 0:
                time.sleep(post_delay)
