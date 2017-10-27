function POST(destination, data, cb_success, cb_fail) {
  let xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function () {
    let DONE = 4; // readyState 4 means the request is done.
    let OK = 200; // status 200 is a successful return.
    if (xhr.readyState === DONE) {
      if (xhr.status === OK) {
        cb_success(xhr.responseText, xhr); // 'This is the returned text.'
      } else {
        cb_fail('Error: ' + xhr.status, xhr); // An error occurred during the request.
      }
    }
  };

  let package = JSON.stringify(data);
  xhr.open('POST', destination);
  xhr.send(package);
}

(function () {
  "use strict";
  let dialog = {
    converse_endpoint: "/converse",
    chatbox: null,
    chatinput: null
  };

  dialog.init = function () {
    dialog.chatbox = document.getElementById("chat_messages");
    dialog.chatinput = document.getElementById("chat_input");
    dialog.chatinput.addEventListener("keydown", function(event) {
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
    let bubble = document.createElement("DIV");
    bubble.className = "msg-ai";
    dialog.msg_into_element(bubble, msg);
    dialog.chatbox.appendChild(bubble);
    //scroll to bottom / scroll to visible
    dialog.chatbox.scrollTop = dialog.chatbox.scrollHeight;
  };

  dialog.make_links = function (el, text) {
    let i;
    let link;

    i = text.indexOf("[");
    if (i > 0) {
      el.appendChild(document.createTextNode(text.slice(0, i)))
      text = text.slice(i)
    }
    i = text.indexOf("]");
  }

  dialog.msg_into_element = function (el, text) {
    const regex = /([^\)]*)\[([^\]]+)\]\(([^)]+)\)([^\[]+)/g;
    let m;
    let link;

    while ((m = regex.exec(text)) !== null) {
      // This is necessary to avoid infinite loops with zero-width matches
      if (m.index === regex.lastIndex) {
        regex.lastIndex++;
      }

      // The result can be accessed through the `m`-variable.
      el.appendChild(document.createTextNode(m[1]));
      link = document.createElement("A");
      link.href = m[2];
      link.innerText = m[3];
      el.appendChild(link);
      el.appendChild(document.createTextNode(m[4]));
    }
    if (text.match(regex) === null) {
      el.innerText = text;
    }
  };

  dialog.user_presses_enter = function () {
    let msg = dialog.chatinput.value;
    dialog.add_user_message(msg);
    dialog.chatinput.value = "";
    dialog.POST_converse(msg);
  };

  dialog.POST_converse = function(msg) {
    let data = {
      'msg': msg
    }
    POST(dialog.converse_endpoint, data, dialog.POST_converse_return, dialog.POST_fail)
  };

  dialog.POST_converse_return = function(response, xhr) {
    console.log("response:", response);
    let data = JSON.parse(response);
    dialog.add_ai_message(data.msg)
  };

  dialog.POST_fail = function(response, xhr) {
    console.error(response);
    console.log(xhr);
  }
  //install layout
  window.dialog = dialog;
  window.onload = function () {
    dialog.init()
  };
}());

