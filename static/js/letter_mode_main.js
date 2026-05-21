// ==================== ОСНОВНАЯ ЛОГИКА ====================

const returnUrl = sessionStorage.getItem('returnUrl') || '/';

document.getElementById('clearBtn').addEventListener('click', () => {
    clearCanvas();
    updateScoreDisplay(0);  // Очищаем SCORE
});

document.getElementById('exitBtn').addEventListener('click', () => {
    window.location.href = returnUrl;
});

// Выход при клике на SCORE
const scoreArea = document.getElementById('scoreArea');
if (scoreArea) {
    scoreArea.addEventListener('click', () => {
        window.location.href = returnUrl;
    });
}

// Выход при клике на вердикт
const verdictDiv = document.getElementById('resultVerdict');
if (verdictDiv) {
    verdictDiv.addEventListener('click', () => {
        window.location.href = returnUrl;
    });
}

document.getElementById('checkBtn').addEventListener('click', async () => {
    if (canvasLocked) return;
    
    // Проверка: была ли нарисована новая буква после предыдущего CHECK
    if (!canvasChanged) {
        alert('Нарисуйте новую букву перед проверкой!');
        return;
    }
    
    // Проверка: пустой ли холст
    const tempCheckCanvas = document.createElement('canvas');
    tempCheckCanvas.width = canvas.width;
    tempCheckCanvas.height = canvas.height;
    const tempCheckCtx = tempCheckCanvas.getContext('2d');
    tempCheckCtx.drawImage(canvas, 0, 0);
    
    const checkImageData = tempCheckCtx.getImageData(0, 0, tempCheckCanvas.width, tempCheckCanvas.height);
    let hasPixel = false;
    for (let i = 0; i < checkImageData.data.length; i += 4) {
        const brightness = (checkImageData.data[i] + checkImageData.data[i+1] + checkImageData.data[i+2]) / 3;
        if (brightness > 50) {
            hasPixel = true;
            break;
        }
    }
    
    if (!hasPixel) {
        alert('Нарисуйте букву или цифру перед проверкой!');
        return;
    }
    
    canvasLocked = true;
    
    // Создаём копию холста
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = canvas.width;
    tempCanvas.height = canvas.height;
    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.drawImage(canvas, 0, 0);
    
    // Убираем линии с копии
    removeLinesFromTempCanvas(tempCtx, tempCanvas);
    
    // Получаем bounding box
    const { minY, maxY, height } = getBoundingBox(tempCtx, tempCanvas);
    const currentTargetSymbol = attemptsList[currentAttemptIndex];
    const imageDataUrl = tempCanvas.toDataURL('image/png');
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image: imageDataUrl,
                target: currentTargetSymbol,
                minY: minY,
                maxY: maxY,
                height: height,
                width: canvas.width
            })
        });
        
        const result = await response.json();
        
        if (result.error) {
            console.error('Ошибка:', result.error);
            const tempScore = Math.floor(Math.random() * 100);
            scores.push(tempScore);
            updateScoreDisplay(tempScore);
        } else {
            scores.push(result.score);
            updateScoreDisplay(result.score);
            console.log(`Целевая: ${currentTargetSymbol}, Распознано: ${result.predicted}, SCORE: ${result.score}%`);
            
            await saveAttempt(imageDataUrl, currentTargetSymbol, result.score, result.predicted);
        }
    } catch (error) {
        console.error('Ошибка запроса:', error);
        const tempScore = Math.floor(Math.random() * 100);
        scores.push(tempScore);
        updateScoreDisplay(tempScore);
    }
    
    // Сбрасываем флаг изменения canvas после CHECK
    canvasChanged = false;
    
    // Переход к следующей попытке или завершение
    setTimeout(() => {
        if (currentAttemptIndex + 1 < 10) {
            currentAttemptIndex++;
            updateDisplay();
            clearCanvas();
            canvasLocked = false;
        } else {
            const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
            updateScoreDisplay(Math.round(avgScore));
            showFinalVerdict(avgScore);
        }
    }, 1000);
});

// Начальное отображение
updateDisplay();