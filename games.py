import queue
import random
from dirtyfunctions import WrongActError

class Match():
    """
    Internal Variables: matchNum, array,
    Object Variables : playerType, player,
                        win, lose, score, tiescore,
                        playerNum, underMatch, upperMatch, finished

    Functions:
        __init__(self, playerType)

        winner(self), loser(self), depth(self), editable(self), endmatch(self)

        underplayers(self), undermatches(self),

        push(self, newplayer), result(self, score1, score2, tiescore1=0, tiescore2=0)
        findschool(self, target), _pushcondition(self, newplayer, direction)
    """
    matchNum=0
    array=[]
    def __init__(self, playerType):
        """Metaobject Control"""
        Match.matchNum+=1
        self.matchNum=Match.matchNum
        Match.array.append(self)

        """Player Variables"""
        self.playerType=playerType
        #Set default players as Dummy - playerType.array should be sorted by power order
        self.player=[playerType.bye(), playerType.bye()]

        """Match Variables"""
        self.win=None
        self.lose=None
        self.score=[0, 0]
        self.tieScore=None

        """System Variables"""
        self.playerNum=0
        self.underMatch=[]
        self.upperMatch=None
        self.finished=False


    """System Functions"""
    def winner(self):
        if self.win is None:
            return self.playerType.dummy("#{0} Winner".format(self.matchNum))
        else:
            return self.win

    def loser(self):
        if self.lose is None:
            return self.playerType.dummy("#{0} Loser".format(self.matchNum))
        else:
            return self.lose

    def depth(self):
        if self.upperMatch is None:
            return 0
        else:
            return self.upperMatch.depth()+1

    def editable(self):
        #leaf : editable if not finished
        if self.underMatch==[]:
            return not(self.finished)

        #branch + finished(true) : Not Editable(already done)
        if self.underMatch!=[] and self.finished:
            return False

        #branch + finished(false) : true if both undermatch is finished
        if self.underMatch!=[] and not (self.finished):
            return self.underMatch[0].finished and self.underMatch[1].finished

    def endmatch(self):
        if self.score[0]>self.score[1]:
            self.win=self.player[0]
            self.lose=self.player[1]
            self.end_match()
            self.finished=True

        if self.score[0]<self.score[1]:
            self.win=self.player[1]
            self.lose=self.player[0]
            self.end_match()
            self.finished=True

        if self.score[0]!=self.score[1] and self.upperMatch is not None:
            self.upperMatch.player[self.upperMatch.underMatch.index(self)]\
            =self.winner()
        
        


    def underplayers(self):
        if self.underMatch==[]:
            return self.player
        else:
            return self.underMatch[0].underplayers()\
                 + self.underMatch[1].underplayers()

    def undermatches(self):#for tournament draw
        if self.underMatch!=[]:
            return self.underMatch[0].undermatches()\
                +[self]\
                +self.underMatch[1].undermatches()
        else:
            return [self]

    """Tournament Functions"""
    def push(self, newplayer):
        if newplayer.isbye():
            return
        #if match is not full
        if self.playerNum<2:
            self.player[self.playerNum]=newplayer
            self.playerNum+=1

        #if match is full / no underMatch
        elif self.underMatch==[]:
            self.underMatch=[self.__class__(self.playerType), \
                             self.__class__(self.playerType)]
            self.underMatch[0].upperMatch=self
            self.underMatch[1].upperMatch=self

            self.underMatch[0].push(self.player[0])
            self.underMatch[1].push(self.player[1])

            self.player[0]=self.underMatch[0].winner()
            self.player[1]=self.underMatch[1].winner()

            self.underMatch[1].push(newplayer)#Initial push direction : right
            self.playerNum=self.underMatch[0].playerNum + self.underMatch[1].playerNum

        #match is full and there is already underMatch
        else:
            #push to smaller subtree
            direction=0 if self.underMatch[0].playerNum<self.underMatch[1].playerNum else 1
            #check pushCondition
            direction=self._pushcondition(newplayer, direction)
            self.underMatch[direction].push(newplayer)
            self.playerNum=self.underMatch[0].playerNum + self.underMatch[1].playerNum

    def result(self, score1, score2, tiescore1=0, tiescore2=0):
        self.score=[score1, score2]
        #TieBreak
        if (score1==6 and score2==6) or 7 in [score1, score2]:
            self.tieScore=[tiescore1, tiescore2]

    """Just For Time Set"""
    def start_match(self):
        self.player[0].start_match()
        self.player[1].start_match()

    def end_match(self):
        self.player[0].end_match()
        self.player[1].end_match()

    # def weight(self):
    #     if self.underMatch==[]:
    #         return self.player[0].power+self.player[1].power
    #     else:
    #         return self.underMatch[0].weight()+self.underMatch[1].weight()
    """Other Functions"""
    def findschool(self, target):
        count=0
        under=self.underplayers()
        for x in under:
            if x.school()==target:
                count+=1
        return count

    def _pushcondition(self, newplayer, direction):
        x=direction
        if newplayer.power>1000:
            return x
        if self.underMatch[direction].findschool(newplayer.school())>\
        self.underMatch[(direction+1)%2].findschool(newplayer.school()):
            # print("school control at match",self.matchNum)\
            x=(direction+1)%2
    
        return x

    def players_ready(self):
        return not (self.player[0].on_play() or self.player[1].on_play())


class Court():
    """
    Internal Variables:
    Object Variables : game

    Functions:
        __init__(self)
        setgame(self, newgame), empty(self)
    """
    def __init__(self, courtnum):
        self.match=None
        self.courtnum=courtnum

    def empty(self):
        return (self.match is None)

    def setgame(self, newgame):
        if self.empty():
            self.match=newgame
        else:
            raise WrongActError("이미 코트에 배정된 경기가 있습니다!")

    def clear_court(self, cleartype='finish'):
        if cleartype=='finish':
            self.match.endmatch()
            self.match=None
        elif cleartype=='reset':
            self.match.end_match() #for resetting time
            self.match.score=[0, 0]
            self.match=None

        
            
