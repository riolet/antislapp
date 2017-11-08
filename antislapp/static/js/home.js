function send_post(destination, data, cb_success, cb_fail) {
    "use strict";
    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        let DONE = 4; // readyState 4 means the request is done.
        let OK = 200; // status 200 is a successful return.
        if (xhr.readyState === DONE) {
            if (xhr.status === OK) {
                cb_success(xhr.responseText, xhr); // "This is the returned text."
            } else {
                cb_fail("Error: " + xhr.status, xhr); // An error occurred during the request.
            }
        }
    };

    let packaged_data = JSON.stringify(data);
    xhr.open("POST", destination);
    xhr.send(packaged_data);
}

(function () {
    "use strict";
    let dialog = {
        converse_endpoint: "/converse",
        chatbox: null,
        chatinput: null,
    };

    dialog.init = function () {
        dialog.chatbox = document.getElementById("chat_messages");
        dialog.chatinput = document.getElementById("chat_input");
        dialog.chatinput.addEventListener("keydown", function (event) {
            if (event.keyCode === 13) {
                dialog.user_presses_enter();
                return true;
            }
            return false;
        });
    };

    dialog.add_user_message = function (msg) {
        //<div class="msg-user">Hello</div>
        let bubble = document.createElement("DIV");
        bubble.className = "msg-user";
        bubble.innerText = msg;
        dialog.chatbox.appendChild(bubble);
        //scroll to bottom / scroll to visible
        dialog.chatbox.scrollTop = dialog.chatbox.scrollHeight;
    };
    dialog.add_ai_message = function (msg) {
        //<div class="msg-user">Hello</div>
        msg = msg.replace(/\\n/g, "\n"); //newlines from literal "\n" pairs
        let bubble = document.createElement("DIV");
        bubble.className = "msg-ai";
        dialog.msg_into_element(bubble, msg);
        dialog.chatbox.appendChild(bubble);
        //scroll to bottom / scroll to visible
        dialog.chatbox.scrollTop = dialog.chatbox.scrollHeight;
    };

    dialog.msg_into_element = function (el, text) {
        const regex = /(.*?)\[([^\]]+)\]\(([^)]+)\)([^\[]+)/g;
        let m;
        let link;

        m = regex.exec(text);
        while (m !== null) {
            // This is necessary to avoid infinite loops with zero-width matches
            if (m.index === regex.lastIndex) {
                regex.lastIndex = regex.lastIndex + 1;
            }

            // The result can be accessed through the `m`-variable.
            el.appendChild(document.createTextNode(m[1]));
            link = document.createElement("A");
            link.href = m[2];
            link.innerText = m[3];
            el.appendChild(link);
            el.appendChild(document.createTextNode(m[4]));
            m = regex.exec(text);
        }
        if (text.match(regex) === null) {
            el.innerText = text;
        }
    };

    dialog.user_presses_enter = function () {
        let msg = dialog.chatinput.value;
        dialog.add_user_message(msg);
        dialog.chatinput.value = "";
        dialog.post_converse(msg);
    };

    dialog.post_converse = function (msg) {
        let data = {
            "msg": msg
        };
        send_post(dialog.converse_endpoint, data, dialog.post_converse_return, dialog.post_fail);
    };

    dialog.post_converse_return = function (response) {
        console.log("response:", response);
        let data = JSON.parse(response);
        dialog.add_ai_message(data.msg);
    };

    dialog.post_fail = function (response, xhr) {
        console.error(response);
        console.log(xhr);
    };
    //install layout
    window.dialog = dialog;
    window.onload = function () {
        dialog.init();
    };
}());

