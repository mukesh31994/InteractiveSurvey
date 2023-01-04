var SpeechRecognition = window.webkitSpeechRecognition;
var recognition = new SpeechRecognition();
debugger;
var Textbox = $("input");
Textbox = Textbox.get(0);
var record_status = false;
previous_resource = null; //make mutex-lock
var button_list = []
var active_background_color = "linear-gradient(to bottom right, #EF4765, #FF9A5A);"

window.onload = feedback_handler;

recognition.continuous = true;
recognition.onresult = function (event) {debugger;
    var current = event.resultIndex;
    var transcript = event.results[current][0].transcript;
    Content = "";
    Content = transcript;
    console.log(Content);
    Textbox.value = $("#chat_text").val() + Content;
};

function feedback_handler() {
    document.getElementById("feeds").onclick = button;
    button_object_list = document.getElementsByTagName("button");
    for (var i = 0; i < button_object_list.length; i++) {
        if (button_object_list.item(i).id != "chatbot-button" && button_object_list.item(i).id) {
            button_list.push(button_object_list.item(i));
        }
    }
}

function button(e) {
    if (e.target.tagName == "BUTTON") {

        if (record_status == true && e.target.innerHTML == "START") {
            recognition.stop();
            record_status = false;
        }

        if (record_status == false) { e.target.innerHTML = "<i class='fa fa-microphone-slash'></i> STOP"; }
        else { e.target.innerHTML = '<i class="fa fa-microphone"></i> Mic'; }
        $("#chat_text").focus();
        // Textbox = $("#textarea_bot" + e.target.id)
        recorder();
    }
}

function recorder() {
    if (record_status == true) {
        recognition.stop();
        record_status = false;
    }
    else {
        recognition.start();
        record_status = true;
    }
}