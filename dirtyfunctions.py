from GoogleAPI import google
import datetime as dt
from players import Person

def _zigzagMerge(a, b):
    timeForA=True
    res=[]
    while len(a)!=0 and len(b)!=0:
        if timeForA:
            res.append(a.pop(0))
            timeForA=False
        else:
            res.append(b.pop(0))
            timeForA=True
    if len(a)!=0:
        res+=a
    elif len(b)!=0:
        res+=b
    return res

def _sortForMS(arr):
    maxdepth=0
    ret=[]
    for g in arr:
        if g.depth()>maxdepth:
            maxdepth=g.depth()
    for i in range(maxdepth, -1, -1):
        for g in arr:
            if g.depth()==i:
                ret.append(g)
    return ret

def makeseq(match):
    if len(match.underMatch)==2:
        left=makeseq(match.underMatch[0])
        right=makeseq(match.underMatch[1])
        merge=_zigzagMerge(left, right)
        merge.append(match)
    else:
        merge=[match]

    merge=_sortForMS(merge)
    return merge

class WrongActError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

def singleproblem(singleroot, root):
    """
    1) 시드권자 8명 (작년 1등/2등/4강진출자 2명/ 8강진출자 4명)
    - AD/ CD/ BD/ CD 이렇게 박스에 분포
    - 128강에서 무조건 bye 탐
    2) 학교 별 선수가 박스 4개에 균등하게 분포
    - 같은 학교가 최대한 나중에 만날 수 있도록
    3) 시드순서 
    - A-D시드와 임의로 선정된 1시드가 128강에서 Bye를 탐
    - 1시드는 초반에 4,5시드와 경기하도록 매칭돼있음 (높은 시드는 낮은 시드를 만나도록 배정)
    - 박스별로 각 시드숫자 선수 명수도 비교적 균등하게 분포
    4) Bye 분포
    - 각 box/ sub-box 별로 bye 개수 균등 분배
    """
    if root.SingleRoot is None:
        return False
    for g in root.singlematchdic.values():
        """leaf match : check 1)"""
        if g.underMatch==[]:
            if g.depth()==7: # 258강 경기 배제 
                print("258 Warning")
                return True
            if g.depth()==5: # 128강 없는 경기(double-bye)배제
                print("DoubleBye Warning")
                return True
            if g.player[0].power>1000 and not g.player[1].isbye(): 
                print("Top-seed Nonbye Warning")
                #톱시드권자가 bye 못타는 상황 배제
                return True
            if g.player[0].power<400 and g.player[1].isbye():
                print("Lower Seed Bye Warning")
                # 모 학교 2시드가 bye타는상황 배제
                return True
        if g.depth()<3:
            if abs(_countBye(g.underMatch[0])-_countBye(g.underMatch[1]))>1:
                print("Non-balanced Bye Warning")
                #8강경기 이상을 중심으로 하는 박스에서 bye의 갯수 불균등한 경우 배제
                return True
    return False

def doubleproblem(doubleroot, root):
    if root.DoubleRoot is None:
        return False
    # for g in root.doublematchdic.values():
    #     """leaf match : check 1)"""
    #     if g.underMatch==[]:
    #         if g.depth()==6: # 128강 경기 배제 
    #             return True
    #         if g.depth()==4: # 64강 없는 경기(double-bye)배제
    #             return True
    #         if g.player[0].power>1000 and not g.player[1].isbye(): 
    #             #톱시드권자가 bye 못타는 상황 배제
    #             return True
    #         if g.player[0].power<400 and g.player[1].isbye():
    #             #모 학교 2시드가 bye타는상황 배제
    #             return True
    #     if g.depth()<3:
    #         if abs(_countBye(g.underMatch[0])-_countBye(g.underMatch[1]))>1:
    #             #8강경기 이상을 중심으로 하는 박스에서 bye의 갯수 불균등한 경우 배제
    #             return True
    return False    

def _countBye(target):
    udm=target.undermatches()
    count=0
    for g in udm:
        if g.player[1].isbye():
            count+=1

    return count

def _countschool(target):
    schools={}
    for i in range(65, 90):
        schools[chr(i)]=0
    udm=target.undermatches()
    for g in udm:
        if g.underMatch==[]:
            schools[g.player[0].school()]+=1
            if not g.player[1].isbye():
                schools[g.player[1].school()]+=1
    s=""
    for scl in schools.keys():
        if schools[scl]>1:
            s+="{0} : {1} / ".format(scl, schools[scl])
    return s

def _countseed(target):
    seeds={}
    for i in range(1, 6):
        seeds[i]=0
    udm=target.undermatches()
    for g in udm:
        if g.underMatch==[]:
            seeds[g.player[0].seed]+=1
            if not g.player[1].isbye():
                seeds[g.player[1].seed]+=1
    
    s=""
    for sd in seeds.keys():
        s+="{0} : {1} / ".format(sd, seeds[sd])
    return s

def google_conn(spreadSheetId):
    googleconn=google(auth="rw")
    googleconn.get_credentials()
    googleconn.setSheetId(spreadSheetId)
    return googleconn

