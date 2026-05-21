import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import warnings
warnings.filterwarnings('ignore')

import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)

import sys
sys.stdout.reconfigure(line_buffering=True)

import numpy as np
from flask import Flask, render_template, request, jsonify
from tensorflow.keras.models import load_model
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

from utils.label_mapping import get_symbol
from utils.image_utils import decode_base64_image
from utils.predict import predict_letter
from routes import bp

app = Flask(__name__)
app.register_blueprint(bp)

print("Загрузка модели...", flush=True)
model = load_model('models/cnn_model.keras')
print("Модель загружена", flush=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/letter/<symbol>')
def letter_mode(symbol):
    return render_template('letter_mode.html')

@app.route('/test/<level>')
def test_mode(level):
    return render_template('test_mode.html')

@app.route('/manual_test')
def manual_test():
    return render_template('manual_test.html')

@app.route('/predict_word', methods=['POST'])
def predict_word():
    try:
        data = request.get_json()
        if not data or 'image' not in data or 'target_word' not in data:
            return jsonify({'error': 'Нет изображения или целевого слова'}), 400
        
        target_word = data.get('target_word', '').lower()
        img = decode_base64_image(data['image'])
        
        from utils.preprocess import preprocess_word
        letters = preprocess_word(img)
        
        if len(letters) == 0:
            return jsonify({'error': 'Буквы не найдены'}), 400
        
        total_score = 0
        results = []
        
        for i in range(min(len(letters), len(target_word))):
            tensor = letters[i]
            pred = model.predict(tensor, verbose=0)
            idx = np.argmax(pred)
            predicted = get_symbol(idx)
            score = float(pred[0][idx] * 100)
            total_score += score
            results.append({
                'target': target_word[i],
                'predicted': predicted,
                'score': int(score),
                'correct': (predicted == target_word[i].upper() or predicted == target_word[i])
            })
        
        avg_score = total_score / len(target_word)
        
        return jsonify({
            'letters': results,
            'avg_score': avg_score
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict():
    print("=" * 50, flush=True)
    print("PREDICT CALLED", flush=True)
    print("=" * 50, flush=True)
    
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'Нет изображения'}), 400
        
        result, error, status = predict_letter(model, data)
        if error:
            return jsonify({'error': error}), status
        
        return jsonify(result)
        
    except Exception as e:
        print(f"[ERROR] {str(e)}", flush=True)
        return jsonify({'error': str(e)}), 500
    

from utils.storage import load_storage, update_best_attempt

@app.route('/save_attempt', methods=['POST'])
def save_attempt():
    data = request.get_json()
    update_best_attempt(
        data['category'],
        data['key'],
        data.get('subkey'),
        data['image'],
        data['score'],
        data['predicted']
    )
    return jsonify({'status': 'ok'})

# Маршрут /best_attempts вынесен в routes/best_attempts.py

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)