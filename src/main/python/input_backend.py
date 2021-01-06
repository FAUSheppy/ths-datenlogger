#!/usr/bin/python3
from config_parse import CFG
from datetime import datetime, timedelta
import requests
import os

from dbfread import DBF
import timeutils

line_colors = ['b', 'r', 'g', 'c', 'm', 'y']
tname       = CFG("temperatur_plot_name")
hname       = CFG("humidity_plot_name")
dname       = CFG("dewcels_plot_name")
color_id    = 0

class Data:
    def __init__(self,name,plot=False):
        global color_id,line_colors
        self.name = name
        self.color=line_colors[color_id%len(line_colors)]
        color_id += 1
        self.data = []
        self.times  = []
        self.plot = plot

    def getFirstTime(self):
        '''Get time of first timestamp'''
        return min(self.times)

    def getLastTime(self):
        '''Get time of last timestamp'''
        return max(self.times)

    def get_timeframe(self, callback, date1=None, date2=None):
        out_x = []
        out_y = []
        i = 0
        if(len(self.times) != len(self.data)):
            raise RuntimeError("len(timestamps) != len(data), cannot continue, this should never happen")
        if(len(self.times) <= 2):
            print("WARNING: No Data for %s!"%self.name)
            return (None,None)
        ############ AVERAGE OUT DATA #############
        if(CFG("combine_data_points") >= (self.times[1] - self.times[0]).total_seconds()):
            x_dp = 5
            m_t  = 3
            while(i+x_dp<len(self.times)):
                # check middle time #
                if callback(self.times[i+m_t],date1,date2):
                    subset=0
                    subset_data=0.0
                    subset_time=timedelta(0)
                    while subset < x_dp:
                        subset_data += self.data [i+subset]
                        subset_time += self.times[i+subset]-datetime(2000,1,1)
                        subset += 1
                    out_x += [ subset_time/x_dp + datetime(2000,1,1) ]
                    out_y += [ subset_data/x_dp ]
                i += x_dp
        ############ AVERAGE OUT DATA ###########
        else:
            while(i<len(self.times)):
                if callback(self.times[i],date1,date2):
                    out_x += [ self.times[i] ]
                    out_y += [ self.data[i]  ]
                i += 1
        return (out_x,out_y)

    ## no idea on what kind of drugs I was when i wrote this function (it is somewhat ingenious though) ##
    def _get_timeframe(self, callback,date1=None,date2=None):
        r=dict()
        for t,c in zip(self.times,self.data):
            t = callback(t,date1,date2)
            if t == None:
                continue
            if t in r:
                r[t]+=[c]
            else:
                r.update({t:[c]})
        arr_t = []
        arr_v = []
        for k,v in r.items():
            arr_t += [k]
            arr_v += [sum(v)/len(v)]
        arr_t = [x for x,_ in sorted(zip(arr_t,arr_v))]
        arr_v = [x for _,x in sorted(zip(arr_t,arr_v))]
        return (arr_t,arr_v)

def parse_line(datapoints, line, timekey, keys, time_parser, timeformat=None):
        # This function expects:
        #       - datapoints { String:DataObject }
        #       - line       { String:Any        }
        #       - timekey      String               (key for timevalue in 'line')
        #       - keys       [ (String,String) ]    (source_key in 'line' to target_key in 'datapoints')
        time = time_parser(line[ timekey ],timeformat)
        for key in keys:
                datapoints[ key[1] ].data  += [ line[ key[0] ] ]
                datapoints[ key[1] ].times += [      time      ]

