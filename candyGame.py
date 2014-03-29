# candyGame.py
# Created by T. J. Tkacik for Assignment 2 of COMP 590
# Spring of 2014 at the University of North Carolina
import util, sys, time

class candyGame(object):
    
    def __init__(self, scoreBoard="game_boards/ReesesPieces.txt", player1="human", player2="human", loud=False):
        self.scoreBoard = []
        self.gameBoard = []
        self.player1 = self.parsePlayer(player1, "A")
        self.player2 = self.parsePlayer(player2, "B")
        self.loud = loud
        self.moveCount = [0, 0]
        
        sourceBoard = open(scoreBoard)        
        for line in sourceBoard:
            self.scoreBoard.append(line.strip().split("\t"))
        sourceBoard.close()
        for i in range(0, len(self.scoreBoard)):
            self.gameBoard.append([])
            for j in range(0, len(self.scoreBoard[i])):
                self.gameBoard[i].append("_")

        turn1 = True
        while not self.isGameOver(self.gameBoard):
            if self.loud: self.printLayout(self.gameBoard)
            if turn1: 
                self.move(self.player1)
                self.moveCount[0] += 1
            else: 
                self.move(self.player2)
                self.moveCount[1] += 1
            turn1 = not turn1 
            
        score = self.score(self.gameBoard)
        print "Game Over!"
        self.printLayout(self.gameBoard)
        print "Player", self.player1.ID, ":", score[0], "points,", self.player1.nodesExpanded, "nodes in", round(self.player1.timeTaken,1), " total seconds and", self.moveCount[0], "moves."
        print "Player", self.player2.ID, ":", score[1], "points,", self.player2.nodesExpanded, "nodes in", round(self.player2.timeTaken,1), " total seconds and", self.moveCount[1], "moves."
        if score[0] > score[1]: print "Player", self.player1.ID, "wins!"
        elif score[0] < score[1]: print "Player", self.player2.ID, "wins!"
        else: print "Tied game!"
    
    def move(self, player):
        while True:
            x,y = player.move()
            if x < len(self.gameBoard) and y < len(self.gameBoard[0]):
                if self.gameBoard[x][y] == "_":
                    self.gameBoard = self.updateState(x, y, player, self.gameBoard)
                    return True
                else: print "Invalid position"
            else: print "Invalid position"
    
    def updateState(self, x, y, player, gameBoard):
        gameBoard[x][y] = player.ID
        neighbors = set([(x-1,y),(x+1,y),(x,y-1),(x,y+1)])
        for i,j in neighbors:
            if self.inBounds(i,j):
                if gameBoard[i][j] == player.ID:
                    for k,l in neighbors:
                        if self.inBounds(k,l):
                            if gameBoard[k][l] is not "_":
                                gameBoard[k][l] = player.ID
        return gameBoard
    
    def score(self, gameBoard):
        score1, score2 = 0,0
        for i in range(0, len(gameBoard)):
            for j in range(0, len(gameBoard[i])):
                if gameBoard[i][j] == self.player1.ID:
                    score1 += eval(self.scoreBoard[i][j])
                if gameBoard[i][j] == self.player2.ID:
                    score2 += eval(self.scoreBoard[i][j])
        return (score1, score2)
    
    #If a player asks for a score, their score is returned first in the tuple
    def myScore(self, gameBoard, playerID):
        if playerID == self.player1.ID: return self.score(gameBoard)
        elif playerID == self.player2.ID:
            score = self.score(gameBoard)
            return (score[1],score[0])
        else: return False
        
    def isGameOver(self, gameBoard):
        vacant = 0
        for row in gameBoard:
            vacant += row.count('_')
        if vacant==0: return True
        return False
                
    def inBounds(self, x, y):
        if x >= (len(self.gameBoard)): return False
        if y >= (len(self.gameBoard[x])): return False
        if x < 0 or y < 0: return False
        return True
        
    def printLayout(self, gameBoard):
        layout = []
        for i in range(0, len(self.scoreBoard)):
            layout.append([])
            for j in range(0, len(self.scoreBoard[i])):
                layout[i].append(gameBoard[i][j] + "(" + self.scoreBoard[i][j] + ")")
        for row in layout:
            print row
            
    def duplicateBoard(self, board=None):
        newBoard = []
        if board == None: board = self.gameBoard
        for row in board:
            newBoard.append(list(row))
        return newBoard
    
    def otherPlayer(self, player):                          #Returns the player other than that given
        if player == self.player1: return self.player2
        return self.player1
    
    def parsePlayer(self, playerString, ID):
        if playerString == "human":
            return humanPlayer(self, ID)
        if "minimax" in playerString:
            if len(playerString) > len("minimax"):
                #print eval(playerString[len("minimax"):])
                return minimaxPlayer(self, ID, eval(playerString[len("minimax"):]))
            else: return minimaxPlayer(self, ID, 3)
        if "alphabeta" in playerString:
            if len(playerString) > len("alphabeta"):
                return alphabetaPlayer(self, ID, eval(playerString[len("alphabeta"):]))
            else: return alphabetaPlayer(self, ID, 4)
        if "quiescence" in playerString:
            if len(playerString) > len("quiescence"):
                return quiescencePlayer(self, ID, eval(playerString[len("quiescence"):]))
            else: return quiescencePlayer(self, ID, 3)
        else:
            print "Invalid player String:", playerString
            sys.exit(0)
    
