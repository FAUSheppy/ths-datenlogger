#!/usr/bin/python3
import sys
from config_parse import CFG
from constants import *
from datetime import datetime, timedelta
from constants      import *

import math
import matplotlib
matplotlib.use(CFG("use_gui_backend"))

import matplotlib.pyplot as plt
import matplotlib.dates
import matplotlib.ticker as ticker

import plot_graphutils
import imageutils
import timeutils

import localization.de as localization


def plot(datapoints, path=None, date1=None, date2=None, forcePath=False, qtTextBrowser=None):
        plotname = "" if CFG("name_of_plot") == "None" else CFG("name_of_plot")
        tup = [None,None,timeutils.between_dates,plotname]
        return __plot(tup, datapoints, path, date1, date2, forcePath, qtTextBrowser)
                        
def __plot(tup, datapoints, path, date1=None, date2=None, forcePath=False, qtTextBrowser=None):
        NO_SERIES  = True
        x,y,ymin,ymax,unix_x,major_xticks = ( [] , [], -1 , -1 , [], [] )
        lw = CFG("plot_line_width")
        ls = CFG("plot_line_style")
        tup[FIGURE],tup[AXIS] = plt.subplots(1, 1)

        # generate datapoints #
        tupelsToIterate = []
        makeLast = None
        for key in datapoints.keys():
            g = datapoints[key]
            if not g.plot:
                continue
            x,y, = g.get_timeframe(tup[CALLBACK],date1,date2)
            
            # ensure a native value is last in the list to fix unix_x last tick #
            if not makeLast and (g.name == CFG("plot_temperatur_key") or CFG("plot_humidity_key")):
                makeLast = (x, y, g)
            else:
                tupelsToIterate += [(x, y, g)]
                
        tupelsToIterate += [makeLast]

        # check for negative values (legend padding) #
        anyValueNegative = False
        for x, y, g in tupelsToIterate:
            if not y or len(y) == 0:
                qtTextBrowser.append("leere Sequenz für {}, y: {}, x: {}".format(g.name, y, x))
                raise ValueError("leere Sequenz für {}, y: {}, x: {}".format(g.name, y, x))
            anyValueNegative = anyValueNegative or min(y) < 0

        # plot #
        for x, y, g in tupelsToIterate:
            if not x or not y or len(x) <= 0 or len(y) <= 0:
                qtTextBrowser.append(localization.warn_empty_series)
                continue
            else:
                NO_SERIES = False
                unix_x = [ el.timestamp() for el in x]
                y_min_tmp, y_max_tmp = plot_graphutils.getlimits_y(y)
                if ymin == -1:
                    ymin = y_min_tmp
                    ymax = y_max_tmp
                else:
                    ymin = min(y_min_tmp, ymin)
                    ymax = min(y_max_tmp, ymax)

                legend_label = plot_graphutils.legend_box_contents(g.name, y, anyValueNegative)
                tup[AXIS].plot(unix_x, y, ls=ls, lw=lw, marker="None", 
                                label=legend_label, color=g.color)
                legacy_x_save = x
                lagacy_y_save = y
        
        if NO_SERIES:
            qtTextBrowser.append(localization.err_empty_series)
            raise ValueError(localization.err_empty_series)

        ## GRID ##
        plot_graphutils.general_background_setup(tup, ymin, ymax, legacy_x_save)

        ## using unix_x relys on unix_x to be the same for all plots ##
        if path == None:
            path = open_file()
        
        if not forcePath:
            pic_path = output_path(path, date1, date2, qtTextBrowser)
        else:
            pic_path = path
        

        ## set resoltuion ##
        DPI = CFG("outfile_resolution_in_dpi")
        fig_x_height = CFG("fig_x_height_inches")/float(1000)
        fig_y_height = CFG("fig_y_height_inches")/float(1000)
        tup[FIGURE].set_size_inches(fig_x_height,fig_y_height)

        ## save the figure ##
        tup[FIGURE].savefig(pic_path,dpi=DPI,pad_inches=0.1,bbox_inches='tight',transparent=CFG("transparent_background"))

        ### do operations on the finished png ###
        imageutils.check_and_rotate(pic_path, qtTextBrowser)

        return pic_path

def output_path(path, date1, date2, qtTextBrowser):
        if date1 != None and date2 == None:
            pic_path = path + "-nach-%s"%date1.strftime("%d.%m.%y")  + ".png"
        elif date1 == None and date2 != None:
            pic_path = path + "-vor-%s"%date2.strftime("%d.%m.%y")  + ".png"
        elif date1 == None and date2 == None:
            pic_path = path + "-alles" + ".png"
        else:
            pic_path = path + "-%s_to_%s"%(date1.strftime("%d.%m.%y"),date2.strftime("%d.%m.%y")) + ".png"
        qtTextBrowser.append(localization.info_output_path.format(pic_path))
        return pic_path
