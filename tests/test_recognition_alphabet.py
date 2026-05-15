import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import sys
import cv2
import numpy as np

import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)

from tensorflow.keras.models import load_model
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.label_mapping import get_symbol
from utils.preprocess import preprocess_from_canvas
from utils.verdict import get_verdict


model = load_model('models/cnn_model.keras')
print("Модель загружена")


TOP_LINE_Y = 50      # верхняя (прописные)
MID_LINE_Y = 110     # средняя (строчные)
BASE_LINE_Y = 180    # базовая


def create_canvas_with_lines():
    canvas = np.zeros((280, 280), dtype=np.uint8)
    cv2.line(canvas, (0, TOP_LINE_Y), (280, TOP_LINE_Y), 80, 1)
    cv2.line(canvas, (0, MID_LINE_Y), (280, MID_LINE_Y), 120, 1)
    cv2.line(canvas, (0, BASE_LINE_Y), (280, BASE_LINE_Y), 160, 2)
    return canvas


def detect_case_by_lines(canvas):
    ys, xs = np.where(canvas > 50)
    if len(ys) == 0:
        return "unknown"
    
    min_y = ys.min()
    max_y = ys.max()
    
    # Прописная
    if min_y <= TOP_LINE_Y + 15 and max_y <= BASE_LINE_Y - 20:
        return "upper"
    # Строчная
    elif min_y >= MID_LINE_Y - 20 and max_y <= BASE_LINE_Y + 10:
        return "lower"
    # Строчная с хвостом
    elif min_y >= MID_LINE_Y - 20 and max_y > BASE_LINE_Y + 15:
        return "lower_tail"
    else:
        return "unknown"


def get_sample_image_handwritten(letter, font_path="static/fonts/Caveat-Regular.ttf"):
    """Создаёт картинку-образец из TTF шрифта"""
    size = 280
    img = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype(font_path, 160)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), letter, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (size - w) // 2
    y = (size - h) // 2 - 60
    
    draw.text((x, y), letter, fill=255, font=font)
    return np.array(img)


def get_top_predictions(pred, n=3):
    """Возвращает список топ-n предсказаний (символ, вероятность)"""
    indices = np.argsort(pred[0])[::-1][:n]
    top = []
    for idx in indices:
        symbol = get_symbol(idx)
        prob = pred[0][idx] * 100
        top.append((symbol, prob))
    return top


def get_class_average_image(class_idx, num_samples=50):
    """
    Возвращает усреднённое изображение для заданного класса из тестовой выборки.
    Загружает num_samples случайных изображений этого класса и усредняет.
    """
    import pandas as pd
    from utils.preprocessing import fix_emnist_batch
    
    TEST_CSV = 'data/emnist/emnist-byclass-test.csv'
    
    # Загружаем только нужный класс
    df = pd.read_csv(TEST_CSV, nrows=50000)
    mask = df.iloc[:, 0] == class_idx
    df_class = df[mask].head(num_samples)
    
    if len(df_class) == 0:
        return None
    
    # Усредняем
    avg_img = np.zeros((28, 28), dtype=np.float32)
    for _, row in df_class.iterrows():
        pixels = row.iloc[1:].values
        img = pixels.reshape(28, 28).astype('float32')
        avg_img += img
    
    avg_img /= len(df_class)
    
    # Применяем ту же предобработку, что и при обучении
    avg_img = fix_emnist_batch(np.array([avg_img]))[0]
    
    # Увеличиваем для отображения
    avg_img_big = cv2.resize(avg_img, (280, 280), interpolation=cv2.INTER_LINEAR)
    
    return avg_img_big


def clear_canvas():
    global canvas
    canvas = create_canvas_with_lines()


canvas = create_canvas_with_lines()
drawing = False


def draw(event, x, y, flags, param):
    global canvas, drawing
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        cv2.circle(canvas, (x, y), 4, 255, -1)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False


def run_draw(target_letter):
    global canvas
    clear_canvas()
    
    cv2.namedWindow("DRAW")
    cv2.setMouseCallback("DRAW", draw)
    
    print(f"\nTARGET: {target_letter}")
    print("SPACE=check  C=clear  ESC=back  Q=quit")
    
    while True:
        cv2.imshow("DRAW", canvas)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):
            # Убираем линии для модели
            model_img = canvas.copy()
            model_img[model_img < 200] = 0
            
            tensor = preprocess_from_canvas(model_img)
            pred = model.predict(tensor, verbose=0)
            idx = np.argmax(pred)
            confidence = float(np.max(pred) * 100)
            predicted = get_symbol(idx)
            
            # Определяем регистр по линиям
            case = detect_case_by_lines(model_img)
            case_sensitive = set("CSMUVWXFcsmuvwxfOo")
            
            if predicted in case_sensitive and case != "unknown":
                if case in ("lower", "lower_tail"):
                    predicted = predicted.lower()
                elif case == "upper":
                    predicted = predicted.upper()
            
            ok = predicted == target_letter
            verdict = get_verdict(confidence)
            
            print(f"\n[RESULT] {target_letter} → {predicted} ({confidence:.1f}%) {verdict} {'✓' if ok else '✗'}")
            if case != "unknown":
                print(f"  case by lines: {case}")
            
            # При ошибке выводим топ-3 предсказания и усреднённые изображения
            if not ok:
                top = get_top_predictions(pred, n=3)
                print(f"  Топ-3 предсказания модели:")
                for symbol, prob in top:
                    print(f"    {symbol}: {prob:.1f}%")
                
                # Получаем усреднённые изображения из модели
                target_class = None
                predicted_class = None
                for k, v in label_dict.items():
                    if v == target_letter:
                        target_class = k
                    if v == predicted:
                        predicted_class = k
                
                if target_class is not None:
                    target_avg = get_class_average_image(target_class)
                    if target_avg is not None:
                        cv2.imshow(f"AVG: {target_letter}", target_avg)
                
                if predicted_class is not None:
                    predicted_avg = get_class_average_image(predicted_class)
                    if predicted_avg is not None:
                        cv2.imshow(f"AVG: {predicted}", predicted_avg)
                
                print("  Показаны усреднённые изображения из модели")
        
        elif key == ord('c'):
            clear_canvas()
            print("[CLEAR]")
        
        elif key == 27:
            cv2.destroyAllWindows()
            return
        
        elif key == ord('q'):
            cv2.destroyAllWindows()
            sys.exit()


# Загружаем соответствие класс -> символ
from utils.label_mapping import MAPPING
label_dict = MAPPING

print("Три линии: верхняя, средняя, базовая")
print("Рисуй букву между линиями\n")

while True:
    inp = input("\nБуква (или = для выхода): ")
    
    if inp == '=':
        print("[DONE]")
        break
    
    if len(inp) != 1:
        print("Один символ")
        continue
    
    target_letter = inp
    
    # Показываем образец
    sample = get_sample_image_handwritten(target_letter)
    cv2.imshow("SAMPLE", sample)
    print("Нажми любую клавишу на окне SAMPLE")
    cv2.waitKey(0)
    cv2.destroyWindow("SAMPLE")
    
    run_draw(target_letter)

cv2.destroyAllWindows()