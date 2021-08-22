#!/usr/bin/python3

#GPL3

#Fake RM command
import sys
import os
import time
from player_sys import *
setup_sys(resetup=False)


pwd = os.system("pwd")
args = sys.argv[1:]

player_power = get_player_laser()
player_attack_wait = .2



def check_for_life(path):
    with open(path) as fh:
        test_line = fh.readline()
        if test_line.startswith("life:"):
            return(int(test_line.split(":")[-1].strip()))
        else:
            return(False)

def rewrite_life_file(path, value):
    print(f"{path} Life:{value}")
    data_to_write = f"life:{value}\nunder_attack:True"
    with open(path, 'w') as fh:
        fh.write(data_to_write)


for thing_to_rm in args:
    if os.path.isfile(thing_to_rm):
        life = check_for_life(thing_to_rm)
        if life:
            print(f"found life: {thing_to_rm}")
            for i in range(0,int(life/player_power)):
                life = life - player_power
                rewrite_life_file(thing_to_rm, life)
                time.sleep(player_attack_wait)
            os.remove(thing_to_rm)
        else:
            print(f"Not a game file: {thing_to_rm}")
    else:
        if os.path.isdir(thing_to_rm):
            print(f"rm: cannot remove '{thing_to_rm}': Is a directory")
        elif len(thing_to_rm) == 2 and thing_to_rm.startswith("-"):
            print(f"rm: No unlocked option {thing_to_rm}")
