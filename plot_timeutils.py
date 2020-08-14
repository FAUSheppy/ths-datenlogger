#!/usr/bin/python3
from config_parse import CFG
from datetime import datetime, timedelta

def between_dates(t,date1,date2):
        if (date1 == None or date1 <= t) and (date2 == None or date2 > t):
            return True
        else:
            return False

def time_from_dbf(l, timeformat):
        timeformat=None #dont need that here
        offset_d = datetime(1970,1,1)-datetime(1900,1,1)
        shit_epoch = l*24*60*60 #days to seconds
        unix_epoch = datetime.fromtimestamp(shit_epoch)-offset_d
        return (unix_epoch-timedelta(days=2)+timedelta(hours=CFG("add_hours_to_input"))).replace(microsecond=0)

def time_from_csv(l, timeformat):
        return datetime.strptime(l, timeformat)

def unix(dt):
    return dt.timestamp()

def round_time_to_step(start,step):
        start  += step / 2
        discard = timedelta(days=0)
        hround  = int(step.seconds/3600)
        mround  = int(step.seconds/60)
        if step >= timedelta(days=1):
                discard = timedelta(days=start.day % step.days,hours=start.hour,minutes=start.minute,seconds=start.second)        
        elif step >= timedelta(hours=1):
                if hround != 0:
                    discard = timedelta(hours=start.hour % hround,minutes=start.minute,seconds=start.second) 
        elif step >= timedelta(minutes=1):
                if mround != 0:
                    discard = timedelta(minutes=start.minute % mround,seconds=start.second)
        elif step >= timedelta(seconds=1):
                    discard = timedelta(seconds=start.second % step.seconds)
        else:
                raise ValueError("Rounding time failed, this actually should be impossible. wtf. ("+str(start)+","+str(step)+","+str(discard)+")")
        start -= discard
        return start
