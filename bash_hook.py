#!/usr/bin/python3
import time
import os
import subprocess
import threading
import copy

import tempfile
import mmap
import pyte
import pty
#sudo apt install python3-pyte


#terminal_size = vt_size()
terminal_size = [80,24]
script_path = os.path.dirname(os.path.realpath(__file__))

needs_started = []
next_tty_index = 0
process_list = []
masters = []
slaves = []
slave_fd, tmpfile = tempfile.mkstemp()
os.write(slave_fd, b'\x00' * mmap.PAGESIZE)
os.lseek(slave_fd, 0, os.SEEK_SET)

output_data = []
history_buffer = []
rendered_data = []
streams = []
bash_threads = []
screens = []
dirty_screens = []
tty_positions = {}
tty_sizes = {}
last_rendered_mouse = [0,0]
mouse_position = [0,0]
clicks = []
space_to_clear = []
target_tty = 0
RUNNING = []

working_dir = script_path
composit_running = f"{working_dir}/running"
with open(composit_running, 'w') as fh:
    pass

#Only used by Draw inside the draw loop/thread

def draw():
    global mouse_position
    global dirty_screens
    global output_data
    global tty_positions
    global tty_sizes
    global last_rendered_mouse
    global clicks
    global space_to_clear
    #really bad, but fine for now
    #if screen_dirty:
    #    vt_clear()
    #    screen_dirty = False
    #vt_move(int(mouse_position[1]) - 1, int(mouse_position[0]) - 1)
    #vt_write("+" + str(mouse_position))
    while True:
        time.sleep(0.2)
        #Draw ttys
        for dirty_tty in dirty_screens:
            dirty_screens.remove(dirty_tty)
            debug(f"dirty_tty {dirty_tty}")
            if output_data[dirty_tty] != "":
                debug(f"drawing screen: {dirty_tty}")
                #This data might change, copy it first
                try:
                    raw_data = copy.deepcopy(output_data[dirty_tty])
                except RuntimeError:
                    debug("This is not very thread safe... Hmmm")
                    #setup callback
                    time.sleep(0.2)
                    dirty_screens.append(dirty_tty)
                    draw()
                for line_index in raw_data:
                    line = raw_data[line_index]
                    for col_index in line:
                        char_obj = line[col_index]
                        char_pos = [line_index, col_index]
                        #might be removed if this tty was just closed
                        try:
                            offset = tty_positions[dirty_tty]
                        except KeyError:
                            #debug(f"offset not available for index {dirty_tty}")
                            continue
                        display_pos = [char_pos[0]+offset[0], char_pos[1]+offset[1]]
                        #write_char(char_obj, display_pos)                        
                        debug(f"Yo: {char_obj.data} {display_pos}")
        
        



#Setup term

def get_slaves():
    raw = get_slaves_raw()
    debug(raw)
    return_data = []
    for less_raw in raw.strip('/').split('/'):
        return_data.append("/dev/pts/" + str(less_raw))
    return return_data


def get_slaves_raw():
    os.lseek(slave_fd, 0, os.SEEK_SET)
    buf = mmap.mmap(slave_fd, mmap.PAGESIZE, mmap.MAP_SHARED, mmap.PROT_READ)
    msg = str(buf.readline())
    msg = ':'.join(msg.split(':')[:-1]).split("'")[-1]
    return(msg)


def add_slave(pid):
    global slaves
    offset = get_slaves_raw()
    offset = len(offset)
    os.lseek(slave_fd, offset, os.SEEK_SET)
    buf = mmap.mmap(slave_fd, mmap.PAGESIZE, mmap.MAP_SHARED, mmap.PROT_WRITE)
    TTY = subprocess.check_output(['ps', 'hotty', str(pid)]).strip().decode()
    TTY = TTY.split("pts")[-1] + ":" # cut off pts and add a : for spacing
    #slaves.append(TTY)
    for index in range(offset, offset + len(TTY)):
        buf[index] = ord(TTY[index - offset])

def read_running(flat=False):
    global composit_running
    
    if flat:
        nice_looking_list_of_stuff_running = {}
    else:
        nice_looking_list_of_stuff_running = []
    with open(composit_running) as tmp_file_handle:
        for line in tmp_file_handle.readlines():
            if line != "":
                line = line.strip()
                index,cmd = line.split(":")
                if flat:
                    nice_looking_list_of_stuff_running[int(index)] = cmd
                else:
                    nice_looking_list_of_stuff_running.append({index:cmd})
    return(nice_looking_list_of_stuff_running)
    

def add_cli(index,cmd):
    global composit_running
    
    if index not in read_running():
        with open(composit_running, 'a') as tmp_file_handle:
            index_and_whatnot = f"{index}:{cmd}\n"
            tmp_file_handle.write(index_and_whatnot)
    else:
        debug(f"Error adding duplicate index {index}:{cmd}")


