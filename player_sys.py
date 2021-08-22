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
    print(life)
    with open(file_name, 'r') as fh:
        life = int(fh.readline().strip())
    with open(file_name, 'w+') as fh:
        life = life + amount
        print(life)
        fh.write(f"{life}")
    lock_away(sys_path)
    return(life)

def change_power(amount):
    global player_power_file
    change_sys_file(player_power_file, amount)

def change_life(amount):
    global player_life_file
    change_sys_file(player_life_file, amount)

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
    
    #setup sys_path(s)
    sys_path = f"{chroot_path}/home/poodillion/.sys"
    player_life_file = f"{sys_path}/player/life"
    player_speed_file = f"{sys_path}/player/speed"
    player_power_file = f"{sys_path}/player/power"
    player_laser_file = f"{sys_path}/player/laser"
    
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
        with open(player_laser_file, 'w+') as power_fh:
            power_fh.write("1")
        with open(player_speed_file, 'w+') as speed_fh:
            speed_fh.write("5")
    
        lock_away(sys_path)

def unlock_door(dir_name):
    os.chmod(dir_name, 0o777)

def lock_away(dir_name):
    os.chmod(dir_name, 0o222)
