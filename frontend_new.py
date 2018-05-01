#!/usr/bin/python3
import sys
import tkinter
from   tkinter        import filedialog

import plot_main
import input_backend
import frontend_utils as     futils
from   config_parse   import CFG
from   language       import LAN

l = LAN[CFG("language")]
tk = tkinter.Tk()
tk.withdraw()

def main_repl(datapoints,path,date1=None,date2=None,done1=False,done2=False):
    ### READ IN DATES ###
    futils.info_list(datapoints)
    while not done1:
        date1,done1,raw1 = futils.input_date_repl(datapoints,startdate=True)
    while not done2:
        date2,done2,raw2 = futils.input_date_repl(datapoints,startdate=False)

    # save history here
    futils.save_history(raw1)
    futils.save_history(raw2)

    ### CHECK DATES ###
    done1,done2 = futils.check_dates(path,date1,date2)
    if not done1 or not done2:
        main_repl(datapoints,path,date1,date2,done1,done2)
    else:
        plot_main.plot(datapoints,path,date1,date2)

def selection_repl(path):
    if path != None:
        datapoints = input_backend.read_in_file(path)
        if CFG("debug_no_interactive"):
            plot_main.plot(datapoints,path)
            return None
        main_repl(datapoints,path)
    if CFG("always_restart"):
        print("----------------------------------------")
        tmp=input(  " -> Type 'n' or 'new' <ENTER> to restart with another file\n -> Type 'r' or 'restart'<ENTER> to use the current file again\n -> Or press just <ENTER> to exit: ") 
        if tmp == None or tmp == "":
            return None
        elif tmp in ["r","restart"]:
            return path
        elif tmp in ["n","new"]:
            return futils.open_file()
        elif tmp.startswith('c'):
            config_options(ret)
        else:
            sys.exit(0)

def main():
    ### PREVENT MULTICORE SUPPORT ###
    if CFG("enable_multicore_support"):
        raise NotImplementedError("multiprocessing not fully implemented")
    
    ### PROMT TO OPEN FILE ###
    FILE_READY = False
    path = None
    while True:
        if not FILE_READY:
            path = futils.open_file()

        path = selection_repl(path)

        if path == None:
            break
        else:
            FILE_READY = True
