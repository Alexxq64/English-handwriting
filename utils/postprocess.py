MID_LINE = 110
BASE_LINE_FOR_I_J = 180
CASE_PAIRS = ['C', 'S', 'U', 'V', 'W', 'X', 'Z', 'O', 'P', 'I', 'Y', 'N', 'M']
HIGH_LOWER = ['b', 'd', 'f', 'h', 'k', 'l', 't']

def postprocess(corrected, confidence, top_predictions, img_28, minY, maxY, has_dot, img_maxY, target):
    # 1. Группа i/j/1 (без l)
    if corrected in ['i', 'j', '1']:
        if has_dot:
            actual_maxY = maxY if maxY is not None else img_maxY
            if actual_maxY > BASE_LINE_FOR_I_J:
                expected = 'j'
            else:
                expected = 'i'
        else:
            from utils.image_utils import aspect_ratio
            ar = aspect_ratio(img_28)
            if ar < 0.4:
                expected = 'l'
            else:
                expected = corrected
        
        if expected != corrected:
            conf_boost = 0
            for sym, prob in top_predictions:
                if sym == expected:
                    conf_boost = prob
                    break
            total_confidence = confidence + conf_boost
            new_confidence = min(100, total_confidence)
            print(f"[LOG] Исправлен {corrected} -> {expected} (группа i/j/1, has_dot={has_dot})", flush=True)
            print(f"[LOG] Уверенность: {confidence:.1f}% -> {new_confidence:.1f}%", flush=True)
            corrected = expected
            confidence = new_confidence
    
    # 2. Группа 0/O/o
    elif corrected in ['0', 'O', 'o']:
        from utils.image_utils import aspect_ratio
        ar = aspect_ratio(img_28)
        if 0.8 < ar < 1.2:
            is_upper = minY <= 80 if minY is not None else True
            expected = 'O' if is_upper else 'o'
        else:
            expected = '0'
        
        if expected != corrected:
            conf_boost = 0
            for sym, prob in top_predictions:
                if sym == expected:
                    conf_boost = prob
                    break
            total_confidence = confidence + conf_boost
            new_confidence = min(100, total_confidence)
            print(f"[LOG] Исправлен {corrected} -> {expected} (группа 0/O, ar={ar:.2f})", flush=True)
            print(f"[LOG] Уверенность: {confidence:.1f}% -> {new_confidence:.1f}%", flush=True)
            corrected = expected
            confidence = new_confidence
    
    # 3. Группа T/t/1/I/l
    elif corrected.upper() == 'T' or corrected in ['1', 'I', 'l', 't']:
        from utils.image_utils import has_horizontal_top
        if has_horizontal_top(img_28, threshold=0.35):
            is_upper = minY <= 80 if minY is not None else True
            expected = 'T' if is_upper else 't'
            if expected != corrected:
                conf_boost = 0
                for sym, prob in top_predictions:
                    if sym == expected:
                        conf_boost = prob
                        break
                total_confidence = confidence + conf_boost
                new_confidence = min(100, total_confidence)
                print(f"[LOG] Исправлен {corrected} -> {expected} (T группа: есть горизонтальная черта)", flush=True)
                print(f"[LOG] Уверенность: {confidence:.1f}% -> {new_confidence:.1f}%", flush=True)
                corrected = expected
                confidence = new_confidence
    
    # 4. Исправление регистра для CASE_PAIRS
    if corrected.upper() in CASE_PAIRS:
        if minY is not None:
            if minY <= 80:
                # Зона высоких букв (50-80)
                if corrected.lower() in HIGH_LOWER:
                    is_upper = False   # высокая строчная
                else:
                    is_upper = True    # заглавная
            else:
                is_upper = False       # строчная (i/j 80-110 и остальные >110)
        else:
            is_upper = False
        
        expected = corrected.upper() if is_upper else corrected.lower()
        if expected != corrected:
            print(f"[LOG] Исправлен регистр: {corrected} -> {expected}", flush=True)
            corrected = expected
    
    # 5. Специальный случай: буква f (самая длинная)
    actual_maxY = maxY if maxY is not None else img_maxY
    actual_minY = minY if minY is not None else 0
    letter_height = actual_maxY - actual_minY
    
    # Если высота больше порога — вероятно f
    if letter_height > 100:
        # Проверяем, что модель предсказала похожую букву
        if corrected in ['t', 'F', 'j', 'I', 'l', '1']:
            expected = 'f'
            
            conf_boost = 0
            for sym, prob in top_predictions:
                if sym == expected:
                    conf_boost = prob
                    break
            total_confidence = confidence + conf_boost
            new_confidence = min(100, total_confidence)
            print(f"[LOG] Исправлен {corrected} -> {expected} (высота {letter_height}px > 100, похожая буква)", flush=True)
            print(f"[LOG] Уверенность: {confidence:.1f}% -> {new_confidence:.1f}%", flush=True)
            corrected = expected
            confidence = new_confidence
    
    return corrected, confidence