import time
import os
# Suppress pygame banner
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame
from PySide6.QtCore import QThread, Signal

# Xbox controller buttons mapping to PES6 / keyboard defaults
XBOX_BUTTON_MAP = {
    0: ('btn_a', '🎮 Nút A (Chuyền ngắn / Lấy bóng [Phím X])', 'x'),
    1: ('btn_b', '🎮 Nút B (Chuyền dài / Xoạc bóng [Phím C])', 'c'),
    2: ('btn_x', '🎮 Nút X (Sút bóng / Máy hỗ trợ [Phím A])', 'a'),
    3: ('btn_y', '🎮 Nút Y (Chọc khe / Thủ môn dâng [Phím W])', 'w'),
    4: ('btn_lb', '🎮 Nút LB (Đổi người / Chạy chỗ [Phím Q])', 'q'),
    5: ('btn_rb', '🎮 Nút RB (Chạy nhanh [Phím E])', 'e'),
    6: ('btn_select', '🎮 Nút Back/Select [Phím Esc]', 'escape'),
    7: ('btn_start', '🎮 Nút Start [Phím Enter]', 'enter'),
    8: ('btn_l3', '🎮 Nút Cần trái L3 [Shift]', 'lshift'),
    9: ('btn_r3', '🎮 Nút Cần phải R3 [Ctrl]', 'lctrl'),
}

class GamepadListener(QThread):
    # Signals
    connection_changed = Signal(bool, str)       # (is_connected, summary_status)
    devices_changed = Signal(list)               # list of [{'index': 0, 'name': '...'}, ...]
    dpad_event = Signal(int, str, bool)          # (joy_index, dpad_dir, is_pressed)
    button_pressed = Signal(int, str, str, str)  # (joy_index, btn_id, friendly_name, default_key)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = True
        self.joysticks = {}      # {joy_idx: joystick_instance}
        self.device_list = []    # [{'index': 0, 'name': 'Controller (Flydigi Dune Fox)'}]
        
        # State tracking for D-Pad directions per joystick index
        # {joy_idx: {'dpad_up': False, 'dpad_down': False, ...}}
        self.dpad_states = {}

    def stop(self):
        self._running = False

    def run(self):
        pygame.init()
        pygame.joystick.init()

        clock = pygame.time.Clock()
        check_conn_timer = 0

        while self._running:
            check_conn_timer += 1
            if check_conn_timer >= 60:
                check_conn_timer = 0
                self._update_connected_devices()

            # Process Pygame input events
            for event in pygame.event.get():
                if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                    self._update_connected_devices()
                
                # Check events from joysticks
                if event.type == pygame.JOYHATMOTION:
                    joy_idx = getattr(event, 'joy', 0)
                    hat_x, hat_y = event.value
                    self._update_hat_state(joy_idx, hat_x, hat_y)
                
                elif event.type == pygame.JOYBUTTONDOWN:
                    joy_idx = getattr(event, 'joy', 0)
                    self._check_button_event(joy_idx, event.button, True)
                elif event.type == pygame.JOYBUTTONUP:
                    joy_idx = getattr(event, 'joy', 0)
                    self._check_button_event(joy_idx, event.button, False)

            clock.tick(60)  # 60 FPS polling

        # Cleanup
        for j in self.joysticks.values():
            try:
                j.quit()
            except Exception:
                pass
        pygame.joystick.quit()
        pygame.quit()

    def _update_connected_devices(self):
        count = pygame.joystick.get_count()
        new_device_list = []
        new_joysticks = {}

        for i in range(count):
            try:
                if i in self.joysticks:
                    j = self.joysticks[i]
                else:
                    j = pygame.joystick.Joystick(i)
                    j.init()

                name = j.get_name()
                new_joysticks[i] = j
                new_device_list.append({"index": i, "name": f"Controller #{i+1} ({name})"})

                if i not in self.dpad_states:
                    self.dpad_states[i] = {
                        'dpad_up': False, 'dpad_down': False,
                        'dpad_left': False, 'dpad_right': False
                    }

            except Exception as e:
                print(f"Error initializing joystick {i}: {e}")

        self.joysticks = new_joysticks

        # Check if list changed
        if new_device_list != self.device_list:
            self.device_list = new_device_list
            self.devices_changed.emit(self.device_list)

            if len(self.device_list) > 0:
                summary = f"✅ Đã kết nối {len(self.device_list)} tay cầm ({self.device_list[0]['name']})"
                self.connection_changed.emit(True, summary)
            else:
                self.connection_changed.emit(False, "❌ Chưa tìm thấy tay cầm nào")

    def _update_hat_state(self, joy_idx: int, x: int, y: int):
        if joy_idx not in self.dpad_states:
            self.dpad_states[joy_idx] = {'dpad_up': False, 'dpad_down': False, 'dpad_left': False, 'dpad_right': False}

        new_state = {
            'dpad_up': (y == 1),
            'dpad_down': (y == -1),
            'dpad_left': (x == -1),
            'dpad_right': (x == 1)
        }

        for direction, pressed in new_state.items():
            if self.dpad_states[joy_idx][direction] != pressed:
                self.dpad_states[joy_idx][direction] = pressed
                self.dpad_event.emit(joy_idx, direction, pressed)

    def _check_button_event(self, joy_idx: int, btn_idx: int, is_down: bool):
        if joy_idx not in self.dpad_states:
            self.dpad_states[joy_idx] = {'dpad_up': False, 'dpad_down': False, 'dpad_left': False, 'dpad_right': False}

        # Check D-Pad button fallbacks
        button_dpad_map = {
            11: 'dpad_up',
            12: 'dpad_down',
            13: 'dpad_left',
            14: 'dpad_right'
        }
        if btn_idx in button_dpad_map:
            direction = button_dpad_map[btn_idx]
            if self.dpad_states[joy_idx][direction] != is_down:
                self.dpad_states[joy_idx][direction] = is_down
                self.dpad_event.emit(joy_idx, direction, is_down)
            return

        # Emit raw Xbox button event on press
        if is_down:
            if btn_idx in XBOX_BUTTON_MAP:
                btn_id, friendly_name, default_key = XBOX_BUTTON_MAP[btn_idx]
                self.button_pressed.emit(joy_idx, btn_id, friendly_name, default_key)
            else:
                self.button_pressed.emit(joy_idx, f"btn_{btn_idx}", f"🎮 Nút Tay Cầm #{btn_idx}", "space")
