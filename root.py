from players import Person, SinglePlayer, DoublePlayer
from games import Match, Court
import filecontrol
from dirtyfunctions import makeseq, singleproblem, doubleproblem, DirtyRoot
import datetime as dt

class Root(DirtyRoot):
    """
    Internal Variables:
    Object Variables : SingleRoot, DoubleRoot, SingleSequence,
                       DoubleSequence, Courts, singlegoogle, doublegoogle
    Functions:
        __init__(self, singleroot=None, doubleroot=None)

        start(self)

        save(self, filepath), load(self, filepath),
        changecourtnum(self, newcourtnum)

        setmainwin(self, win), maketour(self), haveproblem(self)

        at DirtyRoot :
        waitingmatches(self, root), courtbut_exist(self, courtbut),
        askcourtlabel(self, courtbut), waiting_tableform(self, single=True),

    """


    def __init__(self, singleroot=None, doubleroot=None):
        super().__init__()
        self.SingleRoot=singleroot
        self.DoubleRoot=doubleroot
        self.singlematchdic={}
        self.doublematchdic={}
        self.SingleSequence=[]
        self.DoubleSequence=[]
        self.Courts=[]
        self.mainwin=None


    """Match Functions"""
    def _start_single(self):
        #set PlayerID
        queue = [self.SingleRoot]
        playerCnt = 1
        while len(queue) != 0:
            this = queue.pop()
            if this is None:
                break
            elif this.underMatch==[]:
                if not this.player[0].isbye():
                    this.player[0].playerID = playerCnt
                    playerCnt+=1
                if not this.player[1].isbye():
                    this.player[1].playerID = playerCnt
                    playerCnt+=1
            else:
                queue.insert(0, this.underMatch[0])
                queue.insert(0, this.underMatch[1])

        #Refine Matches With Bye
        if self.SingleRoot is not None:
            singleMatches=self.SingleRoot.undermatches()
            for m in singleMatches:
                if m.player[1].isbye() and m.editable():
                    m.result(6, 0)
                    m.endmatch()
        
        if not self.singlematchdic.keys() and self.SingleRoot is not None:
            for g in self.SingleRoot.undermatches():
                self.singlematchdic[g.matchNum]=g
        
        #Make MatchSequence
        if self.SingleRoot is not None:
            self.SingleSequence=makeseq(self.SingleRoot)
        
    def _start_double(self):
        #set PlayerID
        queue = [self.DoubleRoot]
        playerCnt = 1
        while len(queue) != 0:
            this = queue.pop()
            if this is None:
                break
            if len(this.underMatch)==0:
                if not this.player[0].isbye():
                    this.player[0].playerID = playerCnt
                    playerCnt+=1
                if not this.player[1].isbye():
                    this.player[1].playerID = playerCnt
                    playerCnt+=1
            else:
                if this.underMatch[0] is not None:
                    queue.insert(0, this.underMatch[0])
                if this.underMatch[1] is not None:
                    queue.insert(0, this.underMatch[1])

        #Refine Matches With Bye
        if self.DoubleRoot is not None:
            doubleMatches=self.DoubleRoot.undermatches()
            for m in doubleMatches:
                if m.player[1].isbye() and m.editable():
                    m.result(6, 0)
                    m.endmatch()

        if not self.doublematchdic.keys() and self.DoubleRoot is not None:
            for g in self.DoubleRoot.undermatches():
                self.doublematchdic[g.matchNum]=g

        #Make MatchSequence
        if self.DoubleRoot is not None:
            self.DoubleSequence = makeseq(self.DoubleRoot)

    def start(self):
        self._start_single()
        self._start_double()

    """Control Functions"""
    def save(self, filepath, option="whole"):
        path=filepath
        if "." in filepath[-5:]:
            path=filepath[filepath.index(".")-1:]

        if option=='slim':
            filecontrol.write_excel_slim(path+".xlsx", self.SingleRoot, self.DoubleRoot)
        elif option=='both':
            filecontrol.write_excel(path+".xlsx", self.SingleRoot, self.DoubleRoot)
            filecontrol.write_excel_slim(path+"_slim.xlsx", self.SingleRoot, self.DoubleRoot)
        else:
            filecontrol.write_excel(path+".xlsx", self.SingleRoot, self.DoubleRoot)
        filecontrol.write_pickle(path+".tr", self)


    def load(self, filepath):
        filecontrol.read_pickle(filepath, self)
    """
    def googlesave(self, spreadsheetId):
        if self.SingleRoot is not None:
            filecontrol.google_writeall(spreadsheetId, self.SingleRoot, "Singles", self)
        if self.DoubleRoot is not None:
            filecontrol.google_writeall(spreadsheetId, self.DoubleRoot, "Doubles", self)"""

    def changecourtnum(self, newcourtnum):
        while len(self.Courts)!=newcourtnum:
            if len(self.Courts)!=0 and len(self.Courts)>newcourtnum \
                                   and self.Courts[-1].empty():
                self.Courts.pop(-1)
            if len(self.Courts)!=0 and len(self.Courts)>newcourtnum \
                                   and (not self.Courts[-1].empty()):
                raise WrongActError("{0}번 코트는 경기가 진행중입니다!"\
                                    .format(len(self.Courts)+1))
            if len(self.Courts)<newcourtnum:
                self.Courts.append(Court(len(self.Courts)+1))

    def setmainwin(self, win):
        self.mainwin=win

    def set_strattime(self):
        for k in Person.infoDic.keys():
            p=Person.infoDic[k]
            p.final_time=dt.datetime.now()

    """Tour Making Functions"""
    def maketour_single(self):
        """Reset and Initializing"""
        SinglePlayer.reset()
        self.singlematchdic={}

        """singles"""
        Match.matchNum=0
        if len(SinglePlayer.array)>3:
            self.SingleRoot=Match(SinglePlayer)
            for x in SinglePlayer.array:
                self.SingleRoot.push(x)

    def maketour_double(self):
        """Reset and Initializing"""
        DoublePlayer.reset()
        self.doublematchdic={}

        """doubles"""
        Match.matchNum=0
        if len(DoublePlayer.array)>3:
            self.DoubleRoot=Match(DoublePlayer)
            for x in DoublePlayer.array:
                self.DoubleRoot.push(x)
    
    def haveproblem_single(self, err_count=0):
        return singleproblem(self.SingleRoot, self, err_count)
    
    def haveproblem_double(self, err_count=0):
        return doubleproblem(self.DoubleRoot, self, err_count)
