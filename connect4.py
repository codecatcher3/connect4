#!/usr/local/bin/python3
# connect4.py - the python version of the game of dropping counters to form lines
# COPYRIGHT (C) 2017 Chong Shang Shan <codecatcher3@github.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# NOTE: There is still a bug if the recursion depth goes too high. The bug
# is in the undrop() function which somehow does not rewind everything that drop() does.


EMPTY,RED,BLUE = range(3)

def opposite(color):
    return [EMPTY,BLUE,RED][color]

WIDTH = 7
HEIGHT = 7
LINELEN = 4

import copy
import sys
import pdb

import random
random.seed(27868)

MAXSCORE = 10000
INFSCORE = 1000*MAXSCORE

def sign(x): return -1 if x < 0 else +1 if x > 0 else 0


class board:

    def __init__(self,w=WIDTH,h=HEIGHT):
        "Start a new board."
        self.w, self.h = w, h
        self.empty()

    def empty(self):
        "Reset the board to empty."
        self.board = dict()
        for x in range(self.w):
            for y in range(self.h):
                self.board[x,y] = EMPTY
        self.init_lines()
        self.history = []
        self.wincolor = EMPTY
        self.ccolor = RED
        self.gameover = False

    def init_lines(self):
        "Initialize all the 88 possible lines to count zero."
        self.lines = dict()
        for l in self.all_lines(RED):
            self.lines[l] = 0
        for l in self.all_lines(BLUE):
            self.lines[l] = 0
        
    def copy(self):
        "Make a deep copy of the board position and lines."
        return copy.deepcopy(self)
    
    def __ne__(self,a): return not self.__eq__(a)
    def __eq__(self,a):
        if self.w != a.w or self.h != a.w: return False
        if self.history != a.history: return False
        if self.wincolor != a.wincolor: return False
        if self.ccolor != a.ccolor: return False
        if self.gameover != a.gameover: return False
        
        for x in range(self.w):
            for y in range(self.h):
                if self.board[x,y] != a.board[x,y]:
                    return False

        for k,v in self.lines.items():
            if not (k in a.lines): return False
            if self.lines[k] != a.lines[k]: return False
            
        return True

    def pos(self,x,y):
        return self.board[x,y]
        
    def bottom(self, x):
        "Returns first empty row of the xth column or -1 if not"
        y = HEIGHT-1
        while y >= 0 and self.board[x,y] != EMPTY:
            y -= 1
        return y if y >= 0 else -1
    
    def show(self):
        "prints out the board"
        emcell = [' ','r','b']
        for y in range(self.h):
            L = '|'
            for x in range(self.w):
                L += emcell[self.board[x,y]]+'|'
            print(L)

        while False: # turn on True to debug
            L = input('eval: ')
            if L != 'q':
                print(eval(L))
            else:
                break

    def showlines(self,color):
        
        def hlines(color):
            h = dict()
            for i in range(LINELEN+1):
                h[i] = 0

            for l in self.all_lines(color):
                if l in self.lines:
                    h[self.lines[l]] += 1
                else:
                    h[0] += 1
            return h
        
        hR = hlines(RED)
        hB = hlines(BLUE)
        
        print('lines = ', end='')
        print(hR,hB, sep='-')

        
    def lines_including(self,x,y,color):
        "Generator giving the tuples representing the 16 lines that include x,y"
        for ix in range(x,max(x-LINELEN,-1),-1):
            if 0 <= ix < WIDTH-LINELEN+1:
                yield (ix, y, color, 'E')
        
        for iy in range(y,max(y-LINELEN,-1),-1):
            if 0 <= iy < HEIGHT-LINELEN+1:          
                yield (x, iy, color, 'S')

        for d in range(LINELEN):
            (ix,iy) = (x-d, y-d)
            if 0 <= ix < WIDTH-LINELEN+1 and 0 <= iy < WIDTH-LINELEN+1:
                yield (ix, iy, color, 'SE')

        for d in range(LINELEN):
            (ix,iy) = (x+d, y-d)
            if WIDTH-LINELEN <= ix < WIDTH and 0 <= iy < WIDTH-LINELEN+1:
                yield (ix, iy, color, 'SW')
    
    def all_lines(self,color):
        "Generator that gives all the 88 tuples in a board of one color."
        for ix in range(0,WIDTH-LINELEN+1):
            for iy in range(HEIGHT):
                yield (ix,iy,color,'E')

        for ix in range(WIDTH):
            for iy in range(0,HEIGHT-LINELEN+1):
                yield (ix,iy,color,'S')

        for ix in range(0,WIDTH-LINELEN+1):
            for iy in range(0,HEIGHT-LINELEN+1):
                yield (ix,iy,color,'SE')

        for ix in range(WIDTH-LINELEN,WIDTH):
            for iy in range(HEIGHT-LINELEN+1):
                yield (ix,iy,color,'SW')
            
    def incr_lines(self, color, x, y):
        "Increment/decrement the lines that include (x,y)"
        if not self.gameover:
            for zzz in self.lines_including(x,y,color):
                self.lines[zzz] += 1
                    


    def decr_lines(self, color, x, y):
        "Increment/decrement the lines that include (x,y)"
        if not self.gameover:
            for zzz in self.lines_including(x,y,color):
                if self.lines[zzz] > 0:
                    self.lines[zzz] -= 1
                    
        
    def drop(self,x):
        "Makes a move by dropping at the xth column. Returns True/False for success/unsucces."

        if self.gameover:
            return False
        
        if not (0 <= x < self.w):
            return False
        
        y = self.bottom(x)
        if y >= 0:
            self.board[x,y] = self.ccolor
            self.incr_lines(self.ccolor, x, y)
            self.wincolor = self.winning()
            self.history.append(x)
            if self.wincolor != EMPTY:
                self.gameover = True
            else:
                self.ccolor = opposite(self.ccolor)
            return True
        else:
            return False

    def undrop(self):
        "Rewinds the history by one move by removing the last-dropped stone in its column."
            
        if len(self.history) > 0:
            x = self.history.pop()
            y = self.bottom(x)
            if y < 0 or y+1 >= HEIGHT:
                return False
            else:
                y += 1

            color = self.board[x,y]
            if color != EMPTY:
                if color == self.ccolor and self.gameover:
                    self.gameover = False
                else:
                    self.ccolor = opposite(self.ccolor)
                
                self.decr_lines(color, x, y)
                self.wincolor = self.winning()
                self.board[x,y] = EMPTY
                return True
            else:
                #pdb.set_trace()
                return False
        else:
            #pdb.set_trace()
            return False
        
    def lineval(self,ix,iy,c,dir):
        "Returns the line tuple (ix,iy,c,dir). If not exists, return 0. If opposite exists return 0. if the tuple is 0, but the opposite is not, return negative."
        def _lines(t): return self.lines[t] if t in self.lines else 0

        xx,yy = _lines((ix,iy,c,dir)), _lines((ix,iy,opposite(c),dir))
        if xx > 0 and yy > 0:
            return 0
        elif xx > 0 and yy == 0:
            return xx
        elif xx == 0 and yy > 0:
            return -yy
        elif xx == 0 and yy == 0:
            return 0
        
    def winning(self):
        "Is there a winning player at this position?"
        wincolor = EMPTY
        for line in self.all_lines(RED):
            lv = self.lineval(*line)
            if lv >= LINELEN:
                wincolor = RED
                break
            elif lv <= -LINELEN:
                wincolor = BLUE
                break
        
        self.wincolor = wincolor
        self.gameover = (wincolor != EMPTY)
        return wincolor
        
    
    def evaluate(self, color):
        "Evaluates current board position for the player color."
        def val(color):
            value = 0
            for line in list(self.all_lines(color)):
                lv = self.lineval(*line)
                if lv >= LINELEN:
                    return MAXSCORE
                elif lv <= LINELEN:
                    return -MAXSCORE
                else:
                    value += sign(lv)*(lv*lv) # square with sign
            return value
        
        return val(color) - val(opposite(color))
    
    def randomMove(self):
        "Makes a random move by dropping at a random column."
        if self.gameover:
            return False

        columns = [c for c in range(WIDTH) if self.bottom(c) >= 0 ]
        if len(columns) > 0:
            self.drop(random.choice(columns))
            return True
        else:
            return False
    
    def alphabetaMax(self, depth, alpha, beta, moveseq):
        "Search for the best move. Depth is depth to search to."

        if depth <= 0:
            return self.evaluate(self.ccolor)
        elif self.wincolor == self.ccolor:
            return MAXSCORE
        elif self.wincolor == opposite(self.ccolor):
            return -MAXSCORE
        
        bestMove = None
        bestValue = alpha
        columns = [c for c in range(WIDTH) if self.bottom(c) >= 0 ]
        random.shuffle(columns)
        for c in columns:
            if self.drop(c):
                print(". "*(10-depth),"min:%d"%c, self.gameover)
                score = self.alphabetaMin(depth-1, bestValue, beta, moveseq )

                if self.undrop():
                    if bestValue < score:
                        bestValue = score
                        bestMove = c

                    if beta <= bestValue:
                        break
                else:
                    print("Remove of drop %d failed." % c)
            else:
                print("Drop in column %d failed." % c)

        moveseq.append(bestMove)
        return bestValue
    
    def alphabetaMin(self, depth, alpha, beta, moveseq):

        if depth <= 0:
            return self.evaluate(self.ccolor)
        elif self.wincolor == self.ccolor:
            return MAXSCORE
        elif self.wincolor == opposite(self.ccolor):
            return -MAXSCORE
                
        bestMove = None
        bestValue = beta
        columns = [c for c in range(WIDTH) if self.bottom(c) >= 0 ]
        random.shuffle(columns)
        for c in columns:
            if self.drop(c):
                print(". "*(10-depth),"max:%d"%c, self.gameover)
                score = self.alphabetaMax(depth-1, alpha, bestValue, moveseq )

                if self.undrop():
                    if score < bestValue:
                        bestValue = score
                        bestMove = c

                    if bestValue <= alpha:
                        break
                else:
                    print("Remove of drop %d failed" % c)
            else:
                print("Drop in column %d failed." % c)
                    
        moveseq.append(bestMove)
        return bestValue
    
    def makemove(board, thinkahead):
        moves = []
        score = board.alphabetaMax(thinkahead, -INFSCORE, +INFSCORE, moves)
        if len(moves) > 0 and moves[0]:
            board.drop(moves[0])
        else:
            board.randomMove()
        return len(moves) > 0


    
#if __name__ == '__main__':
#    #testdrop()
#    #sys.exit(-1)
#    B = board(WIDTH,HEIGHT)
#    B.show()
#    B.showlines(B.ccolor)
#    thinkahead = 4
#    inp = ''
#    while not B.gameover and inp != 'q':
#        inp = input('column (^D to stop) = ')
#        try:
#            i = int(inp)
#            if i > 0:
#                B.drop(i-1)
#                if B.wincolor == EMPTY:
#                    B.makemove(thinkahead)
#        except EOFError:
#            break

#        B.show()
#        B.showlines(B.ccolor)
    
#    if B.gameover:
#        B.show()
#        if B.wincolor != EMPTY:
#            print(['','RED','BLUE'][B.wincolor], 'wins!')
