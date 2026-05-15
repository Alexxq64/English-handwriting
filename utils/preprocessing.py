import numpy as np

def preprocess_emnist_image(img):
    """
    Поворот + отражение + нормализация
    """
    img = np.rot90(img)
    img = np.fliplr(img)
    return img.astype('float32') / 255.0


def preprocess_canvas_image(img):
    """
    Только нормализация для canvas.
    БЕЗ поворотов и зеркалирования.
    """

    return img.astype('float32') / 255.0

def fix_emnist_batch(images):
    """
    Только ориентация + нормализация
    (ИНВЕРСИЯ УБРАНА)
    """
    images = np.rot90(images, axes=(1, 2))
    images = np.fliplr(images)
    return images.astype('float32') / 255.0