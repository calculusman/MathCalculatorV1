'''
Created on Aug 15, 2017

@author: deriv
'''

import inspect
from math import log

def remove_substring(s: str,substr: str)->str:
    res=s
    if len(s)-len(substr)<0:
        return res
    for i in range(len(s)-len(substr)):
        if s[i:i+len(substr)]==substr:
            res=s[:i]+s[i+len(substr):]
    return res

'''classes with same names in different modules give the same string; package and module names are removed'''
def type_as_str(obj:object)->str:
    s=str(type(obj))[8:-2]
    i=len(s)
    while (s[i:i+1]!='.' and i>=0):
        i=i-1
    return s[i+1:]

'''classes with same names in different modules give different strings; package and module names are kept (except __main__)'''
def type_as_str2(obj:object)->str:
    return remove_substring(str(type(obj))[8:-2],'__main__.')

'''includes class name'''
def func_name_as_str(f:'function')->str:
    return f.__qualname__

'''doesn't include class name'''
def func_name_as_str2(f:'function')->str:
    return f.__name__

'''doesn't include module name'''
def class_name_as_str(c: 'class')->str:
    s=str(c)[8:-2]
    i=len(s)
    while (s[i:i+1]!='.' and i>=0):
        i=i-1
    return s[i+1:]

'''includes module name'''
def class_name_as_str2(c: 'class')->str:
    return str(c)[8:-2]

'''
class_method_validate is a class pseudo-decorator that maintains the rules dictated by an internal rule, f (which must have no parameters).

The rule is called PRIOR TO whenever any method of the class (ex. __init__, __str__,etc.) is called
'''

def class_method_validate(Cls,f,E:BaseException):
    class Newcls(object):
        def __init__(self,*args,**kargs):
            print('initializing...',Cls,*args,**kargs)
            self.instance=Cls(*args,**kargs)
            print('intermission')
            self.instance_dict=dict([(k,v) for k,v in self.instance.__dict__.items()])
            print('initalizing complete')
            #print(self.instance)
            #print(self.instance_dict)
            self.methods=[t[1] for t in inspect.getmembers(Cls,predicate=inspect.isfunction)]
            #print(self.methods)
            if f not in self.methods:
                raise AssertionError("Method not defined inside class")
            else:
                self.f_index=0
                for i in range(len(self.methods)):
                    if self.methods[i] is f:
                        self.f_index=i
                #print(self.f_index)
                print('__init__ complete')
        
        def __setattr__(self,name,val):
            if name=='base_term':
                print('__setattr__',self,name,val)
            else:
                print('__setattr__',name,val)
            if name=='instance' or name=='instance_dict' or name=='methods' or name=='f_index':
                self.__dict__[name]=val
            else:
                self.instance.__setattr__(name,val)
            
        def __getattr__(self,name):
            if name=='instance' or name=='instance_dict' or name=='methods' or name=='f_index':
                return self.__dict__[name]
            else:
                return self.instance_dict[name]
            
        def __getattribute__(self,name):
            if inspect.stack(0)[-2].function=='__init__':
                return object.__getattribute__(self,name)
            if name=='__dict__':
                return object.__getattribute__(self,name)
            elif name=='instance' or name=='instance_dict' or name=='methods' or name=='f_index':
                return object.__getattribute__(self,name)
            for i in range(len(inspect.stack(0))):
                print(inspect.stack(0)[i])
            print('__getattribute__',name)
            try:
                x=super(Newcls,self).__getattribute__(name)
            except AttributeError:
                pass
            else:
                return x
            
            if not inspect.stack(0)[-2].function=='__init__' and not eval("self.instance."+func_name_as_str2(self.methods[self.f_index])+"()"):
                raise E
            return self.instance.__getattribute__(name)
                
        def __getindex__(self,index):
            if not eval("self.instance."+func_name_as_str2(self.methods[self.f_index])+"()"):
                raise E
            return self.instance.__getindex__(index)
        def __str__(self):
            #if not eval("self.instance."+func_name_as_str2(self.methods[self.f_index])+"()"):
            #    raise E
            return self.instance.__str__()
        
        def __repr__(self):
            if not eval("self.instance."+func_name_as_str2(self.methods[self.f_index])+"()"):
                raise E
            return self.instance.__repr__()
        
        def __eq__(self,other):
            if not eval("self.instance."+func_name_as_str2(self.methods[self.f_index])+"()"):
                raise E
            return self.instance.__eq__(other)
        
        def __lt__(self,other):
            if not eval("self.instance."+func_name_as_str2(self.methods[self.f_index])+"()"):
                raise E
            return self.instance.__lt__(other)
        
        def __contains__(self,other):
            if not eval("self.instance."+func_name_as_str2(self.methods[self.f_index])+"()"):
                raise E
            return self.instance.__contains__(other)
        
        def copy(self):
            if not eval("self.instance."+func_name_as_str2(self.methods[self.f_index])+"()"):
                raise E
            return type(self.instance).copy(self.instance)
    return Newcls
        
class InternalClassException(Exception):
    def __init__(self):
        message="Internal Class Exception Error: Not a valid instance of a class"
        super(InternalClassException,self).__init__(message)
        
    def __repr__(self, *args, **kwargs):
        return Exception.__repr__(self, *args, **kwargs)
        
