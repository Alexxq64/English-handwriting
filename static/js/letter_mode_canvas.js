// ==================== CANVAS И РИСОВАНИЕ ====================

const canvas = document.getElementById('drawCanvas');
const ctx = canvas.getContext('2d');
let canvasChanged = false;

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
    ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 4;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    drawLines();
    canvasChanged = false;
}

function clearCanvas() {
    if (canvasLocked) return;
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
    drawLines();
    canvasChanged = false;
}

function removeLinesFromTempCanvas(tempCtx, tempCanvas) {
    tempCtx.beginPath();
    tempCtx.moveTo(0, TOP_LINE_Y);
    tempCtx.lineTo(tempCanvas.width, TOP_LINE_Y);
    tempCtx.strokeStyle = 'black';
    tempCtx.lineWidth = 5;
    tempCtx.stroke();

    tempCtx.beginPath();
    tempCtx.moveTo(0, MID_LINE_Y);
    tempCtx.lineTo(tempCanvas.width, MID_LINE_Y);
    tempCtx.stroke();

    tempCtx.beginPath();
    tempCtx.moveTo(0, BASE_LINE_Y);
    tempCtx.lineTo(tempCanvas.width, BASE_LINE_Y);
    tempCtx.stroke();
}

function getBoundingBox(tempCtx, tempCanvas) {
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
    return { minY, maxY, height: maxY - minY };
}

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
    canvasChanged = true;
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

function setupCanvasEvents() {
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseleave', stopDrawing);
    canvas.addEventListener('touchstart', startDrawing);
    canvas.addEventListener('touchmove', draw);
    canvas.addEventListener('touchend', stopDrawing);
}

initCanvas();
setupCanvasEvents();