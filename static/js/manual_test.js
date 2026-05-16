// static/js/manual_test.js
import { LINES, getCanvasWidthForWord } from './test_mode_config.js';
import { 
    initCanvas, resizeCanvasForWord, clearCanvas, getMousePos,
    getVerdict, segmentWord
} from './test_mode_utils.js';

let currentWord = "";
let scores = [];
let canvasLocked = false;
let drawing = false;
let testStarted = false;

const targetWordEl = document.getElementById('targetWord');
const sampleWordEl = document.getElementById('sampleWord');
const scoreValueEl = document.getElementById('scoreValue');
const checkBtn = document.getElementById('checkBtn');
const clearBtn = document.getElementById('clearBtn');
const exitBtn = document.getElementById('exitBtn');
const startBtn = document.getElementById('startBtn');
const wordInput = document.getElementById('wordInput');
const resultVerdictEl = document.getElementById('resultVerdict');

const canvas = document.getElementById('drawCanvas');
const ctx = canvas.getContext('2d');

initCanvas(canvas, ctx);

function startDrawing(e) {
    if (canvasLocked) return;
    drawing = true;
    const pos = getMousePos(canvas, e);
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
    e.preventDefault();
}

function draw(e) {
    if (!drawing || canvasLocked) return;
    const pos = getMousePos(canvas, e);
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

function onClearCanvas() {
    if (canvasLocked) return;
    clearCanvas(ctx, canvas.width, canvas.height);
}

canvas.addEventListener('mousedown', startDrawing);
canvas.addEventListener('mousemove', draw);
canvas.addEventListener('mouseup', stopDrawing);
canvas.addEventListener('mouseleave', stopDrawing);
canvas.addEventListener('touchstart', startDrawing);
canvas.addEventListener('touchmove', draw);
canvas.addEventListener('touchend', stopDrawing);

clearBtn.addEventListener('click', onClearCanvas);
exitBtn.addEventListener('click', () => {
    window.location.href = '/';
});

startBtn.addEventListener('click', () => {
    const word = wordInput.value.trim().toLowerCase();
    if (!word || !/^[a-z]+$/.test(word)) {
        alert('Введите слово только из букв a-z');
        return;
    }
    currentWord = word;
    targetWordEl.textContent = currentWord;
    sampleWordEl.textContent = currentWord;
    scores = [];
    scoreValueEl.textContent = "0";
    resultVerdictEl.style.display = 'none';
    testStarted = true;
    resizeCanvasForWord(canvas, ctx, currentWord);
    onClearCanvas();
    canvasLocked = false;
    checkBtn.disabled = false;
    clearBtn.disabled = false;
});

async function checkWord() {
    if (!testStarted) {
        alert('Сначала нажми СТАРТ и введи слово');
        return;
    }
    if (canvasLocked) return;
    
    canvasLocked = true;
    
    // Создаём копию холста и удаляем линии
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = canvas.width;
    tempCanvas.height = canvas.height;
    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.drawImage(canvas, 0, 0);
    
    tempCtx.globalCompositeOperation = 'destination-out';
    tempCtx.strokeStyle = 'rgba(0,0,0,255)';
    tempCtx.lineWidth = 3;
    tempCtx.beginPath();
    tempCtx.moveTo(0, LINES.TOP);
    tempCtx.lineTo(tempCanvas.width, LINES.TOP);
    tempCtx.stroke();
    tempCtx.beginPath();
    tempCtx.moveTo(0, LINES.MID);
    tempCtx.lineTo(tempCanvas.width, LINES.MID);
    tempCtx.stroke();
    tempCtx.beginPath();
    tempCtx.moveTo(0, LINES.BASE);
    tempCtx.lineTo(tempCanvas.width, LINES.BASE);
    tempCtx.stroke();
    tempCtx.globalCompositeOperation = 'source-over';
    
    const imageData = tempCanvas.toDataURL('image/png');
    
    try {
        const letters = await segmentWord(imageData, canvas.width, canvas.height);
        
        if (letters.length === 0) {
            console.log("Буквы не найдены");
            scores.push(0);
            scoreValueEl.textContent = "0";
        } else {
            let totalScore = 0;
            const wordLen = currentWord.length;
            
            for (let i = 0; i < Math.min(letters.length, wordLen); i++) {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: letters[i].dataURL,
                        target: currentWord[i],
                        minY: letters[i].minY,
                        maxY: letters[i].maxY,
                        height: letters[i].height,
                        width: letters[i].width
                    })
                });
                const result = await response.json();
                totalScore += result.score;
                console.log(`Буква ${currentWord[i]}: распознано ${result.predicted}, SCORE: ${result.score}%`);
            }
            
            const avgScore = totalScore / wordLen;
            scores.push(avgScore);
            scoreValueEl.textContent = Math.round(avgScore);
            console.log(`Слово "${currentWord}" → SCORE: ${avgScore.toFixed(1)}%`);
            
            // Показываем результат без перехода к следующему слову
            const verdict = getVerdict(avgScore);
            resultVerdictEl.textContent = `Результат: ${verdict.text}`;
            resultVerdictEl.className = `result-verdict ${verdict.className}`;
            resultVerdictEl.style.display = 'block';
        }
    } catch (error) {
        console.error("Ошибка распознавания:", error);
        scores.push(0);
        scoreValueEl.textContent = "0";
    }
    
    setTimeout(() => {
        onClearCanvas();
        canvasLocked = false;
    }, 1000);
}

checkBtn.addEventListener('click', checkWord);