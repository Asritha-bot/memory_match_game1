from flask import Flask, jsonify, render_template
import random

app = Flask(__name__)

class GameConfig:
    def __init__(self):
        self.current_level = 1
        self.score = 0
        self.matched_positions = set()
        # Using emojis instead of images
        self.emojis = [
            '🐶', '🐱', '🐼', '🐨', '🦁', '🐯', 
            '🦊', '🦝', '🐮', '🐷', '🐸', '🐙'
        ]
        self.current_game_emojis = []
    
    def get_level_config(self):
        num_boxes = self.current_level * 2  # Number of pairs increases with level
        selected_emojis = random.sample(self.emojis, num_boxes // 2)
        self.current_game_emojis = selected_emojis * 2  # Double the emojis to create pairs
        random.shuffle(self.current_game_emojis)
        self.matched_positions = set()
        
        return {
            'level': self.current_level,
            'score': self.score,
            'emojis': self.current_game_emojis,
            'display_time': 10000
        }
    
    def positions_matched(self):
        total_positions = len(self.current_game_emojis)
        return len(self.matched_positions) == total_positions
    
    def record_match(self, pos1, pos2):
        self.matched_positions.add(pos1)
        self.matched_positions.add(pos2)

game = GameConfig()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/game-state')
def game_state():
    return jsonify(game.get_level_config())

@app.route('/api/check-match/<int:pos1>/<int:pos2>')
def check_match(pos1, pos2):
    if pos1 == pos2:
        return jsonify({'error': 'Cannot match same position'}), 400
    
    emojis = game.current_game_emojis
    
    if 0 <= pos1 < len(emojis) and 0 <= pos2 < len(emojis):
        is_match = emojis[pos1] == emojis[pos2]
        
        if is_match:
            game.score += 1
            game.record_match(pos1, pos2)
            
            level_complete = game.positions_matched()
            if level_complete:
                game.current_level += 1
            
            return jsonify({
                'match': True,
                'score': game.score,
                'level': game.current_level,
                'levelComplete': level_complete
            })
        
        return jsonify({
            'match': False,
            'score': game.score,
            'level': game.current_level
        })
    
    return jsonify({'error': 'Invalid positions'}), 400

if __name__ == '__main__':
    app.run(debug=True)