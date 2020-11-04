var canvas;
var context;
var clickX = new Array();
var clickY = new Array();
var clickDrag = new Array();
var paint = false;
var curColor = "#000000";


//IE에서는 캔버스 태그를 지원하지 않기 때문에 js에서 만든 후 div에 붙여줘야한다.
//나중에 시간 나면 그렇게 수정하기

function loadFile(input){
    if (input.files && input.files[0]) {
        document.getElementById("canvas").style.display = "none";
        document.getElementById("displayImg").style.display = "block";
        var reader = new FileReader();

        reader.onload = function (e) {
            $('#displayImg')
                .attr('src', e.target.result)
                .width(400)
                .height(400);
        };

        reader.readAsDataURL(input.files[0]);
        // hidden url 에 업로드된 url 저장하기
    }
}

function show(){
    alert("pen selected!");
}


function draw() {

    canvas = document.getElementById('canvas');
    context = document.getElementById('canvas').getContext("2d");

    $('#canvas').mousedown(function (e) {
        var mouseX = e.pageX - this.offsetLeft;
        var mouseY = e.pageY - this.offsetTop;

        paint = true;
        addClick(e.pageX - this.offsetLeft, e.pageY - this.offsetTop);
        redraw();
    });

    $('#canvas').mousemove(function (e) {
        if (paint) {
            addClick(e.pageX - this.offsetLeft, e.pageY - this.offsetTop, true);
            redraw();
        }
    });

    $('#canvas').mouseup(function (e) {
        paint = false;
    });
}

function addClick(x, y, dragging) {
    clickX.push(x);
    clickY.push(y);
    clickDrag.push(dragging);
}

function redraw() {

    context.clearRect(0, 0, context.canvas.width, context.canvas.height); // Clears the canvas
    context.strokeStyle = curColor;
    context.lineJoin = "round";
    context.lineWidth = 3;
    for (var i = 0; i < clickX.length; i++) {
        context.beginPath();
        if (clickDrag[i] && i) {
            context.moveTo(clickX[i - 1], clickY[i - 1]);
        } else {
            context.moveTo(clickX[i] - 1, clickY[i]);
        }
        context.lineTo(clickX[i], clickY[i]);
        context.closePath();
        context.stroke();
    }
}

function erase(){
    context.clearRect(0, 0, context.canvas.width, context.canvas.height);
    clickX = [];
    clickY = [];
    clickDrag = [];
}

function fillCanvasBackgroundWithColor(canvas, color) {
    // Get the 2D drawing context from the provided canvas.
    var canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');

    // We're going to modify the context state, so it's
    // good practice to save the current state first.
    context.save();

    // Normally when you draw on a canvas, the new drawing
    // covers up any previous drawing it overlaps. This is
    // because the default `globalCompositeOperation` is
    // 'source-over'. By changing this to 'destination-over',
    // our new drawing goes behind the existing drawing. This
    // is desirable so we can fill the background, while leaving
    // the chart and any other existing drawing intact.
    // Learn more about `globalCompositeOperation` here:
    // https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/globalCompositeOperation
    context.globalCompositeOperation = 'destination-over';

    // Fill in the background. We do this by drawing a rectangle
    // filling the entire canvas, using the provided color.
    context.fillStyle = color;
    context.fillRect(0, 0, canvas.width, canvas.height);

    // Restore the original context state from `context.save()`
    context.restore();
}

function save() {
    // 업로드 이미지일때의 조건 붙여주기
    document.getElementById("canvas").style.display="block";
    var image = document.getElementById('displayImg')
    var url = document.getElementById('url');
    var canvas = document.getElementById('canvas');
    fillCanvasBackgroundWithColor(canvas, 'white');
    image.src = canvas.toDataURL();
    url.value = canvas.toDataURL();
}
