import base64
import cv2
import numpy as np

def decode_base64_image(base64_str):
    if ',' in base64_str:
        base64_str = base64_str.split(',')[1]
    img_data = base64.b64decode(base64_str)
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def analyze_image_for_dot(img_28):
    height, width = img_28.shape
    minY = height
    maxY = 0
    for y in range(height):
        for x in range(width):
            if img_28[y, x] > 50:
                if y < minY: minY = y
                if y > maxY: maxY = y
    body_height = maxY - minY
    top_limit = min(minY + 5, height)
    top_pixels = 0
    for y in range(top_limit):
        for x in range(width):
            if img_28[y, x] > 50:
                top_pixels += 1
    has_dot = (top_pixels > 3) and (body_height > 10)
    return has_dot, minY, maxY, body_height

def has_horizontal_top(img_28, threshold=0.4):
    h, w = img_28.shape
    top_row = img_28[0, :]
    top_row_width = np.sum(top_row > 50)
    return top_row_width > w * threshold

def has_horizontal_bar(img_28, y_ratio=0.3, threshold=0.3):
    h, w = img_28.shape
    y = int(h * y_ratio)
    if y >= h:
        return False
    row = img_28[y, :]
    return np.sum(row > 50) > w * threshold

def aspect_ratio(img_28):
    h, w = img_28.shape
    return w / h if h > 0 else 0