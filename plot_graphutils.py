#!/usr/bin/python3
from config_parse import CFG
from datetime import datetime, timedelta
import matplotlib
matplotlib.use(CFG("use_gui_backend"))
import matplotlib.pyplot as plt
import matplotlib.dates
import matplotlib.ticker as ticker
from constants import *
import math
import plot_timeutils
matplotlib.rc('font', **GLOBAL_FONT)

def getlimits_y(y):
        ymax = max(y)+CFG("empty_space_above_plot")
        y_min_height = CFG("yaxis_minnimum_hight")
        if y_min_height != 0 and y_min_height > ymax:
                ymax = y_min_height
        y_start_val = CFG("yaxis_start_value")
        if y_start_val < min(y) or CFG("yaxis_force_start_value"):
                ymin=y_start_val
        else:
                ymin=min(y)
        return (ymin,ymax)

def avg(array):
        return sum(array)/float(len(array))

def legend_box_contents(name,y):
	if CFG("show_min"):
		name += " min: %.1f,"%min(y)
	if CFG("show_max"):
		name += " max: %.1f,"%max(y)
	if CFG("show_avg"):
		name += " Mittelwert: %.1f,"% avg(y)
	return name.rstrip(",")    

def general_background_setup(tup,ymin,ymax,x):

    unix_x = list(map(plot_timeutils.unix,x))

    ### SET AXIS LIMITS ###
    tup[AXIS].set_ylim([ymin,ymax])
    tup[AXIS].set_xlim([plot_timeutils.unix(min(x)),plot_timeutils.unix(max(x))])

    if CFG("draw_thresholds"):
        hcrit=CFG("humidity_critical")
        hwarn=CFG("humidity_warning")
        tlow=CFG("acceptable_temp_low")
        thigh=CFG("acceptable_temp_high")
        tup[AXIS].axhline(y=CFG("target_temperatur"),ls=CFG("hline_line_style"),lw=CFG("hline_line_width"),color=CFG("acceptable_temp_color"))
        tup[AXIS].axhline(y=hcrit,ls=CFG("hline_line_style"),lw=CFG("hline_line_width"),color=CFG("humidity_crit_color"))
        tup[AXIS].axhspan(hwarn,hcrit,color=CFG("humidity_warning_color"),alpha=CFG("humidity_warning_alpha"))
        tup[AXIS].axhspan(hcrit,ymax,color=CFG("humidity_crit_color"),alpha=CFG("humidity_crit_alpha"))
        tup[AXIS].axhspan(tlow,thigh,color=CFG("acceptable_temp_color"),alpha=CFG("acceptable_temp_alpha"))
    
    #### GRID ####
    major_xticks = gen_xticks_from_timeseries(x)
    minor_xticks = get_minor_xticks_from_major(major_xticks)
    if CFG("raster"):
        grid(tup,major_xticks,ymin,ymax)
    
    #### XTICKS ####
    tup[AXIS].set_xticks(major_xticks)
    tup[AXIS].xaxis.set_major_formatter(ticker.FuncFormatter(xlabel_formater_callback))
    tup[AXIS].xaxis.set_major_locator(ticker.FixedLocator(major_xticks, nbins=None))
    tup[AXIS].xaxis.set_minor_locator(ticker.FixedLocator(minor_xticks, nbins=None))
    tup[AXIS].xaxis.set_tick_params(which='minor',width=0.2,direction="out")
    
    tup[AXIS].yaxis.set_major_locator(ticker.MultipleLocator(CFG("y_tick_interval")))
    tup[AXIS].yaxis.set_minor_locator(ticker.MultipleLocator(1))
    tup[AXIS].yaxis.set_tick_params(which='minor',width=0.2,direction="out")

    tup[AXIS].tick_params(axis='x',which="major",labelsize=CFG("xticks_font_size"));
    tup[AXIS].tick_params(axis='y',which="major",labelsize=CFG("yticks_font_size"));
                        
    ## ROTATION XLABELS ##
    rotation=CFG("xticks_label_degree")
    if rotation > 0:
        plt.xticks(rotation=rotation,ha='right')

    ## AXIS LABELS
    ylabel_box = dict(boxstyle="square",facecolor='grey', alpha=0.4, edgecolor='black',lw=0.5)
    xlabel_box = ylabel_box
    label_size = CFG("label_font_size")
    spacing=0.1
    tup[AXIS].set_ylabel(CFG("y_label"),rotation='horizontal',size=label_size,bbox=ylabel_box)
    tup[AXIS].yaxis.set_label_coords(0.045,0.970)
    tup[AXIS].set_xlabel(CFG("x_label"),size=label_size,bbox=xlabel_box)
    tup[AXIS].xaxis.set_label_coords(0.945,0.03)
    
    ## GENERAL LEGEND ##
    legend_handle = tup[AXIS].legend(
                    loc=CFG("legend_location"),
                    edgecolor="inherit",
                    fancybox=False,
                    borderaxespad=spacing,
                    prop={'family': 'monospace','size':CFG("legend_font_size")}
                    )
    legend_handle.get_frame().set_linewidth(0.2)
    #tup[AXIS].set_aspect(get_aspect_ratio(unix_x,ymin,ymax,major_xticks))

                
