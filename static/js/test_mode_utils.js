// static/js/test_mode_utils.js
import { LINES, getCanvasWidthForWord } from './test_mode_config.js';

export function drawLines(ctx, canvasWidth) {
    ctx.save();
    ctx.globalAlpha = 0.5;
    ctx.beginPath();
    ctx.moveTo(0, LINES.TOP);
    ctx.lineTo(canvasWidth, LINES.TOP);
    ctx.strokeStyle = '#888';
    ctx.lineWidth = 1;
    ctx.stroke();
    
    ctx.beginPath();
    ctx.moveTo(0, LINES.MID);
    ctx.lineTo(canvasWidth, LINES.MID);
    ctx.stroke();
    
    ctx.beginPath();
    ctx.moveTo(0, LINES.BASE);
    ctx.lineTo(canvasWidth, LINES.BASE);
    ctx.strokeStyle = '#aaa';
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.restore();
}

export function resizeCanvasForWord(canvas, ctx, word) {
    const newWidth = getCanvasWidthForWord(word);
    canvas.width = newWidth;
    canvas.height = 280;
    
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 4;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    drawLines(ctx, canvas.width);
}

export function initCanvas(canvas, ctx) {
    canvas.width = 280;
    canvas.height = 280;
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 4;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    drawLines(ctx, canvas.width);
}

export function clearCanvas(ctx, canvasWidth, canvasHeight) {
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, canvasWidth, canvasHeight);
    drawLines(ctx, canvasWidth);
}

export function getMousePos(canvas, e) {
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

export function loadWordsList(level, WORDS_BY_LEVEL) {
    const lvl = parseInt(level);
    let words;
    if (WORDS_BY_LEVEL[lvl]) {
        words = [...WORDS_BY_LEVEL[lvl]];
    } else {
        words = [...WORDS_BY_LEVEL[1]];
    }
    for (let i = words.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [words[i], words[j]] = [words[j], words[i]];
    }
    return words.slice(0, 10);
}

export function getVerdict(avgScore) {
    if (avgScore >= 76) return { text: 'Excellent!', className: 'excellent' };
    if (avgScore >= 51) return { text: 'Good!', className: 'good' };
    if (avgScore >= 26) return { text: 'Fair', className: 'fair' };
    return { text: 'Bad', className: 'bad' };
}

export function segmentWord(imageData, canvasWidth, canvasHeight) {
    return new Promise((resolve) => {
        const img = new Image();
        img.src = imageData;
        img.onload = () => {
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = canvasWidth;
            tempCanvas.height = canvasHeight;
            const tempCtx = tempCanvas.getContext('2d');
            tempCtx.drawImage(img, 0, 0, canvasWidth, canvasHeight);
            const imgData = tempCtx.getImageData(0, 0, canvasWidth, canvasHeight);
            
            const gray = new Array(canvasWidth * canvasHeight).fill(0);
            for (let i = 0; i < imgData.data.length; i += 4) {
                const brightness = (imgData.data[i] + imgData.data[i+1] + imgData.data[i+2]) / 3;
                const idx = i / 4;
                gray[idx] = brightness > 50 ? 255 : 0;
            }
            
            const projection = new Array(canvasWidth).fill(0);
            for (let x = 0; x < canvasWidth; x++) {
                let sum = 0;
                for (let y = 0; y < canvasHeight; y++) {
                    if (gray[y * canvasWidth + x] > 0) sum++;
                }
                projection[x] = sum;
            }
            
            const bounds = [];
            let inLetter = false;
            let start = 0;
            
            for (let x = 0; x < canvasWidth; x++) {
                const isEmpty = projection[x] < 5;
                if (!isEmpty && !inLetter) {
                    inLetter = true;
                    start = x;
                } else if (isEmpty && inLetter) {
                    inLetter = false;
                    const end = x;
                    if (end - start > 5) {
                        bounds.push({ start, end });
                    }
                }
            }
            if (inLetter) {
                bounds.push({ start, end: canvasWidth });
            }
            
            const PADDING = 10;
            const letters = [];
            
            for (const bound of bounds) {
                const letterWidth = bound.end - bound.start;
                const newWidth = letterWidth + PADDING * 2;
                
                // Находим minY и maxY
                let minY = canvasHeight;
                let maxY = 0;
                for (let y = 0; y < canvasHeight; y++) {
                    for (let x = bound.start; x < bound.end; x++) {
                        const idx = y * canvasWidth + x;
                        if (gray[idx] > 0) {
                            if (y < minY) minY = y;
                            if (y > maxY) maxY = y;
                        }
                    }
                }
                
                const letterCanvas = document.createElement('canvas');
                letterCanvas.width = newWidth;
                letterCanvas.height = canvasHeight;
                const letterCtx = letterCanvas.getContext('2d');
                
                letterCtx.drawImage(
                    img,
                    bound.start, 0,
                    letterWidth, canvasHeight,
                    PADDING, 0,
                    letterWidth, canvasHeight
                );
                
                letters.push({
                    dataURL: letterCanvas.toDataURL(),
                    minY: minY,
                    maxY: maxY,
                    height: maxY - minY,
                    width: letterWidth
                });
            }
            
            resolve(letters);
        };
    });
}