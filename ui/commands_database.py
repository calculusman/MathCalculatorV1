'''
Created on Feb 2, 2018

@author: deriv
'''
import model.expression
import algebrapkg.arithmetic
from kobi.struct_lib import TreePath
from model.expression import ExprTree, ExprNode,Var,Constant
from _functools import reduce
from kobi.lib import InternalClassException
database={}
var_dict={}
const_dict={}

class interface:
    arglist=['setV','setC','get','del']
    def __init__(self,cmd: str):
        self.cmd=cmd
        
    def _is_consistent(self,final_dict:dict,node_item:tuple)->bool:
        tree_nodes=[]
        #print(final_dict,node_item)
        final_dict_dependency={k:set() for k in final_dict.keys()}
        final_dict_keys=[k for k in final_dict.keys()]
        for i in range(len(final_dict_keys)):
            for j in range(i+1,len(final_dict_keys)):
                t=self._substitute(final_dict_keys[i],final_dict[final_dict_keys[i]],final_dict_keys[j],final_dict[final_dict_keys[j]])
                if t[2]==1:
                    final_dict_dependency[final_dict_keys[j]].add(final_dict_keys[i])
                elif t[2]==0:
                    final_dict_dependency[final_dict_keys[i]].add(final_dict_keys[j])
        #print('temp',final_dict_dependency)
        
        new_node_item=(node_item[0],node_item[1])
        node_item_dependency=(node_item[0],set())
        for i in range(len(final_dict_keys)):
            t=self._substitute(final_dict_keys[i],final_dict[final_dict_keys[i]],new_node_item[0],new_node_item[1])
            if t[2]==1:
                node_item_dependency[1].add(final_dict_keys[i])
            elif t[2]==0:
                final_dict_dependency[final_dict_keys[i]].add(node_item_dependency[0])
        #print('check1',node_item_dependency,final_dict_dependency)    
        
        for i in range(len(final_dict_keys)):
            for e in final_dict_dependency[final_dict_keys[i]]:
                if e in final_dict_keys:
                    final_dict_dependency[final_dict_keys[i]]=final_dict_dependency[final_dict_keys[i]].union(final_dict_dependency[e])
            if node_item_dependency[0] in final_dict_dependency[final_dict_keys[i]]:
                final_dict_dependency[final_dict_keys[i]]=final_dict_dependency[final_dict_keys[i]].union(node_item_dependency[1])
        for e in node_item_dependency[1]:
            node_item_dependency=(node_item_dependency[0],node_item_dependency[1].union(final_dict_dependency[e]))
            
        #print('check2',node_item_dependency,final_dict_dependency)
        final_dict_dependency.update({node_item_dependency[0]:node_item_dependency[1]})
        
        
        lookup_dict={}
        
        new_member=ExprNode(node_item_dependency[0],None,node_item_dependency[1])
        tree_nodes.append(new_member)
        #print(node_item_dependency[0])
        lookup_dict[node_item_dependency[0]]=new_member
        
        for i in range(len(final_dict_keys)):
            #print('*',final_dict_keys[i])
            n=ExprNode(final_dict_keys[i],None)
            lookup_dict[final_dict_keys[i]]=n
            tree_nodes.append(n)
        #print('lookup_dict',lookup_dict)
        
        for k in lookup_dict.keys():
            #print('***',k,lookup_dict[k])
            for e in final_dict_dependency[k]:
                if e in lookup_dict.keys() and (len(lookup_dict[k].children)==0 or reduce(lambda x,y: x and y,map(lambda z:not e in final_dict_dependency[z],[child.name for child in lookup_dict[k].children]))):
                    for child in lookup_dict[k].children:
                        #print('testing',child.name)
                        if child.name in final_dict_dependency[e]:
                            #print('removing',child.name)
                            lookup_dict[k].remove_child(child)
                    lookup_dict[k].add_child(lookup_dict[e])
            
        #print('tree_nodes',tree_nodes)
        #for t in tree_nodes:
            #print('**',t)
            #print(t.children)
        for i in range(len(tree_nodes)):
            base_node=tree_nodes[i]
            try:
                t=ExprTree(base_node)
            except (InternalClassException,AssertionError):
                return False
        return True
    
    def _substitute(self,param1:str,arg1: ExprTree,param2:str,arg2: ExprTree)->tuple:
        param1_node=None
        if param1 in [k for k in const_dict.keys()]:
            param1_node=model.expression.Constant(param1)
        else:
            param1_node=model.expression.Var(param1)
        
        param2_node=None
        if param2 in [k for k in const_dict.keys()]:
            param2_node=model.expression.Constant(param2)
        else:
            param2_node=model.expression.Var(param2)
            
        print(param1_node,param2_node,param2_node in arg1, param1_node in arg2)
        if arg1==None or arg2==None:
            return (arg1,arg2,-1)
        elif param1_node in arg2 and param2_node in arg1:
            raise AssertionError("Error 7: Circular reasoning")
        elif param1_node in arg2:
            return (arg1,arg2.replace(param1_node,arg1),1)
        elif param2_node in arg1:
            return (arg1.replace(param2_node,arg2),arg2,0)
        else:
            return (arg1,arg2,-1)
        
    def _build_expr_tree(self,final_dict:dict,name):
        print(final_dict,name)
        other_keys=[k for k in final_dict.keys()]
        other_keys.remove(name)
        if other_keys==None:
            other_keys=[]
        repeat=True
        while repeat:
            print('hi')
            repeat=False
            print(other_keys)
            for k in other_keys:
                t=self._substitute(k,final_dict[k],name,final_dict[name])
                if t[2]==1:
                    repeat=True
                    final_dict[name]=t[1]
                    
        return final_dict[name]
        
    def __call__(self,name,exprTree=None):
        if self.cmd=='setV' and exprTree!=None:
            final_dict={k:v for k,v in const_dict.keys()}
            final_dict.update(var_dict)
            if name in final_dict.keys():
                final_dict.pop(name)
            assert self._is_consistent(final_dict,(name,exprTree)), "Error 7: Circular Reasoning"
            if name in const_dict:
                del const_dict[name]
            var_dict[name]=exprTree
            print(var_dict[name])
            return
        elif self.cmd=='setC' and exprTree!=None:
            final_dict={k:v for k,v in const_dict.keys()}
            final_dict.update(var_dict)
            if name in final_dict.keys():
                final_dict.pop(name)
            assert self._is_consistent(final_dict,(name,exprTree)), "Error 7: Circular Reasoning"
            if name in var_dict:
                del const_dict[name]
            var_dict[name]=exprTree
            return
        elif self.cmd=='get' and exprTree==None:
            if name in const_dict or name in var_dict:
                final_dict={k:v for k,v in const_dict.items()}
                final_dict.update(var_dict)
                
                return self._build_expr_tree(final_dict,name)
            else:
                raise KeyError(name+" not found")
        elif self.cmd=='del' and exprTree==None:
            if name in const_dict:
                del const_dict[name]
            elif name in var_dict:
                del var_dict[name]
            else:
                raise KeyError(name+" not found")
            return
        else:
            raise AttributeError("Incorrect number of parameters")

    def get_arg_count(self):
        if self.cmd=='setV':
            return 2
        elif self.cmd=='setC':
            return 2
        elif self.cmd=='get':
            return 1
        elif self.cmd=='del':
            return 1




database['setV']=interface('setV')
database['setC']=interface('setC')
database['get']=interface('get')
database['del']=interface('del')

#database['reduce']=
#database['expand']=
#database['factor']=

