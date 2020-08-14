#!/usr/bin/python3
import sys
from config_parse import CFG
from constants import *
from datetime import datetime, timedelta
from frontend_utils import open_file
from constants      import *

import math
import matplotlib
matplotlib.use(CFG("use_gui_backend"))

import matplotlib.pyplot as plt
import matplotlib.dates
import matplotlib.ticker as ticker

import plot_graphutils
import plot_imageutils
import plot_timeutils


def plot(datapoints,path=None,date1=None,date2=None):
        plotname = "" if CFG("name_of_plot") == "None" else CFG("name_of_plot")
        tup = [None,None,plot_timeutils.between_dates,plotname]
        if CFG("enable_multicore_support"):
                thread  = Process(target=__plot,args=(tup,datapoints,date1,date2))
                thread.start()
        else:
                __plot(tup,datapoints,path,date1,date2)
                        
def __plot(tup,datapoints,path,date1=None,date2=None):
        NO_SERIES  = True
        x,y,ymin,ymax,unix_x,major_xticks = ( [] , [], -1 , -1 , [], [] )
        lw = CFG("plot_line_width")
        ls = CFG("plot_line_style")
        tup[FIGURE],tup[AXIS] = plt.subplots(1, 1)

        for key in datapoints.keys():
                g = datapoints[key]
                print(key)
                #### Check if we are supposed to plot something ####
                if not g.plot:
                        continue
                #### GET AND CHECK TIMEFRAMES ####
                x,y, = g.get_timeframe(tup[CALLBACK],date1,date2)
                if not x or not y or len(x) <= 0 or len(y) <= 0:
                    print("Warning: Empty series of data '%s' (wrong start/end time?)"%g.name)
                    continue
                else:
                    NO_SERIES = False
                    unix_x = list(map(plot_timeutils.unix,x))
                    ymin,ymax = plot_graphutils.getlimits_y(y)

                #### GET LINE STYLES ####
                legend_label = plot_graphutils.legend_box_contents(g.name,y)
                tup[AXIS].plot(unix_x, y,ls=ls,lw=lw,marker="None", label=legend_label, color=g.color)
                legacy_x_save = x
                lagacy_y_save = y
        
        if NO_SERIES:
                print("Error: no data, nothing to plot. cannot continue. exit.")
                sys.exit(1)

        ## GRID ##
        plot_graphutils.general_background_setup(tup, ymin, ymax, legacy_x_save)

        ## using unix_x relys on unix_x to be the same for all plots ##
        if path == None:
            path = open_file()

        pic_path = output_path(path,date1,date2)
        

        ## set resoltuion ##
        DPI = CFG("outfile_resolution_in_dpi")
        fig_x_height = CFG("fig_x_height_inches")/float(1000)
        fig_y_height = CFG("fig_y_height_inches")/float(1000)
        tup[FIGURE].set_size_inches(fig_x_height,fig_y_height)

        ## save the figure ##
        tup[FIGURE].savefig(pic_path,dpi=DPI,pad_inches=0.1,bbox_inches='tight',transparent=CFG("transparent_background"))

        ### do operations on the finished png ###
        plot_imageutils.check_and_rotate(pic_path)

def output_path(path,date1,date2):
        if date1 != None and date2 == None:
            pic_path = path + "-nach-%s"%date1.strftime("%d.%m.%y")  + ".png"
        elif date1 == None and date2 != None:
            pic_path = path + "-vor-%s"%date2.strftime("%d.%m.%y")  + ".png"
        elif date1 == None and date2 == None:
            pic_path = path + "-alles" + ".png"
        else:
            pic_path = path + "-%s_to_%s"%(date1.strftime("%d.%m.%y"),date2.strftime("%d.%m.%y")) + ".png"
        print("Output wird gespeichert nach: %s"%str(pic_path))
        return pic_path
