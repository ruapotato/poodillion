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
cost = 25


for thing_to_touch in args:
    if not os.path.isfile(thing_to_touch):
        #check if this is a valid command:
        for spawn_line in get_player_can_spawn():
            raw_spawn_data = spawn_line.split(":")
            #Example data for spawn_line
            #1  :100:100:active:frog_guy.png:frog*: 100% walk 3:     1:   3: 100% na
            #get valid_spawn_name_start
            valid_spawn_name_start = raw_spawn_data[5].strip("*")
            
            #Update file name
            raw_spawn_data[5] = thing_to_touch.split("/")[-1]
            start_life = int(raw_spawn_data[8].strip())

            #Example valid_spawn_name_start data
            #frog
            spawn_line = ":".join(raw_spawn_data)

            if "/" in thing_to_touch:
                short_file_name = thing_to_touch.split("/")[-1]
            else:
                short_file_name = thing_to_touch
            if short_file_name.startswith(valid_spawn_name_start):
                print(f"Could Do that... {short_file_name} startswith {valid_spawn_name_start}")
                #check if the player has the power to spawn
                if get_player_power() > cost:
                    change_power(cost * -1)
                    write_life_file(thing_to_touch, start_life, spawn_line)
                    msg = f"Spawned: {short_file_name} (HP:{start_life})"
                else:
                    msg = "Need more power to spawn!"
                write_sys_msg(msg, 25)
                print(msg)
            else:
                msg = f"touch: Cannot create a/an {short_file_name} just yet."
                print(msg)
                write_sys_msg(msg, 25)

        #print(f"File found: {thing_to_touch}")
    #This is a file
    else:
        if check_for_life(thing_to_touch):
            if not friendly(thing_to_touch):
                life = check_for_life(thing_to_touch)
                change_life(-10)
                msg = f"touch: '{thing_to_touch}' is a bad -10 HP"
                write_sys_msg(msg, 25)
                print(msg)
                
