import random
import json
from config import TRIVIA_QUESTIONS, GAMES_TIMEOUT

class GameManager:
    """Manager untuk semua games di bot"""
    
    def __init__(self):
        self.active_games = {}  # Tracking games yang sedang berlangsung
    
    # ===== TRIVIA GAME =====
    def start_trivia(self, group_id):
        """Mulai game trivia"""
        question = random.choice(TRIVIA_QUESTIONS)
        question_id = id(question)
        
        self.active_games[group_id] = {
            'type': 'trivia',
            'question': question['question'],
            'options': question['options'],
            'answer': question['answer'],
            'question_id': question_id,
            'answered_by': []
        }
        
        options_text = '\n'.join([f"{i+1}. {opt}" for i, opt in enumerate(question['options'])])
        
        message = f"""
🎮 *TRIVIA TIME!* 🎮

❓ *Pertanyaan:* {question['question']}

{options_text}

💡 Balas dengan nomor (1-4) untuk menjawab!
⏱️ Timeout: {GAMES_TIMEOUT} detik
"""
        return message
    
    def answer_trivia(self, group_id, user_id, user_name, answer):
        """User menjawab trivia"""
        if group_id not in self.active_games:
            return None
        
        game = self.active_games[group_id]
        
        if game['type'] != 'trivia':
            return None
        
        if user_id in [u[0] for u in game['answered_by']]:
            return "⚠️ Kamu sudah menjawab pertanyaan ini!"
        
        try:
            answer_num = int(answer) - 1
            if answer_num < 0 or answer_num >= len(game['options']):
                return "❌ Pilihan tidak valid! Pilih 1-4"
            
            selected_answer = game['options'][answer_num]
            is_correct = selected_answer == game['answer']
            
            game['answered_by'].append((user_id, user_name, is_correct))
            
            if is_correct:
                return f"✅ *{user_name}* BENAR! Jawaban: *{game['answer']}* 🎉"
            else:
                return f"❌ *{user_name}* salah. Jawaban yang benar: *{game['answer']}*"
        
        except ValueError:
            return "❌ Format tidak valid! Balas dengan angka 1-4"
    
    def end_trivia(self, group_id):
        """Akhiri game trivia"""
        if group_id not in self.active_games:
            return None
        
        game = self.active_games[group_id]
        
        if game['type'] != 'trivia':
            return None
        
        # Hitung skor
        correct_answers = [(name, user_id) for user_id, name, correct in game['answered_by'] if correct]
        
        if not correct_answers:
            result = "😢 Tidak ada yang benar!"
        else:
            winner_name, winner_id = correct_answers[0]
            result = f"🏆 *PEMENANG:* {winner_name}\n\n✅ Jawab benar: {len(correct_answers)}\n❌ Jawab salah: {len(game['answered_by']) - len(correct_answers)}"
        
        del self.active_games[group_id]
        return result
    
    # ===== DICE GAME =====
    def start_dice_game(self, group_id):
        """Mulai game dadu"""
        self.active_games[group_id] = {
            'type': 'dice',
            'bets': {},  # user_id: (bet_amount, predicted_number)
            'result': None
        }
        
        message = """
🎲 *DICE GAME STARTED!* 🎲

📝 Cara bermain:
1️⃣ Pilih angka 1-6 yang menurut kamu akan keluar
2️⃣ Ketik: !bet <angka> (contoh: !bet 5)

⏱️ Betting dibuka selama 30 detik...
Setelah itu dadu akan dilempar!

💰 Menang = +100 poin
❌ Kalah = -50 poin
"""
        return message
    
    def place_bet(self, group_id, user_id, user_name, prediction):
        """User memasang taruhan"""
        if group_id not in self.active_games:
            return "❌ Tidak ada game dice yang aktif!"
        
        game = self.active_games[group_id]
        
        if game['type'] != 'dice':
            return "❌ Game yang sedang berlangsung bukan dice!"
        
        try:
            num = int(prediction)
            if num < 1 or num > 6:
                return "❌ Pilihan harus antara 1-6!"
            
            if user_id in game['bets']:
                return f"⚠️ {user_name} sudah memasang taruhan!"
            
            game['bets'][user_id] = (user_name, num)
            return f"✅ {user_name} memasang taruhan: *{num}* 🎲"
        
        except ValueError:
            return "❌ Format tidak valid! Gunakan !bet <angka>"
    
    def roll_dice(self, group_id):
        """Lempar dadu"""
        if group_id not in self.active_games:
            return None
        
        game = self.active_games[group_id]
        
        if game['type'] != 'dice':
            return None
        
        result = random.randint(1, 6)
        game['result'] = result
        
        message = f"🎲 *HASIL DADU:* `{result}` 🎲\n\n"
        
        winners = []
        losers = []
        
        for user_id, (user_name, prediction) in game['bets'].items():
            if prediction == result:
                winners.append((user_id, user_name))
                message += f"✅ {user_name} MENANG! +100 poin\n"
            else:
                losers.append((user_id, user_name))
                message += f"❌ {user_name} kalah. -50 poin\n"
        
        del self.active_games[group_id]
        
        return message, winners, losers
    
    # ===== WORD GAME =====
    def start_word_game(self, group_id):
        """Mulai game tebak kata"""
        words = ['PYTHON', 'JAVASCRIPT', 'DATABASE', 'ALGORITHM', 'PROGRAMMING']
        word = random.choice(words)
        
        shuffled = ''.join(random.sample(word, len(word)))
        
        self.active_games[group_id] = {
            'type': 'word',
            'word': word,
            'shuffled': shuffled,
            'answered_by': []
        }
        
        message = f"""
🔤 *WORD GAME!* 🔤

📝 Atur huruf-huruf ini menjadi satu kata:
*{shuffled}*

💡 Panjang kata: {len(word)} huruf
⏱️ Waktu: {GAMES_TIMEOUT} detik

Balas dengan jawaban kamu!
"""
        return message
    
    def answer_word_game(self, group_id, user_id, user_name, answer):
        """User menjawab word game"""
        if group_id not in self.active_games:
            return None
        
        game = self.active_games[group_id]
        
        if game['type'] != 'word':
            return None
        
        if user_id in [u[0] for u in game['answered_by']]:
            return "⚠️ Kamu sudah menjawab!"
        
        is_correct = answer.upper() == game['word']
        game['answered_by'].append((user_id, user_name, is_correct))
        
        if is_correct:
            return f"✅ *{user_name}* BENAR! Kata: *{game['word']}* 🎉"
        else:
            return f"❌ *{user_name}* salah"
    
    def end_word_game(self, group_id):
        """Akhiri word game"""
        if group_id not in self.active_games:
            return None
        
        game = self.active_games[group_id]
        
        if game['type'] != 'word':
            return None
        
        correct = [name for uid, name, is_correct in game['answered_by'] if is_correct]
        
        if not correct:
            result = f"😢 Tidak ada yang benar!\nKata yang benar: *{game['word']}*"
        else:
            result = f"🏆 *PEMENANG:* {correct[0]}\n\nKata: *{game['word']}*"
        
        del self.active_games[group_id]
        return result
    
    # ===== COIN FLIP =====
    def coin_flip(self):
        """Game coin flip"""
        result = random.choice(['HEADS', 'TAILS'])
        emoji = '🪙' if result == 'HEADS' else '🪙'
        
        return f"{emoji} Hasil coin flip: *{result}*"
    
    # ===== ROULETTE =====
    def russian_roulette(self, group_id, user_id, user_name):
        """Game Russian Roulette (fun version)"""
        chambers = [True] + [False] * 5
        is_hit = random.choice(chambers)
        
        if is_hit:
            return f"💥 *BOOM!* {user_name} tertembak! 💀\n(Ini hanya game, santai aja 😄)"
        else:
            return f"😅 *CLICK!* {user_name} selamat! Peluru tidak ada di revolver ini 🔫"


# Inisialisasi game manager
game_manager = GameManager()
