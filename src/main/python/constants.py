#!/usr/bin/python3
from config_parse import CFG
GLOBAL_FONT = {'family':CFG("font"),'weight':'normal','size': CFG("global_text_size")}
SOURCE_PATH=CFG("default_target_dir")
FIGURE=0
AXIS=1
CALLBACK=2
