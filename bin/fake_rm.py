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


for thing_to_rm in args:
    if os.path.isfile(thing_to_rm):
        life = check_for_life(thing_to_rm)
        if life:
            if friendly(thing_to_rm):
                msg = f"rm: cannot hurt ally {thing_to_rm}"
                print(msg)
                write_sys_msg(msg, 25)
                continue
            respawn = get_respawn(thing_to_rm)
            #print(f"found life: {thing_to_rm}")
            for i in range(0,int(life/player_power)):
                life = life - player_power
                write_life_file(thing_to_rm, life, respawn, under_attack=True)
                time.sleep(player_attack_wait)
            os.remove(thing_to_rm)
        else:
            msg = f"Not a game file: {thing_to_rm}"
            print(msg)
            write_sys_msg(msg, 25)
    else:
        if os.path.isdir(thing_to_rm):
            msg = f"rm: cannot remove '{thing_to_rm}': Is a directory"
            print(msg)
            write_sys_msg(msg, 25)
        elif len(thing_to_rm) == 2 and thing_to_rm.startswith("-"):
            msg = f"rm: No unlocked option {thing_to_rm}"
            print(msg)
            write_sys_msg(msg, 25)
