
# Socket server in python using select function
 
import socket, select
import random
class game():
    def __init__(self,words,boards,start):
        self.board = random.choice(boards)
        random.shuffle(words)
        self.words = words[:25]
        self.masters = {'red':None,'blue':None}
        self.players = {'red':[],'blue':[]}
        self.current_player = start
    def display_board(self):
        return '\n'.join(['\t'.join(self.words[ii*5:(ii+1)*5]) for ii in range(5)])
    def display_secret(self):
        return '\n'.join(['\t'.join(self.board[ii*5:(ii+1)*5]) for ii in range(5)])
    def make_move(self,word,player):
        index = self.words.index(word)
        self.words[index] = player
        if self.board
        


if __name__ == "__main__":
      
    CONNECTION_LIST = []    # list of socket clients
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    PORT = 5000
         
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)
 
    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)
 
    print "Game server started on port " + str(PORT)

    wordlist = ["Aphrodite",		"Apollo",		"Ares",		"Artemis",		"Athena",		"Demeter",
		"Dionysus",	"Hades",		"Hephaestus",		"Hera",		"Hermes",		"Hestia",
		"Poseidon",		"Zeus",		"Aether",		"Ananke",		"Chaos",		"Chronos",
		"Erebus",		"Eros",		"Hypnos",		"Uranus",		"Gaia",		"Phanes",
		"Pontus",		"Tartarus",		"Thalassa",		"Thanatos",		"Hemera",		"Nyx","Nemesis"]
    board = ['red','blue','civ','secret','red',
             'red','blue','civ','civ','red',
             'red','blue','civ','civ','red',
             'red','blue','civ','civ','red',
             'red','blue','civ','civ','red']
    
    current_game = game(wordlist,[board],'red')
    print current_game.display_board()
    print current_game.display_secret()
    exit()
    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
 
        for sock in read_sockets:
             
            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                print "Client (%s, %s) connected" % addr
                 
            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = sock.recv(RECV_BUFFER)
                    # echo back the client message
                    if data:
                        sock.send('OK ... ' + data)
                 
                # client disconnected, so remove from socket list
                except:
                    broadcast_data(sock, "Client (%s, %s) is offline" % addr)
                    print "Client (%s, %s) is offline" % addr
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    continue
         
    server_socket.close()

