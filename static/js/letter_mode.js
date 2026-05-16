// static/js/letter_mode.js
const urlParts = window.location.pathname.split('/');
const letter = urlParts[urlParts.length - 1];

document.getElementById('targetLetter').textContent = letter === '0' ? 'Digit 0' : 
    (letter >= '0' && letter <= '9') ? `Digit ${letter}` : `Letter ${letter}`;
document.getElementById('sampleLetter').textContent = letter;

let attempt = 1;
let scores = [];
let canvasLocked = false;

const canvas = document.getElementById('drawCanvas');
const ctx = canvas.getContext('2d');

// Линии
const TOP_LINE_Y = 50;
const MID_LINE_Y = 110;
const BASE_LINE_Y = 180;

function drawLines() {
    ctx.save();
    ctx.globalAlpha = 0.5;
    ctx.beginPath();
    ctx.moveTo(0, TOP_LINE_Y);
    ctx.lineTo(canvas.width, TOP_LINE_Y);
    ctx.strokeStyle = '#888';
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, MID_LINE_Y);
    ctx.lineTo(canvas.width, MID_LINE_Y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, BASE_LINE_Y);
    ctx.lineTo(canvas.width, BASE_LINE_Y);
    ctx.strokeStyle = '#aaa';
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.restore();
}

function initCanvas() {
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, 280, 280);
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 4;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    drawLines();
}
initCanvas();

let drawing = false;

function getMousePos(e) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    let clientX, clientY;
    
    if (e.touches) {
        clientX = e.touches[0].clientX;
        clientY = e.touches[0].clientY;
    } else {
        clientX = e.clientX;
        clientY = e.clientY;
    }
    
    let x = (clientX - rect.left) * scaleX;
    let y = (clientY - rect.top) * scaleY;
    x = Math.max(0, Math.min(canvas.width, x));
    y = Math.max(0, Math.min(canvas.height, y));
    return { x, y };
}

function startDrawing(e) {
    if (canvasLocked) return;
    drawing = true;
    const pos = getMousePos(e);
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
    e.preventDefault();
}

function draw(e) {
    if (!drawing || canvasLocked) return;
    const pos = getMousePos(e);
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
    e.preventDefault();
}

function stopDrawing() {
    drawing = false;
    ctx.beginPath();
}

function clearCanvas() {
    if (canvasLocked) return;
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, 280, 280);
    drawLines();
}

canvas.addEventListener('mousedown', startDrawing);
canvas.addEventListener('mousemove', draw);
canvas.addEventListener('mouseup', stopDrawing);
canvas.addEventListener('mouseleave', stopDrawing);
canvas.addEventListener('touchstart', startDrawing);
canvas.addEventListener('touchmove', draw);
canvas.addEventListener('touchend', stopDrawing);

document.getElementById('clearBtn').addEventListener('click', clearCanvas);
document.getElementById('exitBtn').addEventListener('click', () => {
    window.location.href = '/';
});

document.getElementById('checkBtn').addEventListener('click', async () => {
    if (canvasLocked) return;
    
    canvasLocked = true;
    
    // Создаём копию холста и удаляем линии
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = canvas.width;
    tempCanvas.height = canvas.height;
    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.drawImage(canvas, 0, 0);
    
    // Убираем линии
    tempCtx.globalCompositeOperation = 'destination-out';
    tempCtx.strokeStyle = 'rgba(0,0,0,255)';
    tempCtx.lineWidth = 3;
    tempCtx.beginPath();
    tempCtx.moveTo(0, TOP_LINE_Y);
    tempCtx.lineTo(tempCanvas.width, TOP_LINE_Y);
    tempCtx.stroke();
    tempCtx.beginPath();
    tempCtx.moveTo(0, MID_LINE_Y);
    tempCtx.lineTo(tempCanvas.width, MID_LINE_Y);
    tempCtx.stroke();
    tempCtx.beginPath();
    tempCtx.moveTo(0, BASE_LINE_Y);
    tempCtx.lineTo(tempCanvas.width, BASE_LINE_Y);
    tempCtx.stroke();
    tempCtx.globalCompositeOperation = 'source-over';
    
    // Вычисляем minY и maxY для буквы
    const imgData = tempCtx.getImageData(0, 0, tempCanvas.width, tempCanvas.height);
    let minY = tempCanvas.height;
    let maxY = 0;
    for (let y = 0; y < tempCanvas.height; y++) {
        for (let x = 0; x < tempCanvas.width; x++) {
            const idx = (y * tempCanvas.width + x) * 4;
            const brightness = (imgData.data[idx] + imgData.data[idx+1] + imgData.data[idx+2]) / 3;
            if (brightness > 50) {
                if (y < minY) minY = y;
                if (y > maxY) maxY = y;
            }
        }
    }
    const height = maxY - minY;
    const width = tempCanvas.width;
    
    const imageData = tempCanvas.toDataURL('image/png');
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: imageData,
                target: letter,
                minY: minY,
                maxY: maxY,
                height: height,
                width: width
            })
        });
        
        const result = await response.json();
        
        if (result.error) {
            console.error('Ошибка:', result.error);
            const tempScore = Math.floor(Math.random() * 100);
            scores.push(tempScore);
            document.getElementById('scoreValue').textContent = tempScore;
        } else {
            scores.push(result.score);
            document.getElementById('scoreValue').textContent = result.score;
            
            // Вывод в консоль браузера
            console.log(`=== РЕЗУЛЬТАТ РАСПОЗНАВАНИЯ ===`);
            console.log(`Целевая буква: ${letter}`);
            console.log(`Распознано: ${result.predicted}`);
            console.log(`Уверенность: ${result.score}%`);
            console.log(`Правильно: ${result.correct}`);
            console.log(`Вердикт: ${result.verdict}`);
            
            if (result.top_predictions) {
                console.log(`Топ-3 предсказания модели:`);
                for (let i = 0; i < result.top_predictions.length; i++) {
                    console.log(`  ${i+1}. ${result.top_predictions[i][0]}: ${result.top_predictions[i][1].toFixed(1)}%`);
                }
            }
            console.log(`================================`);
        }
    } catch (error) {
        console.error('Ошибка запроса:', error);
        const tempScore = Math.floor(Math.random() * 100);
        scores.push(tempScore);
        document.getElementById('scoreValue').textContent = tempScore;
    }
    
    setTimeout(() => {
        ctx.fillStyle = 'black';
        ctx.fillRect(0, 0, 280, 280);
        drawLines();
        canvasLocked = false;
        
        if (attempt < 10) {
            attempt++;
            document.getElementById('attemptCount').textContent = attempt;
        } else {
            const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
            document.getElementById('scoreValue').textContent = Math.round(avgScore);
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
    }, 1000);
});