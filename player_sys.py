#!/usr/bin/python3
import os
import pwd
import shutil

user = pwd.getpwuid( os.getuid() )[ 0 ]
if user != "poodillion":
    chroot_path = os.path.expanduser("~/.poodillion_root")
else:
    chroot_path = ""


def change_sys_file(file_name, amount):
    global sys_path
    unlock_door(sys_path)
    life = 0
    #print(life)
    with open(file_name, 'r') as fh:
        life = int(fh.readline().strip())
    with open(file_name, 'w+') as fh:
        life = life + amount
        #print(life)
        fh.write(f"{life}")
    lock_away(sys_path)
    return(life)

def change_power(amount):
    global player_power_file
    change_sys_file(player_power_file, amount)

def change_life(amount):
    global player_life_file
    change_sys_file(player_life_file, amount)


def write_life_file(path, value, respawn, is_friend=False, under_attack=False):
    #print(f"{path} Life:{value}")
    data_to_write = f"life:{value}\nunder_attack:{under_attack}\nis_friend:{is_friend}\nrespawn:{respawn}"
    with open(path, 'w') as fh:
        fh.write(data_to_write)

def check_for_life(path):
    with open(path) as fh:
        test_line = fh.readline()
        if test_line.startswith("life:"):
            return(int(test_line.split(":")[-1].strip()))
        else:
            return(False)


def friendly(path):
    with open(path) as fh:
        test_lines = fh.readlines()
        for line in test_lines:
            if line.startswith("is_friend:"):
                true_or_false = line.split(":")[-1].strip()
                true_or_false = true_or_false == "True"
                return(true_or_false)
    #Should not happen
    return(False)

def decrement_sys_msgs(by=1):
    global sys_msg_file
    unlock_door(sys_path)
    rewrite = ""
    with open(sys_msg_file) as fh:
        for line in fh.readlines():
            if line == "" or line.startswith("#"):
                continue
            msg, ticks = split_sys_msg(line)
            ticks = str(int(ticks) - by)
            if int(ticks) >= 1:
                rewrite_line = f"{msg}:{ticks}"
                rewrite = rewrite + rewrite_line

    with open(sys_msg_file, 'w') as fh:
        fh.write(rewrite.strip())
        #print(rewrite)
    lock_away(sys_path)

def write_sys_msg(msg, ticks):
    global sys_msg_file
    unlock_door(sys_path)
    with open(sys_msg_file, 'w+') as fh:
        for line in msg.split('\n'):
            fh.write(f"{line}:{ticks}\n")
    lock_away(sys_path)

def get_sys_msg_ticks(target_msg):
    global sys_msg_file
    unlock_door(sys_path)
    with open(sys_msg_file) as fh:
        for line in fh.readlines():
            if line == "" or line.startswith("#"):
                continue
            msg, ticks = split_sys_msg(line)
            if msg == target_msg:
                lock_away(sys_path)
                return(int(ticks.strip()))
    lock_away(sys_path)

def split_sys_msg(line):
    ticks = line.split(":")[-1]
    msg = line[:-len(ticks)-1]
    return(msg, ticks)

def get_sys_msg():
    global sys_msg_file
    unlock_door(sys_path)
    return_data = {}
    with open(sys_msg_file) as fh:
        for line in fh.readlines():
            if line == "" or line.startswith("#"):
                continue
            print(line)
            print(line)
            msg, ticks = split_sys_msg(line)
            return_data[msg] = ticks
    lock_away(sys_path)
    return(return_data)

def get_respawn(path):
    with open(path) as fh:
        test_lines = fh.readlines()
        for line in test_lines:
            if line.startswith("respawn:"):
                cut_line = ":".join(line.split(":")[1:])
                return(cut_line)

def get_sys_file(file_name):
    unlock_door(sys_path)
    life = 0
    with open(file_name) as fh:
        life = int(fh.readline().strip())
    lock_away(sys_path)
    return(life)

def get_player_power():
    global player_power_file
    return(get_sys_file(player_power_file))

def get_player_laser():
    global player_laser_file
    return(get_sys_file(player_laser_file))

#returns list of what the player can spawn
def get_player_can_spawn():
    global player_can_spawn
    unlock_door(sys_path)
    return_data = []
    with open(player_can_spawn) as fh:
        for line in fh.readlines():
            if line == "" or line.startswith("#"):
                continue
            return_data.append(line.strip())
    lock_away(sys_path)
    return(return_data)

def get_player_life():
    global player_life_file
    return(get_sys_file(player_life_file))

def get_player_speed():
    global player_speed_file
    return(get_sys_file(player_speed_file))

def setup_sys(resetup=True):
    global chroot_path
    global sys_path
    global player_life_file
    global player_speed_file
    global player_power_file
    global player_laser_file
    global player_can_spawn
    global sys_msg_file
    
    #setup sys_path(s)
    sys_path = f"{chroot_path}/home/poodillion/.sys"
    player_life_file = f"{sys_path}/player/life"
    player_speed_file = f"{sys_path}/player/speed"
    player_power_file = f"{sys_path}/player/power"
    player_laser_file = f"{sys_path}/player/laser"
    player_can_spawn = f"{sys_path}/player/spawnable"
    sys_msg_file = f"{sys_path}/player/msg"
    
    if resetup:
        #clean up old sys_path
        if os.path.isdir(sys_path):
            unlock_door(sys_path)
            shutil.rmtree(sys_path)
    
        #build new 
        os.mkdir(sys_path)
        os.mkdir(f"{sys_path}/player")
        
        with open(player_life_file, 'w+') as life_fh:
            life_fh.write("100")
        with open(player_power_file, 'w+') as power_fh:
            power_fh.write("100")
        with open(player_can_spawn, 'w+') as spawn_strength_fh:
            #                                 img: name:    % action:damage:life:    % drops
            spawn_strength_fh.write("frog_guy.png:frog*: 100% walk 3:     1:   3: 100% na")
        with open(player_laser_file, 'w+') as laser_fh:
            laser_fh.write("1")
        with open(player_speed_file, 'w+') as speed_fh:
            speed_fh.write("5")
        with open(sys_msg_file, 'w+') as msg_fh:
            msg_fh.write("")
    
        lock_away(sys_path)

def unlock_door(dir_name):
    os.chmod(dir_name, 0o777)

def lock_away(dir_name):
    os.chmod(dir_name, 0o222)
