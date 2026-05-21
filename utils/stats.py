def compute_letter_stats(data):
    """Вычисляет avg_score, avg_count, max_error_count для буквы"""
    best_list = data.get('best', [])
    stats = data.get('stats', {})
    
    if stats.get('attempts_count', 0) > 0:
        avg_score = stats['total_score'] // stats['attempts_count']
        avg_count = stats['attempts_count']
    else:
        if best_list:
            total = sum(a['score'] for a in best_list)
            avg_score = total // len(best_list)
            avg_count = len(best_list)
        else:
            avg_score = 0
            avg_count = 0
    
    confusion = data.get('confusion', {})
    if confusion:
        max_error_count = max(confusion.values())
    else:
        max_error_count = 0
    
    return avg_score, avg_count, max_error_count


def compute_digit_stats(data):
    """Вычисляет avg_score, avg_count, max_error_count для цифры"""
    best_list = data.get('best', [])
    stats = data.get('stats', {})
    
    if stats.get('attempts_count', 0) > 0:
        avg_score = stats['total_score'] // stats['attempts_count']
        avg_count = stats['attempts_count']
    else:
        if best_list:
            total = sum(a['score'] for a in best_list)
            avg_score = total // len(best_list)
            avg_count = len(best_list)
        else:
            avg_score = 0
            avg_count = 0
    
    confusion = data.get('confusion', {})
    if confusion:
        max_error_count = max(confusion.values())
    else:
        max_error_count = 0
    
    return avg_score, avg_count, max_error_count