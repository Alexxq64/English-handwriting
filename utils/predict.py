import numpy as np
from utils.label_mapping import get_symbol, MAPPING
from utils.preprocess import preprocess_from_canvas
from utils.verdict import get_verdict
from utils.image_utils import decode_base64_image, analyze_image_for_dot
from utils.postprocess import postprocess

def predict_letter(model, data):
    target = data.get('target', '')
    if len(target) != 1:
        return None, 'Нет целевой буквы', 400
    
    minY = data.get('minY')
    maxY = data.get('maxY')
    height = data.get('height')
    width = data.get('width')
    
    img = decode_base64_image(data['image'])
    tensor = preprocess_from_canvas(img)
    pred = model.predict(tensor, verbose=0)
    
    img_28 = (tensor[0, :, :, 0] * 255).astype(np.uint8)
    has_dot, img_minY, img_maxY, img_height = analyze_image_for_dot(img_28)
    
    print(f"[LOG] Целевая буква: '{target}'", flush=True)
    if minY is not None:
        print(f"[LOG] Геометрия с клиента: minY={minY}, maxY={maxY}, height={height}, width={width}", flush=True)
    print(f"[LOG] Анализ 28x28: has_dot={has_dot}, minY={img_minY}, maxY={img_maxY}, height={img_height}", flush=True)
    
    top_indices = np.argsort(pred[0])[::-1][:3]
    top_predictions = [(get_symbol(idx), pred[0][idx] * 100) for idx in top_indices]
    
    print(f"[LOG] Топ-3 предсказания:", flush=True)
    for symbol, prob in top_predictions:
        print(f"        {symbol}: {prob:.1f}%", flush=True)
    
    # Найти уверенность в целевой букве
    target_idx = None
    for k, v in MAPPING.items():
        if v == target:
            target_idx = k
            break
    
    confidence_target = float(pred[0][target_idx] * 100) if target_idx is not None else 0.0
    print(f"[LOG] Уверенность для '{target}': {confidence_target:.1f}%", flush=True)
    
    idx = np.argmax(pred)
    predicted = get_symbol(idx)
    original_confidence = float(pred[0][idx] * 100)
    
    print(f"[LOG] Исходное предсказание: '{predicted}' ({original_confidence:.1f}%)", flush=True)
    
    corrected = predicted
    confidence = original_confidence
    
    corrected, confidence = postprocess(
        corrected, confidence, top_predictions, img_28, 
        minY, maxY, has_dot, img_maxY, target
    )
    
    # Итоговая уверенность для оценки
    if corrected == target:
        final_confidence = max(confidence, confidence_target)
    else:
        final_confidence = confidence_target
    
    correct = (corrected == target)
    verdict = get_verdict(final_confidence)
    
    print(f"[LOG] Финальный результат: '{corrected}' (уверенность {int(final_confidence)}%)", flush=True)
    print(f"[LOG] correct={correct}, score={int(final_confidence)}%", flush=True)
    print("", flush=True)
    
    final_confidence = float(final_confidence)
    
    return {
        'predicted': corrected,
        'confidence': final_confidence,
        'score': int(final_confidence),
        'verdict': verdict,
        'correct': correct,
        'top_predictions': [(sym, float(prob)) for sym, prob in top_predictions]
    }, None, 200