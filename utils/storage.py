import json
import os
from datetime import datetime

STORAGE_FILE = 'best_attempts.json'

def load_storage():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'r') as f:
            return json.load(f)
    return {
        'letters': {},
        'digits': {}
    }

def save_storage(data):
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def update_best_attempt(category, key, subkey, image_data, score, predicted):
    storage = load_storage()
    
    if category not in storage:
        storage[category] = {}
    if key not in storage[category]:
        storage[category][key] = {} if category == 'letters' else {'best': [], 'confusion': {}, 'stats': {'total_score': 0, 'attempts_count': 0}}
    
    if category == 'letters':
        if subkey not in storage[category][key]:
            storage[category][key][subkey] = {'best': [], 'confusion': {}, 'stats': {'total_score': 0, 'attempts_count': 0}}
        target = storage[category][key][subkey]
    else:
        target = storage[category][key]
        if 'stats' not in target:
            target['stats'] = {'total_score': 0, 'attempts_count': 0}
    
    # 1. Обновляем статистику (все попытки)
    target['stats']['total_score'] = target['stats'].get('total_score', 0) + score
    target['stats']['attempts_count'] = target['stats'].get('attempts_count', 0) + 1
    
    # 2. Обновляем confusion (только если ошибка)
    if predicted != key and (category == 'digits' or (subkey and predicted.lower() != key.lower())):
        conf = target['confusion']
        conf[predicted] = conf.get(predicted, 0) + 1
    
    # 3. Обновляем best (ровно 3 лучших)
    best_list = target['best']
    best_list.append({
        'image': image_data,
        'score': score,
        'timestamp': datetime.now().isoformat()
    })
    best_list.sort(key=lambda x: x['score'], reverse=True)
    target['best'] = best_list[:3]
    
    save_storage(storage)