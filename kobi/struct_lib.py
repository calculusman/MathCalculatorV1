'''
Created on Aug 18, 2017

@author: deriv
'''

from _functools import reduce
from kobi.lib import type_as_str,class_validation,get_all_subclasses
from math import ceil,log
from _collections import defaultdict
import inspect

class Stack:
    def __init__(self):
        self.items=[]
        
    def __repr__(self):
        return self.__class__.__name__+"("+str(reduce(lambda x,y:str(x)+','+str(y),self.items))+")" if len(self.items)!=0 else self.__class__.__name__+"()"
        
    def isEmpty(self):
        return self.items==[]
    
    def push(self, item):
        self.items.append(item)
        
    def pop(self):
        return self.items.pop()
    
    def peek(self,index:int=0):
        return self.items[len(self.items)-1-index]
    
    def size(self):
        return len(self.items)
    
    @staticmethod
    def copy(s: 'Stack'):
        res=Stack()
        for e in s.items:
            res.push(e)
        return res
    
    @staticmethod
    def toDequeue(s: 'Stack'):
        res=Dequeue()
        for e in s.items:
            res.append(e)
        return res
    
class Queue:
    def __init__(self):
        self.items=[]
        
    def __repr__(self):
        return self.__class__.__name__+"("+str(reduce(lambda x,y:str(x)+','+str(y),self.items))+")" if len(self.items)!=0 else self.__class__.__name__+"()"
        
    def isEmpty(self):
        return self.items==[]
    
    def enqueue(self, item):
        self.items.append(item)
        
    def dequeue(self):
        x=self.items[0]
        self.items.remove(x)
        return x
    
    def peek(self,index:int=0):
        return self.items[index]
    
    def size(self):
        return len(self.items)
    
    @staticmethod
    def copy(q: 'Queue'):
        res=Queue()
        for e in q.items:
            res.enqueue(e)
        return res
    
    @staticmethod
    def toDequeue(q: 'Queue'):
        res=Dequeue()
        for e in q.items:
            res.append(e)
        return res
    
class Dequeue:
    def __init__(self):
        self.items=[]
        
    def __repr__(self):
        return self.__class__.__name__+"("+str(reduce(lambda x,y:str(x)+','+str(y),self.items))+")" if len(self.items)!=0 else self.__class__.__name__+"()"
    
    def isEmpty(self):
        return self.items==[]
    
    def append(self,item):
        self.items.append(item)
    
    def appendleft(self,item):
        self.items.insert(0, item)
        
    def pop(self):
        return self.items.pop()
    
    def popleft(self):
        x=self.items[0]
        self.items.remove(x)
        return x
        
    def __getitem__(self,index: int):
        if index==0:
            return self.items[0]
        elif index==-1 or index==len(self.items)-1:
            return self.items[-1]
        else:
            raise IndexError("Invalid Index")
        
    def size(self):
        return len(self.items)
    
    @staticmethod
    def copy(d: 'Dequeue'):
        res=Dequeue()
        for e in d.items:
            res.append(e)
        return res
    
    @staticmethod
    def toStack(d: 'Dequeue'):
        res=Stack()
        for e in d.items:
            res.push(e)
        return res
    
    @staticmethod
    def toQueue(d: 'Dequeue'):
        res=Queue()
        for e in d.items:
            res.enqueue(e)
        return res

class TreeNode:
    def __init__(self,name=None,value=None,children: 'TreeNode'=[],debug:bool=False):
        #print(name,value,children)
        if type_as_str(name)!='str':
            raise AssertionError("Name must be of type str")
        self.name=name
        self.value=value
        self.children=[]
        if children!=None:
            for child in children:
                self.add_child(child)
        self.debug=debug
        
    def __repr__(self):
        if self.debug:
            return self.__class__.__name__+"(name="+self.name+",value="+str(self.value)+",children="+str(self.children)+")"
        else:
            return self.__str__()
    
    def __str__(self):
        if self.debug:
            return self.__repr__()
        else:
            return self.name+"("+str(self.value)+")"
    
    def __getattr__(self,s):
        if s=='name':
            return self.name
        elif s=='value':
            return self.value
        elif s=='children':
            return self.children
        elif s=='debug':
            return self.debug
        else:
            raise AttributeError("Attribute does not exist")
    
    def set_value(self,value):
        self.value=value
        
    def add_child(self,child: 'TreeNode'):
        self.children.append(child)
            
    def add_children(self,children):
        for child in children:
            self.add_child(child)
        
    def remove_child(self,child: 'TreeNode'):
        for i in range(len(self.children)-1,-1,-1):
            if id(self.children[i])==id(child):
                self.children.pop(i)
                 
    def remove_children(self,children):
        for child in children:
            self.remove_child(child)
            
    def remove_all_children(self):
        self.remove_children(self.children)
            
    def __eq__(self,other: 'TreeNode'):
        return self.value==other.value if type_as_str(other)=='TreeNode' else False
    
    @staticmethod
    def copy(node: 'TreeNode',**kargs):
        assert len(kargs.keys())==0 or 'children' in kargs.keys() and len(kargs.keys())==1,"Unknown key arguments"
        if len(kargs.keys())==0:
            return TreeNode(node.name,node.value,node.children)
        else:
            return TreeNode(node.name,node.value,[child for child in kargs['children']])
    