def processExternalData(datapoints, plotNameKey, fromTime, toTime, dtype):
    '''Download and parses external data of type dtype'''

    # prepare strings #
    cacheDir    = CFG("cache_dir")
    fromTimeStr = fromTime.strftime(CFG("nff_url_timeformat"))
    toTimeStr   = toTime.strftime(CFG("nff_url_timeformat"))
    cacheFile   = "cache_{}_{}_{}.data".format(dtype, fromTimeStr, toTimeStr)
    fullpath   = os.path.join(cacheDir, cacheFile)

    # check for cache file
    content = None
    if not os.path.isfile(fullpath):
        
        # download date if it doesn't exist #
        url = CFG("outside_data_url").format(dtype=dtype, fromDate=fromTimeStr, toDate=toTimeStr)
        r = requests.get(url)
        print(url)
        content = r.content.decode('utf-8', "ignore") # ignore bad bytes

        # cache data #
        if not os.path.isdir(cacheDir):
            os.mkdir(cacheDir)
        with open(fullpath, 'w') as f:
            f.write(content)

    else:

        # get data from cache otherwise
        print("INFO: Cache hit: {}".format(cacheFile))
        with open(fullpath) as f:
            content = f.read()

    skipBecauseFirstLine = True
    for l in content.split("\n"):
        if not ";" in l:
            continue
        elif not l.strip():
            continue
        elif skipBecauseFirstLine:
            skipBecauseFirstLine = False
            continue

        try:
            timeStr, value = l.split(";")
            timestamp = timeutils.time_from_csv(timeStr, CFG("nff_input_timeformat"))
            cleanFloat = value.replace(",",".")

            # - means the value is missing in the external data set, this is common #
            if cleanFloat.strip() == "-" or cleanFloat.strip() == "+":
                continue

            datapoints[plotNameKey].data  += [float(cleanFloat)]
            datapoints[plotNameKey].times += [timestamp]
        except ValueError as e:
            print(l)
            raise e


def read_in_file(path, backend=None, outsideData=False, plotOutsideTemp=True, plotOutsideHum=True):
        '''Read in a file, add outside data if requested'''

        datapoints = dict()
        identifiers =  [ CFG("plot_temperatur_key"),
                         CFG("plot_humidity_key"),
                         CFG("plot_dewcels_key"),
                         CFG("plot_outside_temperatur_key"),
                         CFG("plot_outside_humidity_key") ]

        names  = [ CFG("temperatur_plot_name"),
                   CFG("humidity_plot_name"),
                   CFG("dewcels_plot_name"),
                   CFG("temperatur_outside_plot_name"),
                   CFG("humidity_outside_plot_name") ]

        colors = [ CFG("temperatur_color"),
                   CFG("humidity_color"),
                   CFG("dewcels_color"),
                   CFG("temperatur_outside_color"),
                   CFG("humidity_outside_color") ]

        global line_colors
        line_colors = colors

        plotSettings = [ CFG("plot_temperatur"),
                         CFG("plot_humidity"),
                         CFG("plot_dewcels"),
                         plotOutsideTemp,
                         plotOutsideHum ]
        
        assert(len(names) == len(colors) == len(identifiers) == len(plotSettings))

        max_name_len = max([len(s) for s in names])
        for i in range(0, len(names)):
            while len(names[i]) < max_name_len:
                names[i] += " "
            datapoints.update({ identifiers[i] : Data(names[i], plotSettings[i]) })

        # legacy variables...
        pt, ph, pd, pto, pho = identifiers

        # parse input file #
        if path == None:
            raise Exception("Path in plot.read_in was None")
        elif backend != None:
                backend(path)
        elif path.endswith(".DBF") or path.endswith(".dbf"):
                dbfread(path,datapoints,pt,ph,pd)
        elif path.endswith(".xls") or path.endswith(".XLS"):
                csvread(path,datapoints,pt,ph,pd)
        elif path.endswith(".txt"):
                csvread_txt(path,datapoints,pt,ph,pd)
        else:
                raise NotImplementedError("Cannot determine filetype, cannot continue. Exit.")
        
        # if nessesary download and process external data #
        if outsideData:

            fromTime = datapoints[CFG("plot_temperatur_key")].getFirstTime()
            toTime   = datapoints[CFG("plot_temperatur_key")].getLastTime()

            processExternalData(datapoints, pto, fromTime, toTime, CFG("dtype_temperatur"))
            processExternalData(datapoints, pho, fromTime, toTime, CFG("dtype_humidity"))

        # sanity check result #
        check_read_in(datapoints)

        return datapoints