'''(@class_validation) a class decorator of class_method_validate that uses __bool__ as the rule and an InternalClassException is the Exception Class'''
def class_validation(Cls):
    func=None
    for f in inspect.getmembers(Cls,predicate=inspect.isfunction):
        if f[0]=='__bool__':
            func=f[1]
    if func==None:
        raise AssertionError("__bool__ not defined inside class")
    return class_method_validate(Cls,func,InternalClassException())

class OverrideException(Exception):
    def __init__(self):
        message="Override Exception: Method not in any of the class' superclass"
        super(OverrideException,self).__init__(message)
        
    def __repr__(self, *args, **kwargs):
        return Exception.__repr__(self, *args, **kwargs)

'''(@override) a method decorator that checks if the method can be overridden'''
'''not finished'''
def override(method):
    class OverrideCheck():
        def __init__(self):
            try:
                self.other_method=method
                self.instance=inspect.getmembers(self.other_method)
            except AttributeError:
                raise AttributeError
                
            self.__superclass__=self.__mro__
            self.methods=[]
            for c in self.__superclass__:
                method=[t[1] for t in inspect.getmembers(c,predicate=inspect.isfunction)]
                for m in method:
                    if not m in self.methods:
                        self.methods.append(m)
                        
        def overrider(self,method):
            if not method in self.methods:
                raise OverrideException()
            else:
                return method
        
def get_all_superclasses(cls:type):
    return cls.mro().remove(cls)

def get_all_subclasses(cls:type):
    res=[]
    for subclass in cls.__subclasses__():
        res.append(subclass)
        res.extend(get_all_subclasses(subclass))
    return res

@class_validation
class Test(object):
    def __init__(self,c:int,override:int=1):
        i=0
        n=c
        while n>0.0:
            n=log(n)
            i+=1
        self.value=i
        self.temp=override
    
    def is_valid(self)->bool:
        return True if self.value>=0 and self.temp>=0 else False
    
    def __bool__(self):
        return self.is_valid()
    
    def get_value(self)->int:
        return self.value
    
    def get_value2(self)->int:
        return self.temp
    
    def set_value(self,i:int):
        self.temp=i
        
    def __repr__(self):
        return self.__class__.__name__+"("+str(self.value)+","+str(self.temp)+")"


def f(x:int):
    return x**3-12*x+7

def g(x:int):
    return log(x/(x-1))

##Test class should not have @class_method_validate decorator for the following tests##
'''
assert type_as_str(Test(2))=='Test'
assert type_as_str(4)=='int'
assert type_as_str('c')=='str'
assert type_as_str2(4)=='int'
assert type_as_str2('c')=='str'
assert type_as_str2(Test(-1))=='Test'


assert func_name_as_str(Test.is_valid)=='Test.is_valid'
assert func_name_as_str2(f)=='f'
assert func_name_as_str2(Test.is_valid)=='is_valid'
assert func_name_as_str2(f)=='f'
'''
if __name__=='__main__':
    ##Test class should not have @class_method_validate decorator for the following tests##
    '''
    print(type_as_str(Test(2)))
    print(type_as_str2(4))
    print(type_as_str2('c'))
    print(type_as_str2(Test(-1)))
    
    print(type(Test(2)))
    print(type(4))
    
    import kobi.dir_lib
    print(type_as_str2(kobi.dir_lib.Test()))
    '''
    '''
    #print([t[1] for t in inspect.getmembers(Test,predicate=inspect.isfunction)])
    #print(Test.is_valid in [t[1] for t in inspect.getmembers(Test,predicate=inspect.isfunction)])
    #print(Test.__dict__)
    Ptest=class_method_validate(Test,Test.is_valid,AssertionError("Function not in the domain"))(1)
    print('****')
    print(Ptest.get_value())
    '''
    '''
    Ptest.set_value(-1)
    print(Ptest.get_value()) #raises Error
    '''
    '''
    Qtest=class_method_validate(Test,Test.is_valid,AssertionError("Function not in the domain"))(-2,-1)
    print(Qtest.get_value()) #raises Error
    '''
    
    ##Test class should have @class_method_validate decorator for the following tests##
    '''
    P2test=Test(1)
    print('****')
    print(P2test.get_value())
    print(P2test)
    
    P2test.set_value(-1)
    print(P2test.get_value()) #raises Error
    '''
    
    ##Test2 should be enabled for the following tests##
    '''
    @class_validation
    class Test2(object):
        def __init__(self,c:int):
            self.value=c
        
        def __bool__(self)->bool:
            return self.value>=0
    
        def set_value(self,i:int)->None:
            self.value=i
            
        def get_value(self)->int:
            return self.value
    '''
    '''
    P3test=Test2(-1)
    print(P3test.get_value()) #raises Error
    '''
    '''
    P4test=Test2(0)
    P4test.set_value(P4test.get_value()-1)
    P4test.set_value(P4test.get_value()+1) #raises Error
    '''
    
    
    
    '''
    def getclassname(method):
        print(inspect.isfunction(method))
        print(method.__class__)
        print(eval(method.__qualname__[:5])+'()')
    
    class Test3(object):
        def __init__(self):
            self.value=0
        @getclassname
        def set_value(self,i:int)->None:
            self.value=2*(self.value+i)
    '''