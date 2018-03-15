'''
Created on Aug 15, 2017

@author: deriv
'''


IS_CONFIRMED=0
FILEPATH=1

import pathlib
from _functools import reduce
def find_files(dirs: pathlib.Path,ext:str,*rules:bool)->list:
    res=reduce(lambda x,y: x and y,[not rules[i] for i in range(len(rules))])
    return [[False,file] for file in sorted(dirs.rglob('*.'+ext)) if res]

class Test():
    def __init__(self):
        i=0
        while i==0:
            i=i+1