import configparser
import sys

conf = None
default_conf = None

def parse_config():
        global conf
        global default_conf
        
        conf = configparser.ConfigParser()
        conf.read("ths_config.txt")
        default_conf = configparser.ConfigParser()
        default_conf.read("ths_readonly_default.conf")
        
        if conf == None or (len(conf.sections()) == 0 and len(default_conf.sections()) == 0):
                print("Error: Missing configuration file, cannot continue")
                raise Exception("Missing configuration file")

def get_keys(like=None):
        ret = conf["plot"].keys()
        if like != None:
            ret = list(filter(lambda x:like in x,ret))
            if len(ret) == 0:
                print("No options that contain the string '%s'"%like)
                return ""
        return ret

def change_cfg(key,value):
        global conf
        confs = conf["plot"]
        v = str(value)
        key = str(key)
        if key not in confs:
            return False
        else:
            confs[key] = value
            return True


        
        
def CFG(tag):
        global conf
        global default_conf
        
        if conf == None:
                parse_config()
        if len(default_conf.sections()) > 0:
                default_confs = default_conf["plot"]
        else:
                default_confs = None
        confs = conf["plot"]
        
        if tag in confs:
                return parse_cfg(confs[tag])
        elif default_confs != None and tag in default_confs:
                print("Warning: %s no found in configuration, defaulting to %s" % (str(tag),str(default_conf[tag])),sys.stderr)
                return parse_cfg(default_confs[tag])
        else:
                raise Exception("Error: configuration option %s not found in configuration and no default value for it, cannot continue, exit." % str(tag))

def parse_cfg(c):
        if c == None:
                raise Exception("Config key (%s) found but has no value. Cannot continue, exit." % str(c))
        c = c.strip("'")
        c = c.strip('"')
        if c in ["yes","ja","True","Yes","Ja","true"]:
                return True
        if c in ["no","nein","False","No","Nein","false"]:
                return False
        try:
                return int(c)
        except ValueError:
                pass
        try:
                return float(c)
        except ValueError:
                pass
        return c
                

CFG("show_avg")
