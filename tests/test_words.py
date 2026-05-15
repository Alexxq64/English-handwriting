# tests/test_words.py
import pytest
from utils.words import get_words_by_level, get_random_word


class TestWords:
    
    def test_get_words_by_level_1(self):
        """Уровень 1 возвращает список слов"""
        words = get_words_by_level(1)
        assert isinstance(words, list)
        assert len(words) > 0
    
    def test_get_words_by_level_2(self):
        """Уровень 2 возвращает список слов"""
        words = get_words_by_level(2)
        assert isinstance(words, list)
        assert len(words) > 0
    
    def test_get_words_by_level_3(self):
        """Уровень 3 возвращает список слов"""
        words = get_words_by_level(3)
        assert isinstance(words, list)
        assert len(words) > 0
    
    def test_invalid_level_returns_test1(self):
        """Неверный уровень (99) возвращает список уровня 1"""
        words = get_words_by_level(99)
        assert words == get_words_by_level(1)
    
    def test_get_random_word_returns_string(self):
        """get_random_word возвращает строку"""
        word = get_random_word(1)
        assert isinstance(word, str)
        assert len(word) > 0
    
    def test_get_random_word_from_level_1(self):
        """Случайное слово из уровня 1 имеет длину 2-3 буквы"""
        for _ in range(20):
            word = get_random_word(1)
            assert 2 <= len(word) <= 3
    
    def test_get_random_word_from_level_2(self):
        """Случайное слово из уровня 2 имеет длину 4-5 букв"""
        for _ in range(20):
            word = get_random_word(2)
            assert 4 <= len(word) <= 5
    
    def test_get_random_word_from_level_3(self):
        """Случайное слово из уровня 3 имеет длину 6-7 букв"""
        for _ in range(20):
            word = get_random_word(3)
            assert 6 <= len(word) <= 7
    
    def test_words_contain_only_letters(self):
        """Все слова состоят только из букв (нет цифр, дефисов, пробелов)"""
        for level in [1, 2, 3]:
            words = get_words_by_level(level)
            for word in words:
                assert word.isalpha(), f"Слово '{word}' содержит небуквенные символы"