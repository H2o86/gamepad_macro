import os
import json
import shutil
import zipfile
from datetime import datetime

def get_default_player_mapping(is_pes6: bool = True) -> dict:
    if is_pes6:
        # Advanced PES6 Skill Presets (Numpad Layout) with D-Pad Up set to Knuckle Shot
        return {
            "dpad_up": {
                "name": "Sút Lắc Đổi Hướng (Knuckle Shot)",
                "type": "sequence",
                "sequence": [
                    {"action": "tap", "key": "num2", "hold_duration": 0.20, "post_delay": 0.35},
                    {"action": "tap", "key": "num2", "hold_duration": 0.05, "post_delay": 0.05}
                ]
            },
            "dpad_down": {
                "name": "Super Cancel Nâng Cao (Tap X ➔ RB+RT)",
                "type": "sequence",
                "sequence": [
                    {"action": "tap", "key": "num2", "hold_duration": 0.04, "post_delay": 0.04},
                    {"action": "combo", "keys": ["num0", "num1"], "hold_duration": 0.15, "post_delay": 0.05}
                ]
            },
            "dpad_left": {
                "name": "Sút Má Trong (Hold X 0.35s ➔ RT)",
                "type": "sequence",
                "sequence": [
                    {"action": "tap", "key": "num2", "hold_duration": 0.35, "post_delay": 0.03},
                    {"action": "tap", "key": "num1", "hold_duration": 0.15, "post_delay": 0.05}
                ]
            },
            "dpad_right": {
                "name": "Chip Shot Nâng Cao (Tap X ➔ RB)",
                "type": "sequence",
                "sequence": [
                    {"action": "tap", "key": "num2", "hold_duration": 0.05, "post_delay": 0.04},
                    {"action": "tap", "key": "num0", "hold_duration": 0.15, "post_delay": 0.05}
                ]
            }
        }
    else:
        return {
            "dpad_up": {"name": "Di chuyển Lên", "type": "single", "key": "up", "mode": "tap"},
            "dpad_down": {"name": "Di chuyển Xuống", "type": "single", "key": "down", "mode": "tap"},
            "dpad_left": {"name": "Di chuyển Trái", "type": "single", "key": "left", "mode": "tap"},
            "dpad_right": {"name": "Di chuyển Phải", "type": "single", "key": "right", "mode": "tap"}
        }

def get_default_macro_library() -> list[dict]:
    return [
        {
            "name": "Sút Lắc Đổi Hướng (Knuckle Shot)",
            "description": "Bấm Sút (Num 2 - 0.20s) ➔ Nhắp Sút lần 2 (Num 2 - 0.05s) tạo đường bay chao đảo ngặt nghèo.",
            "type": "sequence",
            "sequence": [
                {"action": "tap", "key": "num2", "hold_duration": 0.20, "post_delay": 0.35},
                {"action": "tap", "key": "num2", "hold_duration": 0.05, "post_delay": 0.05}
            ]
        },
        {
            "name": "Super Cancel Nâng Cao (Tap X ➔ RB+RT)",
            "description": "Nhắp X hủy lệnh sút/chuyền ➔ Nhấn giữ combo RB+RT để di chuyển tự do cắt mặt.",
            "type": "sequence",
            "sequence": [
                {"action": "tap", "key": "num2", "hold_duration": 0.04, "post_delay": 0.04},
                {"action": "combo", "keys": ["num0", "num1"], "hold_duration": 0.15, "post_delay": 0.05}
            ]
        },
        {
            "name": "Sút Má Trong (Hold X 0.35s ➔ RT)",
            "description": "Tích lực Sút 0.35s ➔ Nhấn RT vuốt bóng cứa lòng góc xa.",
            "type": "sequence",
            "sequence": [
                {"action": "tap", "key": "num2", "hold_duration": 0.35, "post_delay": 0.03},
                {"action": "tap", "key": "num1", "hold_duration": 0.15, "post_delay": 0.05}
            ]
        },
        {
            "name": "Giả Sút (Tap X ➔ A)",
            "description": "Bấm Sút ➔ Hủy lập tức bằng Chuyền ngắn qua chân trụ làm lỡ đà hậu vệ.",
            "type": "sequence",
            "sequence": [
                {"action": "tap", "key": "num2", "hold_duration": 0.04, "post_delay": 0.04},
                {"action": "tap", "key": "numdel", "hold_duration": 0.05, "post_delay": 0.05}
            ]
        },
        {
            "name": "Chip Shot Nâng Cao (Tap X ➔ RB)",
            "description": "Tích lực Sút nhẹ ➔ Bấm RB bấm bóng bổng qua đầu thủ môn.",
            "type": "sequence",
            "sequence": [
                {"action": "tap", "key": "num2", "hold_duration": 0.05, "post_delay": 0.04},
                {"action": "tap", "key": "num0", "hold_duration": 0.15, "post_delay": 0.05}
            ]
        },
        {
            "name": "Bật Tường Nhanh 1-2 (LB+A ➔ Y)",
            "description": "Đập nhả bật tường 1-2 dâng cao trung lộ rồi chọc khe xé nát hàng thủ.",
            "type": "sequence",
            "sequence": [
                {"action": "combo", "keys": ["rctrl", "numdel"], "hold_duration": 0.12, "post_delay": 0.15},
                {"action": "tap", "key": "num5", "hold_duration": 0.15, "post_delay": 0.05}
            ]
        },
        {
            "name": "Chọc Khe Bổng Kỹ Thuật (LB+Y)",
            "description": "Phất bóng bổng chuẩn xác vượt tuyến cho tiền đạo cắm bứt tốc.",
            "type": "sequence",
            "sequence": [
                {"action": "combo", "keys": ["rctrl", "num5"], "hold_duration": 0.20, "post_delay": 0.05}
            ]
        }
    ]

