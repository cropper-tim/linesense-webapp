in_line_buttons = document.getElementsByClassName("in_line_button");
var user_id = document.getElementById('user_data').dataset.user_id
current_line_button = null;
startTime = null;
endTime = null;

console.log(user_id)

if (sessionStorage.getItem('businessID')) {
    business_id = JSON.parse(sessionStorage.getItem('businessID'))
    startTime = JSON.parse(sessionStorage.getItem('startTime'));
    button_id = "business_button_" + business_id;
    current_line_button = document.getElementById(button_id);
    if (current_line_button) {
        in_line_button_pressed(current_line_button, true)
    } else {
        set_buttons(in_line_buttons, function (x) {
            x.disabled = true;
        });
    }
}

function set_buttons(button_group, func) {
    for (i = 0; i < button_group.length; i++) {
        func(button_group[i]);
    }
}

function in_line_button_pressed(button, is_storage) {
    current_line_button = button;
    business_id = current_line_button.dataset.business;
    addButtons();
    set_buttons(in_line_buttons, function (x) {
        x.disabled = true;
    });

    if (!is_storage) {
        console.log("nothing in storage, new start time set");
        startTime = new Date().getTime()
    }

    sessionStorage.setItem('businessID', JSON.stringify(current_line_button.dataset.business));
    sessionStorage.setItem('startTime', JSON.stringify(startTime));
}

function addButtons() {
    ool_button = document.createElement("button");
    ool_button.innerHTML = "Done Waiting";
    ool_button.addEventListener("click", ool_button_pressed);
    ool_button.className += "ool btn btn-sm btn-success"
    current_line_button.parentElement.appendChild(ool_button);

    cancel_button = document.createElement("button");
    cancel_button.innerHTML = "Cancel";
    cancel_button.addEventListener("click", cancel_button_pressed);
    cancel_button.className += "cancel btn btn-xs btn-default"
    current_line_button.parentElement.parentElement.appendChild(cancel_button);
}

function removeButtons() {
    $('.ool').remove();
    $('.cancel').remove();
    $('.in_line_button').removeAttr("disabled")
    set_buttons(in_line_buttons, function (x) {
        x.disabled = false;
    });
}

function ool_button_pressed() {
    endTime = new Date().getTime();
    interval = (endTime - startTime) / 1000;
    startTime = null;
    endTime = null;
    console.log(interval);
    removeButtons();

    clearSession();

    sendData(interval);
}

function cancel_button_pressed() {
    removeButtons();
    startTime = null;
    clearSession();
}

function set_in_line_buttons(item) {
    item.addEventListener("click", function (e) {
        in_line_button_pressed(e.currentTarget, false);
    });
}

function clearSession() {
    sessionStorage.removeItem('businessID');
    sessionStorage.removeItem('startTime');
}

function sendData(interval) {
    data = {
        "business": current_line_button.dataset.business,
        "wait_time": interval
    };
    console.log(data);

    makeReq("POST", "/user_input/", 200, function (x) { }, JSON.stringify(data));
}

function makeReq(method, target, retCode, action, data) {
    var httpRequest = new XMLHttpRequest();

    if (!httpRequest) {
        alert('Giving up :( Cannot create an XMLHTTP instance');
        return false;
    }

    httpRequest.onreadystatechange = makeHandler(httpRequest, retCode, action);
    httpRequest.open(method, target);

    if (data) {
        httpRequest.setRequestHeader("Content-Type", "application/json");
        httpRequest.send(data);
    }
    else {
        httpRequest.send();
    }
}

function makeHandler(httpRequest, retCode, action) {
    function handler() {
        if (httpRequest.readyState === XMLHttpRequest.DONE) {
            if (httpRequest.status === retCode) {
                console.log("recieved response text:  " + httpRequest.responseText);
                action(httpRequest.responseText);
            } else {
                alert("There was a problem with the request.  You'll need to refresh the page!");
            }
        }
    }
    return handler;
}

set_buttons(in_line_buttons, set_in_line_buttons);

setInterval(function () { location.reload(); }, 60000);
