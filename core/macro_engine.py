import time
import threading
from PySide6.QtCore import QObject
from core.input_simulator import InputSimulator
from core.profile_manager import ProfileManager

class MacroEngine(QObject):
    def __init__(self, profile_manager: ProfileManager):
        super().__init__()
        self.profile_manager = profile_manager
        self.enabled = True
        self._active_rapid_fires = {}  # {(player_id, dpad_dir): threading.Event}
        self._active_holds = {}        # {(player_id, dpad_dir): key_name}

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        if not enabled:
            self._stop_all()

    def _stop_all(self):
        # Stop all rapid fires
        for event in self._active_rapid_fires.values():
            event.set()
        self._active_rapid_fires.clear()

        # Release any held keys
        for key in list(self._active_holds.values()):
            InputSimulator.release_key(key)
        self._active_holds.clear()

    def handle_dpad_event(self, joy_idx: int, dpad_dir: str, is_pressed: bool):
        if not self.enabled:
            return

        # Find which player_id is bound to joy_idx
        matching_players = []
        for p in range(1, 9):
            if self.profile_manager.get_player_device_index(p) == joy_idx:
                matching_players.append(p)

        # Fallback: if no explicit device index matches, assume player 1 maps to joy 0, etc.
        if not matching_players and joy_idx < 8:
            matching_players = [joy_idx + 1]

        for player_id in matching_players:
            self._process_player_dpad_event(player_id, dpad_dir, is_pressed)

    def _process_player_dpad_event(self, player_id: int, dpad_dir: str, is_pressed: bool):
        mapping = self.profile_manager.get_player_dpad_mapping(player_id, dpad_dir)
        if not mapping:
            return

        macro_type = mapping.get("type", "single")
        mode = mapping.get("mode", "press_hold")
        state_key = (player_id, dpad_dir)

        if is_pressed:
            if macro_type == "single":
                key = mapping.get("key", "")
                if not key:
                    return

                if mode == "press_hold":
                    self._active_holds[state_key] = key
                    InputSimulator.press_key(key)
                elif mode == "tap":
                    hold_dur = mapping.get("hold_duration", 0.06)
                    threading.Thread(target=InputSimulator.tap_key, args=(key, hold_dur), daemon=True).start()
                elif mode == "rapid_fire":
                    interval = mapping.get("rapid_interval", 0.1)
                    stop_event = threading.Event()
                    self._active_rapid_fires[state_key] = stop_event
                    threading.Thread(
                        target=self._run_rapid_fire,
                        args=(key, interval, stop_event),
                        daemon=True
                    ).start()

            elif macro_type == "combo":
                keys = mapping.get("keys", [])
                hold_dur = mapping.get("hold_duration", 0.06)
                if keys:
                    threading.Thread(target=InputSimulator.send_combo, args=(keys, hold_dur), daemon=True).start()

            elif macro_type == "sequence":
                sequence = mapping.get("sequence", [])
                if sequence:
                    threading.Thread(target=InputSimulator.send_sequence, args=(sequence,), daemon=True).start()

        else:
            # D-Pad Button Released
            if state_key in self._active_holds:
                key = self._active_holds.pop(state_key)
                InputSimulator.release_key(key)

            if state_key in self._active_rapid_fires:
                stop_event = self._active_rapid_fires.pop(state_key)
                stop_event.set()

    def _run_rapid_fire(self, key: str, interval: float, stop_event: threading.Event):
        while not stop_event.is_set():
            InputSimulator.tap_key(key, 0.03)
            time.sleep(max(0.01, interval))
