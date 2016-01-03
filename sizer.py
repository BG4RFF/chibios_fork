'''
Created on 31. 12. 2015

@author: kubanec
'''

import subprocess
import re
import sys
import argparse

parser = argparse.ArgumentParser(description ="Get section sizes of stm32 elf file")
parser.add_argument("filename",help="Path to the arm executable",type=str)

args = parser.parse_args()

filename =  args.filename


def size(st):
    assert isinstance(st,str)
    m = re.sub("\s+", " ", st)
    m = m.strip().split(" ")
    name = m[2]
    start = m[4]
    size = m[6]

    r = (name, int(start,16), int(size,16))
    return r


o = subprocess.check_output(["readelf","-S", filename])
o = o.split("\n")

l = {}
for a in o:
    if ("WA" in a) or ("AX" in a):
        m = size(a)
        l[m[0]] = m

text = l["startup"][2]
text += l[".text"][2]
try:
    text += l[".textalign"][2]
except:
    pass
try:
    text += l[".data"][2]
    data = l[".data"][2]
except:
    data = 0


bss = l[".bss"][2]
bss += l[".mstack"][2]
bss += l[".pstack"][2]

flash = text
ram = data + bss

offset = l["startup"][1]

f1 = ("flash","ram",".bss", ".data", "Program starts at")
f2 = (str(flash),str(ram),str(bss),str(data),"0x%X" % offset)

l = (f1,f2)

print filename

for args in l:
    print '{0:<10} {1:<10} {2:<10} {3:<10} {4:<8}'.format(*args)
