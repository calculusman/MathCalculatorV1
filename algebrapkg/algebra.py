'''
Created on Mar 12, 2018

@author: deriv
'''
import model.expression as expr
from algebrapkg.arithmetic import Arithmetic
from model.expression import ExprNode,ExprTree,ImmutableConst,Int,Operator
from kobi.lib import get_all_subclasses
from kobi.struct_lib import TreePath


def get_value(oper_node)->int:
    oper=oper_node.name
    if oper=='+' or oper=='-':
        return 2
    elif oper=='*' or oper=='/':
        return 3
    elif oper=='^':
        return 4
    else:
        raise AssertionError("Error 2: Not a valid operator")

class Term(ExprNode):
    def __init__(self,expr:ExprTree,const:ImmutableConst=Int(1)):
        assert type(expr) is ExprTree, "term must be of type ExprTree, not "+str(type(expr))
        assert type(const) is ImmutableConst or type(const) in get_all_subclasses(ImmutableConst), "term must be of type ExprTree, not "+str(type(expr))
        self.term=expr
        self.const=const
        super(Term,self).__init__('Term')
        
    def __str__(self):
        return "{}:\t constant=[{}] term=[{}]".format("Term",self._simple_parser(ExprTree(self.const)),self._simple_parser(self.term))
    
    def _simple_parser(self,t:ExprTree):
        def _recurse_parser(base:ExprNode,parent:ExprNode):
            if base.is_leaf() and type(base) is ImmutableConst or type(base) in get_all_subclasses(ImmutableConst):
                return base.value
            elif base.is_leaf():
                return base.name
            else:
                if type(base) is expr.Function:
                    return "{}({})".format(base.name,";".join([_recurse_parser(child,base) for child in base.children]))
                else:
                    if parent!=None and get_value(base)<get_value(parent):
                        return "({}{}{})".format(_recurse_parser(base.args[0],base),base.name,_recurse_parser(base.args[1],base))
                    else:
                        return "{}{}{}".format(_recurse_parser(base.args[0],base),base.name,_recurse_parser(base.args[1],base))
        return _recurse_parser(t.base,None)
        
    def get_degree(self):
        return
        
    def get_dim(self):
        return
        
class TermTree(ExprTree):
    def __init__(self,base):
        self.base_term=None
        base_copy=ExprTree.copy(ExprTree(base)).base
        current_node=base_copy
        if current_node!=None and current_node.is_leaf():
            base_copy=Term(ExprTree(current_node))
        elif current_node!=None and type(current_node) is Operator and get_value(current_node)>get_value(Operator('+')) and max([type(child) is expr.Function or type(child) is Operator and get_value(child)==get_value(Operator('+')) for child in [n for n in ExprTree(current_node).get_descendents(current_node,[])]])==0:
            base_copy=Term(ExprTree(current_node))
        elif current_node!=None:
            descendents=[(child,current_node) for child in current_node.children]
            t=descendents.pop()
            base_copy=current_node
            current_node=t[0]
            current_parent=t[1]
            is_last=False
            while (len(current_node.children)!=0 or len(descendents)!=0) and not is_last:
                if len(current_node.children)==0 and len(descendents)==0:
                    is_last=True
                if current_node.is_leaf():
                    current_parent.remove_child(current_node)
                    current_parent.add_child(Term(ExprTree(current_node)))
                elif type(current_node) is expr.Function:
                    for child in current_node.children:
                        descendents.append((child,current_node))
                else:
                    all_descendents=[n for n in ExprTree(current_node).get_descendents(current_node,[])]
                    if get_value(current_node)>get_value(Operator('+')) and max([type(child) is expr.Function or type(child) is Operator and get_value(child)==get_value(Operator('+')) for child in all_descendents])==0:
                        current_parent.remove_child(current_node)
                        current_parent.add_child(Term(ExprTree(current_node)))
                    else:
                        for child in current_node.children:
                            descendents.append((child,current_node))
                if not len(descendents)==0:
                    t=descendents.pop()
                    current_node=t[0]
                    current_parent=t[1]
                else:
                    is_last=True
                print(current_node,current_parent,current_parent.children)
        self.base=base_copy
        super(TermTree,self).__init__(self.base)
    
    def get_degree(self):
        return 
    
    def get_dim(self):
        return
    
    
class Algebra:
    arglist=['expand','factor']
    def __init__(self,cmd):
        self.cmd=cmd
        
    
    
        
    def __call__(self,expr_tree):
        temp=expr.ExprTree.copy(expr_tree)
        a=Arithmetic('reduce')
        temp=a(temp)
        if self.cmd=='expand':
            pass
        elif self.cmd=='factor':
            pass
        else:
            raise AttributeError("Incorrect number of parameters")
        
        
if __name__=='__main__':
    import ui.parser as pars
    p=pars.Parser('-4*x^2-3*cos(1/x)')
    t=p.output()
    r=pars.RParser(t)
    print(r.output())
    tt=TermTree(t.base)
    print(tt)
    
    p2=pars.Parser('-2*(x+1)^3-6*asin(1-4*x^2)')
    t2=p2.output()
    r2=pars.RParser(t2)
    print(r2.output())
    tt2=TermTree(t2.base)
    print(tt2)
    