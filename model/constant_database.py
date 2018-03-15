'''
Created on Jan 13, 2018

@author: deriv
'''
from collections import namedtuple
from _functools import reduce
database=[]
'''format of each entry in the function database is as follows:
    constant name
    algorithm for computing the constant
'''
Constant=namedtuple('Constant','name algorithm')
MAX_ITERATIONS=500

class Summation():
    def __init__(self,f):
        self._f=f
        
    def __getitem__(self,start: int):
        return reduce(lambda x,y:x+y,map(lambda z: self._f(z),[i for i in range(start,MAX_ITERATIONS)]))
    
def double_fact(n: int):
    if n==0:
        return 1
    elif n==1:
        return 1
    else:
        return n*double_fact(n-2)
    
def get_constant(name: str):
    for i in range(len(database)):
        if database[i].name==name:
            return database[i].algorithm[0]
    return None

#print(double_fact(500))
database.append(Constant('PI',Summation(lambda x: 2*double_fact(2*x)/double_fact(2*x+1)*(1/2)**x)))