// ==================== СОХРАНЕНИЕ ПОПЫТОК ====================

async function saveAttempt(imageDataUrl, targetSymbol, score, predicted) {
    const isUpper = targetSymbol === targetSymbol.toUpperCase() && 
                    targetSymbol !== targetSymbol.toLowerCase();
    const subkey = isUpper ? 'upper' : 'lower';
    const category = (targetSymbol >= '0' && targetSymbol <= '9') ? 'digits' : 'letters';
    
    try {
        await fetch('/save_attempt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                category: category,
                key: targetSymbol.toUpperCase(),
                subkey: category === 'letters' ? subkey : null,
                image: imageDataUrl,
                score: score,
                predicted: predicted
            })
        });
    } catch (error) {
        console.error('Ошибка сохранения:', error);
    }
}