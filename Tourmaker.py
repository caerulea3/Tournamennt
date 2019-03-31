import sys
import os
from players import Person, SinglePlayer, DoublePlayer
from filecontrol import read_excel, write_excel, write_pickle
from games import Match
from root import Root

MAXTRY=5000

warnings=True
trial=0
singles_err=0
doubles_err=0
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


"""Make Singles"""
while warnings==True:
    trial+=1
    if trial>MAXTRY:
        print("Fail To Make Tournament at Singles!!")
        break
    print("Try {0:>2d} : ".format(trial), end="")
    rt.maketour_single()
    rt._start_single()
    warnings_single = rt.haveproblem_single (singles_err)
    singles_err+=1 if warnings_single else 0
    warnings=warnings_single

if warnings == False:
    input("Singles Success!")
else:
    input("failed To make Singles Tournament")


warnings = True
trial = 0
"""Make Doubles"""
while warnings==True:
    trial+=1
    if trial>MAXTRY:
        print("Fail To Make Tournament at Doubles!!")
        break
    print("Try {0:>2d} : ".format(trial), end="")
    rt.maketour_double()
    rt._start_double()
    warnings_double = rt.haveproblem_double (doubles_err)
    doubles_err+=1 if warnings_double else 0
    warnings=warnings_double


print("Success!")
rt.changecourtnum(3)
print(rt.SingleRoot, rt.DoubleRoot)
rt._start_single()

"""Write To Files"""

if filename=="":
    folder=input("Enter Folder Name(Present Folder if enters none) :")
    if folder!="" and not os.path.exists("./"+folder):
        os.makedirs("./"+folder)
        print("MakeDir Success")
    path="./" if folder=="" else "./"+folder+"/"
    filename=input("Enter FileName : ")
    filename=path + filename
rt.save(filename, option='both')
