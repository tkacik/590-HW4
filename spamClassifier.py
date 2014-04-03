# candyGame.py
# Created by T. J. Tkacik for Assignment 4 of COMP 590
# Spring of 2014 at the University of North Carolina
import util, sys, time, os, math, random


class lexicon(object):
    def __init__(self, folder = None, dictionary = None, n=1):
        self.dictionary = {}
        self.folder = folder
        if dictionary != None:
            self.dictionary = dictionary
            #print "Dictionary Copied", len(dictionary)
        if folder != None:
            self.load(self.folder)
        
    def load(self, folder):
        for root, subFolders, files in os.walk(folder):
            for txt in files:
                with open(os.path.join(root, txt), 'r') as fin:
                    for lines in fin:
                        for words in lines.strip().split(" "):
                            if words in self.dictionary:
                                self.dictionary[words] += 1
                            else:
                                self.dictionary[words] = 1
    def nload(self, folder, n):
        lastWords = [None]*n
        i=0
        for root, subFolders, files in os.walk(folder):
            for txt in files:
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
    def __init__(self, folder=None, m =2, k = 5, tune = False, loud = False):
        self.folder = folder
        self.loud = loud
        m, k = float(m), float(k)
        if self.folder == None:
            self.folder = "emails"
       
        #Compute Features
        self.lexicon = lexicon(self.folder)
        
        #Tune and Train
        self.lgPriors = self.calcPriors(self.folder)
        if tune:
            k,m = self.tuneParameters(self.folder, m, k)
        self.lexicon.purge(k)
        self.lgLikelihoods = self.calcLikelihoods(self.folder, self.lexicon, m)
        
        #Test
        confusionMatrix = self.test(self.folder, self.lgPriors, self.lgLikelihoods)
        if self.loud:
            print "Confusion Matrix:"
            print "Spam, Ham"
            for lines in confusionMatrix:
                print lines
            print "Overall Accuracy:", self.calcAccuracy(confusionMatrix)
            print "Spam Accuracy:", float(confusionMatrix[0][0])/(sum(confusionMatrix[0]))
            print "Ham Accuracy:", float(confusionMatrix[1][1])/(sum(confusionMatrix[1]))
            
    def predict(self, predictionSet):
        if predictionSet.endswith(".txt"):
            pSpam, pHam = self.lgPriors[0], self.lgPriors[1]
            for lines in open(predictionSet):
                for words in lines.strip().split(" "):
                    if words in self.lgLikelihoods:
                        pSpam += self.lgLikelihoods[words][0]
                        pHam += self.lgLikelihoods[words][1]
            if pSpam == pHam : print "ERROR: NO ASSIGNMENT"
            elif pSpam > pHam: print "Spam"
            else: print "Ham"
            print "pSpam/pHam:", math.exp(pSpam - pHam)
            
    def tuneParameters(self, folder, m, k):   #Tuple: k, m
        if self.loud:
            print "Tuning values for M and K..."
        parameterMatrix = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
        M, K = 99, 99
        best = 0
        for i in range(0,4):
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
            for x in range(0,5):
                M = 1 + math.floor(m*1.8**(x-1))
                for y in range(0,5):
                    K = math.floor(k*1.8**(y-1))
                    lex = self.lexicon.duplicate()
                    lex.purge(K)
                    lgLikelihoods = self.calcLikelihoods(self.folder, lex, M, trainingSet)
                    parameterMatrix[x][y] += self.calcAccuracy(self.test(self.folder, self.lgPriors, lgLikelihoods, holdOutSet))
                    if parameterMatrix[x][y] > best:
                        best, bestM, bestK = parameterMatrix[x][y], M, K
                    #parameterMatrix[x+1][y+1] = accuracy
        if self.loud:
            print "Best values for M, K:", bestM, bestK 
            
        return bestK, bestM
    
    def calcAccuracy(self, matrix):
        correct = 0
        total = 0.0
        for x in range(0, len(matrix)):
            correct += matrix[x][x]
            total += sum(matrix[x])
        return correct/total                
        
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
                    #print "pSpam/pHam:", math.exp(pSpam - pHam)
            elif path[1] == "ham":
                if pSpam > pHam: 
                    confusionMatrix[1][0] += 1
                    #print "Bad Assignment:", path[0], "as spam"
                    #print "pSpam/pHam:", math.exp(pSpam - pHam)
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
        return counts
          
if  __name__ =='__main__':
    loud = False
    m = 2
    k = 5
    tune = False
    folder = "emails"
    
    if "-l" in sys.argv:
        loud = True
    if "-t" in sys.argv:
        tune = True
    if "-m" in sys.argv:
        m = sys.argv[sys.argv.index("-m")+1]
    if "-k" in sys.argv:
        k = sys.argv[sys.argv.index("-k")+1]
    if "-f" in sys.argv:
        folder = sys.argv[sys.argv.index("-f")+1]
        
    classifier = spamClassifier(folder, m, k, tune, loud)
    
    if "-p" in sys.argv:
         classifier.predict(sys.argv[sys.argv.index("-p")+1])
    
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