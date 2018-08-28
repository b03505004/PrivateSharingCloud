
socket = io.connect('http://' + document.domain + ':' + location.port+ '/data');

var timers = [];
// show or not
var isShow = true;
var dic = {}
var time = {}
var context = {}

// send button
function send_button() {
    var vid = document.getElementById("vid");
    // create danmu
    var jqueryDom = createScreenbullet($("#screenBulletText").val());
    socket.emit('new_bullet', {bullet: $("#screenBulletText").val(), id: $("#send_button").val(), time: vid.currentTime} );
    document.getElementById('screenBulletText').value = ""
    // move danmu
    addInterval(jqueryDom);
}

$("#screenBulletText").on("keydown", function (event) {
    if (event.keyCode == 13) {
        // create danmu
        var jqueryDom = createScreenbullet($("#screenBulletText").val());
        socket.emit('new_bullet', {bullet: $("#screenBulletText").val(), id: $("#send_button").val(), time: vid.currentTime} );
        document.getElementById('screenBulletText').value = ""
        // move danmu
        addInterval(jqueryDom);

    
    }
});
const binarySearch = (arr, target, start, end) => {
    const m = Math.floor((start + end)/2);
    if (target == arr[m]) return m;
    if (end - 1 === start) return Math.abs(arr[start] - target) > Math.abs(arr[end] - target) ? end : start; 
    if (target > arr[m]) return binarySearch(arr,target,m,end);
    if (target < arr[m]) return binarySearch(arr,target,start,m);
  }

$(document).ready(function(){
    $("#vid").on( "timeupdate", function(event){ 
        //onTrackedVideoFrame(this.currentTime, this.duration);
        time_match_context(this.currentTime);
    });
  });
  
function onTrackedVideoFrame(currentTime, duration){
      $("#current").text(currentTime); //Change #current to currentTime
    
  }
function time_match_context(vidTime){
    //$("#duration").text(vidTime);
    if(time.length>0){
        var timeIndex = binarySearch(time, vidTime, 0, time.length);
        console.log('TIME:', vidTime-time[timeIndex]);
        if (vidTime>time[timeIndex] && (vidTime-time[timeIndex]<0.25)){
            var jqueryDom = createScreenbullet(context[timeIndex]);
            addInterval(jqueryDom);
        }
    }
}

function get_list(dic){
    console.log(dic);
    console.log(dic['context']);
    console.log(dic);
    for (i in dic.context) {
        console.log(dic);
    }
    console.log(dic.context[0]);
    console.log(dic.context[1]);
    time = dic.time;
    context = dic.context;
    console.log(time);
}
function print_list(){
    console.log(time);
    console.log(context);
}

// danmu on/off
$(".clear").on("click", function () {
    if (isShow) {
        $(".bullet").css("opacity", 0);
        isShow = false;
    } else {
        $(".bullet").css("opacity", 1);
        isShow = true;
    }   
});
// new danmu
function createScreenbullet(text) {
    var jqueryDom = $("<div class='bullet'>" + text + "</div>");
    var fontColor = "rgb(" + Math.floor(Math.random() * 256) + "," + Math.floor(Math.random() * 256) + "," + Math.floor(Math.random()) + ")";
    var fontSize = Math.floor((Math.random() + 1) * 24) + "px";
    var left = $(".screen_container").width() + "px";
    var top = Math.floor(Math.random() * 400) + "px";
    top = parseInt(top) > 352 ? "352px" : top;
    jqueryDom.css({
        "position": 'absolute',
        "color": fontColor,
        "font-size": fontSize,
        "left": left,
        "top": top
    });
    $(".screen_container").append(jqueryDom);
    return jqueryDom;
}
// move danmu
function addInterval(jqueryDom) {
    var left = jqueryDom.offset().left - $(".screen_container").offset().left;
    var timer = setInterval(function () {
        left--;
        jqueryDom.css("left", left + "px");
        if (jqueryDom.offset().left + jqueryDom.width() < $(".screen_container").offset().left) {
            jqueryDom.remove();
            clearInterval(timer);
        }
    }, 10);
    timers.push(timer);
}
