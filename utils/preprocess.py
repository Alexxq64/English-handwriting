import numpy as np
import cv2
from utils.preprocessing import preprocess_canvas_image


def preprocess_from_canvas(image_bytes, img_size=28):
    """
    Предобработка изображения с canvas.
    Сохраняет пропорции буквы.
    """
    # 1. Оттенки серого
    if len(image_bytes.shape) == 3:
        if image_bytes.shape[2] == 4:
            image = cv2.cvtColor(image_bytes, cv2.COLOR_RGBA2GRAY)
        else:
            image = cv2.cvtColor(image_bytes, cv2.COLOR_RGB2GRAY)
    else:
        image = image_bytes

    # 2. Бинаризация
    _, thresh = cv2.threshold(image, 20, 255, cv2.THRESH_BINARY)

    # 3. Поиск bounding box буквы
    coords = cv2.findNonZero(thresh)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        image = image[y:y+h, x:x+w]
    else:
        # Пустой холст
        return np.zeros((1, img_size, img_size, 1), dtype=np.float32)

    # 4. Выравнивание до квадрата (как в оригинале)
    h, w = image.shape
    if h > w:
        diff = h - w
        left = diff // 2
        right = diff - left
        image = cv2.copyMakeBorder(
            image,
            0, 0, left, right,
            cv2.BORDER_CONSTANT,
            value=0
        )
    else:
        diff = w - h
        top = diff // 2
        bottom = diff - top
        image = cv2.copyMakeBorder(
            image,
            top, bottom, 0, 0,
            cv2.BORDER_CONSTANT,
            value=0
        )

    # 5. Resize до 28×28
    image = cv2.resize(image, (img_size, img_size), interpolation=cv2.INTER_AREA)

    # 6. Нормализация
    image = image.astype('float32') / 255.0

    return image.reshape(1, img_size, img_size, 1)


def preprocess_word(canvas_bytes, img_size=28):
    """Разбивает слово на буквы и обрабатывает каждую"""
    if len(canvas_bytes.shape) == 3:
        if canvas_bytes.shape[2] == 4:
            gray = cv2.cvtColor(canvas_bytes, cv2.COLOR_RGBA2GRAY)
        else:
            gray = cv2.cvtColor(canvas_bytes, cv2.COLOR_RGB2GRAY)
    else:
        gray = canvas_bytes

    _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)

    vertical_projection = np.sum(binary, axis=0)
    empty_cols = vertical_projection == 0

    letter_bounds = []
    in_letter = False
    start = 0

    for i, is_empty in enumerate(empty_cols):
        if not is_empty and not in_letter:
            in_letter = True
            start = i
        elif is_empty and in_letter:
            in_letter = False
            end = i
            if end - start > 5:
                letter_bounds.append((start, end))

    letters = []
    for start, end in letter_bounds:
        letter_img = gray[:, start:end]
        
        # Выравнивание до квадрата
        h, w = letter_img.shape
        if h > w:
            diff = h - w
            left = diff // 2
            right = diff - left
            letter_img = cv2.copyMakeBorder(
                letter_img,
                0, 0, left, right,
                cv2.BORDER_CONSTANT,
                value=0
            )
        else:
            diff = w - h
            top = diff // 2
            bottom = diff - top
            letter_img = cv2.copyMakeBorder(
                letter_img,
                top, bottom, 0, 0,
                cv2.BORDER_CONSTANT,
                value=0
            )
        
        # Resize до 28×28
        letter_img = cv2.resize(letter_img, (img_size, img_size), interpolation=cv2.INTER_AREA)
        
        # Нормализация
        letter_img = letter_img.astype('float32') / 255.0
        
        letters.append(letter_img.reshape(1, img_size, img_size, 1))
    
    return letters