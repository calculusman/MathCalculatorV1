'''
Created on Sep 11, 2017

@author: deriv
'''
from collections import namedtuple
from _functools import reduce
import model.constant_database as Constants
database=[]
'''format of each entry in the function database is as follows:
    function name
    num. of arguments required
    domain [length of the domain list= num. of arguments required]
    definition [how to compute the function; put Taylor series or Laurent series or Puiseux series
    Power/Taylor series representation [None if unknown or doesn't exist]
    Laurent series representation [None if unknown or doesn't exist]
    Puiseux series representation [None if unknown or doesn't exist]
    Infinite Product representation [None if unknown or doesn't exist]
'''
MAX_ITERATIONS=1000

Function=namedtuple('Function', 'name argcount domain definition taylor laurent puiseux product')


class Measure:
    O=('dim',8)
    H=('dim',4)
    C=('dim',2)
    R=('dim',1)
    Q=('dim',0)
    Z=('dim',0)
    N=Z
    
class Magnitude:
    INF=('inf',1)
    NEG_INF=('inf',-1)
        
class TaylorSeries:
    def __init__(self,f,a:int,start:int=0):
        self._f=f
        self._a=a
        self._i=start
        
    def __getitem__(self,u: int):
        return reduce(lambda x,y: x+y,map(lambda z: self._f(z)*(u-self._a)**z,[i for i in range(self._i,MAX_ITERATIONS)]))

def fact(n: int):
    res=1
    for i in range(1,n):
        res*=i
    return res


def get_function(name: str):
    for i in range(len(database)):
        if database[i].name==name:
            return database[i]
    return None

#print(Constants.get_constant('PI'))
t_exp=TaylorSeries(lambda n: 1/fact(n),0)
t_ln=TaylorSeries(lambda n: (-1)**n/(n+1),1)
database.append(Function('sqrt',1,(Measure.R,lambda x: x>=0),None,None,None,None,None))
database.append(Function('exp',1,(Measure.R),t_exp,t_exp,None,None,None))
database.append(Function('ln',1,(Measure.R,lambda x: x>0),t_ln,t_ln,None,None,None))
database.append(Function('cos',1,(Measure.R),None,None,None,None,None))
database.append(Function('asin',1,(Measure.R,lambda x: -Constants.get_constant('PI')/2<x and x<Constants.get_constant('PI')/2),None,None,None,None,None))
database.append(Function('F',2,(Measure.R),None,None,None,None,None))
database.append(Function('Fh',4,(Measure.R),None,None,None,None,None))