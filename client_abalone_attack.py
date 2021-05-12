import socket
import sys
from jsonNetwork import Timeout, sendJSON, receiveJSON, NotAJSONObject, fetch
import random
#from games.tictactoe.game import iswinning

sc=socket.socket()

directions = {
	'NE': (-1,  0),
	'SW': ( 1,  0),
	'NW': (-1, -1),
	'SE': ( 1,  1),
	 'E': ( 0,  1),
	 'W': ( 0, -1)
}

#Inscription auprès du serveur
def subscribe(port):
    sc.connect((socket.gethostname(), 3000))
    sendJSON(sc, {
        'request': 'subscribe',
        'port': port,
        'name': 'Attack',
        'matricules': ['18316', '18155']
    })
    received = receiveJSON(sc)
    response = str(received['response'])

#Récupère la couleur du player en cours
def getPlayer(msj):
    current = msj['state']['current']
    player = 'B' if current == 0 else 'W'
    return player

#récupère la couleur de l'adversaire
def getOpponent(target):
    opponent = 'B' if target == 'W' else 'W'
    return opponent

#Retourne la liste des coordonées d'un état demandée
def map(target,board):
    i=-1
    black = []
    white = []
    for line in board:
        i+=1
        j=-1
        for place in line:
            j+=1
            if place == 'B':
                black.append((i,j))
            if place == 'W':
                white.append((i,j))
    if target == 'B':
        return black
    if target == 'W':
        return white

#mapAround renvoie une liste de l'état et de la position des cases autour de la pos donnée, exemple [[(7, 8), 'B'],...]
def mapAround(pos,board):
    D = directions.values()
    around = []
    for i in D:
        line = pos[0] + i[0]
        col = pos[1] + i[1]
        if 0 <= line <= 8 and 0<= col <= 8:
            around.append([(line,col),board[line][col]])
    return around

#Renvoie une liste de toutes les billes déplaçables (pas les trains)
def marblesYouCanMove(target,board):
    okToMove = []
    for elem in map(target,board):
        for i in mapAround(elem,board):
            if "E" in i:
                direction = (i[0][0] - elem[0],i[0][1] - elem[1])
                okToMove.append([[elem], direction])
    return okToMove

#Renvoie une liste contenant l'ensemble des trains de 2 billes d'une couleur demandée
def find2MarblesTrains(target, board):
    twoMarblesTrains = []
    for elem in map(target,board):
        for i in mapAround(elem,board):
            if target in i:
                direction = (elem[0] - i[0][0],elem[1] - i[0][1])
                twoMarblesTrains.append([[elem,i[0]],direction])
    return twoMarblesTrains

#Renvoie une liste contenant l'ensemble des trains de 3 billes d'une couleur demandée
def find3MarblesTrains(target,board):
    threeMarblesTrains = []
    for elem in find2MarblesTrains(target,board):
        inFront = checkInFront(elem,board,1)
        if inFront[0][1] == target:
            threeMarblesTrains.append([[elem[0][0],elem[0][1],inFront[0][0]],elem[1]])
    return threeMarblesTrains

#Regarde dans la direction d'un train, a une certaine distance et renvoie l'état des cases
def checkInFront(train,board,depth):
    inFront = []
    if len(train[0]) == 2:
        line = train[0][0][0]
        col = train[0][0][1]
    elif len(train[0]) == 3:
        line = train[0][2][0]
        col = train[0][2][1]
    if depth == 1:
        inFrontCoords = [(line + train[1][0],col + train[1][1])]
        if 0 <= inFrontCoords[0][0] <= 8 and 0<= inFrontCoords[0][1] <= 8:
            inFront.append([inFrontCoords[0],board[inFrontCoords[0][0]][inFrontCoords[0][1]]])
        else:
            inFront.append([inFrontCoords[0],'X'])
    elif depth == 2:
        inFrontCoords = [(line + train[1][0],col + train[1][1]),(line + 2*train[1][0],col + 2*train[1][1])]
        if 0 <= inFrontCoords[0][0] <= 8 and 0<= inFrontCoords[0][1] <= 8:
            inFront.append([inFrontCoords[0],board[inFrontCoords[0][0]][inFrontCoords[0][1]]])
            if 0 <= inFrontCoords[1][0] <= 8 and 0<= inFrontCoords[1][1] <= 8:
                inFront.append([inFrontCoords[1],board[inFrontCoords[1][0]][inFrontCoords[1][1]]])
            else:
                inFront.append([inFrontCoords[1],'X'])
        else:
            inFront.append([inFrontCoords[0],'X'])
    elif depth == 3:
        inFrontCoords = [(line + train[1][0],col + train[1][1]),(line + 2*train[1][0],col + 2*train[1][1]),(line + 3*train[1][0],col + 3*train[1][1])]
        if 0 <= inFrontCoords[0][0] <= 8 and 0<= inFrontCoords[0][1] <= 8:
            inFront.append([inFrontCoords[0],board[inFrontCoords[0][0]][inFrontCoords[0][1]]])
            if 0 <= inFrontCoords[1][0] <= 8 and 0<= inFrontCoords[1][1] <= 8:
                inFront.append([inFrontCoords[1],board[inFrontCoords[1][0]][inFrontCoords[1][1]]])
                if 0 <= inFrontCoords[2][0] <= 8 and 0<= inFrontCoords[2][1] <= 8:
                    inFront.append([inFrontCoords[2],board[inFrontCoords[2][0]][inFrontCoords[2][1]]])
                else:
                    inFront.append([inFrontCoords[2],'X'])
            else:
                inFront.append([inFrontCoords[1],'X'])
        else:
            inFront.append([inFrontCoords[0],'X'])
    return inFront