def create_default_8player_profile(name: str, is_pes6: bool = True) -> dict:
    players = {}
    for p in range(1, 9):
        players[str(p)] = {
            "device_index": p - 1,
            "dpad_mappings": get_default_player_mapping(is_pes6)
        }
    return {
        "name": name,
        "description": f"Profile 8 Người chơi ({name})",
        "players": players
    }

def create_default_ps4_8player_profile() -> dict:
    prof = create_default_8player_profile("PlayStation 4 DualShock 4", is_pes6=True)
    prof["description"] = "Profile 8 Player chuẩn tay cầm PlayStation 4 (DualShock 4)"
    return prof

def create_default_ps5_8player_profile() -> dict:
    prof = create_default_8player_profile("PlayStation 5 DualSense", is_pes6=True)
    prof["description"] = "Profile 8 Player chuẩn tay cầm PlayStation 5 (DualSense)"
    return prof

class ProfileManager:
    def __init__(self, profiles_dir: str = "profiles"):
        self.profiles_dir = profiles_dir
        self.active_profile = None
        self.active_profile_name = "pes6"
        self._ensure_profiles_exist()
        self.load_profile("pes6")

    def _ensure_profiles_exist(self):
        if not os.path.exists(self.profiles_dir):
            os.makedirs(self.profiles_dir, exist_ok=True)
            
        pes6_path = os.path.join(self.profiles_dir, "pes6.json")
        self.save_profile_file("pes6.json", create_default_8player_profile("PES6 Xbox Profile", is_pes6=True))

        ps4_path = os.path.join(self.profiles_dir, "ps4_pes6.json")
        if not os.path.exists(ps4_path):
            self.save_profile_file("ps4_pes6.json", create_default_ps4_8player_profile())

        ps5_path = os.path.join(self.profiles_dir, "ps5_pes6.json")
        if not os.path.exists(ps5_path):
            self.save_profile_file("ps5_pes6.json", create_default_ps5_8player_profile())

        default_path = os.path.join(self.profiles_dir, "default.json")
        if not os.path.exists(default_path):
            self.save_profile_file("default.json", create_default_8player_profile("Default Profile", is_pes6=False))

    def list_profiles(self) -> list[str]:
        if not os.path.exists(self.profiles_dir):
            return []
        files = os.listdir(self.profiles_dir)
        return [f.replace('.json', '') for f in files if f.endswith('.json')]

    def load_profile(self, profile_name: str) -> dict:
        filename = f"{profile_name}.json" if not profile_name.endswith('.json') else profile_name
        filepath = os.path.join(self.profiles_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "players" not in data:
                        legacy_dpad = data.get("dpad_mappings", {})
                        data["players"] = {}
                        for p in range(1, 9):
                            data["players"][str(p)] = {
                                "device_index": p - 1,
                                "dpad_mappings": json.loads(json.dumps(legacy_dpad)) if legacy_dpad else get_default_player_mapping(True)
                            }
                    self.active_profile = data
                    self.active_profile_name = profile_name.replace('.json', '')
                    return self.active_profile
            except Exception as e:
                print(f"Error loading profile {profile_name}: {e}")
        
        self.active_profile = create_default_8player_profile("PES6 Profile", True)
        self.active_profile_name = "pes6"
        return self.active_profile

    def save_profile_file(self, filename: str, data: dict):
        if not filename.endswith('.json'):
            filename += '.json'
        filepath = os.path.join(self.profiles_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def save_current_profile(self):
        if self.active_profile and self.active_profile_name:
            self.save_profile_file(f"{self.active_profile_name}.json", self.active_profile)

    def save_profile_as(self, new_name: str) -> str:
        clean_name = new_name.strip().lower().replace(" ", "_")
        if not clean_name:
            clean_name = "custom_profile"

        new_data = json.loads(json.dumps(self.active_profile))
        new_data["name"] = new_name
        self.save_profile_file(f"{clean_name}.json", new_data)
        self.load_profile(clean_name)
        return clean_name

    def export_profile(self, profile_name: str, target_filepath: str) -> bool:
        src_path = os.path.join(self.profiles_dir, f"{profile_name}.json")
        if not os.path.exists(src_path):
            return False
        try:
            shutil.copy2(src_path, target_filepath)
            return True
        except Exception as e:
            print(f"Error exporting profile: {e}")
            return False

    def import_profile(self, source_filepath: str) -> str:
        if not os.path.exists(source_filepath):
            return ""
        try:
            with open(source_filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            base_name = os.path.splitext(os.path.basename(source_filepath))[0]
            clean_name = base_name.lower().replace(" ", "_")

            if "players" not in data:
                legacy_dpad = data.get("dpad_mappings", {})
                data["players"] = {}
                for p in range(1, 9):
                    data["players"][str(p)] = {
                        "device_index": p - 1,
                        "dpad_mappings": json.loads(json.dumps(legacy_dpad)) if legacy_dpad else get_default_player_mapping(True)
                    }

            self.save_profile_file(f"{clean_name}.json", data)
            self.load_profile(clean_name)
            return clean_name
        except Exception as e:
            print(f"Error importing profile: {e}")
            return ""

    def export_full_backup(self, target_zip_path: str) -> bool:
        try:
            with zipfile.ZipFile(target_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in os.listdir(self.profiles_dir):
                    if file.endswith('.json'):
                        full_path = os.path.join(self.profiles_dir, file)
                        zipf.write(full_path, file)
            return True
        except Exception as e:
            print(f"Error creating full backup: {e}")
            return False

    def import_full_backup(self, source_zip_path: str) -> bool:
        if not os.path.exists(source_zip_path):
            return False
        try:
            with zipfile.ZipFile(source_zip_path, 'r') as zipf:
                zipf.extractall(self.profiles_dir)
            self._ensure_profiles_exist()
            self.load_profile("pes6")
            return True
        except Exception as e:
            print(f"Error restoring full backup: {e}")
            return False

    # -------------------------------------------------------------
    # 8-Player Helper Methods, Copy & Reset Defaults
    # -------------------------------------------------------------
    def get_player_data(self, player_id: int) -> dict:
        if not self.active_profile or "players" not in self.active_profile:
            return {}
        return self.active_profile["players"].get(str(player_id), {})

    def get_player_dpad_mapping(self, player_id: int, dpad_dir: str) -> dict:
        p_data = self.get_player_data(player_id)
        dpad_map = p_data.get("dpad_mappings", {})
        return dpad_map.get(dpad_dir, {})

    def update_player_dpad_mapping(self, player_id: int, dpad_dir: str, mapping_data: dict):
        if not self.active_profile:
            return
        if "players" not in self.active_profile:
            self.active_profile["players"] = {}
        pid_str = str(player_id)
        if pid_str not in self.active_profile["players"]:
            self.active_profile["players"][pid_str] = {"device_index": player_id - 1, "dpad_mappings": {}}
        
        self.active_profile["players"][pid_str]["dpad_mappings"][dpad_dir] = mapping_data
        self.save_current_profile()

    def get_player_device_index(self, player_id: int) -> int:
        p_data = self.get_player_data(player_id)
        return p_data.get("device_index", player_id - 1)

    def set_player_device_index(self, player_id: int, device_idx: int):
        if not self.active_profile or "players" not in self.active_profile:
            return
        pid_str = str(player_id)
        if pid_str in self.active_profile["players"]:
            self.active_profile["players"][pid_str]["device_index"] = device_idx
            self.save_current_profile()

    def reset_player_defaults(self, player_id: int = 0, is_pes6: bool = True) -> bool:
        if not self.active_profile:
            return False
        if "players" not in self.active_profile:
            self.active_profile["players"] = {}

        default_map = get_default_player_mapping(is_pes6)

        if player_id == 0:
            for p in range(1, 9):
                pid_str = str(p)
                if pid_str not in self.active_profile["players"]:
                    self.active_profile["players"][pid_str] = {"device_index": p - 1, "dpad_mappings": {}}
                self.active_profile["players"][pid_str]["dpad_mappings"] = json.loads(json.dumps(default_map))
        else:
            pid_str = str(player_id)
            if pid_str not in self.active_profile["players"]:
                self.active_profile["players"][pid_str] = {"device_index": player_id - 1, "dpad_mappings": {}}
            self.active_profile["players"][pid_str]["dpad_mappings"] = json.loads(json.dumps(default_map))

        self.save_current_profile()
        return True

    def copy_player_mappings(self, source_player_id: int, target_player_id: int = 0) -> bool:
        if not self.active_profile or "players" not in self.active_profile:
            return False
        
        src_str = str(source_player_id)
        src_data = self.active_profile["players"].get(src_str, {})
        src_mappings = src_data.get("dpad_mappings", {})
        if not src_mappings:
            return False

        copied_mappings = json.loads(json.dumps(src_mappings))

        if target_player_id == 0:
            for p in range(1, 9):
                if p != source_player_id:
                    pid_str = str(p)
                    if pid_str not in self.active_profile["players"]:
                        self.active_profile["players"][pid_str] = {"device_index": p - 1, "dpad_mappings": {}}
                    self.active_profile["players"][pid_str]["dpad_mappings"] = json.loads(json.dumps(copied_mappings))
        else:
            target_str = str(target_player_id)
            if target_str not in self.active_profile["players"]:
                self.active_profile["players"][target_str] = {"device_index": target_player_id - 1, "dpad_mappings": {}}
            self.active_profile["players"][target_str]["dpad_mappings"] = json.loads(json.dumps(copied_mappings))

        self.save_current_profile()
        return True

    def copy_player1_to_all(self):
        return self.copy_player_mappings(1, 0)

    # -------------------------------------------------------------
    # Macro Library Persistence
    # -------------------------------------------------------------
    def get_macro_library_filepath(self) -> str:
        return os.path.join(self.profiles_dir, "macro_library.json")

    def get_macro_library(self) -> list[dict]:
        filepath = self.get_macro_library_filepath()
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        return data
            except Exception as e:
                print("Error reading macro library:", e)
        
        # Default initialization
        default_lib = get_default_macro_library()
        self.save_macro_library(default_lib)
        return default_lib

    def save_macro_library(self, library_list: list[dict]):
        filepath = self.get_macro_library_filepath()
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(library_list, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print("Error saving macro library:", e)

    def add_macro_to_library(self, macro_data: dict) -> bool:
        lib = self.get_macro_library()
        lib.append(macro_data)
        self.save_macro_library(lib)
        return True

    def update_macro_in_library(self, index: int, macro_data: dict) -> bool:
        lib = self.get_macro_library()
        if 0 <= index < len(lib):
            lib[index] = macro_data
            self.save_macro_library(lib)
            return True
        return False

    def delete_macro_from_library(self, index: int) -> bool:
        lib = self.get_macro_library()
        if 0 <= index < len(lib):
            lib.pop(index)
            self.save_macro_library(lib)
            return True
        return False

