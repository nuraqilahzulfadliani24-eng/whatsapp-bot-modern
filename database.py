import sqlite3
import os
from config import DB_PATH
from datetime import datetime

class Database:
    """Database manager untuk WhatsApp Bot"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.ensure_dir()
        self.init_db()
    
    def ensure_dir(self):
        """Pastikan folder data ada"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def init_db(self):
        """Inisialisasi database dengan tabel-tabel yang diperlukan"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabel User
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id TEXT UNIQUE,
                name TEXT,
                role TEXT DEFAULT 'member',
                warnings INTEGER DEFAULT 0,
                is_muted INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel Grup
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY,
                group_id TEXT UNIQUE,
                group_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                settings TEXT DEFAULT '{}'
            )
        ''')
        
        # Tabel Games (Score)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_scores (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                group_id TEXT,
                game_name TEXT,
                score INTEGER,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Tabel Warnings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                group_id TEXT,
                reason TEXT,
                warned_by TEXT,
                warned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Tabel Logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY,
                group_id TEXT,
                action TEXT,
                actor TEXT,
                target TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")
    
    def get_connection(self):
        """Ambil koneksi database"""
        return sqlite3.connect(self.db_path)
    
    # ===== USER OPERATIONS =====
    def add_user(self, user_id, name, role='member'):
        """Tambah user baru"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, name, role)
                VALUES (?, ?, ?)
            ''', (user_id, name, role))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error adding user: {e}")
            return False
        finally:
            conn.close()
    
    def get_user(self, user_id):
        """Ambil data user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def mute_user(self, user_id):
        """Mute user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET is_muted = 1, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()
        conn.close()
    
    def unmute_user(self, user_id):
        """Unmute user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET is_muted = 0, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()
        conn.close()
    
    def ban_user(self, user_id):
        """Ban user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET is_banned = 1, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()
        conn.close()
    
    def unban_user(self, user_id):
        """Unban user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET is_banned = 0, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()
        conn.close()
    
    def add_warning(self, user_id, group_id, reason, warned_by):
        """Tambah warning ke user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO warnings (user_id, group_id, reason, warned_by)
            VALUES (?, ?, ?, ?)
        ''', (user_id, group_id, reason, warned_by))
        
        # Update warning count
        cursor.execute('''
            UPDATE users SET warnings = warnings + 1
            WHERE user_id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
    
    def get_user_warnings(self, user_id):
        """Ambil jumlah warning user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT warnings FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    
    def reset_warnings(self, user_id):
        """Reset warning user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET warnings = 0
            WHERE user_id = ?
        ''', (user_id,))
        conn.commit()
        conn.close()
    
    # ===== GROUP OPERATIONS =====
    def add_group(self, group_id, group_name):
        """Tambah grup baru"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO groups (group_id, group_name)
            VALUES (?, ?)
        ''', (group_id, group_name))
        conn.commit()
        conn.close()
    
    def get_group(self, group_id):
        """Ambil data grup"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM groups WHERE group_id = ?', (group_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    # ===== GAME OPERATIONS =====
    def add_game_score(self, user_id, group_id, game_name, score):
        """Tambah skor game"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO game_scores (user_id, group_id, game_name, score)
            VALUES (?, ?, ?, ?)
        ''', (user_id, group_id, game_name, score))
        conn.commit()
        conn.close()
    
    def get_leaderboard(self, group_id, game_name, limit=10):
        """Ambil leaderboard untuk game tertentu"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.name, SUM(g.score) as total_score
            FROM game_scores g
            JOIN users u ON g.user_id = u.user_id
            WHERE g.group_id = ? AND g.game_name = ?
            GROUP BY g.user_id
            ORDER BY total_score DESC
            LIMIT ?
        ''', (group_id, game_name, limit))
        results = cursor.fetchall()
        conn.close()
        return results
    
    # ===== LOG OPERATIONS =====
    def add_log(self, group_id, action, actor, target, details=''):
        """Tambah log aksi"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (group_id, action, actor, target, details)
            VALUES (?, ?, ?, ?, ?)
        ''', (group_id, action, actor, target, details))
        conn.commit()
        conn.close()
    
    def get_logs(self, group_id, limit=50):
        """Ambil logs grup"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM logs
            WHERE group_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (group_id, limit))
        results = cursor.fetchall()
        conn.close()
        return results


# Inisialisasi database global
db = Database()
