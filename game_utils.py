"""
Utility module for game authentication and save/load functionality
"""
import os
import json
import hashlib
from datetime import datetime

class AuthManager:
    """Manages user authentication (register, login, logout)"""
    
    def __init__(self):
        self.users_file = os.path.join(os.path.dirname(__file__), "users.json")
        self.current_user = None
        self._ensure_users_file()
    
    def _ensure_users_file(self):
        """Create users.json file if it doesn't exist"""
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
    
    def _hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username, password):
        """
        Register a new user
        Returns: (success: bool, message: str)
        """
        if not username or not password:
            return False, "Tên đăng nhập và mật khẩu không được để trống"
        
        if len(username) < 3:
            return False, "Tên đăng nhập phải có ít nhất 3 ký tự"
        
        if len(password) < 4:
            return False, "Mật khẩu phải có ít nhất 4 ký tự"
        
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            
            if username in users:
                return False, "Tên đăng nhập đã tồn tại"
            
            users[username] = {
                'password': self._hash_password(password),
                'created_at': datetime.now().isoformat(),
                'saves': []
            }
            
            with open(self.users_file, 'w') as f:
                json.dump(users, f, indent=2)
            
            return True, f"Đăng ký thành công! Chào mừng {username}"
        except Exception as e:
            return False, f"Lỗi đăng ký: {str(e)}"
    
    def login(self, username, password):
        """
        Login user
        Returns: (success: bool, message: str)
        """
        if not username or not password:
            return False, "Vui lòng nhập tên đăng nhập và mật khẩu"
        
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
            
            if username not in users:
                return False, "Tên đăng nhập hoặc mật khẩu không đúng"
            
            hashed_password = self._hash_password(password)
            if users[username]['password'] != hashed_password:
                return False, "Tên đăng nhập hoặc mật khẩu không đúng"
            
            self.current_user = username
            return True, f"Đăng nhập thành công! Chào mừng {username}"
        except Exception as e:
            return False, f"Lỗi đăng nhập: {str(e)}"
    
    def logout(self):
        """Logout current user"""
        if self.current_user:
            username = self.current_user
            self.current_user = None
            return f"Đã đăng xuất khỏi tài khoản {username}"
        return "Không có người dùng đang đăng nhập"
    
    def is_logged_in(self):
        """Check if user is logged in"""
        return self.current_user is not None
    
    def get_current_user(self):
        """Get current logged in username"""
        return self.current_user


class SaveManager:
    """Manages game save/load functionality"""
    
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.saves_dir = os.path.join(os.path.dirname(__file__), "saves")
        self._ensure_saves_directory()
    
    def _ensure_saves_directory(self):
        """Create saves directory if it doesn't exist"""
        if not os.path.exists(self.saves_dir):
            os.makedirs(self.saves_dir)
    
    def _get_user_saves_dir(self):
        """Get user-specific saves directory"""
        if not self.auth_manager.is_logged_in():
            return None
        user_dir = os.path.join(self.saves_dir, self.auth_manager.get_current_user())
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        return user_dir
    
    def save_game(self, save_name, game_state, explorer_char, mw_chars, mr_chars, sw_chars, sr_chars, current_map):
        """
        Save game state to file
        Returns: (success: bool, message: str)
        """
        if not self.auth_manager.is_logged_in():
            return False, "Vui lòng đăng nhập để lưu game"
        
        if not save_name:
            return False, "Tên file lưu không được để trống"
        
        try:
            user_dir = self._get_user_saves_dir()
            save_path = os.path.join(user_dir, f"{save_name}.sav")
            
            # Prepare save data
            save_data = {
                'version': '1.0',
                'current_map': current_map,
                'timestamp': datetime.now().isoformat(),
                'game_state': {
                    'explorer_position': [explorer_char.get_x(), explorer_char.get_y()],
                    'explorer_direction': getattr(game_state, 'explorer_direction', 'RIGHT'),
                    'gate': game_state.gate.copy() if game_state.gate else {},
                    'mummy_white_positions': [[m.get_x(), m.get_y()] for m in mw_chars],
                    'mummy_red_positions': [[m.get_x(), m.get_y()] for m in mr_chars],
                    'scorpion_white_positions': [[s.get_x(), s.get_y()] for s in sw_chars],
                    'scorpion_red_positions': [[s.get_x(), s.get_y()] for s in sr_chars],
                    'history': game_state.history.copy() if hasattr(game_state, 'history') else []
                }
            }
            
            with open(save_path, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            return True, f"Lưu game thành công: {save_name}"
        except Exception as e:
            return False, f"Lỗi lưu game: {str(e)}"
    
    def load_game(self, save_name):
        """
        Load game state from file
        Returns: (success: bool, data: dict or None, message: str)
        """
        if not self.auth_manager.is_logged_in():
            return False, None, "Vui lòng đăng nhập để tải game"
        
        try:
            user_dir = self._get_user_saves_dir()
            save_path = os.path.join(user_dir, f"{save_name}.sav")
            
            if not os.path.exists(save_path):
                return False, None, f"Không tìm thấy file lưu: {save_name}"
            
            with open(save_path, 'r') as f:
                save_data = json.load(f)
            
            return True, save_data, f"Tải game thành công: {save_name}"
        except Exception as e:
            return False, None, f"Lỗi tải game: {str(e)}"
    
    def list_saves(self):
        """
        List all save files for current user
        Returns: list of save names (without .sav extension)
        """
        if not self.auth_manager.is_logged_in():
            return []
        
        try:
            user_dir = self._get_user_saves_dir()
            if not os.path.exists(user_dir):
                return []
            
            saves = [f[:-4] for f in os.listdir(user_dir) if f.endswith('.sav')]
            saves.sort(reverse=True)  # Newest first
            return saves
        except:
            return []
    
    def delete_save(self, save_name):
        """
        Delete a save file
        Returns: (success: bool, message: str)
        """
        if not self.auth_manager.is_logged_in():
            return False, "Vui lòng đăng nhập"
        
        try:
            user_dir = self._get_user_saves_dir()
            save_path = os.path.join(user_dir, f"{save_name}.sav")
            
            if not os.path.exists(save_path):
                return False, f"Không tìm thấy file: {save_name}"
            
            os.remove(save_path)
            return True, f"Đã xóa: {save_name}"
        except Exception as e:
            return False, f"Lỗi xóa: {str(e)}"