class candyPlayer(object):
    def __init__(self, candyGame, ID="X", searchDepth=3):
        self.ID = ID
        self.candyGame = candyGame
        self.searchDepth = searchDepth
        self.nodesExpanded = 0
        self.timeTaken = 0
        self.quiesce = 0
        
    def evaluate(self, gameBoard):
        score = self.candyGame.myScore(gameBoard, self.ID)
        if score[0]+score[1] == 0: return .5
        if score[0] == 0:
            return float(-1*score[1])
        return float(score[0])/float(score[0]+score[1])
         
class humanPlayer(candyPlayer):
    def move(self):
        startTime = time.clock()
        move = eval(raw_input("Human player " + self.ID + ": ")) 
        timeTaken = time.clock()-startTime
        self.timeTaken += timeTaken
        #print "Expanded", (self.nodesExpanded - nodes), "nodes in", round(timeTaken, 3), "seconds."
        return move
         
class minimaxPlayer(candyPlayer):  
    def move(self):
        spot = self.minimax(self.candyGame.duplicateBoard())
        print "Minimax", self.ID, "will take", spot
        return spot
    
    def minimax(self, gameBoard):
        nodes = self.nodesExpanded
        startTime = time.clock()
        x,y = None, None
        max = float("-inf")
        for i in range(0, len(gameBoard)):
            for j in range(0, len(gameBoard[i])):
                if gameBoard[i][j] == "_":
                    newBoard = self.candyGame.updateState(i, j, self, self.candyGame.duplicateBoard(gameBoard))
                    #print "If I start with", (i,j), "..."
                    value = self.minvalue(newBoard, 1)
                    #print "So optimal play after", (i,j), "gives me", value, "odds."
                    if value > max:
                        #print "Taking", (i,j), "is the best move I see so far..."
                        max = value
                        x,y = i,j
        timeTaken = time.clock()-startTime
        self.timeTaken += timeTaken
        if self.candyGame.loud: print "Minimax", self.ID, "expanded", (self.nodesExpanded - nodes), "nodes in", round(timeTaken, 3), "seconds."
        return (x, y)
    
    def minvalue(self,gameBoard, depth):
        self.nodesExpanded+=1
        if depth == self.searchDepth:
            #print "then my chance of winning is", self.evaluate(gameBoard)
            return self.evaluate(gameBoard)
        if self.candyGame.isGameOver(gameBoard):
            score = self.candyGame.myScore(gameBoard, self.ID)
            if score[0] > score[1]:
                #print "I could win!"
                return 1
            #print "This is your game to lose..."
            return 0
        min = float("inf")
        for i in range(0, len(gameBoard)):
            for j in range(0, len(gameBoard[i])):
                if gameBoard[i][j] == "_":
                    #print "and you take", (i,j)
                    newBoard = self.candyGame.updateState(i, j, self.candyGame.otherPlayer(self), self.candyGame.duplicateBoard(gameBoard))
                    value = self.maxvalue(newBoard, depth+1)
                    if value < min:
                        min = value
        return min
    
    def maxvalue(self,gameBoard, depth):
        self.nodesExpanded+=1
        if depth == self.searchDepth:
            #print "then my chance of winning is", self.evaluate(gameBoard)
            return self.evaluate(gameBoard)
        if self.candyGame.isGameOver(gameBoard):
            score = self.candyGame.myScore(gameBoard, self.ID)
            if score[0] > score[1]:
                #print "I will win!"
                return 1
            #print "I mustn't lose..."
            return 0
        max = float("-inf")
        for i in range(0, len(gameBoard)):
            for j in range(0, len(gameBoard[i])):
                if gameBoard[i][j] == "_":
                    #print "then I take", i,j
                    newBoard = self.candyGame.updateState(i, j, self, self.candyGame.duplicateBoard(gameBoard))
                    value = self.minvalue(newBoard, depth+1)
                    if value > max:
                        max = value
        return max
        