def google_singleset(googleconn, matchindex, x, sheetname, waiting_info=""):
    nodeHeight=7
    matchindex+=1

    startHeight=(nodeHeight * x.depth()) + 2
    countToFormat=""
    thiscount=matchindex

    while thiscount>25:
        countToFormat=chr(int(65+(thiscount%26)))+countToFormat
        thiscount=thiscount/26
    if matchindex>=26:
        countToFormat=chr(int(64+(thiscount%26)))+countToFormat
    else:
        countToFormat=chr(int(65+(thiscount%26)))+countToFormat
    # print(matchindex, countToFormat)
    # print(x.depth)

    rangeName = '{3}!{0}{1}:{0}{2}'.\
            format(countToFormat, startHeight, startHeight+8, sheetname)
    googleconn.addData(rangeName, \
    [
    ["Match #" + str(x.matchNum)],
    ["{0} vs. {1}".format(x.player[0].name('schoollong'), x.player[1].name('schoollong'))],
    ["Level : {0}".format(str(2**x.depth()*2)+"강" if x.depth()!=0 else "결승")],
    ["score : {0} : {1}".format(x.score[0], x.score[1])],
    ["power : {0} : {1}".format(x.player[0].power, x.player[1].power)],
    ["UpperMatch" + str(x.upperMatch.matchNum) if x.upperMatch is not None else "-"],
    [
        "UnderMatch {0}, {1}".format(\
        x.underMatch[0].matchNum if len(x.underMatch)!=0 else "-", \
        x.underMatch[1].matchNum if len(x.underMatch)!=0 else "-")\
    ],
    [waiting_info]
    ])


def google_update(googleconn):
    googleconn.updateData()


def match_general_info(target):
    s="Match {0} Information\t\t\n{1} vs. {2} ({3}-{4})".format(target.matchNum, \
    target.player[0].name('schoollong', sep="&"), target.player[1].name('schoollong', sep="&"),\
    target.score[0], target.score[1])
    return s

class DirtyRoot():
    def __init__(self):
        pass

    def waitingmatches(self, root):
        udm=root.undermatches()
        wm=[]
        incourt=[]
        for c in self.Courts:
            if not c.empty():
                incourt.append(c.match)

        for m in udm:
            if m.editable() and (m not in incourt) and m.players_ready():
                wm.append(m)
        return wm

    def askcourtlabel(self, courtbut):
        if courtbut not in self.mainwin.courtbuttons:
            raise WrongActError("Asked Court Does Not Exist")
        else:
            courtnum=courtbut.court.courtnum
            returnstr="Court {0}\n".format(courtnum)

            if not courtbut.court.empty():
                match=courtbut.court.match
                returnstr+="Match#{4}\n{0}({1})\nvs.\n{2}({3})".\
                        format(match.player[0].name(sep='\n'), \
                        match.score[0], match.player[1].name(sep="\n"), match.score[1],\
                        match.matchNum)

            return returnstr

    def waiting_tableform(self, single=True):
        waitingArray=self.waitingmatches(self.SingleRoot if single else self.DoubleRoot)
        waitingArray=_sortForMS(waitingArray)
        items=[]
        for i in range(len(waitingArray)):
            g=waitingArray[i]
            items.append([str(2**(g.depth()+1))+"강" if g.depth()!=0 else "결승",\
             g.player[0].name("school, short, time"),g.player[1].name("school, short, time"),"{0}->{1}->{2}".\
             format(g.upperMatch.matchNum if g.upperMatch is not None else "-", \
             g.upperMatch.upperMatch.matchNum if g.upperMatch is not None \
             and g.upperMatch.upperMatch is not None else "-", \
             g.upperMatch.upperMatch.upperMatch.matchNum if g.upperMatch is not None\
             and g.upperMatch.upperMatch is not None\
             and g.upperMatch.upperMatch.upperMatch is not None else "-"),\
             str(g.matchNum)])
        return items

    
    def _unLockMatchRec(self, target):
        if target.finished==False:
            return []
        else:
            resetLog=[]
            print(target.matchNum)
            target.finished=False
            target.score=[0, 0]
            if target.upperMatch.underMatch[0]==target:
                target.upperMatch.player[0]=\
                target.upperMatch.playerType("#" + str(target.matchNum) + "Winner", 0)
            else:
                target.upperMatch.player[1]=\
                target.upperMatch.playerType("#" + str(target.matchNum) + "Winner", 0)

            if target.upperMatch.finished==True:
                resetLog=self._unLockMatchRec(target.upperMatch)
            resetLog.append(target)
            return resetLog

    def _shifttime(self):
        for k in Person.infoDic.keys():
            p=Person.infoDic[k]
            p.final_time-=dt.timedelta(minutes=1)

    def waiting_information(self, match):
        if match in self.SingleRoot.waitingmatches():
            return "대기번호 : {0}".format(self.SingleRoot.waitingmatches().index(match))
        elif match in self.DoubleRoot.waitingmatches():
            return "대기번호 : {0}".format(self.DoubleRoot.waitingmatches().index(match))
        else:
            return ""