#!/usr/local/bin/python3

from connect4 import *
import pdb
import random


def testdrop():
    maxdepth = 6
    B = board(WIDTH,HEIGHT)
    B1 = B.copy()
    
    def randomMove(B1,depth):
        if depth == 0:
            return True
        else:
            columns = [c for c in range(WIDTH) if B.bottom(c) >= 0]
            c = random.choice(columns)
            t1 = B1.drop(c)
            if not t1:
                print(". "*(maxdepth-depth) + "B1.drop(%d) failed" % c)
                pdb.set_trace()
            else:
                print(". "*(maxdepth-depth), "B1.drop(%d)." % c)
            
                t2 = randomMove(B1,depth-1)
                t3 = B1.undrop() if t2 else False
                
                if not t3:
                    print(". "*(maxdepth-depth) + "B1.undrop() failed")
                    pdb.set_trace()
                else:
                    print(". "*(maxdepth-depth), "B1.undropped() done")
            
            return t1 and t2 and t3

    depth = 8
    while True:
        try:
            if randomMove(B1,depth):
                if B != B1:
                    print("B1 does not compare to B!")
                    pdb.set_trace()
                    B1 = B.copy()
                else:
                    print("Depth %d Rewind successful." % depth)
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    testdrop()