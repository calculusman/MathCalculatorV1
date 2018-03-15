'''
Created on Feb 12, 2018

@author: deriv
'''
import model.expression as expr
from kobi.lib import get_all_subclasses
from kobi.struct_lib import Stack
from model.expression import ExprTree,Int

class Arithmetic:
    arglist=['reduce']
    def __init__(self,cmd):
        self.cmd=cmd
    
    def _get_operator(self,oper: expr.Operator,arg1:expr.ExprNode,arg2:expr.ExprNode)->expr.ExprNode:
        if oper.name=="+":
            return arg1+arg2
        elif oper.name=="-":
            return arg1-arg2
        elif oper.name=="*":
            return arg1*arg2
        elif oper.name=="/":
            return arg1/arg2
        elif oper.name=="^":
            return arg1**arg2
        else:
            return arg1%arg2
    
    def _int_inspect(self,expr_tree):
        if min([child.is_leaf() for child in expr_tree.base.children])==1:
            return self._get_operator(expr_tree.base,expr_tree.base[0],expr_tree.base[1])
        else:
            if type(expr_tree.base) is expr.Operator:
                if expr_tree.base[0].is_leaf():
                    return self._get_operator(expr_tree.base,expr_tree.base[0],self._int_inspect(expr_tree.base,expr.ExprTree(expr_tree.base[1])))
                elif expr_tree.base[1].is_leaf():
                    return self._get_operator(expr_tree.base,self._int_inspect(expr.ExprTree(expr_tree.base[0])),expr_tree.base[1])
                else:
                    return self._get_operator(expr_tree.base,self._int_inspect(expr.ExprTree(expr_tree.base[0])),self._int_inspect(expr.ExprTree(expr_tree.base[1])))
                    
    def __call__(self,expr_tree):
        temp=expr.ExprTree.copy(expr_tree)
        if self.cmd=='reduce':
            if temp.base==None:
                return
            elif len(temp.base.children)==0:
                return temp
            elif min([type(leaf) is expr.ImmutableConst or type(leaf) in get_all_subclasses(expr.ImmutableConst) for leaf in temp.get_all_leaves()])==1 and min([type(branch_pt) is expr.Operator for branch_pt in temp.get_all_branchpts()])==1:
                return expr.ExprTree(self._int_inspect(temp))
            else:
                children=[child for child in temp.base.children]
                temp.base.remove_all_children()
                #print(children,temp.base.children)
                for child in children:
                    temp.base.add_child(self.__call__(expr.ExprTree(child)).base)
                #print('*',temp.base.children)
                return temp
        else:
            raise AttributeError("Incorrect number of parameters")
    
    def get_arg_count(self):
        return 1

if __name__=='__main__':
    import model.expression as expr
    import ui.parser as pars
    #t1: 8*(4-9)^4
    c1=expr.Int(-9)
    c2=expr.Int(4)
    c3=expr.Int(4)
    c4=expr.Int(8)
    o1=expr.Operator('+',None,[c1,c2])
    o2=expr.Operator('^',None,[c3,o1])
    o3=expr.Operator('*',None,[c4,o2])
    t1=expr.ExprTree(o3)
    print(pars.RParser(t1).output())
    
    a=Arithmetic('reduce')
    
    print('output:',pars.RParser(a(t1)).output())
    
    #t2: x*(4-9)^4
    c1=expr.Int(-9)
    c2=expr.Int(4)
    c3=expr.Int(4)
    c4=expr.Var('x')
    o1=expr.Operator('+',None,[c1,c2])
    o2=expr.Operator('^',None,[c3,o1])
    o3=expr.Operator('*',None,[c4,o2])
    t2=expr.ExprTree(o3)
    print(pars.RParser(t2).output())
    
    a=Arithmetic('reduce')
    
    print('output:',pars.RParser(a(t2)).output())
    
    #t3: 8*(4-9)^x
    c1=expr.Int(-9)
    c2=expr.Int(4)
    c3=expr.Var('x')
    c4=expr.Int(8)
    o1=expr.Operator('+',None,[c1,c2])
    o2=expr.Operator('^',None,[c3,o1])
    o3=expr.Operator('*',None,[c4,o2])
    t3=expr.ExprTree(o3)
    print(pars.RParser(t3).output())
    
    a=Arithmetic('reduce')
    
    print('output:',pars.RParser(a(t3)).output())
    
    
    #t4: 8*(x-9)^4
    c1=expr.Int(-9)
    c2=expr.Var('x')
    c3=expr.Int(4)
    c4=expr.Int(8)
    o1=expr.Operator('+',None,[c1,c2])
    o2=expr.Operator('^',None,[c3,o1])
    o3=expr.Operator('*',None,[c4,o2])
    t4=expr.ExprTree(o3)
    print(pars.RParser(t4).output())
    
    a=Arithmetic('reduce')
    
    print('output:',pars.RParser(a(t4)).output())
    
    
    #t5: sin(8-9)
    c1=expr.Int(-9)
    c2=expr.Int(8)
    o1=expr.Operator('+',None,[c1,c2])
    o2=expr.Function('asin',None,[o1])
    t5=expr.ExprTree(o2)
    print(pars.RParser(t5).output())
    
    a=Arithmetic('reduce')
    
    print('output:',pars.RParser(a(t5)).output())