'''
Created on Aug 12, 2017

@author: deriv
'''
import inspect
from kobi.struct_lib import TreeNode,TreePath
from kobi.lib import get_all_subclasses


class ExprNode(TreeNode):
    def __init__(self,name: str,value=None,children=[]):
        self.args=[]
        super(ExprNode,self).__init__(name,value,children)
    
    #def __repr__(self):
    #    return self.name+"("+", ".join([arg for arg in self.args])+")"
    
    def add_child(self, child):
        self.args.insert(0, child)
        super(ExprNode,self).add_child(child)
        
    def remove_child(self, child):
        self.args.remove(child)
        super(ExprNode,self).remove_child(child)
    
    def __getitem__(self, i: int):
        assert type(i) is int and i>=0 and i<len(self.args)
        return self.args[i]

    def __eq__(self,other):
        assert other==None or type(other) is ExprNode or type(other) in get_all_subclasses(ExprNode),"Comparison checks are allowed only among ExprNodes, not "+str(type(other))
        if other==None:
            return super(ExprNode,self).__eq__(other)
        elif (type(self) is ImmutableConst or type(self) in get_all_subclasses(ImmutableConst)) or (type(other) is ImmutableConst or type(other) in get_all_subclasses(ImmutableConst)):
            return self.value==other.value if other!=None and self.value!=None and other.value!=None else False
        elif (type(self) is Constant or type(self) is Var) and (type(other) is Constant or type(other) is Var):
            return self.value==other.value if other!=None and self.value!=None and other.value!=None else self.name==other.name if other!=None and type(self) is type(other) else False
        else:
            return self.name==other.name if other!=None and len(self.name)!=0 and len(other.name)!=0 and self.name!=None and other.name!=None else False
    
    def is_leaf(self):
        return type(self) is Var or type(self) is Constant or type(self) is Int or type(self) is Fraction
    
    def is_branch_pt(self):
        return (type(self) is Function or type(self) is Operator) and not self.is_leaf()
    
    def __hash__(self):
        return hash(repr(self))
    
    @staticmethod
    def copy(node: 'TreeNode',**kargs):
        assert type(node) is ExprNode or type(node) in get_all_subclasses(ExprNode), "node must be of type ExprNode, not"+str(type(node))
        assert len(kargs.keys())==0 or 'children' in kargs.keys() and len(kargs.keys())==1,"Unknown key arguments"
        if len(kargs.keys())==0:
            if node.is_leaf():
                if type(node) is Int or type(node) is Fraction and len(node.value.split('/'))==1:
                    return type(node)(int(node.value)) if type(node) is Int else type(node)(Int(int(node.value)))
                elif type(node) is Fraction:
                    return type(node)(Int(int(node.value.split('/')[0])),Int(int(node.value.split('/')[1])))
                else:
                    return type(node)(node.name)
            else:
                return type(node)(node.name,node.value,node.children)
        else:
            if node.is_leaf():
                assert len(kargs.keys())==0, "leaf nodes may not have children"
            else:
                return type(node)(node.name,node.value,[child for child in kargs['children']])
        
    
class ExprTree(TreePath):
    def __init__(self,base_node:ExprNode):
        #assert base_node==None or type(base_node) is ExprNode or type(base_node) in get_all_subclasses(ExprNode), "ExprTree allow bases to be of type ExprNode, not "+str(type(base_node))
        super(ExprTree,self).__init__(base_node)
        
    def replace(self,node:ExprNode,sub_tree:'ExprTree'):
        def _replace(tree_base:ExprNode,node:ExprNode,sub_tree_base:ExprNode):
            if len(tree_base.children)==0 and tree_base==node:
                t=ExprTree.copy(ExprTree(sub_tree_base))
                return t.base
            elif len(tree_base.children)==0:
                return tree_base
            else:
                tree_base.children=[_replace(child,node,sub_tree_base) for child in tree_base.children]
                return tree_base
        tree_copy=ExprTree.copy(ExprTree(self.base))
        sub_tree_copy=ExprTree.copy(ExprTree(sub_tree.base))
        if not node in self or not node.is_leaf():
            return tree_copy
        else:
            return ExprTree(_replace(tree_copy.base,node,sub_tree_copy.base))

    def get_all_leaves(self):
        if self.base==None:
            return []
        elif len(self.base.children)==0:
            return [self.base]
        else:
            res=[]
            for child in self.base.children:
                res.extend(ExprTree(child).get_all_leaves())
            return res
        
    def get_all_branchpts(self):
        if self.base==None or len(self.base.children)==0:
            return []
        else:
            res=[self.base]
            for child in self.base.children:
                res.extend(ExprTree(child).get_all_branchpts())
            return res

    @staticmethod
    def copy(tree:'TreePath'):
        def _copy(tree_base):
            if len(tree_base.children)==0:
                return ExprNode.copy(tree_base)
            else:
                return ExprNode.copy(tree_base,children=[_copy(child) for child in tree_base.children])
        if tree.base==None:
            return ExprTree(None)
        elif len(tree.base.children)==0:
            return ExprTree(ExprNode.copy(tree.base))
        else:
            return ExprTree(_copy(tree.base))

