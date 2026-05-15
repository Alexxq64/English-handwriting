# utils/verdict.py

def get_verdict(score: float) -> str:
    """
    Преобразует числовой SCORE (процент точности) в текстовый вердикт.
    
    Параметры:
        score (float): число от 0 до 100
    
    Возвращает:
        str: 'Excellent', 'Good', 'Fair' или 'Bad'
    """
    if score >= 76:
        return "Excellent"
    elif score >= 51:
        return "Good"
    elif score >= 26:
        return "Fair"
    else:
        return "Bad"


def get_verdict_color(verdict: str) -> str:
    """
    Возвращает цвет для визуальной индикации вердикта.
    
    Параметры:
        verdict (str): 'Excellent', 'Good', 'Fair' или 'Bad'
    
    Возвращает:
        str: название цвета (для CSS)
    """
    colors = {
        "Excellent": "#2ecc71",  # зелёный
        "Good": "#27ae60",       # тёмно-зелёный
        "Fair": "#f39c12",       # оранжевый
        "Bad": "#e74c3c"         # красный
    }
    return colors.get(verdict, "#cccccc")


def get_verdict_by_score(score: float) -> tuple:
    """
    Возвращает одновременно вердикт и его цвет.
    
    Параметры:
        score (float): число от 0 до 100
    
    Возвращает:
        tuple: (verdict, color)
    """
    verdict = get_verdict(score)
    color = get_verdict_color(verdict)
    return verdict, color