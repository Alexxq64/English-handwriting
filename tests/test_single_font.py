import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from tensorflow.keras.models import load_model

from utils.label_mapping import get_symbol
from utils.preprocess import preprocess_from_canvas

# Загрузка модели
model = load_model('models/cnn_model.keras')
print("Модель загружена\n")

# Папка со шрифтами
FONTS_DIR = "static/fonts"

# Все 62 символа
ALL_SYMBOLS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

# Проблемные символы для нормализации регистра
CASE_SENSITIVE = set("CSMUVWXFcsmuvwxfOo")

def get_available_fonts():
    """Возвращает список доступных шрифтов"""
    fonts = []
    for file in os.listdir(FONTS_DIR):
        if file.endswith('.ttf'):
            fonts.append(file)
    return sorted(fonts)

def test_font(font_path, font_name):
    """Тестирует шрифт на всех 62 символах"""
    try:
        font = ImageFont.truetype(font_path, 160)
    except:
        print(f"  ОШИБКА: не удалось загрузить шрифт")
        return None
    
    print(f"\n{'='*60}")
    print(f"ТЕСТИРОВАНИЕ ШРИФТА: {font_name}")
    print(f"{'='*60}")
    
    correct = 0
    total = len(ALL_SYMBOLS)
    errors = []
    
    for letter in ALL_SYMBOLS:
        # Создаём картинку 280×280
        size = 280
        canvas = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(canvas)
        
        bbox = draw.textbbox((0, 0), letter, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        
        x = (size - w) // 2
        y = (size - h) // 2
        
        draw.text((x, y), letter, fill=255, font=font)
        
        canvas_np = np.array(canvas)
        tensor = preprocess_from_canvas(canvas_np)
        pred = model.predict(tensor, verbose=0)
        idx = np.argmax(pred)
        predicted = get_symbol(idx)
        conf = float(np.max(pred) * 100)
        
        # Нормализация регистра по высоте буквы
        coords = cv2.findNonZero(canvas_np)
        if coords is not None:
            x, y, w, h = cv2.boundingRect(coords)
            letter_height = h
            case = "upper" if letter_height > 100 else "lower"
        else:
            case = "unknown"
        
        if predicted in CASE_SENSITIVE and case != "unknown":
            if case == "lower":
                predicted = predicted.lower()
            elif case == "upper":
                predicted = predicted.upper()
        
        if predicted == letter:
            correct += 1
            status = "✓"
        else:
            errors.append((letter, predicted, conf))
            status = "✗"
        
        print(f"{status} {letter} → {predicted} ({conf:.1f}%)")
    
    accuracy = correct / total * 100
    
    print(f"\n{'='*60}")
    print(f"РЕЗУЛЬТАТ:")
    print(f"  Правильно: {correct}/{total} = {accuracy:.1f}%")
    
    if errors:
        print(f"\n  ОШИБКИ ({len(errors)}):")
        for letter, predicted, conf in errors:
            print(f"    {letter} → {predicted} (уверенность: {conf:.1f}%)")
    
    print(f"{'='*60}")
    return accuracy

def main():
    # Получаем список доступных шрифтов
    fonts = get_available_fonts()
    
    if not fonts:
        print("ОШИБКА: Нет шрифтов в папке static/fonts/")
        return
    
    print("ДОСТУПНЫЕ ШРИФТЫ:")
    for i, font in enumerate(fonts, 1):
        print(f"  {i}. {font}")
    
    # Выбор шрифта
    while True:
        try:
            choice = input(f"\nВыберите шрифт (1-{len(fonts)}) или 0 для выхода: ")
            if choice == '0':
                print("Выход")
                return
            choice = int(choice)
            if 1 <= choice <= len(fonts):
                break
            print(f"Введите число от 1 до {len(fonts)}")
        except ValueError:
            print("Введите число")
    
    selected_font = fonts[choice - 1]
    font_path = os.path.join(FONTS_DIR, selected_font)
    
    # Тестируем выбранный шрифт
    test_font(font_path, selected_font)

if __name__ == "__main__":
    main()