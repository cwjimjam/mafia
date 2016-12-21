
document.getElementById('name_input').onkeypress = function(e) {
    if (e.keyCode == 13) {
        document.getElementById('submit_button').click();
    }
}

function joinFailure(message) {
    console.log("join failure: " + message)
    name = "~";
    accepted = false;
    if (document.getElementById('name_input')) {
        document.getElementById('name_input').value = "";
    }
    document.getElementById('error_message').innerHTML = message + "<br>";
    if (!server_responding) {
        document.getElementById('main').innerHTML = ""
        document.getElementById('player_list').innerHTML = "";
        document.getElementById('role_list').innerHTML = "";
    }
}

function checkName(name) {
    if (name == "") {
        return false
    }
    var allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
    for (var i in name) {
        if (allowed.indexOf(name[i]) == -1) {
            return false
        }
    }
    return true
}

var name = "~"
var accepted = false
var server_responding = true
var is_host = false;

lobbyUpdate();
var render_loop = setInterval(lobbyUpdate, 2000);

var role_loop = setInterval(checkRole, 2000);

function tryJoin() {
    if (is_host) {
        var xhr = new XMLHttpRequest();
        
        xhr.onreadystatechange = function() {
            if (xhr.readyState == xhr.DONE) {
                if (xhr.status != 200) {
                    if (xhr.status == 0) {
                        server_responding = false;
                        joinFailure("Server unresponsive");
                        clearInterval(render_loop);
                    } else {
                        joinFailure(xhr.statusText);
                    }
                    return;
                }
                document.getElementById('error_message').innerHTML = "<br>";
            }
        }
        
        xhr.open("POST", "/", true);
        xhr.send("HOST " + document.getElementById('name_input').value);
        document.getElementById('name_input').value = "";
        lobbyUpdate();
        return;
    }
    name = document.getElementById('name_input').value;
    if (!checkName(name)) {
        joinFailure("Invalid name");
        return;
    }

    lobbyUpdate();
    document.getElementById('name_input').value = "";
}

function lobbyUpdate() {
    var xhr_players = new XMLHttpRequest();
    
    xhr_players.onreadystatechange = function() {
        if (xhr_players.readyState == xhr_players.DONE) {
            if (xhr_players.status != 200) {
                console.log("Error:", xhr_players.status, xhr_players.statusText)
                if (xhr_players.status == 0 || xhr_players.statusText == "Kicked.") {
                    server_responding = false;
                    var msg = xhr_players.statusText == "" ? "Server not responding":xhr_players.statusText;
                    joinFailure(msg);
                    clearInterval(render_loop);
                } else {
                    joinFailure(xhr_players.statusText);
                }
                return;
            }
            if (name != "~" && !accepted) {
                if (name == "HOST") {
                    initHost();
                } else {
                    document.getElementById('main').innerHTML = "";
                }
                document.getElementById('error_message').innerHTML = "<br>";
                checkRole();
                accepted = true;
            }
            document.getElementById('player_list').innerHTML = xhr_players.responseText;
        }
    }
    
    xhr_players.open("POST", "/", true);
    xhr_players.send(name + " PLAYERS");
    
    
    var xhr_roles = new XMLHttpRequest();
    
    xhr_roles.onreadystatechange = function() {
        if (xhr_roles.readyState == xhr_roles.DONE) {
            if (xhr_roles.status != 200) {
                console.log("Error:", xhr_roles.status, xhr_roles.statusText)
                if (xhr_roles.status == 0 || xhr_roles.statusText == "Kicked.") {
                    server_responding = false;
                    var msg = xhr_roles.statusText == "" ? "Server not responding":xhr_roles.statusText;
                    joinFailure(msg);
                    clearInterval(render_loop);
                } else {
                    joinFailure(xhr_roles.statusText);
                }
                return;
            }
            if (name != "~" && !accepted) {
                if (name == "HOST") {
                    initHost();
                } else {
                    document.getElementById('main').innerHTML = "";
                }
                document.getElementById('error_message').innerHTML = "<br>";
                checkRole();
                accepted = true;
            }
            document.getElementById('role_list').innerHTML = xhr_roles.responseText;
        }
    }
    
    xhr_roles.open("POST", "/", true);
    xhr_roles.send(name + " ROLES");
}

function checkRole() {
    if (is_host) {
        clearInterval(role_loop);
        return;
    }
    if (!accepted) {
        return;
    }
    var xhr = new XMLHttpRequest();
    
    xhr.onreadystatechange = function() {
        if (xhr.readyState == xhr.DONE) {
            if (xhr.status != 200) {
                console.log("Error:", xhr.status, xhr.statusText)
                if (xhr.status == 0 || xhr.statusText == "Kicked.") {
                    server_responding = false;
                    var msg = xhr.statusText == "" ? "Server not responding":xhr.statusText;
                    joinFailure(msg);
                    clearInterval(role_loop);
                } else {
                    joinFailure(xhr.statusText);
                }
                return;
            }
            if (xhr.responseText != "") {
                document.getElementById('main').innerHTML = "<button id=\"hideshow\" onclick=\"hide_show()\">Show</button><p id=\"role_description\" style=\"display:none\">" + xhr.responseText + "</p>";
                clearInterval(role_loop);
            }
        }
    }
    
    xhr.open("POST", "/", true);
    xhr.send(name + " DESCRIPTION")
}

function hide_show() {
    var x = document.getElementById('role_description');
    if (x.style.display == 'none') {
        x.style.display = 'block';
        document.getElementById('hideshow').innerHTML = "Hide";
    } else {
        x.style.display = 'none'
        document.getElementById('hideshow').innerHTML = "Show";
    }
}

function initHost() {
    is_host = true;
    document.getElementById('submit_button').innerHTML = "Submit"
}
