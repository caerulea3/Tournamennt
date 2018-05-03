import sys
import os
from players import Person, SinglePlayer, DoublePlayer
from filecontrol import read_excel, write_excel, write_pickle
from games import Match
from root import Root

warnings=True
trial=0
filename=""
path=""

"""open file"""
playersFileName=input("Enter Filename of players : ")
while not os.path.exists("./"+playersFileName):
    if playersFileName=="?":
        print(os.system("dir"))
    else:
        print("Invalid Filename")
    playersFileName=input("Enter Filename of players : ")
read_excel("./"+playersFileName)

rt=Root()

while warnings==True:
    trial+=1
    if trial>1000:
        print("Fail To Make Tournament!!")
        break
    print("Try {0:>2d} : ".format(trial), end="")
    del(rt)
    rt=Root()
    rt.maketour()
    rt.start()
    warnings_single, warnings_double=rt.haveproblem(trial)
    warnings=warnings_single or warnings_double


if trial<1001:
    print("Success!")
    rt.changecourtnum(3)

    """Write To Files"""
    if filename=="":
        folder=input("Enter Folder Name(Present Folder if enters none) :")
        if folder!="" and not os.path.exists("./"+folder):
            os.makedirs("./"+folder)
            print("MakeDir Success")
        path="./" if folder=="" else "./"+folder+"/"
        filename=input("Enter FileName : ")
        filename=path + filename
    rt.save(filename)
