# utils/words.py
import random

# Test 1: слова из 2-3 букв
TEST1_WORDS = [
    "cat", "dog", "sun", "car", "bus", "hat", "leg", "eye", "cup", "bag",
    "ant", "bed", "box", "fox", "hen", "pig", "rat", "pen", "red"
]

# Test 2: слова из 4-5 букв
TEST2_WORDS = [
    "house", "mouse", "apple", "table", "chair", "door",
    "bird", "fish", "horse", "duck", "frog", "star", "moon", "sweet", "happy",
    "bread", "water", "light"
]

# Test 3: слова из 6-7 букв
TEST3_WORDS = [
    "pencil", "teacher", "window", "garden", "flower", "brother", "sister",
    "morning", "evening", "dinner", "bicycle", "blanket", "picture", "project",
    "student", "monster", "kitchen", "weather", "library"
]

def get_words_by_level(level):
    """
    Возвращает список слов для указанного уровня.
    
    Параметры:
        level (int): 1, 2 или 3
    
    Возвращает:
        list: список слов
    """
    if level == 1:
        return TEST1_WORDS.copy()
    elif level == 2:
        return TEST2_WORDS.copy()
    elif level == 3:
        return TEST3_WORDS.copy()
    else:
        return TEST1_WORDS.copy()


def get_random_word(level):
    """
    Возвращает случайное слово для указанного уровня.
    
    Параметры:
        level (int): 1, 2 или 3
    
    Возвращает:
        str: случайное слово
    """
    words = get_words_by_level(level)
    return random.choice(words)