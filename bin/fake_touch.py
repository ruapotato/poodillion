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



for thing_to_touch in args:
    if not os.path.isfile(thing_to_touch):
        #check if this is a valid command:
        for spawn_line in get_player_can_spawn():
            #print("Debug")
            raw_spawn_data = spawn_line.split(":")
            #Example data for spawn_line
            #frog_guy.png:frog*: 100% walk 3:     1:   3: 100% na
            #Update file name
            raw_spawn_data[1] = thing_to_touch.split("/")[-1]
            start_life = int(raw_spawn_data[4].strip())
            valid_spawn_name_start = raw_spawn_data[1].strip("*")
            #Example valid_spawn_name_start data
            #frog
            spawn_line = ":".join(raw_spawn_data)
            spawn_line = "active:" + spawn_line

            if "/" in thing_to_touch:
                short_file_name = thing_to_touch.split("/")[-1]
            else:
                short_file_name = thing_to_touch
            if short_file_name.startswith(valid_spawn_name_start):
                print(f"Could Do that... {thing_to_touch} with spawn {spawn_line}")
                write_life_file(thing_to_touch, start_life, spawn_line, is_friend=True)

        #print(f"File found: {thing_to_touch}")
    #This is a file
    else:
        if check_for_life(thing_to_touch):
            if not friendly(thing_to_touch):
                life = check_for_life(thing_to_touch)
                change_life(-1)
                print(f"{thing_to_touch}: This is a badguy -1 HP")
                
