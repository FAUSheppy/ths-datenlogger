#!/usr/bin/python3
from config_parse import CFG
from PIL import Image
import math
import localization.de as localization

def check_and_rotate(path, qtTextBrowser):
        img = Image.open(path)
        div=abs(float(img.size[1])/float(img.size[0])-a4_aspect())/a4_aspect()*100
        qtTextBrowser.append(localization.info_divergence.format(div))
        img.rotate(CFG("image_rotation"),expand=True).save(path.strip(".png")+"_rotated.png")

def a4_aspect():
        return 1/math.sqrt(2)
