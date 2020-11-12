var canvas;
var context;
var clickX = new Array();
var clickY = new Array();
var clickDrag = new Array();
var paint = false;
var curColor ="rgb(255,255,255)";
var saveX = new Array();
var saveY = new Array();

//IE에서는 캔버스 태그를 지원하지 않기 때문에 js에서 만든 후 div에 붙여줘야한다.
//나중에 시간 나면 그렇게 수정하기

var canvas = document.getElementById("canvas");
var context = canvas.getContext("2d");
context.fillStyle = "rgb(0,0,0)";
context.fillRect(0, 0, canvas.width, canvas.height);

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


function draw() {
    context.fillStyle = "rgb(0,0,0)";
    context.fillRect(0, 0, canvas.width, canvas.height);

    $('#canvas').mousedown(function (e) { //click
        var mouseX = e.pageX - this.offsetLeft; //pagex는 좌표 & offset은 부모 element의 좌표와 상대적인 좌표
        var mouseY = e.pageY - this.offsetTop;

        paint = true;
        addClick(e.pageX - this.offsetLeft, e.pageY - this.offsetTop);
        redraw();

    });

    $('#canvas').mousemove(function (e) { //dragging
        if (paint) {
            addClick(e.pageX - this.offsetLeft, e.pageY - this.offsetTop, true);
            redraw();
        }
    });

    $('#canvas').mouseup(function (e) {  //release
        paint = false;
    });
}

function addClick(x, y, dragging) {
    clickX.push(x);
    clickY.push(y);
    clickDrag.push(dragging); //T/F value
}

function redraw() {
    context.clearRect(0, 0, canvas.width, canvas.height); // Clears the canvas
    context.fillStyle = "rgb(0,0,0)";//fillback
    context.fillRect(0, 0, canvas.width, canvas.height); //fillback
    context.strokeStyle = curColor;
    context.lineJoin = "round";
    context.lineWidth = 1;
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
    context.fillStyle = "rgb(0,0,0)";//fillback
    context.fillRect(0, 0, canvas.width, canvas.height); //fillback
    clickX = [];
    clickY = [];
    clickDrag = [];
    saveX = [];
    saveY = [];
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
    fillCanvasBackgroundWithColor(canvas, 'rgb(0,0,0)');
    // image.src = canvas.toDataURL(); // save 눌렀을때 이미지 하나 더 뜨는 거 없애려면 이거 지우기
    url.value = canvas.toDataURL();
    console.log("image saved!");
    // url.value = [saveX, saveY];
}
