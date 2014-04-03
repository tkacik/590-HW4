The python file spamClassifier.py was used to complete answers.pdf. The help information can be accessed using the flag --help and is displayed below.

spamClassifier.py by T. J. Tkacik
        
        Accepted flags:

        --help    for this help information
        -l        for loud output, default False
        -f        to select folder, default 'emails'
        -m        to assign Laplace smoothing m value, default 2
        -k        to assign minimum observations, default 5
        -p        to provide the relative path to a email to predict
               
        Examples:   spamClassifier.py -l -m 10 -k 10
                    spamClassifier.py -t -p emails/hamtesting/3110.2004-12-08.GP.spam.txt
                    spamClassifier.py -l -m 4 -t
