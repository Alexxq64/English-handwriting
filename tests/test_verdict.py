# tests/test_verdict.py
import pytest
from utils.verdict import get_verdict, get_verdict_color, get_verdict_by_score


class TestVerdict:
    
    # Тесты для get_verdict
    @pytest.mark.parametrize("score,expected", [
        (100, "Excellent"),
        (90, "Excellent"),
        (76, "Excellent"),
        (75, "Good"),
        (60, "Good"),
        (51, "Good"),
        (50, "Fair"),
        (40, "Fair"),
        (26, "Fair"),
        (25, "Bad"),
        (10, "Bad"),
        (0, "Bad"),
    ])
    def test_get_verdict(self, score, expected):
        assert get_verdict(score) == expected
    
    # Тесты для get_verdict_color
    @pytest.mark.parametrize("verdict,expected_color", [
        ("Excellent", "#2ecc71"),
        ("Good", "#27ae60"),
        ("Fair", "#f39c12"),
        ("Bad", "#e74c3c"),
        ("Unknown", "#cccccc"),
    ])
    def test_get_verdict_color(self, verdict, expected_color):
        assert get_verdict_color(verdict) == expected_color
    
    # Тесты для get_verdict_by_score
    @pytest.mark.parametrize("score,expected_verdict,expected_color", [
        (100, "Excellent", "#2ecc71"),
        (80, "Excellent", "#2ecc71"),
        (76, "Excellent", "#2ecc71"),
        (75, "Good", "#27ae60"),
        (60, "Good", "#27ae60"),
        (51, "Good", "#27ae60"),
        (50, "Fair", "#f39c12"),
        (30, "Fair", "#f39c12"),
        (26, "Fair", "#f39c12"),
        (25, "Bad", "#e74c3c"),
        (0, "Bad", "#e74c3c"),
    ])
    def test_get_verdict_by_score(self, score, expected_verdict, expected_color):
        verdict, color = get_verdict_by_score(score)
        assert verdict == expected_verdict
        assert color == expected_color
    
    def test_get_verdict_by_score_returns_tuple(self):
        result = get_verdict_by_score(80)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], str)