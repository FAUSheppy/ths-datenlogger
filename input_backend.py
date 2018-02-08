#!/usr/bin/python3
from config_parse import CFG
from datetime import datetime, timedelta

from dbfread import DBF
import plot_timeutils

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

    def get_timeframe(self, callback,date1=None,date2=None):
        out_x = []
        out_y = []
        i = 0
        if(len(self.times) != len(self.data)):
            raise RuntimeError("len(timestamps) != len(data), cannot continue, this should never happen")
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

def parse_line(datapoints,line,timekey,keys,time_parser,timeformat=None):
        # This function expects:
        #       - datapoints { String:DataObject }
        #       - line       { String:Any        }
        #       - timekey      String               (key for timevalue in 'line')
        #       - keys       [ (String,String) ]    (source_key in 'line' to target_key in 'datapoints')
        time = time_parser(line[ timekey ],timeformat)
        for key in keys:
                datapoints[ key[1] ].data  += [ line[ key[0] ] ]
                datapoints[ key[1] ].times += [      time      ]

def read_in_file(path,backend=None):
        global tname
        global hname
        global dname
        global opath
        
        datapoints = dict()

        pt=CFG("plot_temperatur_key")
        ph=CFG("plot_humidity_key")
        pd=CFG("plot_dewcels_key")
        
        ## NAME PADDING ##
        max_name_len = max(len(tname),len(hname),len(dname))
        while len(tname) < max_name_len:
                tname += " "
        while len(hname) < max_name_len:
                hname += " "    
        while len(dname) < max_name_len:
                dname += " "

        datapoints.update({ pt:Data( tname,CFG("plot_temperatur") ) })
        datapoints[pt].color = CFG("temperatur_color")      
        
        datapoints.update({ ph:Data( hname,CFG("plot_humidity") ) })
        datapoints[ph].color = CFG("humidity_color")
        
        datapoints.update({ pd:Data( dname,CFG("plot_dewcels") ) })
        datapoints[pd].color = CFG("dewcels_color")
        
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

        check_read_in(datapoints)
        return datapoints

def dbfread(path,datapoints,pt,ph,pd):
        for record in DBF(path):
            parse_line(datapoints,record,'DATETIME',[ ('TEMPCELS',pt) , ('HUMIDITY',ph) , ('DEWCELS',pd) ] ,plot_timeutils.time_from_dbf)

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
                                        plot_timeutils.time_from_csv,timeformat="%d-%m-%Y%H:%M:%S")
        print("Info: Ignored %d lines at beginning of file"%count)

def csvread_txt(path,datapoints,pt,ph,pd):
        count = 0;
        with open(path) as f:
            for l in f:
                    if any(s in l for s in ["Logger","Datenquelle","Sensortyp","Einheit","Daten"]):
                            count += 1
                            continue
                    else:
                        row_arg = list(map(lambda s:s.replace(" ","").replace(",","."),l.split("\t")))
                        row = {"temp":None,"hum":None,"taupunkt":None,"datetime":None}
                        row["datetime"]     = "%s-%s-%s_%s:%s"%(row_arg[0],row_arg[1],row_arg[2],row_arg[3],row_arg[4])
                        print(row["datetime"])
                        row["temp"]         = float(row_arg[6])
                        row["hum"]          = float(row_arg[7])
                        row["taupunkt"]     = 0.0
                        parse_line(datapoints,row,'datetime',[ ('temp',pt) , ('hum',ph) , ('taupunkt',pd) ],\
                                        plot_timeutils.time_from_csv,timeformat="%d-%m-%Y_%H:%M")
        print("Info: Ignored %d lines at beginning of file"%count)

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
