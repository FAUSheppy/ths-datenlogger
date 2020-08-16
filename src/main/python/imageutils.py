#!/usr/bin/python3
from config_parse import CFG
from PIL import Image
import math
def check_and_rotate(path):
        img = Image.open(path)
        div=abs(float(img.size[1])/float(img.size[0])-a4_aspect())/a4_aspect()*100
        print("Seitenverhältnisabweichung zu A4: %.2f"%div+r'%')
        img.rotate(CFG("image_rotation"),expand=True).save(path.strip(".png")+"_rotated.png")

def a4_aspect():
        return 1/math.sqrt(2)
