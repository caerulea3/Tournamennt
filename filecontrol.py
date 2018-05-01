import xlrd         #for read_excel
import xlsxwriter   #for write_excel
import pickle
from players import Person, SinglePlayer, DoublePlayer
from dirtyfunctions import google_conn, google_singleset, google_update, _countschool, _countseed, _countBye
from games import Match, Court
import sys
NODEHEIGHT=8
DEBUGHEIGHT=12

def read_excel(filepath):
    file=xlrd.open_workbook(filepath)
    meta=file.sheet_by_index(0)
    singles=file.sheet_by_index(1)
    doubles=file.sheet_by_index(2)
    schools=file.sheet_by_index(3)

    """Get Metadata"""
    # print(meta.col_values(1))
    useSingles=True if meta.col_values(1)[9]==1 else False
    useDoubles=True if meta.col_values(1)[10]==1 else False
    if meta.col_values(1)[10]==1:
        useDoubles=True

    """Get Schoool Data"""
    schoolDic={}
    cur=1
    while True:
        thisrow=schools.row_values(cur)
        cur+=1
        if thisrow[0]=="":
            break
        else:
            schoolDic[thisrow[1]]=thisrow[0]

    """Read Player Data"""
    if useSingles:
        cur=0
        while True:
            cur+=1
            thisrow=singles.row_values(cur)
            if thisrow[0]=="":
                break
            else:
                #make person
                thisperson=Person()
                thisperson.set(thisrow[1], thisrow[0], thisrow[3])
                #set singleplayer object
                thisPlayer=SinglePlayer(Person.infoDic[(thisrow[1], thisrow[3])],\
                seed=int(thisrow[2]))
        #set Topseed
        SinglePlayer.topseed=[]
        seedinfo=[singles.col_values(9)[4:11], singles.col_values(10)[4:11]]
        for i in range(len(seedinfo[0])):
            SinglePlayer.topseed.append((seedinfo[0][i], seedinfo[1][i]))

        #sort singleplayer.array by power
        SinglePlayer.reset()

    if useDoubles:
        cur=0
        while True:
            cur+=1
            thisrow=doubles.row_values(cur)
            if thisrow[0]=="":
                break
            else:
                #make person
                person1=Person()
                person1.set(thisrow[1], thisrow[0], thisrow[3])
                person2=Person()
                person2.set(thisrow[1], thisrow[0], thisrow[4])
                #make player object
                thisPlayer=DoublePlayer(Person.infoDic[(thisrow[1], thisrow[3])],\
                Person.infoDic[(thisrow[1], thisrow[4])], seed=int(thisrow[2]))

        #set Topseed
        DoublePlayer.topseed=[]
        seedinfo=[doubles.col_values(9)[4:11], doubles.col_values(10)[4:11]]
        for i in range(len(seedinfo[0])):
            for i in range(len(seedinfo[0])):
                DoublePlayer.topseed.append((seedinfo[0][i], seedinfo[1][i]))

        #sort doubleplayer.array
        DoublePlayer.reset()

