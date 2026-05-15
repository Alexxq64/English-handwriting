import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from tensorflow.keras.models import load_model

from utils.label_mapping import get_symbol
from utils.preprocess import preprocess_from_canvas

model = load_model('models/cnn_model.keras')
print("Модель загружена\n")

FONTS_DIR = "static/fonts"

ALL_SYMBOLS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
SIMPLE_SYMBOLS = "ABCDEFGHJKLMNPQRTUVWXYZ"
COMPLEX_SYMBOLS = "015IlOSB8cfiops"

def get_fonts():
    fonts = []
    for file in os.listdir(FONTS_DIR):
        if file.endswith('.ttf'):
            fonts.append(file)
    return fonts

def test_font_with_errors(font_path, symbols):
    try:
        font = ImageFont.truetype(font_path, 160)
    except:
        return None, 0, 0, {}
    
    correct = 0
    total = len(symbols)
    errors = {}
    
    for letter in symbols:
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
        

        # Находим bounding box буквы для определения высоты
        coords = cv2.findNonZero(canvas_np)
        if coords is not None:
            x, y, w, h = cv2.boundingRect(coords)
            letter_height = h
            # Если высота буквы больше 100 пикселей (на 280×280) — заглавная
            case = "upper" if letter_height > 100 else "lower"
        else:
            case = "unknown"
        
        case_sensitive = set("CSMUVWXFcsmuvwxfOo")
        
        if predicted in case_sensitive and case != "unknown":
            if case == "lower":
                predicted = predicted.lower()
            elif case == "upper":
                predicted = predicted.upper()
        
        if predicted == letter:
            correct += 1
        else:
            errors[letter] = (predicted, conf)
    
    return font_path, correct, total, errors

print("=" * 70)
print("ТЕСТИРОВАНИЕ ВСЕХ ШРИФТОВ В ПАПКЕ")
print("=" * 70)

fonts = get_fonts()
print(f"Найдено шрифтов: {len(fonts)}")
for f in fonts:
    print(f"  - {f}")

results = {}

for font_file in fonts:
    font_path = os.path.join(FONTS_DIR, font_file)
    font_name = os.path.splitext(font_file)[0]
    
    print(f"\n{'='*70}")
    print(f"ШРИФТ: {font_name}")
    print(f"{'='*70}")
    
    path, correct, total, errors_all = test_font_with_errors(font_path, ALL_SYMBOLS)
    if path is None:
        print(f"  ОШИБКА: не удалось загрузить шрифт")
        continue
    
    all_acc = correct / total * 100
    print(f"  Все символы (62): {correct}/{total} = {all_acc:.1f}%")
    
    if errors_all:
        print(f"\n  ВСЕ ОШИБКИ ({len(errors_all)}):")
        for letter, (predicted, conf) in sorted(errors_all.items()):
            print(f"    {letter} → {predicted} (уверенность: {conf:.1f}%)")
    else:
        print(f"\n  Ошибок нет!")
    
    _, correct_simple, total_simple, _ = test_font_with_errors(font_path, SIMPLE_SYMBOLS)
    simple_acc = correct_simple / total_simple * 100
    print(f"\n  Простые ({len(SIMPLE_SYMBOLS)}): {correct_simple}/{total_simple} = {simple_acc:.1f}%")
    
    _, correct_complex, total_complex, _ = test_font_with_errors(font_path, COMPLEX_SYMBOLS)
    complex_acc = correct_complex / total_complex * 100
    print(f"  Проблемные ({len(COMPLEX_SYMBOLS)}): {correct_complex}/{total_complex} = {complex_acc:.1f}%")
    
    results[font_name] = {
        "all": all_acc,
        "simple": simple_acc,
        "complex": complex_acc,
        "errors": errors_all
    }

print("\n" + "=" * 70)
print("ИТОГОВАЯ ТАБЛИЦА (сортировка по точности на всех символах)")
print("=" * 70)
print(f"{'Шрифт':<40} {'Все 62':<10} {'Простые':<12} {'Проблемные':<10}")
print("-" * 75)

sorted_results = sorted(results.items(), key=lambda x: x[1]["all"], reverse=True)

for font_name, scores in sorted_results:
    print(f"{font_name:<40} {scores['all']:>6.1f}%     {scores['simple']:>6.1f}%       {scores['complex']:>6.1f}%")

print("\n" + "=" * 70)
print(f"ЛУЧШИЙ ШРИФТ ПО ВСЕМ СИМВОЛАМ: {sorted_results[0][0]} ({sorted_results[0][1]['all']:.1f}%)")
print("=" * 70)

best_simple = max(results.items(), key=lambda x: x[1]["simple"])
best_complex = max(results.items(), key=lambda x: x[1]["complex"])

print(f"\nЛучший по простым символам: {best_simple[0]} ({best_simple[1]['simple']:.1f}%)")
print(f"Лучший по проблемным символам: {best_complex[0]} ({best_complex[1]['complex']:.1f}%)")

print("\n" + "=" * 70)
print("СВОДКА ВСЕХ ОШИБОК НА ЛУЧШЕМ ШРИФТЕ:")
print("=" * 70)
best_font_name = sorted_results[0][0]
best_errors = results[best_font_name]["errors"]
if best_errors:
    for letter, (predicted, conf) in sorted(best_errors.items()):
        print(f"  {letter} → {predicted} (уверенность: {conf:.1f}%)")
else:
    print("  Нет ошибок!")
print("=" * 70)