from flask import Flask, render_template, request, jsonify
from a import generate_ai_notes, play_tune, EMOTION_SCALES
import threading

app = Flask(__name__)
from flask_cors import CORS
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    emotion = data.get('emotion')

    if emotion not in EMOTION_SCALES:
        return jsonify({'error': 'Invalid emotion!'})

    notes = generate_ai_notes(emotion)
    
    # Run play_tune() in a separate thread without blocking Flask
    threading.Thread(target=play_tune, args=(notes,), daemon=True).start()

    return jsonify({'notes': notes})

if __name__ == '__main__':
    app.run(debug=True)