class Function(ExprNode):
    def __init__(self,name: str,value=None,children=[]):
        super(Function,self).__init__(name,value,children)
        pass
         
class Operator(Function):
    def __init__(self,name: str,value=None,children=[]):
        super(Operator,self).__init__(name,value,children)
        pass

class Var(ExprNode):
    def __init__(self,name: str,value=None):
        super(Var,self).__init__(name,value)
        pass
    
    
class Constant(ExprNode):
    def __init__(self,name: str,value=None):
        if value!=None:
            pass
        if name=="" and (type(self) is Int or type(self) is Fraction):
            super(Constant,self).__init__(name,value)
        elif name=="":
            raise AssertionError("Error 4: Reserved name")
        else:
            super(Constant,self).__init__(name,value)
            
class ImmutableConst(Constant):
    def __init__(self,name: str,value):
        assert value!=None, "Error 7: Immutable Constant must have a preset value"
        super(Constant,self).__init__(name,value)
        
    def __setattr__(self,s,v):
        if s=="value" and inspect.stack()[1].function!='__init__':
            raise AssertionError("Error 5: Cannot modify Immutable Constant")
        else:
            super(ImmutableConst,self).__setattr__(s,v)
    
    def set_value(self,value):
        raise AssertionError("Error 5: Cannot modify Immutable Constant")
    
    def __lt__(self,other):
        #print(type(other),get_all_subclasses(ImmutableConst))
        assert type(other) is ImmutableConst or type(other) in get_all_subclasses(ImmutableConst)
        return self.value<other.value

