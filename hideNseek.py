# hideNseek.py
# Created by T. J. Tkacik for Assignment 2 of COMP 590
# Spring of 2014 at the University of North Carolina
import util, sys

class hideNseek(object):
    
    def __init__(self, input="stdin", heuristic="nullHeuristic", loud=False):
        self.trees = []
        self.N = 0
        self.T = 0
        self.expanded = 0
        self.assignment = []
        self.heuristic = heuristic
        self.backTracked = 0
        self.loud = loud
        
        if input == "stdin":
            self.N = eval(raw_input("How many friends?: "))
            self.T = eval(raw_input("How many trees?: "))
            #self.heuristic = raw_input("Heuristic to use?: ")
            for i in range(0, self.T):
                self.trees.append(eval(raw_input("Next tree? (X,Y): ")))
                self.trees[i] = (self.trees[i][0]-1, self.trees[i][1]-1)
                      
        else:
            source = open("hide_places/"+input)
            self.N, self.T = source.readline().strip().split("\t")
            if self.loud: print self.N, "friends to hide."
            self.N=eval(self.N)
            if self.loud: print self.T, "trees to consider."
            self.T=eval(self.T)
            for i in range(0, self.T):
                self.trees.append(source.readline().strip().split("\t"))
                self.trees[i] = (eval(self.trees[i][0])-1, eval(self.trees[i][1])-1)
           
        self.assignment = self.recursiveHide(self.assignment)
        if not self.assignment: 
            print "No valid assignment."
            sys.exit(0)
        for friend in self.assignment:
            print friend[0], friend[1]
        print self.expanded, " nodes expanded."
        print self.backTracked, " times back-tracked."
 
    def printLayout(self):
        layout = []
        for i in range(0, self.N):
            layout.append([])
            for j in range(0, self.N):
                layout[i].append('0')
        for x,y in self.trees:        
            layout[x][y] = 'T'
        for x,y in self.assignment:
            layout[x][y] = 'P'
            
        for row in layout:
            print row
            
    def runHeuristic(self, position, assignment):
        if self.heuristic == "nullHeuristic" or self.heuristic == "":
            return 0
        if self.heuristic == "localManhattan":
            if len(assignment) == 0: return 0
            dx = abs(position[1] - assignment[len(assignment)-1][1])
            dy = abs(position[0] - assignment[len(assignment)-1][0])
            #print position, ": ", dx + dy
            return 0 - dx - dy
        if self.heuristic == "globalManhattan":
            if len(assignment) == 0: return 0
            dx = 0
            dy = 0
            for i,j in assignment:
                dx += abs(position[1] - j)
                dy += abs(position[0] - i)
            #print position, ": ", dx + dy
            return 0 - dx - dy

    #recursiveHid takes a dictionary of variables to values    
    def recursiveHide(self, assignment):
        positions = util.PriorityQueue()
        if len(assignment) == self.N:
            return assignment
        for i in range(0, self.N):
            for j in range(0, self.N):                          #for each i, j that is potential next assignment
                positions.push((i,j), self.runHeuristic((i,j), assignment))
        while not positions.isEmpty():
            i,j = positions.pop()
            self.expanded += 1                              #Expanding Node
            if self.loud: print "checking position", (i, j)
            if (i, j) in self.trees + assignment:           #Alldiff 
                continue  
            seeFriend = False
            for x,y in assignment:                          #tree between friends
                if x == i:
                    seeFriend = True
                    for k in range(min(j, y)+1, max(j, y)):
                        if (i, k) in self.trees:
                            seeFriend = False
                            break
                if seeFriend: break
                if y == j:
                    seeFriend = True
                    for k in range(min(i, x)+1, max(i, x)):
                        if (k, j) in self.trees:
                            seeFriend = False
                            break
                if seeFriend: break
                if abs(x-i)==abs(y-j):
                    seeFriend = True
                    #print "Diagonals found at", x,y ,"and", i,j                    
                    ratio = (x-i)/(y-j)
                    for k in range(1, (i-x)):
                        #print "checking for tree in", (x+k,y+(ratio*k))
                        if(x+k,y+(ratio*k)) in self.trees:
                            #print "Diagonal tree found at", x+k, y+(ratio*k)
                            seeFriend = False
                            break
                if seeFriend: break
            if seeFriend:
                continue
            newAssignment = assignment + [(i, j)]
            if self.loud: print "position valid, continuing with ", newAssignment
            result = self.recursiveHide(newAssignment)
            if result != False: return result
        self.backTracked += 1                               #Backtrack
        return False
         
if  __name__ =='__main__':
    input = "stdin"
    heuristic = ""
    loud = False
    doPrint = False
    
    if "--help" in sys.argv:
        print """
        hideNseek.py by T. J. Tkacik
        
        Accepted flags:

        --help    for this help information
        -l        for loud output, default False
        -p        to print the final game board
        -s        for input source, default stdin
        -h        for heuristic, default nullHeuristic
        
        Examples:   hideNseek.py -s 10in5.txt -h globalManhattan
                    hideNseek.py -s 15in8.txt -h localManhattan
                    hideNseek.py -l
        """
        sys.exit(0)
    if "-l" in sys.argv:
        loud = True
    if "-s" in sys.argv:
        input = sys.argv[sys.argv.index("-s")+1]
    if "-h" in sys.argv:
        heuristic = sys.argv[sys.argv.index("-h")+1]
    if "-p" in sys.argv:
        doPrint = True
    
    game = hideNseek(input, heuristic, loud)
    
    if doPrint: game.printLayout()