#Renvoie les trains pouvant être déplacés ainsi que les moves offensifs 
def trainsYouCanMove(trainSize,board,target):
    opponent = getOpponent(target)   

    attack = []
    trainsYouCanMove = []

    trains = find2MarblesTrains(target,board) if trainSize == 2 else find3MarblesTrains(target,board)

    if len(trains) != 0:
        for train in trains:
            for trainCoords in train[0]:
                inFront = checkInFront(train,board,trainSize)
                if inFront[0][1] != target and inFront[0][1] != 'X':
                    if len(inFront) == 2:
                        if inFront[0][1] == opponent and inFront[1][1] == 'X':
                            attack.append(train)
                        if inFront[1][1] == 'E' or inFront[1][1] == 'X':
                            trainsYouCanMove.append(train)
                    elif len(inFront) == 3:
                        if inFront[0][1] == opponent and (inFront[1][1] == 'X' or (inFront[1][1] == opponent)) and inFront[2][1] == 'X':
                            attack.append(train)
                        if inFront[1][1] == 'E' or inFront[1][1] == 'X' or inFront[1][1] == opponent:
                            if inFront[2][1] == 'E' or inFront[2][1] == 'X':
                                trainsYouCanMove.append(train)
    return trainsYouCanMove,attack

#Renvoie tout les moves possibles ou les moves offensifs s'il en existe
def moves(board, target):
    moves = []
    attack = []


    movableTwoMarblesTrains = trainsYouCanMove(2,board,target)
    if len(movableTwoMarblesTrains[1]) != 0:
        for train in movableTwoMarblesTrains[1]:
            attack.append(train)
    elif len(movableTwoMarblesTrains[0]) != 0:
        for train in movableTwoMarblesTrains[0]:
            moves.append(train)

    movableThreeMarblesTrains = trainsYouCanMove(3,board,target)
    if len(movableThreeMarblesTrains[1]) != 0:
        for train in movableThreeMarblesTrains[1]:
            attack.append(train)
    elif len(movableThreeMarblesTrains[0]) != 0:
        for train in movableThreeMarblesTrains[0]:
            moves.append(train)
    movableMarbles = marblesYouCanMove(target,board)
    if len(movableMarbles) != 0:
        for marble in movableMarbles:
            moves.append(marble)

    random.shuffle(moves)

    return attack if len(attack) != 0 else moves

#Explore tout les moves possible et en choisis un
def run(msj):
    board = msj['state']['board']
    target = getPlayer(msj)
    choice = random.choice(moves(board,target))
    marbles = choice[0]
    direction = choice[1]
    moveCardinal = list(directions.keys())[list(directions.values()).index(direction)]

    move = {'marbles':marbles,'direction':moveCardinal}

    return move

if __name__ == '__main__':
    port = sys.argv[1]
    s=socket.socket()
    s.bind(("",int(port)))
    s.listen()
    subscribe(port)
    while True:
        s.listen()
        xconté,address=s.accept()
        msj=receiveJSON(xconté)
        response={}
        if msj['request']=='ping':
            response['response']='pong'
        if msj['request']=='play':
            response = {
                "response": "move",
                "move": run(msj),
                "message": "Fun message"
            }
        sendJSON(xconté, response)