def get_aspect_ratio(ux,ymin,ymax,xticks):
        ratio = 100
        tmp = CFG("aspect_ratio")
        if str(tmp) == "A4":
            ratio = a4_aspect()
        else:
            ratio=tmp
        magic_value = 3.25
        return ratio * ( max(ux) - min(ux) ) / float(ymax - ymin + magic_value)

def a4_aspect(x):
        return ( 1/math.sqrt(2) ) * x

def grid(tup,xticks,ymin,ymax):
        lw = CFG("grid_line_width")
        ls = CFG("grid_line_style")
        color = CFG("grid_line_color")
        hour_mul = 24
        expected_vlines = len(list(filter(lambda xt: xt%3600 < 60,xticks)))
        safety_first = 60*60 +10
        step = xticks[1]-xticks[0] 
        if step < (24*3600)-safety_first:
            if expected_vlines <= 6:
                    hour_mul = 1
            elif expected_vlines <=12:
                    hour_mul = 2
            elif expected_vlines <=24:
                    hour_mul = 4

        for xt in xticks:
                leck_mich = datetime.fromtimestamp(xt)
                if leck_mich.hour == leck_mich.minute == leck_mich.second == 0:
                    tup[AXIS].axvline(xt,ls="-",lw=CFG("major_line_width"),color=color)
                else:
                    tup[AXIS].axvline(xt,ls=ls,lw=lw,color=color)
        ## HLINES ##
        y_interval = CFG("raster_hline_prefered_interval")
        cur = ymin
        while cur < ymax:
                cur += y_interval
                tup[AXIS].axhline(cur,ls=ls,lw=lw,color=color)

def find_step(step,x,total_xticks):
        intervals = parse_possible_intervals()
        start = min(x)
        if CFG("always_allow_days_as_xticks") and step > timedelta(days=1)/2:
                step = timedelta(days=round(step.days+1))
                start = min(x).replace(hour=0,second=0,minute=0)
                return (start,step)
        
        min_delta_step = timedelta(days=1)      # the actual step that has the lowest delta
        min_delta      = timedelta(days=1000)   # the delta o thus step
        for s in intervals:
            delta = max(s,step)-min(s,step)
            if delta < min_delta:
                min_delta_step = s
                min_delta      = delta

        step  = min_delta_step
        start = plot_timeutils.round_time_to_step(start,step)

        warn_on_too_much_xticks(x,total_xticks,step)
        return (start,step)

def parse_possible_intervals():
        intervals = CFG("acceptable_x_intervals")
        parsed_intervals = []
        for s in intervals.split(','):
            try:
                st = int(s[:-1])
            except ValueError:
                raise ValueError("'acceptable_x_intervals' muss die Form 'Zahl[s(econds),m(minutes),h(ours),d(days)]' haben!")
            except Exception:
                raise ValueError("invalid intervals for x_labels %s [index out of bounds], did you write something like this ',,,,' ?]"%str(intervals))
            if s.endswith("s"):
                if 60 % st != 0:
                    raise ValueError("interval must fit to next bigger interval so basicly for hours 24%interval==0")
                parsed_intervals += [timedelta(seconds=st)]
            elif s.endswith("m"):
                if 60 % st != 0:
                    raise ValueError("interval must fit to next bigger interval so basicly for hours 24%interval==0")
                parsed_intervals += [timedelta(minutes=st)]
            elif s.endswith("h"):
                if 24 % st != 0:
                    raise ValueError("interval must fit to next bigger interval so basicly for hours 24%interval==0")
                parsed_intervals += [timedelta(hours=st)]
            elif s.endswith("d"):
                parsed_intervals += [timedelta(days=st)]
            else:
                raise ValueError("invalide Zeitspezifizierer in %s (muss, s,m,h oder d sein)"%str(intervals))
        return parsed_intervals

def warn_on_too_much_xticks(x,total_xticks,step):
        if (max(x)-min(x))/step > 2*total_xticks:
                print("Warnung: maximales xinterval zu niedrig eine sinnvolle Anzahl an xticks zu generieren (total x_ticks: %d"%total_xticks)

def get_minor_xticks_from_major(major):
        mult = CFG("minor_xticks_per_major")
        step = (major[1]-major[0])/mult
        ret = []
        for x in major:
                if x == max(major):
                    break
                ret += [x+ 0*step]
                ret += [x+ 1*step]
                ret += [x+ 2*step]
                ret += [x+ 3*step]
                ret += [x+ 4*step]
        return ret

def gen_xticks_from_timeseries(x):
        ticks=CFG("prefered_total_xticks")
        xmin = min(x)
        xmax = max(x)
        delta = xmax-xmin
        step = delta/ticks
        cur,step = find_step(step,x,ticks)
        xticks = []
        xmax += step*CFG("add_x_labels_at_end")
        while cur < xmax:
            xticks += [plot_timeutils.unix(cur)]
            cur+=step
        return xticks

def xlabel_formater_callback(tick_val, tick_pos):
        dt = datetime.fromtimestamp(tick_val)
        tformat = CFG("timeformat_x_axis").replace('$','%')
        return dt.strftime(tformat)
