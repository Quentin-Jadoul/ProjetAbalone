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


def subscribe(port):
    sc.connect((socket.gethostname(), 3000))
    sendJSON(sc, {
        'request': 'subscribe',
        'port': port,
        'name': 'Imane_Quentin',
        'matricules': ['18316', '18155']
    })
    received = receiveJSON(sc)
    response = str(received['response'])

def getPlayer(msj):
    current = msj['state']['current']
    if current == 0:
        player = 'B'
    else:
        player = 'W'
    return player

def map(target,board):
    i=-1
    empty = []
    black = []
    white = []
    for line in board:
        i+=1
        j=-1
        for place in line:
            j+=1
            if place =="E":
                empty.append((i,j))
            if place == 'B':
                black.append((i,j))
            if place == 'W':
                white.append((i,j))
    if target == 'E':
        return empty
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

def marblesYouCanMove(target,board):
    okToMove = []
    liste = []
    for elem in map(target,board):
        #elem est un tuple de map, qui est elle même une liste contenant toutes les billes de la couleur du joueur
        liste = mapAround(elem,board)
        for i in liste:
            if "E" in i:
                direction = (i[0][0] - elem[0],i[0][1] - elem[1])
                okToMove.append([[elem], direction])
    return okToMove

#find2MarblesTrains va crée une liste contenant l'ensemble des trains de 2 billes d'une même couleur
def find2MarblesTrains(target, board):
    twoMarblesTrains = []
    liste = []
    for elem in map(target,board):
        #elem est une sous liste de map, qui est elle même une liste contenant toutes les billes de la couleur du joueur
        liste = mapAround(elem,board)
        for i in liste:
            if target in i:
                direction = (elem[0] - i[0][0],elem[1] - i[0][1])
                twoMarblesTrains.append([[elem,i[0]],direction])
    return twoMarblesTrains

def find3MarblesTrains(target,board):
    twoMarblesTrains = find2MarblesTrains(target,board)
    threeMarblesTrains = []
    for elem in twoMarblesTrains:
        inFront = checkInFront(elem,board,1)
        if inFront[0][1] == target:
            threeMarblesTrains.append([[elem[0][0],elem[0][1],inFront[0][0]],elem[1]])
    return threeMarblesTrains

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

def trainsYouCanMove(trainSize,board,target):
    if trainSize == 2:
        trains = find2MarblesTrains(target,board)
    elif trainSize == 3: 
        trains = find3MarblesTrains(target,board)

    trainsYouCanMove = []
    if len(trains) != 0:
        for train in trains:
            for trainCoords in train[0]:
                inFront = checkInFront(train,board,trainSize)
                if inFront[0][1] != target and inFront[0][1] != 'X':
                    if len(inFront) == 1:
                        trainsYouCanMove.append(train)
                    elif len(inFront) == 2:
                        if inFront[1][1] == 'E' or inFront[1][1] == 'X':
                            trainsYouCanMove.append(train)
                    elif len(inFront) == 3:
                        if inFront[2][1] == 'E' or inFront[2][1] == 'X':
                            trainsYouCanMove.append(train)
    return trainsYouCanMove

def moves(board, target):
    lengths = [1,2,3]
    moves = []

    movableTwoMarblesTrains = trainsYouCanMove(2,board,target)
    if len(movableTwoMarblesTrains) != 0:
        for train in movableTwoMarblesTrains:
            moves.append(train)

    movableThreeMarblesTrains = trainsYouCanMove(3,board,target)
    if len(movableThreeMarblesTrains) != 0:
        for train in movableThreeMarblesTrains:
            moves.append(train)
    movableMarbles = marblesYouCanMove(target,board)
    if len(movableMarbles) != 0:
        for marble in movableMarbles:
            moves.append(marble)
    
    return moves


def run(msj):
    board = msj['state']['board']
    #get the actual player
    target = getPlayer(msj)

    choice = random.choice(moves(board,target))

    print('choice',choice)
    start = choice[0]
    print('start',start)
    direction = choice[1]
    moveCardinal = list(directions.keys())[list(directions.values()).index(direction)]
    print('moveCardinal',moveCardinal)

    # start = random.choice(marblesYouCanMove(target,board))
    # print('start',start)
    # end = random.choice(possibleCoord(start,board))
    # print('end',end)
    # direction = translateMove(start,end)
    # print('direction',direction)


    move = {'marbles':start,'direction':moveCardinal}

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

        
        