class alphabetaPlayer(candyPlayer):
    def move(self):
        spot = self.minimax(self.candyGame.duplicateBoard())
        print "AlphaBeta", self.ID, "will take", spot
        return spot
    
    def minimax(self, gameBoard):
        nodes = self.nodesExpanded
        startTime = time.clock()
        x,y = None, None
        max = float("-inf")
        for i in range(0, len(gameBoard)):
            for j in range(0, len(gameBoard[i])):
                if gameBoard[i][j] == "_":
                    newBoard = self.candyGame.updateState(i, j, self, self.candyGame.duplicateBoard(gameBoard))
                    #print "If I start with", (i,j), "..."
                    value = self.minvalue(newBoard, 1, float("-inf"), float("inf"))
                    #print "So optimal play after", (i,j), "gives me", value, "odds."
                    if value > max:
                        #print "Taking", (i,j), "is the best move I see so far..."
                        max = value
                        x,y = i,j
        timeTaken = time.clock()-startTime
        self.timeTaken += timeTaken
        if self.candyGame.loud: print "AlphaBeta", self.ID, "expanded", (self.nodesExpanded - nodes), "nodes in", round(timeTaken, 3), "seconds."
        return (x, y)
    
    def minvalue(self,gameBoard, depth, alpha, beta):
        self.nodesExpanded+=1
        if depth == self.searchDepth:
            #print "then my chance of winning is", self.evaluate(gameBoard)
            return self.evaluate(gameBoard)
        if self.candyGame.isGameOver(gameBoard):
            score = self.candyGame.myScore(gameBoard, self.ID)
            if score[0] > score[1]:
                #print "I could win!"
                return 1
            #print "This is your game to lose..."
            return 0
        min = float("inf")
        for i in range(0, len(gameBoard)):
            for j in range(0, len(gameBoard[i])):
                if gameBoard[i][j] == "_":
                    #print "and you take", (i,j)
                    newBoard = self.candyGame.updateState(i, j, self.candyGame.otherPlayer(self), self.candyGame.duplicateBoard(gameBoard))
                    value = self.maxvalue(newBoard, depth+1, alpha, beta)
                    if value < min:
                        min = value
                    if value < beta: beta = value
                    if value <= alpha: return value
        return min
    
    def maxvalue(self,gameBoard, depth, alpha, beta):
        self.nodesExpanded+=1
        if depth == self.searchDepth:
            #print "then my chance of winning is", self.evaluate(gameBoard)
            return self.evaluate(gameBoard)
        if self.candyGame.isGameOver(gameBoard):
            score = self.candyGame.myScore(gameBoard, self.ID)
            if score[0] > score[1]:
                #print "I will win!"
                return 1
            #print "I mustn't lose..."
            return 0
        max = float("-inf")
        for i in range(0, len(gameBoard)):
            for j in range(0, len(gameBoard[i])):
                if gameBoard[i][j] == "_":
                    #print "then I take", (i,j)
                    newBoard = self.candyGame.updateState(i, j, self, self.candyGame.duplicateBoard(gameBoard))
                    value = self.minvalue(newBoard, depth+1, alpha, beta)
                    if value > max:
                        max = value
                    if value > alpha: alpha = value
                    if value >= beta: return value
        return max
    
