#!/usr/bin/python3
import sys
import tkinter
import plot_main
import config_parse
from config_parse   import CFG
from language       import LAN
from datetime       import datetime,timedelta
from plot_timeutils import between_dates

l = LAN[CFG("language")]
timeformat = "%d.%m.%y %H:%M:%S (%A)"
def parse_date_from_user_input(s,end_of_day=False,datapoints=None):
    today  = datetime.now()
    day    = 0
    month  = 0
    year   = 0
    hour   = 0
    minute = 0
    second = 0
    
    ## EMPTY ##
    if s == None or s == "":
        return (None,True)

    ## TIME ##
    if len(s.split(" ")) > 1:
        time = s.split(" ")[1]
        time_a = time.split(":")
        if len(time_a) > 0:
            hour = int(time_a[0])
        elif end_of_day > 0:
            hour = 23
        if len(time_a) > 1:
            minute = int(time_a[1])
        elif end_of_day:
            minute = 59
        if len(time_a) > 2:
            second = int(time_a[2])
        elif end_of_day:
            second = 59
    elif end_of_day:
        hour = 23
        minute = 59
        second = 59

    ## DATE ##
    tmp = s.split(" ")[0]

    ## allow more speperators ##
    sep = None
    for c in ["-",".",","]:
        if c in tmp:
            sep = c
            break
    if sep == None:
        sep = "-"
    tmp = tmp.strip(sep)

    if len(tmp.split(sep)) == 0:
        raise ValueError("Invalid Date '%s'"%str(s))
    else:
        date_a = tmp.split(sep)
        if len(date_a) > 0:
            day = int(date_a[0])
        if len(date_a) > 1:
            month = int(date_a[1])
        if len(date_a) > 2:
            year = int(date_a[2])
            if year < 1000:
                year+=2000
    
    # remember if an explizit date was give #
    NO_YEAR=False
    NO_MONTH=False

    if year == 0:
        NO_YEAR=True
        if today.month > month:
            year = today.year
        else:
            year = today.year-1
    if month == 0:
        NO_MONTH = True
        if today.day > day and today.year == year:
            month = today.month
        else:
            month = today.month-1
            if month < 1:
                month = 12-month 

    ret = datetime(year,month,day,hour,minute,second)
    tmp = list(datapoints.values())[0].times
    status = True
    if NO_MONTH:
        ret,status = correct_month(ret,min(tmp),max(tmp))
    if NO_YEAR and status:
        ret,status = correct_year(ret,min(tmp),max(tmp))
    return (ret,status)

def correct_year(date,data_start,data_end):
        if not CFG("enable_automatic_date_correction"):
            return (date,True)
        elif date == None:
            return (None,True)
        else:
            if between_dates(date,data_start,data_end):
                return (date,True)
            elif data_start.year != data_end.year:
                print("Datensätze aus mehr als einem Jahr gefunden, Jahr muss daher angegeben werden.")
                return (None,False)
            else:
                maxi = 12
                count = 0
                while count < maxi:
                    if between_dates(date.replace(year=date.year-count),data_start-timedelta(days=1),data_end+timedelta(days=1)):
                        return (date.replace(year=date.year-count),True)
                    count += 1

        return (date,True)

def correct_month(date,data_start,data_end):
        tmp_date = date.replace(year=data_end.year)
        if not CFG("enable_automatic_date_correction"):
            return (date,True)
        elif date == None:
            return (None,True)
        else:
            if between_dates(date,data_start,data_end):
                return (date,True)
            elif data_start.month != data_end.month:
                print("Datensätze aus mehr als einem Monat gefunden, Monat muss daher angegeben werden.")
                return (None,False)
            else:
                maxi = 12
                count = maxi
                while count >= 0:
                    if between_dates(date.replace(month=((date.month+count)%12)+1),data_start,data_end):
                        return (date.replace(month=date.month-count),True)
                    count -= 1

        return (date,True)

#TODO cfg histfile
#TODO cfg histlength
#TODO cfg histshow
#TODO cfg dontsaveonhistcall
history=None
def load_history(histfile="history.log"):
    tmp = []
    histlength = CFG("history_file_length")
    try:
        with open(histfile,"r") as f:
            for l in f:
                tmp_line = l.strip("\n")
                if not tmp_line in tmp:
                    tmp += [tmp_line]
        if len(tmp) > histlength:
            with open(histfile,"w") as f:
                for l in tmp[(len(tmp)-histlength-1):]:
                    f.write("{}\n".format(l.strip("\n")))
        tmp = tmp[(len(tmp)-histlength-1):]
    except IOError:
        print(">> Warnung: Eingabehistorie Datei nicht gefunden <<")
    return tmp

def save_history(string,histfile="history.log"):
    global history
    if not string:
        return
    # remove previous occourence if exists
    if string in history:
        history.remove(string)
    # add
    string = string.strip("\n")
    history += [string]
    # check max file length
    with open(histfile,"a") as f:
        f.write("{}\n".format(string.strip("\n")))

def load_from_history(index):
    global history
    index = int(index)
    return history[-index]