class Int(ImmutableConst):
    def __init__(self,value: int):
        assert type(value) is int, "parameters of type,{} must be an int".format(type(value))
        super(Int,self).__init__('',str(value))
        
    def __add__(self,other):
        if type(other) is Fraction: return other.__radd__(self)
        assert type(other) is Int,str(type(other))+" is not int"
        return Int(int(self.value)+int(other.value))
    
    def __neg__(self):
        return Int(-1*int(self.value))
    
    def __inv__(self):
        return Fraction(Int(1),Int(int(self.value)))
    
    def __sub__(self,other):
        if type(other) is Fraction: return other.__neg__().__radd__(self)
        return Int(int(self.value)+-int(other.value))
    
    def __abs__(self):
        return Int(abs(int(self.value)))
    
    def __mul__(self,other):
        if type(other) is Fraction: return other.__rmul__(self)
        assert type(other) is Int,str(type(other))+" is not Int"
        return Int(int(self.value)*int(other.value))
    
    def __truediv__(self,other):
        if type(other) is Fraction: return other.__rtruediv__(self)
        assert type(other) is Int,str(type(other))+" is not Int"
        return Int(int(self.value)//int(other.value))
    
    def __mod__(self,other):
        if type(other) is Fraction: return other.__rmod__(self)
        assert type(other) is Int,str(type(other))+" is not Int"
        return Int(int(self.value)%int(other.value))
    
    def __pow__(self,other):
        assert type(other) is Int,str(type(other))+" is not Int"
        return Int(int(self.value)**int(other.value))
class Fraction(ImmutableConst):
    def __init__(self,numerator: Int, denominator: Int=Int(1)):
        assert type(numerator) is Int and type(denominator) is Int, "parameters of type,{} and {} must be an Int".format(type(numerator),type(denominator))
        if denominator==Int(0):
            raise AssertionError("Error 201: Division by Zero")
        elif numerator==Int(0):
            self.num=numerator
            self.denom=Int(1)
        else:
            if denominator<Int(0):
                num=-numerator
                denom=-denominator
            else:
                num=numerator
                denom=denominator
            self.num=Int(int(num.value))/Int(int(Fraction._gcd(abs(num),denom).value))
            self.denom=Int(int(denom.value))/Int(int(Fraction._gcd(abs(num),denom).value))
        super(Fraction,self).__init__('',self.num.value+'/'+self.denom.value if self.denom!=Int(1) else self.num.value)


    def __repr__(self):
        return self.__class__.__name__+"(num="+str(self.num)+",denom="+str(self.denom)+")"
            #return False
    
    def __add__(self,other):
        if type(other) is Int:
            return Fraction(self.num+other*self.denom,self.denom)
        else:
            return Fraction(self.num*other.denom+other.num*self.denom,self.denom*other.denom)
        
    def __neg__(self):
        return Fraction(-self.num,self.denom)
        
    def __inv__(self):
        return Fraction(self.denom,self.num)
        
    def __radd__(self,other):
        return self.__add__(other)
    
    def __sub__(self,other):
        return self.__add__(-other)
    
    def __mul__(self,other):
        if type(other) is Int:
            return Fraction(self.num*other,self.denom)
        else:
            return Fraction(self.num*other.num,self.denom*other.denom)
        
    def __rmul__(self,other):
        return self.__mul__(other)
    
    def __truediv__(self,other):
        if type(other) is Int:
            return Fraction(self.num,self.denom*other)
        else:
            return Fraction(self.num*other.denom,self.denom*other.num)
    
    def __rtruediv__(self,other):
        return self.num.__inv__().__mul__(other)
    
    def num(self)->Int:
        return self.num
    
    def denom(self)->Int:
        return self.denom
    
    @staticmethod
    def _gcd(num1: Int,num2: Int)->Int:
        mini=num1
        if num2<num1:
            mini=num2
        while(mini>Int(1) and (num1%mini!=Int(0) or num2%mini!=Int(0))):
            mini-=Int(1)
        return mini

    @staticmethod
    def _lcm(num1: Int,num2: Int)->Int:
        maxi=num1
        if num2>num1:
            maxi=num2
        while(maxi<num1*num2 and (maxi%num1!=Int(0) or maxi%num2!=Int(0))):
            maxi+=Int(1)
        return maxi
    
    def is_proper_fraction(self)->bool:
        return abs(self.num)<self.denom
            
    def get_proper_fraction(self)->'Fraction':
        if self.is_proper_fraction():
            return self
        elif self.num<self.denom:
            return Fraction(self.num%self.denom-self.denom,self.denom)
        else:
            return Fraction(self.num%self.denom,self.denom)
        
    def truncate(self)->Int:
        if self.is_proper_fraction():
            return Int(0)
        elif self.num<self.denom:
            return Int(self.num//self.denom-1)
        else:
            return Int(self.num//self.denom)

if __name__=='__main__':
    a1=Int(2)
    a2=Int(3)
    a3=Var('a')
    plus1=Operator('+')
    mins1=Operator('-')
    plus1.add_child(a1)
    plus1.add_child(a2)
    mins1.add_child(plus1)
    mins1.add_child(a3)
    t=ExprTree(mins1)
    
    b1=Int(-1)
    b2=Constant('b')
    times1=Operator('*')
    times1.add_child(b1)
    times1.add_child(b2)
    sub_t=ExprTree(times1)
    
    a4=Var('a')
    a5=Constant('a')
    print(a1.value)
    print(t.replace(a3,sub_t))
    print(t)
    
    print(a4==a5)
    print(b1==a1)
    print(Fraction(Int(-1),Int(1)))
    print(b1==Fraction(Int(-1),Int(1)))
    print(a3==a4)
    print(b2==a5)
    a5=Int(-22)
    print(a4==a5)
    c5=ExprNode.copy(a5)
    print(a5,c5)
    print(Fraction(Int(-3)),ExprNode.copy(Fraction(Int(-3))))
    print(Fraction(Int(-3),Int(-2)),ExprNode.copy(Fraction(Int(-3),Int(-2))))
    print(a4,ExprNode.copy(a4))
    print(mins1,ExprNode.copy(mins1))
    print(Int(2)**Int(4))
    
    print(t)
    print(t.get_all_leaves())
    print(t.get_all_branchpts())
    pass