def remove_cli(index):
    stuff_running = read_running()    
    #TODO
    #clear composit_running
    open(composit_running, 'w').close()
    
    #loop stuff_running and add it back
    for still_open in stuff_running:
        open_index = list(still_open.keys())[0]
        if int(open_index) != int(index):
            debug(f"still running {still_open}")
            cmd = still_open[open_index]
            add_cli(open_index, cmd)
    
        

def bash_screen_ref(cmd, local_screen):
    global streams
    global screens
    global output_data
    global dirty_screens
    global composit_running
    global RUNNING
    
    #store current output screen
    debug("OPENING SCREEN WITH DISPLAY: " + str(local_screen))
    
    #store what we just ran
    add_cli(local_screen, cmd)
    composit_running
    output_index = 0
    for output_bit in bash_attach(cmd, local_screen):

        if local_screen not in RUNNING:
            remove_cli(local_screen)
            debug("end bash")
            #exit()
        #debug("output_bit: " + str(output_bit))

        #update main terminal (Debug only)
        #VT = output_bit.decode('utf-8', errors='ignore')
        #vt_write(VT)
        #feed vt100 into pyte
        streams[local_screen].feed(output_bit)
        
        #read screen data
        tmp_data = screens[local_screen].buffer

        if tmp_data != "":
            debug(f"Stuff from {local_screen}")
            output_data[local_screen] = tmp_data
            dirty_screens.append(local_screen)
        
        

def open_tty():
    global output_data #   only used to init new bash session
    global history_buffer# needs to be the size of the open screens
    global rendered_data #init as well...
    global masters #bash sessions input
    global streams
    global force_while_loop #most likely not needed
    global bash_threads
    global next_tty_index #used to ctrl which screen is active
    global screens #pyte screens
    global out_put_screen #tty index of screen we are opening
    global needs_started
    global tty_positions
    global tty_positions
    global RUNNING
    global terminal_size

    new_command = {}
    new_command['position'] = [0, 0]
    new_command['size']     = terminal_size
    new_command['cmd']     = "/bin/bash"
    needs_started = [new_command]

    for needed_tty in needs_started:
        #needed_tty should look like: 
        ##{'position': [0,0], 'size': [90,66], 'cmd': '/bin/bash'}
        term_size = needed_tty['size']
        cmd = needed_tty['cmd']
        #run bash while piping it's ouput/err/in to new pts
        
        #setup new screen index
        out_put_screen = next_tty_index
        next_tty_index = next_tty_index + 1
        
        RUNNING.append(out_put_screen)
        
        
        tty_positions[out_put_screen] = needed_tty['position']
        tty_sizes[out_put_screen] = needed_tty['size']
        
        #init new bash session
        debug("NEW bash session")
        output_data.append([])
        rendered_data.append([])
        history_buffer.append([])

        #kick off shell thread (the middle bash part)
        #master_new, slave_new = pty.openpty()
        #masters.append(master_new)
        #masters.append(slave_new)
        #open new virt term
        #new_screen = pyte.Screen(term_size[1], term_size[0] - 2)
        debug("Opening tty with size: " + str(term_size))
        new_screen = pyte.screens.HistoryScreen(term_size[0],term_size[1],history=1000)
        #debug("80 : " + str(term_size[1]))
        screens.append(new_screen)
        streams.append(pyte.ByteStream(screens[-1]))

        streams[-1].escape["N"] = "next_page"
        streams[-1].escape["P"] = "prev_page"



        #win_size = struct.pack("HHHH", term_size[0] - 2, term_size[1], 0, 0)
        #fcntl.ioctl(masters[-1], termios.TIOCSWINSZ, win_size)

        #debug(dir(streams.copy), Level=3)
        #wait for tty to be ready
        #try to a connect over socket
        bash_threads.append(threading.Thread(target=bash_screen_ref, args=(cmd,out_put_screen)))
        bash_threads[-1].daemon = True
        bash_threads[-1].start()
        #vt_clear()
        #vt_move(0,0)
        
        #resize tty:
        #screens[-1].resize(lines=term_size[0], columns=term_size[1])
        #screens[-1].set_margins(term_size[0], term_size[1])
        #vt_send(resize_as_vt(term_size[0], term_size[1]), out_put_screen)
        #vt_send(f"\x1b[8;{term_size[0]};{term_size[1]}t", out_put_screen)
        bash_run('echo "$(tput cols)x$(tput lines)";tty\n', out_put_screen)
        #bash_run('./top_bar.py\n', out_put_screen)
        #c = 'KEY_RESIZE' #force resize
        #force_while_loop = True
        #wait for term to move
        time.sleep(0.15)
    #everything should be running now
    #TODO remove these as we process them, in case something else is added while we are processing stuff. 
    needs_started = []

def resize_as_vt(row,col):
    return(f'\033[8;{row};{col}t')

