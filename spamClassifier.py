# candyGame.py
# Created by T. J. Tkacik for Assignment 4 of COMP 590
# Spring of 2014 at the University of North Carolina
import util, sys, time, os, math, random


class lexicon(object):
    def __init__(self, folder = None, dictionary = None):
        self.dictionary = {}
        self.folder = folder
        if dictionary != None:
            self.dictionary = dictionary
            #print "Dictionary Copied", len(dictionary)
        if folder != None:
            self.load(self.folder)
        
    def load(self, folder):
        fileCount = 0
        for root, subFolders, files in os.walk(folder):
                for txt in files:
                    fileCount += 1
                    with open(os.path.join(root, txt), 'r') as fin:
                        for lines in fin:
                            for words in lines.strip().split(" "):
                                if words in self.dictionary:
                                    self.dictionary[words] += 1
                                else:
                                    self.dictionary[words] = 1
    
    def purge(self, k=0):
        toDrop = set()
        for keys in self.dictionary:
            if self.dictionary[keys] < k:
                toDrop.add(keys)
        for keys in toDrop:
            del self.dictionary[keys]

    def duplicate(self):
        return lexicon(None, self.dictionary.copy())

        
class spamClassifier(object):
    def __init__(self, folder=None):
        self.folder = folder
        if self.folder == None:
            self.folder = "emails"
       
        #Compute Features
        self.lexicon = lexicon(self.folder)
        
        #Tune and Train
        self.lgPriors = self.calcPriors(self.folder)
        k,m = self.tuneParameters(self.folder)
        self.lexicon.purge(k)
        lgLikelihoods = self.calcLikelihoods(self.folder, self.lexicon, m)
        
        #Test
        confusionMatrix = self.test(self.folder, self.lgPriors, lgLikelihoods)
        print confusionMatrix
        
    def tuneParameters(self, folder):   #Tuple: k, m
        parameterMatrix = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
        M, K = 99, 99
        best = 0
        x, y = -1, -1
        for k in set([0,1,5,10,20]):
            x += 1
            y = -1
            for m in set([1,5,10,25,50]):
                y += 1
                trainingSet = set()
                holdOutSet = set()
                for txt in os.listdir(os.path.join(folder, "spamtraining")):
                    if random.random() < 0.50:
                        holdOutSet.add((os.path.join(folder, "spamtraining", txt), "spam"))
                    else: trainingSet.add((os.path.join(folder, "spamtraining", txt), "spam"))
                for txt in os.listdir(os.path.join(folder, "hamtraining")):
                    if random.random() < 0.50:
                        holdOutSet.add((os.path.join(folder, "hamtraining", txt), "ham"))
                    else: trainingSet.add((os.path.join(folder, "hamtraining", txt), "ham"))
                    wat = txt
                lex = self.lexicon.duplicate()
                lex.purge(k)
                lgLikelihoods = self.calcLikelihoods(self.folder, lex, m, trainingSet)
                accuracy = self.calcAccuracy(self.test(self.folder, self.lgPriors, lgLikelihoods, holdOutSet))
                if accuracy > best:
                    best, M, K = accuracy, m, k
                    print "new best M, K:", M, K
                parameterMatrix[x][y] = accuracy
        print parameterMatrix
        print K, M
            
        return K, M
    
    def calcAccuracy(self, matrix):
        return (float(matrix[0][0]) + matrix[1][1])/(matrix[0][0] + matrix[0][1] + matrix[1][0] + matrix[1][1])
                
        
    def test(self, folder, lgPriors, lgLikelihoods, testSet=None):
        confusionMatrix = [[0,0],[0,0]]  #m[0][1] is count of spam labeled ham
        
        if testSet == None:
            testSet = set()
            for txt in os.listdir(os.path.join(folder, "spamtesting")):
                testSet.add((os.path.join(folder, "spamtesting", txt), "spam"))
            for txt in os.listdir(os.path.join(folder, "hamtesting")):
                testSet.add((os.path.join(folder, "hamtesting", txt), "ham"))
                
                
        for path in testSet:
            pSpam, pHam = lgPriors[0], lgPriors[1]
            for lines in open(path[0]):
                for words in lines.strip().split(" "):
                    if words in lgLikelihoods:
                        pSpam += lgLikelihoods[words][0]
                        pHam += lgLikelihoods[words][1]
            if pSpam == pHam : print "ERROR: NO ASSIGNMENT"
            if path[1] == "spam":
                if pSpam > pHam: confusionMatrix[0][0] += 1
                else: 
                    confusionMatrix[0][1] += 1
                    #print "Bad Assignment:", path[0], "as ham"
            elif path[1] == "ham":
                if pSpam > pHam: 
                    confusionMatrix[1][0] += 1
                    #print "Bad Assignment:", path[0], "as spam"
                else: confusionMatrix[1][1] += 1

        return confusionMatrix
        
    def calcPriors(self, folder):   #Tuple: (lg(spamPrior), lg(hamPrior))
        spamCount = 0.0
        hamCount = 0.0
        for txt in os.listdir(os.path.join(folder, "spamtraining")):
            spamCount += 1
        for txt in os.listdir(os.path.join(folder, "hamtraining")):
            hamCount += 1
        return (math.log(spamCount/(spamCount+hamCount)), math.log(hamCount/(spamCount+hamCount)))
    
    def calcLikelihoods(self, folder, lexicon, m=1, trainingSet=None):    #Dictionary of tuples: {key: (lg(spamLikelihood), lg(hamLikelihood))}
        counts = {}
        m += 0.0
        spamTotal = 0.0
        hamTotal = 0.0
        if trainingSet == None:
            trainingSet = set()
            for txt in os.listdir(os.path.join(folder, "spamtraining")):
                trainingSet.add((os.path.join(folder, "spamtraining", txt), "spam"))
            for txt in os.listdir(os.path.join(folder, "hamtraining")):
                trainingSet.add((os.path.join(folder, "hamtraining", txt), "ham"))
                
        for path in trainingSet:
            for lines in open(path[0]):
                for words in lines.strip().split(" "):
                    if words in lexicon.dictionary:
                        if words not in counts:
                            counts[words] = (m, m)
                            spamTotal += m
                            hamTotal += m
                        elif path[1] == "spam":
                            counts[words] = (counts[words][0] + 1, counts[words][1])
                            spamTotal += 1
                        elif path[1] == "ham":
                            counts[words] = (counts[words][0], counts[words][1] + 1)
                            hamTotal += 1

        for words in counts:
            counts[words] = (math.log(counts[words][0]/(spamTotal)), math.log(counts[words][1]/(hamTotal)))
        print spamTotal, hamTotal
        return counts
                
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
    spamClassifier()
    
    ''' board = "game_boards/ReesesPieces.txt"
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
'''