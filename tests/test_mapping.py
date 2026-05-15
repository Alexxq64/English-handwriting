# tests/test_mapping.py
import pytest
from utils.label_mapping import get_symbol, get_index, MAPPING

class TestLabelMapping:
    
    @pytest.mark.parametrize("idx,expected", [
        (10, 'A'),
        (36, 'a'),
        (61, 'z'),
        (99, '?')
    ])
    def test_get_symbol(self, idx, expected):
        assert get_symbol(idx) == expected
    
    @pytest.mark.parametrize("sym,expected", [
        ('A', 10),
        ('a', 36),
        ('Z', 35),
        ('?', -1)
    ])
    def test_get_index(self, sym, expected):
        assert get_index(sym) == expected
    
    def test_all_indices_roundtrip(self):
        """Проверка: index -> symbol -> index = исходный index"""
        for i in range(62):
            assert get_index(get_symbol(i)) == i
    
    def test_mapping_has_62_items(self):
        assert len(MAPPING) == 62
    
    def test_first_10_are_digits(self):
        for i in range(10):
            assert MAPPING[i].isdigit()
    
    def test_uppercase_letters(self):
        for i in range(10, 36):
            assert MAPPING[i].isupper()
    
    def test_lowercase_letters(self):
        for i in range(36, 62):
            assert MAPPING[i].islower()