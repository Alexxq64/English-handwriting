import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import cv2

from utils.preprocessing import fix_emnist_batch
from utils.label_mapping import MAPPING

IMG_SIZE = 28
TRAIN_CSV = 'data/emnist/emnist-byclass-train.csv'
OUTPUT_DIR = 'static/samples'
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_best_sample_for_class(df, target_label, n=50):
    """Находит лучший образец класса по чёткости и центрированности"""
    subset = df[df.iloc[:, 0] == target_label].head(n)
    best_score = -1
    best_img = None
    
    for idx, row in subset.iterrows():
        pixels = row.iloc[1:].values
        img = pixels.reshape(IMG_SIZE, IMG_SIZE).astype('float32')
        
        # Критерий качества: количество чёрных пикселей (не слишком много, не слишком мало)
        black_pixels = np.sum(img < 128)
        # Центрированность: момент инерции
        y, x = np.where(img > 128)
        if len(x) > 0 and len(y) > 0:
            center_x = np.mean(x)
            center_y = np.mean(y)
            centeredness = 1.0 - (abs(center_x - 14) + abs(center_y - 14)) / 28
        else:
            centeredness = 0
        
        # Итоговая оценка
        score = (black_pixels / 784) * 0.5 + centeredness * 0.5
        if score > best_score:
            best_score = score
            best_img = img
    
    return best_img


def polish_image(img):
    """Улучшает внешний вид буквы"""
    # Преобразуем в uint8
    img = (img * 255).astype(np.uint8)
    
    # Бинаризация
    _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    
    # Морфологическое закрытие 
    kernel = np.ones((2, 2), np.uint8)
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    
    # Увеличиваем с интерполяцией
    img_big = cv2.resize(img, (280, 280), interpolation=cv2.INTER_CUBIC)
    
    # Применяем GaussianBlur для сглаживания ступенек
    img_big = cv2.GaussianBlur(img_big, (3, 3), 0)
    
    # Контрастирование
    img_big = cv2.equalizeHist(img_big)
    
    return img_big


def save_samples():
    print("Загрузка данных...")
    df = pd.read_csv(TRAIN_CSV, nrows=300000)
    
    # Только буквы (классы 10-61)
    mask = (df.iloc[:, 0] >= 10) & (df.iloc[:, 0] <= 61)
    df = df[mask]
    
    for orig_label in range(10, 62):
        # Находим лучший образец
        img = get_best_sample_for_class(df, orig_label, n=50)
        if img is None:
            print(f"  Нет образца для класса {orig_label}")
            continue
        
        # Предобработка (как в обучении)
        img_fixed = fix_emnist_batch(np.array([img]))[0]
        
        # Улучшение внешнего вида
        img_polished = polish_image(img_fixed)
        
        # Получаем символ из MAPPING (используем оригинальный класс 10-61)
        symbol = MAPPING.get(orig_label - 10, '?')
        
        filename = f"{symbol}.png"
        safe_name = filename
        filepath = os.path.join(OUTPUT_DIR, safe_name)
        cv2.imwrite(filepath, img_polished)
        print(f"  Сохранён: {symbol} -> {filepath}")
    
    print(f"\nГотово! Образцы сохранены в {OUTPUT_DIR}")


if __name__ == "__main__":
    save_samples()