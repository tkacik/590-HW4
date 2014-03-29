Two python files contain the code used to complete the Assignment 2 writeup. The help information can be accessed using the flag --help and is displayed below.

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