#@class_validation
class TreePath:
    def __init__(self,base_node:TreeNode):
        self.base=base_node
        if not self.__bool__():
            raise AssertionError("Not a valid Tree")
       
        
    def __bool__(self):
        return self.is_valid_tree(self.base,[]) and (self.base==None or type(self.base) is TreeNode or type(self.base) in get_all_subclasses(TreeNode))
        
    def is_valid_tree(self,node:TreeNode,descendent:list,s:Stack=Stack()):
        if len(descendent)!=0 and reduce(lambda x,y: x or y,map(lambda z: z is node,descendent)):
            return False
        elif node==None or (len(node.children)==0 and s.isEmpty()):
            return True
        elif len(node.children)==0:
            descendent.append(node)
            e=s.pop()
            return self.is_valid_tree(e,descendent,s)
        elif len(node.children)==1:
            descendent.append(node)
            return self.is_valid_tree(node.children[0],descendent,s)
        else:
            descendent.append(node)
            for e in node.children[1:]:
                s.push(e)
            return self.is_valid_tree(node.children[0],descendent,s)
            
    def get_descendents(self,node:TreeNode,descendents:list,s:Stack=Stack())->list:
        if node==None:
            return []
        descendents.append(node)
        if len(node.children)==0 and s.isEmpty():
            return descendents[1:]
        elif len(node.children)==0:
            e=s.pop()
            return self.get_descendents(e,descendents,s)
        elif len(node.children)==1:
            return self.get_descendents(node.children[0],descendents,s)
        else:
            for e in node.children[1:]:
                s.push(e)
            return self.get_descendents(node.children[0],descendents,s)

    def get_all_nodes(self):
        return [self.base]+self.get_descendents(self.base,[]) if self.base!=None else []
    
    def __contains__(self,e):
        #print('-start-')
        #print(e,self.get_all_nodes(),reduce(lambda x,y: x or y, map(lambda z: type(e).__eq__(e,z),self.get_all_nodes())))
        #print([b for b in map(lambda z: type(e).__eq__(e,z),self.get_all_nodes())])
        #print('-end-')
        return reduce(lambda x,y: x or y, map(lambda z: z==e,self.get_all_nodes()))
    
    def get_node(self,node:TreeNode):
        for n in self.get_all_nodes():
            if n==node:
                return n
        return None
    
    def get_base_node(self):
        return self.base
    
    def __str__(self):
        return self.get_str(self.base)[1:] if self.base!=None else "None"
        
    def get_str(self,node:TreeNode,layer: int=0,s:Stack=Stack())->str:
        res="\n"+"   "*layer+str(node)
        if len(node.children)==0 and s.isEmpty():
            return res
        elif len(node.children)==0:
            e=s.pop()
            return res+self.get_str(e[0],e[1],s)
        elif len(node.children)==1:
            return res+self.get_str(node.children[0],layer+1,s)
        else:
            for e in node.children[1:]:
                s.push((e,layer+1))
            return res+self.get_str(node.children[0],layer+1,s)
        
    def get_path_from_base(self,dest_node:TreeNode)->list:
        if len(self.get_all_nodes())==0:
            raise AssertionError("Node not in Tree")
        if not reduce(lambda x,y: x or y,map(lambda z: z is dest_node,self.get_all_nodes())):
            raise AssertionError("Node not in Tree")
        return self.get_path_from_base2(self.base,dest_node,Stack(),Stack())
    
    def get_path_from_base2(self,curr_node:TreeNode,dest_node:TreeNode,path:Stack,s:Stack):
        path.push(curr_node)
        if curr_node==dest_node:
            final_path=[]
            while not path.isEmpty():
                final_path.insert(0, path.pop())
            return final_path
        elif len(curr_node.children)==0:
            e=s.pop()
            return self.get_path_from_base2(e[0],dest_node,e[1],s)
        elif len(curr_node.children)==1:
            return self.get_path_from_base2(curr_node.children[0],dest_node,path,s)
        else:
            for e in curr_node.children[1:]:
                s.push((e,Stack.copy(path)))
            return self.get_path_from_base2(curr_node.children[0],dest_node,path,s)
        
    def get_path(self,start:TreeNode,end:TreeNode):
        if len(self.get_all_nodes())==0:
            raise AssertionError("Node not in Tree")
        if not reduce(lambda x,y: x or y,map(lambda z: z is start,self.get_all_nodes())) or not reduce(lambda x,y: x or y,map(lambda z: z is end,self.get_all_nodes())):
            raise AssertionError("Node not in Tree")
        base_to_start=self.get_path_from_base2(self.base,start,Stack(),Stack())
        base_to_end=self.get_path_from_base2(self.base,end,Stack(),Stack())
        path=[]
        i_min=0
        while (i_min<len(base_to_end) and i_min<len(base_to_start) and base_to_end[i_min]==base_to_start[i_min]):
            i_min+=1
        i_min-=1
        if i_min+1<len(base_to_end):
            for i in range(i_min+1,len(base_to_end)):
                path.append(base_to_end[i])
        for i in range(i_min,len(base_to_start)):
            path.insert(0,base_to_start[i])
        return path
                
    def get_path_length(self,start:TreeNode,end:TreeNode):
        return len(self.get_path(start,end))-1
    
    def get_height(self):
        return max(map(lambda p: self.get_path_length(self.base,p),self.get_all_nodes())) if self.base!=None else 0
    
    def get_width(self):
        return max(map(lambda p,q:self.get_path_length(p,q),[self.get_all_nodes()[i//len(self.get_all_nodes())] for i in range(len(self.get_all_nodes())**2)],self.get_all_nodes()*len(self.get_all_nodes()))) if self.base!=None else 0
    
    def get_subtree(self,node:TreeNode):
        n=self.get_node(node)
        return TreePath(n) if n!=None else None
        
    def _eq_helper(self,other):
            if not type(other) is TreePath:
                return False
            if len(self.get_all_nodes())==0 and len(other.get_all_nodes())==0:
                return True
            elif len(self.get_all_nodes())==0 or len(other.get_all_nodes())==0:
                return False
            elif len(self.get_all_nodes())==1 and len(other.get_all_nodes())==1:
                return self.base==other.base
            elif len(self.get_all_nodes())==1 or len(other.get_all_nodes())==1:
                return False
            elif self.base!=other.base:
                return False
            else:
                possible=[]
                for i in range(len(self.base.children)):
                    flag=False
                    e_tree=TreePath(self.base.children[i])
                    possible.append((e_tree,[]))
                    for e_other in other.base.children:
                        if self.base.children[i]==e_other:
                            flag=True
                        e_other_tree=TreePath(e_other)
                        possible[i][1].append(e_other_tree)
                    if not flag:
                        return False
                unchecked_keys=[t[0] for t in possible]
                for i in range(len(unchecked_keys)):
                    flag=False
                    possible_copy=[tree_other for tree_other in possible[i][1]]
                    for tree_other in possible_copy:
                        #print(unchecked_keys[i]==tree_other)
                        if not flag and unchecked_keys[i]==tree_other:
                            flag=True
                            for j in range(i+1,len(unchecked_keys)):
                                possible[j][1].remove(tree_other)
                    if not flag:
                        return False
                return len(possible[-1][1])==1
    
    def __eq__(self,other):
        return self._eq_helper(other)
    
    @staticmethod
    def copy(tree:'TreePath'):
        def _copy(tree_base):
            if tree.get_height()==1:
                return TreeNode.copy(tree_base)
            else:
                return TreeNode.copy(tree_base,children=[_copy(child) for child in tree_base.children])
        if tree.get_height()==0:
            return TreePath(None)
        elif tree.get_height()==1:
            return TreePath(TreeNode.copy(tree.base))
        else:
            return TreePath(_copy(tree.base))
class Node:
    def __init__(self,name=None,value=None):
        if type_as_str(name)!='str':
            raise AssertionError("Name must be of type str")
        self.name=name
        self.value=value
        
    def __repr__(self):
        return self.__class__.__name__+"(name="+self.name+",value="+str(self.value)+")"
        
    def get_name(self):
        return self.name
    
    def get_value(self):
        return self.value
    
    def set_value(self,value):
        self.value=value
        

class Tree:
    def __init__(self,name, base_node: Node=None, tree_type: int=0):
        if type_as_str(name)!='str':
            raise AssertionError("Name must be of type str")
        self.name=name
        self.basenode=base_node
        self.nodelist=[]
        if self.basenode!=None:
            self.nodelist.append(self.basenode)
            self.height=1
        else:
            self.height=0
        if tree_type==0:
            self.ismutable=True
            self.treetype=1
        else:
            self.ismutable=False
            self.treetype=tree_type
        
    def __repr__(self):
        return self.__class__.__name__+"(name="+self.name+",nodelist=["+str(reduce(lambda x,y:str(x)+','+str(y),self.nodelist))+"])" if len(self.nodelist)!=0 else self.__class__.__name__+"(name="+self.name+",nodelist=[])"
        '''
    def __str__(self):
        return ""
        '''

    def get_name(self):
        return self.name
    
    def get_base_node(self):
        return self.basenode
    
    def get_tree_type(self):
        return self.treetype
    
    def get_index(self,n:Node):
        for i in range(len(self.nodelist)):
            if n is self.nodelist[i]:
                return i
        raise IndexError("Node not found")
    
    def get_height(self):
        return self.height
    
    ''' Tree Analysis Variables and Domains
    treetype: {x->Z | x>=0}
    level: {x->Z | x>0}
    pos: {x->Z | x>=0}
    '''
            
    @staticmethod
    def get_child_pos(treetype:int,parent_pos:int,rel_pos:int)->int:
            return treetype*parent_pos+1+rel_pos
        
    @staticmethod
    def get_first_pos(treetype:int,level:int)->int:
        return (treetype**level-1)/(treetype-1) if treetype-1!=0 else level
        
    @staticmethod
    def get_last_pos(treetype:int,level:int)->int:
        return (treetype**level-1)*treetype/(treetype-1) if treetype-1!=0 else level
        
    @staticmethod
    def get_level(treetype:int,pos:int)->int:
        return ceil(log((treetype-1)/treetype*pos+1)/log(treetype)) if log(treetype)!=0 else pos
    
    @staticmethod
    def get_pos_per_level(treetype:int,level:int)->int:
        return treetype**level
    
    def add_tree_type(self,tree_type_ext:int):
        if tree_type_ext<0:
            raise AssertionError("Requested tree base is less than or equal to the current tree base")
        else:
            temp=self.nodelist
            self.nodelist=[]
            k=0
            rowtemp=[]
            for i in range(self.height):
                if rowtemp==[] or not reduce(lambda x,y: x or y,map(lambda z: z==None,rowtemp)):
                    rowtemp=[]
                    for j in range(Tree.get_pos_per_level(self.treetype, i)):
                        rowtemp.append(temp[k])
                        k+=1
                        
                    if i!=0:
                        for j in range(tree_type_ext):
                            rowtemp.append(None)
                else:
                    rowtemp2=[e for e in rowtemp]
                    rowtemp=[]
                    j2=0
                    for j in range(self.treetype+tree_type_ext):
                        if j2<len(rowtemp2) and rowtemp2[j2]!=None:
                            for e in rowtemp2:
                                rowtemp.append(e)
                        else:
                            for e in rowtemp2:
                                rowtemp.append(None)
                        j2+=1
                            
                    for j in range(Tree.get_pos_per_level(self.treetype+tree_type_ext, i)):
                        if rowtemp[j]!=None:
                            rowtemp[j]=temp[k]
                            k=k+1
                
                for e in rowtemp:
                    self.nodelist.append(e)
        self.treetype+=tree_type_ext

    def add_level(self):
        for i in range(self.treetype**self.height):
            self.nodelist.append(None)
        self.height+=1
        
    def remove_level(self):
        if self.basenode!=None:
            for i in range(self.treetype**(self.height-1)):
                self.nodelist.pop()
            self.height-=1
            if self.height==0:
                self.basenode=None
        else:
            raise Exception("Cannot remove from an empty tree")
    
    def set_child(self,n:Node,parent:Node=None,pos:int=0):
        if n in self.nodelist:
            raise Exception("Cannot add the same node twice")
        if n!=None:
            if self.basenode==None and parent==None:
                self.basenode=n
                self.nodelist.append(self.basenode)
                self.height+=1
            elif self.basenode==None:
                raise Exception("No parent node exists")
            else:
                minpos=Tree.get_child_pos(self.treetype,self.get_index(parent),0)
                newpos=Tree.get_child_pos(self.treetype,self.get_index(parent),pos)
                maxpos=Tree.get_child_pos(self.treetype,self.get_index(parent),self.treetype-1)
                if newpos<minpos or newpos>maxpos:
                    if self.ismutable and pos>=0:
                        self.add_tree_type(newpos-maxpos)
                    else:
                        raise IndexError("No such position exists")
                
                if newpos>=len(self.nodelist):
                    self.add_level()
                self.nodelist[Tree.get_child_pos(self.treetype,self.get_index(parent),pos)]=n
        else:
            print("Cannot remove from tree")
            print("Author is currently working on this feature")
        

if __name__=='__main__':
    '''
    s=Stack()
    s.push('a')
    s.push('b')
    s.push('c')
    print(s.pop())
    print(s.pop())
    s.push('d')
    s.push('e')
    print(s.peek()+str(s.size()))
    print(s)
    print(Stack.copy(s))
    print(Stack.toDequeue(s))
    
    q=Queue()
    q.enqueue('a')
    q.enqueue('b')
    q.enqueue('c')
    print(q.dequeue())
    print(q.dequeue())
    q.enqueue('d')
    q.enqueue('e')
    print(q.peek()+str(q.size()))
    print(q)
    print(Queue.copy(q))
    print(Queue.toDequeue(q))
    
    d=Dequeue()
    d.append('a')
    d.append('b')
    d.append('c')
    d.appendleft('d')
    d.appendleft('e')
    print(d.popleft())
    print(d.pop())
    print(d[0]+d[-1]+str(d.size()))
    print(d)
    print(Dequeue.copy(d))
    print(Dequeue.toStack(d))
    print(Dequeue.toQueue(d))
    '''
    
    '''
    g3=TreeNode('3',3)
    g2=TreeNode('2',2)
    g1=TreeNode('1',1,[g2,g3])
    g=TreeNode('0',0,[g1])
    
    g3.add_child(g1)
    TreePath(g) #raises AssertionError
    '''
    '''
    g3=TreeNode('3',3)
    g2=TreeNode('2',2)
    g1=TreeNode('1',1,[g2,g3])
    g=TreeNode('0',0,[g1])
    T1=TreePath(g)
    g3.add_child(g1)
    print(T1.get_descendents(g)) #raises kobi.lib.InternalClassException
    '''
    '''
    t14=TreeNode('13',13)
    t13=TreeNode('12',12)
    t12=TreeNode('11',11)
    t11=TreeNode('10',10)
    t10=TreeNode('9',9,[t11,t12,t14])
    t9=TreeNode('8',8)
    t8=TreeNode('7',7)
    t7=TreeNode('6',6,[t8,t9])
    print(t7.name)
    print(t7)
    t6=TreeNode('5',5)
    t5=TreeNode('4',4,[t10,t13])
    t4=TreeNode('3',3,[t6])
    t3=TreeNode('2',2,[t7])
    t2=TreeNode('1',1,[t4,t5])
    t=TreeNode('0',0,[t2,t3])
    print('*')
    T=TreePath(t)
    print(T.__bool__())
    print(T)
    print(T.get_all_nodes())
    print(T.get_path(t,t7))
    print(T.get_path(t14,t8))
    print(T.get_path(t10,t13))
    print(T.get_height())
    print(T.get_width())
    '''
    a3=TreeNode('3',3)
    a20=TreeNode('2',2)
    a21=TreeNode('2',2,[a3])
    a4=TreeNode('4',4)
    a1=TreeNode('1',1,[a20,a4,a21])
    
    b22=TreeNode('2',2) #adding this node to b1 (b21 is added) should make T1==T2 False
    b3=TreeNode('3',3)
    b20=TreeNode('2',2,[b3])
    b4=TreeNode('4',4)
    b21=TreeNode('2',2) #removing this node from b1 (b22 is not added) should make T1==T2 False
    b1=TreeNode('1',1,[b20,b4,b21])
    T1=TreePath(a1)
    T2=TreePath(b1)
    #print(T1)
    #print(T2)
    #print('*',T1==T2)
    #print(type(T1))
    
    T2_=TreePath.copy(TreePath(b1))
    print(T2_)
    #T2_.base.children=[]
    #print(T2)
    print('**********')
    print(b22 in T2_)
    #print(b22==b20)
    '''
    tree=Tree('')
    print(tree)
    base=Node('0',0)
    tree.set_child(base)
    print(tree)
    e=Node('1',1)
    tree.set_child(e,base)
    print(tree)
    tree.set_child(Node('2',2),e)
    print(tree)
    e1=Node('3',3)
    tree.set_child(e1,base,1)
    print(tree)
    tree.set_child(Node('4',4),e,1)
    print(tree)
    tree.set_child(Node('5',5),e1)
    print(tree)
    e2=Node('6',6)
    tree.set_child(e2,e1,1)
    print(tree)
    tree.set_child(Node('7',7),e2,2)
    print(tree)
    '''