def bash_run(cmd, index, redo=True):
    global masters
    if not cmd.endswith("\n"):
        cmd = cmd + "\n" 
    try: #If tty are opened fast, this can crash
        os.write(masters[index], cmd.encode())
    except Exception:
        time.sleep(.2) #wait for tty
        if redo:
            bash_run(cmd, index, redo=False)

def vt_send(vt_data, index, redo=True):
    global slaves
    try: #If tty are opened fast, this can crash
        os.write(slaves[index], vt_data.encode())
    except Exception:
        time.sleep(.2) #wait for tty
        if redo:
            vt_send(vt_data, index, redo=False)


def bash_attach(cmd, screen_id):
    global needs_started
    global process_list
    global masters

    #init process list if needed
    if 'process_list' not in list(globals().keys()):
        process_list = []


    #Thanks! https://stackoverflow.com/a/52157066/5282272
    # fork this script such that a child process writes to a pty that is
    # controlled or "spied on" by the parent process

    (child_pid, new_master_handle) = pty.fork()
    masters.append(new_master_handle)
    # A new child process has been spawned and is continuing from here.
    # The original parent process is also continuing from here.
    # They have "forked".

    if child_pid == 0:
        debug("This is the child process fork, pid %s" % os.getpid())
        debug("ADDING")
        add_slave(os.getpid())
        debug(f"shared map: {get_slaves_raw()}")
        debug(get_slaves())
        process_list.append(subprocess.run(cmd))

    else:
        debug("This is the parent process fork, pid %s" % os.getpid())

        while True:
            try:
                data = os.read(masters[screen_id], 1026)
            except Exception:
                #time.sleep(.2)
                continue
            yield data

def debug(error_string):
    global DEBUG_LOG
    DEBUG_LOG = f"{script_path}/debug"
    
    with open(DEBUG_LOG, 'a+') as the_log:
        the_log.write(str(error_string) + "\n")
        #print(error_string, file=sys.stderr)


#Send keys to the runnning tty
def composit_process(key):
    global mouse_position
    global target_tty
    global clicks
    global masters


    #handle keyboard events

    debug(f"Sending {key} to TTY index {target_tty}")
    if type(key) == bytes:
        os.write(masters[target_tty], key)
        print("Info")
    elif type(key) == str:
        #print(f"writing {key}")
        os.write(masters[target_tty], key.encode())
        #debug reset mouse
        #vt_move(0,0)
    

#thanks https://medium.com/@aliasav/how-follow-a-file-in-python-tail-f-in-python-bca026a901cf
def follow(thefile):
    '''generator function that yields new lines in a file
    '''
    # seek the end of the file
    thefile.seek(0, os.SEEK_END)
    
    # start infinite loop
    while True:
        # read last line of file
        line = thefile.readline()        # sleep if file hasn't been updated
        if not line:
            time.sleep(0.1)
            continue

        yield line


###################################################
################trigger/hook stuff#################
###################################################
#echo "0,0:90,44:/bin/bash" >> /dev/shm/compositerm/hook
#This will open a tty running at x=0, y=0 size 90x44 running bash

#echo "45,0:90,44:/bin/bash" >> /dev/shm/compositerm/hook

#echo "close:1" >> /dev/shm/compositerm/hook
#will close the tty at index 1

#echo "min:1" >> /dev/shm/compositerm/hook


####################################################
##################Display Thread####################
####################################################
draw_thread = threading.Thread(target=draw)
draw_thread.daemon = True
draw_thread.start()
####################################################
###############Librem 5/Touchscreen#################
####################################################
display_size = (720,1440)
def screen_to_pos(x,y):
    global size
    global terminal_size
    
    (term_rows, term_cols) = terminal_size
    term_rows = term_rows - 1
    term_cols = term_cols - 1
    x = int(x)
    y = int(y)
    if x == 0:
        new_x = x
    else:
        tmp = display_size[0]/x
        new_x = terminal_size[1]/tmp
    
    if y == 0:
        new_y = y
    else:
        tmp =  display_size[1]/y
        new_y = terminal_size[0]/tmp
    rounded_x = round(new_x)
    rounded_y = round(new_y)
    
    if rounded_x > term_cols:
        rounded_x = term_cols
    if rounded_y > term_rows:
        rounded_y = term_rows
        
    return(rounded_x, rounded_y)

#Example
"""
#Open new virt tty shell
open_tty()

#run cmds
composit_process('l')
composit_process('s')
#composit_process('\r')
composit_process('\n')
composit_process('c')
composit_process('d')
composit_process('\n')
composit_process('')

#Read screen and draw tty
raw_data = copy.deepcopy(output_data[target_tty])

cmd_text = ""
for line_index in raw_data:
    line = raw_data[line_index]
    cmd_text = cmd_text + "\n"
    for col_index in line:
        char_obj = line[col_index]
        char_pos = [line_index, col_index]
        cmd_text = cmd_text + char_obj.data
        print(char_obj)
print(f"New shell: {cmd_text}")
"""
