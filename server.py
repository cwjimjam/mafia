import time
import random
import os
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

names_dict = {}
kicked = []
kicked_dict = {}

role_list = []

role_assigned = {}

host_address = ""

game_running = False

roles_name = {}
roles_description = {}
roles_alignment = {}
alignment_roles = {}
roles_knowledge = {}

def resetGame():
    time.sleep(10)
    #global names_dict.removeall()
#global kicked.removeall()

def beginGame():
    global game_running
    global roles_name
    global roles_description
    global roles_alignment
    global alignment_roles
    global roles_knowledge
    if len(names_dict) > len(role_list):
        return (False, "Too many players")
    random.shuffle(role_list)
    names = names_dict.keys()
    for i in range(len(names)):
        role_assigned[names[i]] = role_list[i]
        print "ASSIGN ROLE %s to %s" % (role_list[i], names[i])
    role_list.sort()
    for i in list(set(role_list)):
        path = "roles/" + i + ".txt"
        if os.path.isfile(path):
            with open(path, "r") as f:
                roles_name[i] = f.readline().rstrip()
                roles_alignment[i] = f.readline().rstrip()
                alignment_roles[roles_alignment[i]] = i
                roles_knowledge[i] = f.readline().rstrip().split(' ')
                roles_description[i] = f.readline().rstrip()
        else:
            roles_name[i] = i
            roles_alignment[i] = "unique"
            roles_knowledge[i] = []
            roles_description[i] = ""
    game_running = True
    print "GAME RUNNING"
    return (True, "")

def role_print(role):
    global roles_name
    global roles_description
    global roles_alignment
    global alignment_roles
    global roles_knowledge
    return "<span class=" + roles_alignment[role] + "><b>" + roles_name[role] + "</b></span>"

def getDescription(name):
    global roles_name
    global roles_description
    global roles_alignment
    global alignment_roles
    global roles_knowledge
    role = role_assigned[name]
    o = "You are " + role_print(role) + "<br><br>"
    for i in names_dict.keys():
        r = role_assigned[i]
        if i != name and (r in roles_knowledge[role] or roles_alignment[r] in roles_knowledge[role]):
            o += i + " - " + role_print(r) + "<br>"
    o += "<br>" + roles_description[role]
    return o


def handlePlayerCommands(cmd):
    global game_running
    l = cmd.split(" ")
    if len(l) < 2: return (False, "Invalid command")
    name = l[0]
    cmd = l[1]

    if cmd == "PLAYERS":
        if game_running and name == "HOST":
            l = [i + " - " + role_print(role_assigned[i]) for i in sorted(names_dict.keys())]
            return (True, "<br>".join(l))
        l = ["<span class=my_player>"+i+"</span>" if i == name else i for i in sorted(names_dict.keys())]
        return (True, "<br>".join(l))
    elif cmd == "ROLES":
        role_text = ""
        for t in role_list:
            role_text += t + "<br>"
        return (True, role_text)
    elif cmd == "DESCRIPTION":
        if game_running: return (True, getDescription(name))
        return (True, "")
    else:
        return (False, "Invalid command")

def handleHostCommands(cmd):
    global game_running
    l = cmd.split(" ")[1:]
    if len(l) < 1: return (False, "Invalid command")
    cmd = l[0]

    if cmd == "add":
        if len(l) < 2: return (False, "Invalid command")
        print "ADD ROLE:", l[1]
        role_list.append(l[1])
        role_list.sort()
        return (True, "success!")
    if cmd == "remove":
        if len(l) < 2: return (False, "Invalid command")
        if not l[1] in role_list: return (False, "None to remove")
        print "REMOVE ROLE:", l[1]
        role_list.remove(l[1])
        return (True, "success!")
    if cmd == "kick":
        if len(l) < 2: return (False, "Invalid command")
        if not l[1] in names_dict.keys(): return (False, "No player to kick")
        print "KICK PLAYER:", l[1]
        kicked.append(names_dict[l[1]])
        kicked_dict[l[1]] = names_dict[l[1]]
        names_dict.pop(l[1])
        return (True, "success!")
    if cmd == "unkick":
        if len(l) < 2: return (False, "Invalid command")
        if not kicked_dict[l[1]] in kicked: return (False, "No player to unkick")
        print "UNKICK PLAYER:", l[1]
        kicked.remove(kicked_dict[l[1]])
        kicked_dict.pop(l[1])
        return (True, "success!")
    if cmd == "start" and not game_running:
        return beginGame()
    if cmd == "reset":
        resetGame()
    


    return (False, "Invalid command")


def receiveJoin(name, address):
    global host_address
    if name == "~": return (True, "success!")
    if name == "HOST":
        if host_address == "" or host_address == address:
            host_address = address
            return (True, "success!")
        else: return (False, "Cannot be host!")
    if address in kicked:
        return (False, "Kicked.")
    if name in names_dict.keys() or name in kicked_dict.keys():
        if names_dict[name] != address:
            return (False, "Name is already in use")
    elif game_running:
        return (False, "Game in progress")
    else:
        print "ADD PLAYER: %s [%s]" % (name, address)
        names_dict[name] = address
    return (True, "success!")




VERBOSE = False


HOST_NAME = ""
PORT_NUMBER = 8080

log_file = "logs/server_" + time.strftime("%d-%b-%Y_%H-%M-%S.txt")

class MyHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        if VERBOSE:
            SimpleHTTPRequestHandler.log_message(self, format, *args)
        with open(log_file, "a") as f:
            f.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format % args))
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        SimpleHTTPRequestHandler.end_headers(self)
    def do_HEAD(self):
        self.send_response(200, "hi")
        self.send_header("Content-type", "text/html")
        self.end_headers()
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
        if self.path == "roles/":
            self.path = "/roles/index.html"
        return SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        host, port = self.client_address
        content_len = int(self.headers.getheader('content-length', 0))
        text = self.rfile.read(content_len)

        if VERBOSE: print "[%s] %s - POST \"%s\"" % (self.log_date_time_string(), host, text)
        with open(log_file, "a") as f:
            f.write("[%s] %s - POST \"%s\"\n" % (self.log_date_time_string(), host, text))

        words = text.split(' ')
        name = words[0]
 
        if host == host_address and name == "HOST":
            success, msg = handlePlayerCommands(text)
            if not success:
                success, msg = handleHostCommands(text)
            if not success:
                self.send_response(400, msg)
                self.end_headers()
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(msg)
            return
        

        
        success, msg = receiveJoin(name, host)
        
        if not success:
            self.send_response(400, msg)
            self.end_headers()
            return
        
        success, msg = handlePlayerCommands(text)
        
        if not success:
            self.send_response(400, msg)
        else:
            self.send_response(200)

        self.end_headers()

        self.wfile.write(msg)



if __name__ == "__main__":
    
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    print "\r", time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)

