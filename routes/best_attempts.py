from flask import render_template
from routes import bp
from utils.storage import load_storage
from utils.stats import compute_letter_stats, compute_digit_stats


@bp.route('/best_attempts')
def best_attempts():
    storage = load_storage()
    
    # Вычисляем статистику для каждой буквы
    for letter, data in storage.get('letters', {}).items():
        for case in ['upper', 'lower']:
            if case in data:
                avg_score, avg_count, max_error_count = compute_letter_stats(data[case])
                data[case]['avg_score'] = avg_score
                data[case]['avg_count'] = avg_count
                data[case]['max_error_count'] = max_error_count
    
    # Вычисляем статистику для каждой цифры
    for digit, data in storage.get('digits', {}).items():
        avg_score, avg_count, max_error_count = compute_digit_stats(data)
        data['avg_score'] = avg_score
        data['avg_count'] = avg_count
        data['max_error_count'] = max_error_count
    
    return render_template('best_attempts.html', storage=storage)