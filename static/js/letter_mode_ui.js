// ==================== UI КОМПОНЕНТЫ ====================

// Заголовок "Тренировка A/a"
function updateTrainingTitle() {
    const titleEl = document.getElementById('trainingTitle');
    if (titleEl && attemptsList.length > 0) {
        const currentTarget = attemptsList[currentAttemptIndex];
        titleEl.textContent = `📝 Тренировка ${currentTarget}`;
        titleEl.style.fontSize = '18px';
        titleEl.style.fontWeight = 'bold';
        titleEl.style.marginBottom = '15px';
        titleEl.style.textAlign = 'center';
    }
}

function drawSampleWithLines() {
    const sampleCanvas = document.getElementById('sampleCanvas');
    if (!sampleCanvas || attemptsList.length === 0) return;
    
    const ctxSample = sampleCanvas.getContext('2d');
    const currentTarget = attemptsList[currentAttemptIndex];
    
    // Очистка и фон
    ctxSample.fillStyle = 'white';
    ctxSample.fillRect(0, 0, 140, 140);
    
    // Рисуем линии (как на основном холсте, но уменьшенные пропорции)
    const scale = 140 / 280;
    const TOP = 50 * scale;
    const MID = 110 * scale;
    const BASE = 180 * scale;
    
    ctxSample.save();
    ctxSample.beginPath();
    ctxSample.moveTo(0, TOP);
    ctxSample.lineTo(140, TOP);
    ctxSample.strokeStyle = '#888';
    ctxSample.lineWidth = 1;
    ctxSample.stroke();
    
    ctxSample.beginPath();
    ctxSample.moveTo(0, MID);
    ctxSample.lineTo(140, MID);
    ctxSample.stroke();
    
    ctxSample.beginPath();
    ctxSample.moveTo(0, BASE);
    ctxSample.lineTo(140, BASE);
    ctxSample.strokeStyle = '#aaa';
    ctxSample.lineWidth = 2;
    ctxSample.stroke();
    
    // Рисуем образец буквы
    // Заглавные буквы и цифры — увеличенный шрифт (73px = 55 * 1.33)
    // Строчные буквы — обычный шрифт (55px)
    const isUpperCase = currentTarget === currentTarget.toUpperCase() && currentTarget !== currentTarget.toLowerCase();
    const isDigit = /[0-9]/.test(currentTarget);
    const fontSize = (isUpperCase || isDigit) ? 73 : 55;
    
    ctxSample.font = `bold ${fontSize}px "Caveat", cursive`;
    ctxSample.fillStyle = 'black';
    ctxSample.textAlign = 'center';
    ctxSample.textBaseline = 'middle';
    
    // Для заглавных и цифр поднимаем выше (yOffset = -8)
    const yOffset = (isUpperCase || isDigit) ? -8 : 0;
    ctxSample.fillText(currentTarget, 70, 75 + yOffset);
    
    ctxSample.restore();
}

function updateDisplay() {
    if (attemptsList.length === 0) return;
    const currentTarget = attemptsList[currentAttemptIndex];
    document.getElementById('attemptCount').textContent = `${currentAttemptIndex + 1} / 10`;
    updateTrainingTitle();
    drawSampleWithLines();
}

function updateScoreDisplay(score) {
    document.getElementById('scoreValue').textContent = score || 0;
}

function showFinalVerdict(avgScore) {
    canvasLocked = true;
    document.getElementById('checkBtn').disabled = true;
    document.getElementById('clearBtn').disabled = true;
    
    let verdict = '';
    let verdictClass = '';
    if (avgScore >= 76) { verdict = 'Excellent!'; verdictClass = 'excellent'; }
    else if (avgScore >= 51) { verdict = 'Good!'; verdictClass = 'good'; }
    else if (avgScore >= 26) { verdict = 'Fair'; verdictClass = 'fair'; }
    else { verdict = 'Bad'; verdictClass = 'bad'; }
    
    const verdictDiv = document.getElementById('resultVerdict');
    verdictDiv.textContent = `Итоговый вердикт: ${verdict}`;
    verdictDiv.className = `result-verdict ${verdictClass}`;
    verdictDiv.style.display = 'block';
}

// Скрыть старые элементы, если они есть
function cleanupOldElements() {
    const oldTargetLetter = document.getElementById('targetLetter');
    if (oldTargetLetter) oldTargetLetter.style.display = 'none';
    
    const oldSampleLetter = document.getElementById('sampleLetter');
    if (oldSampleLetter) oldSampleLetter.style.display = 'none';
    
    const oldCurrentTarget = document.getElementById('currentTarget');
    if (oldCurrentTarget) oldCurrentTarget.style.display = 'none';
    
    const oldHeaderH1 = document.querySelector('.header h1');
    if (oldHeaderH1) oldHeaderH1.style.display = 'none';
}

// Вызвать очистку после загрузки
setTimeout(cleanupOldElements, 100);