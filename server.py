
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
        self.current_moves = 0
        self.waiting_on = '{}_master'.format(start)
        self.send_message = False
    def display_board(self):
        return '\n'.join(['\t'.join(self.words[ii*5:(ii+1)*5]) for ii in range(5)])
    def display_secret(self):
        return '\n'.join(['\t'.join(self.board[ii*5:(ii+1)*5]) for ii in range(5)])
    def make_move(self,word,player):
        index = self.words.index(word)

        team = player.split('_')[0]
        
        self.words[index] = self.board[index]
        
        other = {'red':'blue','blue':'red'}
        if self.board[index] == team:
            score = 1
        elif self.board[index] == other[team]:
            score = 0
        elif self.board[index] == 'civ':
            score = 0
        else:
            score = -1

        self.current_moves -= 1
                
        return score
    def progress(self):
        other = {'red':'blue','blue':'red'}
        if 'master' in self.waiting_on:
            self.waiting_on = '{}_guesser'.format(self.waiting_on.split('_')[0])
        else:
            self.waiting_on = '{}_master'.format(other[self.waiting_on.split('_')[0]])
            
def parse_message(message):
    import re

    match = re.search('REGISTER (\w+) (.+)',message)
    if match:
        return ['REGISTER', match.group(1),match.group(2)]

    match = re.search('CLUE (\w+) (\d+)',message)

    if match:
        return ['CLUE', match.group(1),match.group(2)]

    

    match = re.search('GUESS (\w+)',message)

    if match:
        return ['GUESS', match.group(1)]

    return ['UNRECOGNIZED', message]


    
if __name__ == "__main__":
      
    CONNECTION_LIST = []    # list of socket clients
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    PORT = 5000
    players = {'red_master':[None,None],
               'blue_master':[None,None],
               'red_guesser':[None,None],
               'blue_guesser':[None,None]}
    sock2players = {}


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

    active_game = False
    waiting = True
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

                    message = parse_message(data.rstrip())
                    
                    
                 
                # client disconnected, so remove from socket list
                except:
                    broadcast_data(sock, "Client (%s, %s) is offline" % addr)
                    print "Client (%s, %s) is offline" % addr
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    continue
                print message
                
                if message[0] == 'REGISTER':
                    stop = False
                    for p in players:
                        print p, players[p][0], sock
                        if players[p][0] == sock:
                            print 'WARNING: {} "{}" tried to register more than once'.format(sock,players[p][1])
                            stop = True
                            break
                    if stop:
                        continue
                    if players[message[1]][0] == None:
                        players[message[1]] = (sock,message[2])
                        sock.send(current_game.display_board() +'\n')
                        if 'master' in message[1]:
                            sock.send(current_game.display_secret() +'\n')
                    foundall = True
                    for p in players:
                        foundall = foundall and players[p][0] != None
                    if not active_game and foundall:                        
                        active_game = True
                        players[current_game.waiting_on][0].send('SUBMIT\n')
                        current_game.send_message =True
                        sock2players = {s[0]:p for p,s in players.items()}
                elif active_game:
                    print current_game.waiting_on
                    if sock != players[current_game.waiting_on][0]:
                        print 'WARNING: {} "{}" tried to take their turn out of order'.format(sock,players[sock2players[sock]][1])
                    else:
                        if message[0] == 'GUESS':
                            score = current_game.make_move(message[1],current_game.waiting_on)
                            if score < 0:
                                print '{} loss doubleagent'.format(current_game.waiting_on.split('_')[0])
                                exit()
                            if score == 0 or current_game.current_moves <= 0:
                                current_game.progress()
                            current_game.send_message = True
                        if message[0] == 'CLUE':
                            players[current_game.waiting_on.split('_')[0]+'_guesser'][0].send('CLUE {} {}\n'.format(message[1],message[2]))
                            current_game.progress()
                            current_game.current_moves = 1+ int(message[2])
                            current_game.send_message = True
                                    
        if current_game.send_message:
            players[current_game.waiting_on][0].send(current_game.display_board()+'\n')
            players[current_game.waiting_on][0].send('SUBMIT\n')
            current_game.send_message = False
                        
                        
                    
    server_socket.close()

