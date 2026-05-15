import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import warnings
warnings.filterwarnings('ignore')

import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)

import sys
sys.stdout.reconfigure(line_buffering=True)

import base64
import cv2
import numpy as np
from flask import Flask, request, jsonify, render_template
from tensorflow.keras.models import load_model
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

from utils.label_mapping import get_symbol, MAPPING
from utils.preprocess import preprocess_from_canvas
from utils.verdict import get_verdict

app = Flask(__name__)

# Загрузка модели
print("Загрузка модели...", flush=True)
model = load_model('models/cnn_model.keras')
print("Модель загружена", flush=True)

# Словарь для преобразования
label_dict = MAPPING

def decode_base64_image(base64_str):
    """Декодирует base64 строку в numpy массив"""
    if ',' in base64_str:
        base64_str = base64_str.split(',')[1]
    
    img_data = base64.b64decode(base64_str)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/letter/<symbol>')
def letter_mode(symbol):
    return render_template('letter_mode.html')

@app.route('/test/<level>')
def test_mode(level):
    """Страница теста"""
    return render_template('test_mode.html')

@app.route('/predict', methods=['POST'])
def predict():
    print("=" * 50, flush=True)
    print("PREDICT CALLED", flush=True)
    print("=" * 50, flush=True)
    
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'Нет изображения'}), 400
        
        target = data.get('target', '')
        if len(target) != 1:
            return jsonify({'error': 'Нет целевой буквы'}), 400
        
        # Получаем геометрические параметры
        minY = data.get('minY')
        maxY = data.get('maxY')
        height = data.get('height')
        width = data.get('width')
        
        print(f"[LOG] Целевая буква: '{target}'", flush=True)
        if minY is not None:
            print(f"[LOG] Геометрия: minY={minY}, maxY={maxY}, height={height}, width={width}", flush=True)
        
        img = decode_base64_image(data['image'])
        tensor = preprocess_from_canvas(img)
        pred = model.predict(tensor, verbose=0)
        
        # Топ-3 предсказания
        top_indices = np.argsort(pred[0])[::-1][:3]
        print(f"[LOG] Топ-3 предсказания:", flush=True)
        for idx in top_indices:
            symbol = get_symbol(idx)
            prob = pred[0][idx] * 100
            print(f"        {symbol}: {prob:.1f}%", flush=True)
        
        # Уверенность для целевой буквы
        target_idx = None
        for k, v in label_dict.items():
            if v == target:
                target_idx = k
                break
        
        if target_idx is not None:
            confidence_for_target = float(pred[0][target_idx] * 100)
            print(f"[LOG] Уверенность для '{target}': {confidence_for_target:.1f}%", flush=True)
        else:
            confidence_for_target = 0.0
            print(f"[LOG] Буква '{target}' не найдена", flush=True)
        
        # Предсказанная буква
        idx = np.argmax(pred)
        predicted = get_symbol(idx)
        print(f"[LOG] Предсказано: '{predicted}'", flush=True)
        
        # Исправление регистра для визуально похожих пар
        MID_LINE = 110
        CASE_PAIRS = ['C', 'S', 'U', 'V', 'W', 'X', 'Z', 'O', 'P', 'I', 'Y', 'N', 'M']        
        if minY is not None and predicted.upper() in CASE_PAIRS:
            is_upper = minY < MID_LINE
            expected = predicted.upper() if is_upper else predicted.lower()
            if predicted != expected:
                pred_confidence = float(pred[0][np.argmax(pred)] * 100)
                target_confidence = confidence_for_target
                total_confidence = pred_confidence + target_confidence
                if total_confidence > 100:
                    total_confidence = 100
                
                print(f"[LOG] Исправлен регистр: {predicted} -> {expected}", flush=True)
                print(f"[LOG] Сложение: {pred_confidence:.1f}% + {target_confidence:.1f}% = {total_confidence:.1f}%", flush=True)
                
                predicted = expected
                confidence_for_target = total_confidence
        
        # Исправление: 0 → O или o в зависимости от высоты
        if minY is not None and predicted == '0' and target.upper() == 'O':
            is_upper = minY < MID_LINE
            expected = 'O' if is_upper else 'o'
            if predicted != expected:
                pred_confidence = float(pred[0][np.argmax(pred)] * 100)
                target_confidence = confidence_for_target
                total_confidence = pred_confidence + target_confidence
                if total_confidence > 100:
                    total_confidence = 100
                
                print(f"[LOG] Исправлен 0 -> {expected} (minY={minY}, is_upper={is_upper})", flush=True)
                print(f"[LOG] Сложение: {pred_confidence:.1f}% + {target_confidence:.1f}% = {total_confidence:.1f}%", flush=True)
                
                predicted = expected
                confidence_for_target = total_confidence
        
        correct = (predicted == target)
        verdict = get_verdict(confidence_for_target)
        
        print(f"[LOG] Результат: correct={correct}, score={int(confidence_for_target)}%", flush=True)
        print("", flush=True)
        
        return jsonify({
            'predicted': predicted,
            'confidence': confidence_for_target,
            'score': int(confidence_for_target),
            'verdict': verdict,
            'correct': correct
        })
        
    except Exception as e:
        print(f"[ERROR] {str(e)}", flush=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)