def write_excel(filepath, singleRoot, doubleRoot, DEBUG=False, width=10):
    workbook = xlsxwriter.Workbook(filepath)
    singles = workbook.add_worksheet("Singles")
    doubles = workbook.add_worksheet("Doubles")

    """Singles"""
    if singleRoot is not None:
        count=1
        nodeHeight=NODEHEIGHT if not DEBUG else DEBUGHEIGHT
        ask=input("DEBUG?:")
        singleGames=singleRoot.undermatches()
        for x in singleGames:
            thingsToWrite=\
            [
            "Match #" + str(x.matchNum),
            "{0} vs. {1}".format(x.player[0].name(), x.player[1].name()),
            "{0} vs. {1}".format(x.player[0].schoolname(), x.player[1].schoolname()),
            "Level : {0}".format(str(2**x.depth()*2)+"강" if x.depth()!=0 else "결승"),
            "score : {0} : {1}".format(x.score[0], x.score[1]),
            "power : {0} : {1}".format(x.player[0].power, x.player[1].power),
            "UpperMatch" + str(x.upperMatch.matchNum) if x.upperMatch is not None else "-",
            "UnderMatch {0}, {1}".format(x.underMatch[0].matchNum if len(x.underMatch)!=0 else "-",\
                x.underMatch[1].matchNum if len(x.underMatch)!=0 else "-")
        # For Debug
            # "Seedcnt   " + _countseed(x),
            # "Schoolcnt : "+ _countschool(x),
            # "Byes : " + str(_countBye(x))
            ]

            startHeight=(nodeHeight * x.depth()) + 1
            for i in range(len(thingsToWrite)):
        # For Debug
                # if x.depth()>4 and i>len(thingsToWrite)-4:
                #     continue
                singles.write(startHeight+i, count, thingsToWrite[i])
                singles.set_column(1, count, width)

            #debug_0327
            if ask=='DEBUG':
                singles.write(startHeight+4, count, x.player[0].power)
                singles.write(startHeight+4, count+1, x.player[1].power)

            count+=1

    """Doubles"""
    if doubleRoot is not None:
        count=1
        nodeHeight=NODEHEIGHT if not DEBUG else DEBUGHEIGHT
        singleGames=doubleRoot.undermatches()
        for x in singleGames:
            thingsToWrite=\
            [
            "Match #" + str(x.matchNum),
            "{0} vs. {1}".format(x.player[0].name(), x.player[1].name()),
            "{0} vs. {1}".format(x.player[0].schoolname(), x.player[1].schoolname()),
            "Level : {0}".format(str(2**x.depth()*2)+"강" if x.depth()!=0 else "결승"),
            "score : {0} : {1}".format(x.score[0], x.score[1]),
            "power : {0} : {1}".format(x.player[0].power, x.player[1].power),
            "UpperMatch" + str(x.upperMatch.matchNum) if x.upperMatch is not None else "-",
            "UnderMatch" + str(x.underMatch[0].matchNum) if len(x.underMatch)!=0 else "-"+ ", "+ str(x.underMatch[1].matchNum) if len(x.underMatch)!=0 else "-",
            # "Seedcnt   " + ''.join(''.join((str(k), " : ",  str(v), "   ")) for k,v in seedinfo.items()),
            # "Schoolcnt   " + ''.join(''.join((str(k), " : ",  str(v), "   ")) for k,v in schoolinfo.items()),
            # "Byes : " + str(_countBye(x))
            ]

            startHeight=(nodeHeight * x.depth()) + 1
            for i in range(len(thingsToWrite)):
                doubles.write(startHeight+i, count, thingsToWrite[i])
                doubles.set_column(1, count, width)
            count+=1

    workbook.close()

def write_pickle(filepath, root=None):
    metadata={}
    metadata['infoDic']=Person.infoDic
    metadata['schoolDic']=Person.schoolDic
    metadata['SingleArray']=SinglePlayer.array
    metadata['SingleSeed']=SinglePlayer.topseed
    metadata['DoubleArray']=DoublePlayer.array
    metadata['DoubleSeed']=DoublePlayer.topseed
    metadata['Matches']=Match.array

    if root is not None:
        metadata["SingleRoot"] = root.SingleRoot
        metadata["DoubleRoot"] = root.DoubleRoot
        metadata["singlematchdic"] = root.singlematchdic
        metadata["doublematchdic"] = root.doublematchdic
        metadata["Courts"] = root.Courts

    f=open(filepath, "wb")
    pickle.dump(metadata, f)
    f.close()

def read_pickle(filepath, root=None):
    fo=open(filepath, "rb")
    metadata=pickle.load(fo)
    fo.close()

    Person.infoDic=metadata['infoDic']
    Person.schoolDic=metadata['schoolDic']
    SinglePlayer.array=metadata['SingleArray']
    SinglePlayer.topseed=metadata['SingleSeed']
    DoublePlayer.array=metadata['DoubleArray']
    DoublePlayer.topseed=metadata['DoubleSeed']
    Match.array=metadata['Matches']

    if root is not None:
        try:
            root.SingleRoot = metadata["SingleRoot"]
            root.DoubleRoot = metadata["DoubleRoot"]
            root.singlematchdic = metadata["singlematchdic"]
            root.doublematchdic = metadata["doublematchdic"]
            root.Courts=metadata['Courts']
        except KeyError:
            pass

def google_writeall(spreadSheetId, rootMatch, sheetname, root=None):
    googleconn=google_conn(spreadSheetId)

    nodeHeight=NODEHEIGHT
    count=1
    games=rootMatch.undermatches()
    for i in range(len(games)):
        x=games[i]
        google_singleset(googleconn, i, x, sheetname=sheetname, waiting_info="" if root is None else root.waiting_information(x))

    google_update(googleconn)