def recently_used():
    global history
    if not history:
        history = load_history()
    ret = ""
    if len(history) == 0:
        return "  Historie leider nicht verfügbar."
    count = 1
    count_max = CFG("history_show")
    count_max = len(history) if len(history) < count_max else count_max
    double_col =  CFG("history_double_col")
    col = 0
    hist_reversed = history[-count_max:].copy()
    hist_reversed.reverse()
    #print(hist_reversed)
    for e in hist_reversed:
        if col == 0 and double_col:
            ret += "  [{}] {}\t".format(count,e)
            col = 1
        else:
            ret += "  [{}] {}\n".format(count,e)
            col = 0
        count += 1
    return ret
    

def info_list(datapoints):
    if len(datapoints.keys()) > 0:
        print("Erster Datensatz:  "+min(datapoints[list(datapoints.keys())[0]].times).strftime(timeformat))
        print("Letzer Datensatz:  "+max(datapoints[list(datapoints.keys())[0]].times).strftime(timeformat))
        print("Anzahl Datensätze: "+str(len(datapoints[list(datapoints.keys())[0]].times)))
        print("Kürzlich genutze Data/Zeiten: (auswählen mit 1-5 <ENTER>):\n\n{}".format(recently_used()))
    else:
        print("Keine Datesätze gefunden!")
    print_sep_line(True)

end_date_available = None
def input_date_repl(datapoints,startdate=True):
    global end_date_available
    date = None

    while True:
        try:
            if startdate:
                ret = input(l["input_first_date"])
            else:
                ret = input(l["input_second_date"])
        except EOFError:
            return (date,True,None)
        except KeyboardInterrupt:
            sys.exit(2)
        # change ret to value if it was an history one
        try:
            if int(ret) in range(1,CFG("history_show")+1):
                try:
                    ret = load_from_history(ret)
                except Exception:
                    print("Konnte historische Eingabe nicht finden.")
                    continue
        except:
            pass
        if ret in ["h","help","hilfe"]:
            if startdate:
                print(l["input_first_date_help"])
            else:
                print(l["input_second_date_help"])
            continue
        elif ret == "list":
            info_list(datapoints)
            continue
        else:
            try:
                if startdate:
                    date,ok=parse_date_from_user_input(ret,datapoints=datapoints)
                else:
                    date,ok=parse_date_from_user_input(ret,True,datapoints)
                if not ok:
                    return (None,False,ret)
                else:
                    return (date,True,ret)
            except ValueError as e:
                print(l["cannot_parse_date"] + "( was: {} )\n".format(ret))
                return (None,False,ret)

def print_sep_line(ln=False):
    if not ln:
        print("-----------------------------------------------")
    else:
        print("-----------------------------------------------",end='')


def check_dates(path,date1,date2,options=""):
    print_sep_line()
    if options!="":
        print("Config options: %s"%options)
    print("Datei: %s"%path)
    if date1 == None and date2 == None:
        print("Info:  Keine Zeitbeschränkung gewählt. Alle vorhandenen Daten werden verwendet.")
        return (True,True)
    elif date1 == None:
        print("Alle Werte vor %s"%date2.strftime(timeformat))
    elif date2 == None:
        print("Alle Werte nach %s"%date1.strftime(timeformat))
    else:
        print("Start: %s\nEnde:  %s"%(date1.strftime(timeformat),date2.strftime(timeformat)))

    FIRST=True
    while(True):
        try:
            if FIRST:
                ret = input("Stimmt das so?\n -> <ENTER> für ja/weiter\n -> 's'<ENTER> für Startzeit ändern\n -> 'e'<ENTER> für Endzeit ändern\n -> 'b'<ENTER> für beides ändern\n -> 'exit'<ENTER> to exit\n---> ")
            else:
                ret = input("Versuchen sie es nochmal: ")
        except EOFError:
            ret = ""

        if ret == 's':
            return (False,True)
        elif ret == 'e':
            return (True,False)
        elif ret == 'b':
            return (False,False)
        elif ret.startswith('c '):
            tmp = config_options(ret)
            if tmp == "":
                pass
            else:
                options += "\n     "+tmp
                check_dates(path,date1,date2,options)
        elif ret == "":
            return (True,True)
        elif ret == "exit":
            sys.exit(0)
        FIRST=False

def open_file():
    front_end_source_path = CFG("default_source_path")
    if CFG("use_input_filename"):
        f = front_end_source_path + CFG("input_filename")
        return f

    path=None
    path=tkinter.filedialog.askopenfilename(filetypes=(("DBF/XLS Files",("*.DBF","*.dbf","*.xls","*.XLS","*.txt","*.TXT")),("All Files","*.*")))
    if path == None or path=="":
        print("Error: No file selected!")
        return None
    try:
        open(path,'r').close()
    except IOError:
        print("Error: Unable to open selected file, perhaps it does no longer exist or you have insufficient permissions to open it?")
        return None
    return path

def config_options(string):
        opt = ""
        arg = string.split(" ")
        if len(arg) == 2:
            for l in config_parse.get_keys(arg[1]):
                print(l)
        elif len(arg) == 3:
            if not config_parse.change_cfg(arg[1],arg[2]):
                print("Option %s does not exist."%str(arg[1]))
            else:
                opt += "set %s %s"%(arg[1],arg[2])
                print("set %s %s"%(arg[1],arg[2]))
        else:
            print("Ussage: c <configname> <value> / c <part_of_config_name> / c (= list all ), e to exit")
        return opt
