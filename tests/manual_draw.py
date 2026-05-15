# tests/manual_draw.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
from utils.preprocess import preprocess_from_canvas

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

print("Рисуй букву. Пробел → обработка, C → очистить, ESC → выход")

while True:
    cv2.imshow("Нарисуй букву (белым на чёрном)", img)
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord(' '):
        result = preprocess_from_canvas(img)
        result_img = (result[0, :, :, 0] * 255).astype(np.uint8)
        cv2.imshow("После обработки (28x28)", result_img)
    elif key == ord('c'):
        img.fill(0)
    elif key == 27:
        break

cv2.destroyAllWindows()