def dbfread(path,datapoints,pt,ph,pd):
        for record in DBF(path):
            parse_line(datapoints,record,'DATETIME',[ ('TEMPCELS',pt) , ('HUMIDITY',ph) , ('DEWCELS',pd) ] ,timeutils.time_from_dbf)

def csvread(path,datapoints,pt,ph,pd):
        count = 0;
        with open(path) as f:
            for l in f:
                    if l.startswith(">>") or l.startswith("--") or l.startswith("NO."):
                            count += 1
                            continue
                    else:
                        row_arg = list(map(lambda s:s.replace(" ","").replace(",","."),l.split("\t")))
                        row = {"temp":None,"hum":None,"taupunkt":None,"datetime":None}
                        row["datetime"]     = row_arg[1]+row_arg[2]
                        row["temp"]         = float(row_arg[3])
                        row["hum"]          = float(row_arg[4])
                        row["taupunkt"]     = float(row_arg[5])
                        parse_line(datapoints,row,'datetime',[ ('temp',pt) , ('hum',ph) , ('taupunkt',pd) ],\
                                        timeutils.time_from_csv,timeformat="%d-%m-%Y%H:%M:%S")
        print("Info: Ignored %d lines at beginning of file"%count)

import codecs
def csvread_txt(path,datapoints,pt,ph,pd):
        count = 0;
        f = open(path) 
        try:
            for l in f:
                    if any(s in l for s in ["Logger","Datenquelle","Sensortyp","Einheit","Daten"]):
                            count += 1
                            continue
                    else:
                        row_arg = list(map(lambda s:s.replace(" ","").replace(",","."),l.split("\t")))
                        row = {"temp":None,"hum":None,"taupunkt":None,"datetime":None}
                        row["datetime"]     = "%s-%s-%s_%s:%s"%(row_arg[0],row_arg[1],row_arg[2],row_arg[3],row_arg[4])
                        row["temp"]         = float(row_arg[6])
                        row["hum"]          = float(row_arg[7])
                        row["taupunkt"]     = 0.0
                        parse_line(datapoints,row,'datetime',[ ('temp',pt) , ('hum',ph) , ('taupunkt',pd) ],\
                                        timeutils.time_from_csv,timeformat="%d-%m-%Y_%H:%M")
        except (UnicodeError, IndexError):
            count = csvread_txt_fallback(path,datapoints,pt,ph,pd)

        print("Info: Ignored %d lines at beginning of the file"%count)
        f.close()

def csvread_txt_fallback(path,datapoints,pt,ph,pd):
    '''fallback for different format and encoding of txt'''
    count = 0
    with codecs.open(path, "r",encoding="ISO8859_2", errors='repalce') as f:
        for l in f:
            if any(s in l for s in ["Logger","Datenquelle","Sensortyp","Einheit","Daten"]):
                count += 1
                continue
            else:
                date,time,temp,hum = l.replace(" ","").replace(".","-").replace(",",".").split("\t")
                row = {"temp":None,"hum":None,"taupunkt":None,"datetime":None}
                row["datetime"]     = "{}_{}".format(date,time[:5])
                row["temp"]         = float(temp)
                row["hum"]          = float(hum)
                row["taupunkt"]     = 0.0
                parse_line(datapoints,row,'datetime',[ ('temp',pt) , ('hum',ph) , ('taupunkt',pd) ],\
                                timeutils.time_from_csv,timeformat="%d-%m-%Y_%H:%M")
    return count


def check_read_in(datapoints):
        good = False
        for v in datapoints.values():
            if len(v.times) != len(v.data):
                print("more timestamps than data (or visa versa), this indicates that the file is corrupted, cannot continue")
                good = False
                break
            if len(v.times) > 1:
                good = True
        if not good:
            input("reading input file failed for an unknown reason, <ENTER> to exit")
            import sys
            sys.exit(1)