class quiescencePlayer(candyPlayer):
    def move(self):
        self.quiesce = 0
        spot = self.minimax(self.candyGame.duplicateBoard())
        print "Quiescence", self.ID, "will take", spot
        return spot
    
    def minimax(self, gameBoard):
        nodes = self.nodesExpanded
        startTime = time.clock()
        x,y = None, None
        max = float("-inf")
        for i in range(0, len(gameBoard)):
            for j in range(0, len(gameBoard[i])):
                if gameBoard[i][j] == "_":
                    newBoard = self.candyGame.updateState(i, j, self, self.candyGame.duplicateBoard(gameBoard))
                    #print "If I start with", (i,j), "..."
                    value = self.minvalue(newBoard, 1, float("-inf"), float("inf"), False)
                    #print "So optimal play after", (i,j), "gives me", value, "odds."
                    if value > max:
                        #print "Taking", (i,j), "is the best move I see so far..."
                        max = value
                        x,y = i,j
        timeTaken = time.clock()-startTime
        self.timeTaken += timeTaken
        if self.candyGame.loud: print "Quiescence", self.ID, "expanded", (self.nodesExpanded - nodes), "nodes in", round(timeTaken, 3), "seconds after", self.quiesce, " dives."
        return (x, y)
    
    def minvalue(self, gameBoard, depth, alpha, beta, prevNode):
        self.nodesExpanded+=1
        if prevNode:
            if depth >= 2+self.searchDepth:
                #print "then my chance of winning is", self.evaluate(gameBoard)
                return self.evaluate(gameBoard)
            elif depth >= self.searchDepth:
                quiet = self.isQuiet(prevNode, gameBoard)
                if quiet: return self.evaluate(gameBoard)
                else: self.quiesce += 1
            elif self.candyGame.isGameOver(gameBoard):
                score = self.candyGame.myScore(gameBoard, self.ID)
                if score[0] > score[1]:
                    #print "I could win!"
                    return 1
                #print "This is your game to lose..."
                return 0
        min = float("inf")
        for i in range(0, len(gameBoard)):
            for j in range(0, len(gameBoard[i])):
                if gameBoard[i][j] == "_":
                    #print "and you take", (i,j)
                    newBoard = self.candyGame.updateState(i, j, self.candyGame.otherPlayer(self), self.candyGame.duplicateBoard(gameBoard))
                    value = self.maxvalue(newBoard, depth+1, alpha, beta, (i,j))
                    if value < min:
                        min = value
                    if value < beta: beta = value
                    if value <= alpha: return value
        return min
    
    def maxvalue(self,gameBoard, depth, alpha, beta, prevNode):
        self.nodesExpanded+=1
        if prevNode:
            if depth >= 2+self.searchDepth:
                #print "then my chance of winning is", self.evaluate(gameBoard)
                return self.evaluate(gameBoard)
            elif depth >= self.searchDepth:
                quiet = self.isQuiet(prevNode, gameBoard)
                if quiet: return self.evaluate(gameBoard)
                else: self.quiesce += 1
            elif self.candyGame.isGameOver(gameBoard):
                score = self.candyGame.myScore(gameBoard, self.ID)
                if score[0] > score[1]:
                    #print "I could win!"
                    return 1
                #print "This is your game to lose..."
                return 0
        max = float("-inf")
        for i in range(0, len(gameBoard)):
            for j in range(0, len(gameBoard[i])):
                if gameBoard[i][j] == "_":
                    #print "then I take", (i,j)
                    newBoard = self.candyGame.updateState(i, j, self, self.candyGame.duplicateBoard(gameBoard))
                    value = self.minvalue(newBoard, depth+1, alpha, beta, (i,j))
                    if value > max:
                        max = value
                    if value > alpha: alpha = value
                    if value >= beta: return value
        return max       
    
    def isQuiet(self, prevNode, gameBoard):
        x, y = prevNode[0], prevNode[1]
        for i,j in set([(x-1,y),(x+1,y),(x,y-1),(x,y+1)]):
            if self.candyGame.inBounds(i,j):
                if gameBoard[i][j] == "_":
                    for k,l in set([(i-1,j),(i+1,j),(i,j-1),(i,j+1)]):
                        if self.candyGame.inBounds(k,l):
                            #print "Checking", (k, l), ":", gameBoard[k][l], 
                            if gameBoard[k][l] != gameBoard[x][y]:
                                if gameBoard[k][l] != "_":
                                    """print prevNode, "noisy because", self.candyGame.otherPlayer(self).ID, "controls", (k,l)
                                    self.candyGame.printLayout(gameBoard)
                                    sys.exit(0)"""
                                    return False
        return True
        
         
if  __name__ =='__main__':
    board = "game_boards/ReesesPieces.txt"
    heuristic = ""
    loud = False
    p1 = "human"
    p2 = "human"
    if "--help" in sys.argv:
        print """
        candyGame.py by T. J. Tkacik
        
        Accepted flags:

        --help    for this help information
        -l        for loud output, default False
        -b        for game board source, default ReesesPieces.txt
        -p1       for player one, default is human, see below
        -p2       for player two, default is human, see below
            players are given in form <playertype><depth>
                Acceptable playertypes: human minimax alphabeta quiescence
            Default depth is used if none is given
                Default depths: human:0 minimax:3 alphabeta:4 quiescence:2
                
        Examples:   candyGame.py -l -p2 minimax3 -b Ayds.txt
                    candyGame.py -b long.txt -p1 minimax -p2 alphabeta3
                    candyGame.py -b oases.txt -p1 human -p2 quiescence
        """
        sys.exit(0)
    if "-l" in sys.argv:
        loud = True
    if "-b" in sys.argv:
        board = "game_boards/" + sys.argv[sys.argv.index("-b")+1]
    if "-p1" in sys.argv:
        p1 = sys.argv[sys.argv.index("-p1")+1]
    if "-p2" in sys.argv:
        p2 = sys.argv[sys.argv.index("-p2")+1]
    
    game = candyGame(board, p1, p2, loud)
