# tests/test_preprocess.py
import pytest
import numpy as np
from utils.preprocess import preprocess_from_canvas, preprocess_word

class TestPreprocessSingle:
    
    def test_output_shape(self):
        img = np.zeros((100, 100), dtype=np.uint8)
        img[25:75, 25:75] = 255
        result = preprocess_from_canvas(img)
        assert result.shape == (1, 28, 28, 1)
    
    def test_values_normalized(self):
        img = np.zeros((50, 50), dtype=np.uint8)
        img[10:40, 10:40] = 255
        result = preprocess_from_canvas(img)
        assert result.min() >= 0.0
        assert result.max() <= 1.0
    
    def test_empty_canvas(self):
        img = np.zeros((100, 100), dtype=np.uint8)
        result = preprocess_from_canvas(img)
        assert result.shape == (1, 28, 28, 1)


class TestPreprocessWord:
    
    def test_split_simple_word(self):
        # Белые квадраты на чёрном
        img = np.zeros((100, 300), dtype=np.uint8)
        img[20:80, 20:60] = 255
        img[20:80, 120:160] = 255
        img[20:80, 220:260] = 255
        
        result = preprocess_word(img)
        assert len(result) == 3
        for letter in result:
            assert letter.shape == (1, 28, 28, 1)
    
    def test_empty_word(self):
        img = np.zeros((100, 100), dtype=np.uint8)
        result = preprocess_word(img)
        assert result == []