# tests/manual_test_model.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
from tensorflow.keras.models import load_model
from utils.label_mapping import get_symbol
from utils.preprocess import preprocess_from_canvas

model = load_model('models/cnn_model.keras')
print("Модель загружена")

img = np.zeros((280, 280), dtype=np.uint8)
drawing = False

def draw_circle(event, x, y, flags, param):
    global drawing, img
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            cv2.circle(img, (x, y), 12, 255, -1)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False

cv2.namedWindow("Нарисуй букву (белым на чёрном)")
cv2.setMouseCallback("Нарисуй букву (белым на чёрном)", draw_circle)

print("Рисуй букву. Пробел → распознать, C → очистить, ESC → выход")

while True:
    cv2.imshow("Нарисуй букву (белым на чёрном)", img)
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord(' '):
        tensor = preprocess_from_canvas(img)
        pred = model.predict(tensor, verbose=0)
        predicted_class = np.argmax(pred)
        confidence = np.max(pred) * 100
        letter = get_symbol(predicted_class)
        print(f"Распознано: {letter} (уверенность: {confidence:.1f}%)")
        
        processed = (tensor[0, :, :, 0] * 255).astype(np.uint8)
        cv2.imshow("После обработки (28x28)", processed)
        
    elif key == ord('c'):
        img.fill(0)
        print("Холст очищен")
        
    elif key == 27:
        break

cv2.destroyAllWindows()