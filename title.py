import socket
import subprocess
import osascript

# Paramètres du serveur IRC
SERVER = "labynet.fr"
PORT = 6667
CHANNEL = "#labynet"
NICK = "title"

# Connexion au serveur IRC
irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc_socket.connect((SERVER, PORT))
irc_socket.send(f"USER {NICK} {NICK} {NICK} :{NICK}\r\n".encode())
irc_socket.send(f"NICK {NICK}\r\n".encode())
irc_socket.send(f"JOIN {CHANNEL}\r\n".encode())

# Boucle principale
while True:
    data = irc_socket.recv(4096).decode()
    if data.find('PING') != -1:
        irc_socket.send('PONG :pingis\n'.encode())
    elif data.find('PRIVMSG') != -1:
        user = data.split('!', 1)[0][1:]
        message = data.split('PRIVMSG', 1)[1].split(':', 1)[1].strip()

        if message.startswith('!title'):
            result = osascript.osascript('tell application "Music" to get {name, artist} of current track')
            irc_socket.send(f"PRIVMSG {CHANNEL} :Page title: {result[1]} \r\n".encode())
        if message.startswith('!next'):
            script = '''
                tell application "Music"
                    next track
                end tell
                '''
            subprocess.run(['osascript', '-e', script])
            irc_socket.send(f"PRIVMSG {CHANNEL} :Changement de musique en cours\r\n".encode())


        if message.startswith('!prev'):
            script = '''
                tell application "Music"
                    previous track
                end tell
                '''
            subprocess.run(['osascript', '-e', script])
            irc_socket.send(f"PRIVMSG {CHANNEL} :Changement de musique en cours\r\n".encode())

