'''
Created on Aug 15, 2017

@author: deriv
'''
import model.expression
from builtins import str, range
from kobi.struct_lib import Stack,Queue, TreePath
from kobi.lib import type_as_str
from model import function_database
from model.expression import ExprTree


class Parser():
    def __init__(self,raw:str):
        self.string=Parser._add_padding(self._modify_raw_str(raw.strip()))
        self.tree=None
        
        #print(self.string)
        s=Parser.get_tokens(self.string)
        #print(s)
        q=Parser.str_to_queue(s)
        #print(q)
        q2=Parser.get_postfix(q)
        #print(q2)
        t=Parser.get_expr_tree(q2)
        #print('result:\n'+str(t))
        self._result=t
    @staticmethod
    def _add_padding(raw:str):
        for i in range(len(raw)-2,-1,-1):
            if raw[i]=='-' and raw[i+1].isalpha() and (i==0 or i>0 and (Parser.is_binary_operator(raw[i-1]) or Parser.is_separator(raw[i-1]) and raw[i-1]!=')')):
                raw=raw[:i]+'(-1)*'+raw[i+1:]
            elif raw[i]=='-' and raw[i+1].isalpha():
                raw=raw[:i]+'+(-1)*'+raw[i+1:]
        return raw

    @staticmethod
    def is_binary_operator(char: str)->bool:
        return char=='+' or char=='-' or char=='*' or char=='/' or char=='^'
    
    @staticmethod
    def is_separator(char: str)->bool:
        return char=='(' or char==')' or char=='[' or char==']' or char=='{' or char=='}' or char==';'
        
    @staticmethod
    def get_value(oper: str)->int:
        if oper=='+' or oper=='-':
            return 2
        elif oper=='*' or oper=='/':
            return 3
        elif oper=='^':
            return 4
        else:
            raise AssertionError("Error 2: Not a valid operator")
        
    @staticmethod
    def get_tokens(string: str)->str:
        paren_stack=Stack()
        temp_str=''
        curr_type=''
        is_negative=False
        func_name=''
        for i in range(len(string)):
            char=string[i:i+1]
            if char.isdigit() and curr_type!='digit':
                curr_type='digit'
                if is_negative:
                    temp_str+=','+curr_type+'=-'+char
                    is_negative=False
                else:
                    temp_str+=','+curr_type+'='+char
            elif char.isalpha() and curr_type!='alpha':
                curr_type='alpha'
                temp_str+=','+curr_type+'='+char
            elif char=='-' and (curr_type=='digit' or string[i+1:i+2].isalpha()):
                curr_type='operator'
                temp_str+=','+curr_type+'='+char
            elif char=='-':
                is_negative=True
            elif Parser.is_binary_operator(char) and curr_type!='operator':
                curr_type='operator'
                temp_str+=','+curr_type+'='+char
            elif Parser.is_separator(char):
                if char=='(' and curr_type=='alpha':
                    j=len(temp_str)-1
                    while temp_str[j:j+1]!=',' and j>0:
                        j=j-1
                    c=len('alpha')
                    temp_str=temp_str[:j+1]+'funcB'+temp_str[j+c+1:]
                    paren_stack.push('func'+temp_str[j+c+1:])
                    func_name=temp_str[j+c+2:]
                elif char=='(':
                    temp_str+=',parenB='
                    paren_stack.push('(')
                elif char==';':
                    temp_str+=',funcD='+func_name
                else:
                    if char==')' and not paren_stack.isEmpty() and paren_stack.peek()[:4]=='func':
                        temp=paren_stack.pop()
                        temp_str+=','+temp[:4]+"E"+temp[4:]
                        if paren_stack.isEmpty():
                            func_name=''
                        else:
                            func_name=paren_stack.peek()[5:]
                    elif char==')':
                        temp=paren_stack.pop()
                        temp_str+=',parenE='
                    else:
                        temp_str+=','+char
                
                curr_type=char
            elif not char.isdigit() and not char.isalpha() and not Parser.is_binary_operator(char) and not Parser.is_separator(char):
                raise SyntaxError("Error 1: Unknown character")
            else:
                temp_str+=char
        temp_str=temp_str[1:]
        
        return temp_str
        
    @staticmethod
    def str_to_queue(string: str)->str:
        q=Queue()
        temp_tuple=["",""]
        temp_str=''
        string2=string+","
        for i in range(len(string2)):
            if string2[i]=='=':
                temp_tuple[0]=temp_str
                temp_str=''
            elif string2[i]==',':
                temp_tuple[1]=temp_str
                temp_str=''
                q.enqueue(temp_tuple)
                temp_tuple=["",""]
            else:
                temp_str+=string2[i]
        return q
                
    @staticmethod
    def get_postfix(q: Queue)->Queue:
        oper_stack=Stack()
        end_q=Queue()
        
        while not q.isEmpty():
            e=q.dequeue()
            if e[0]=='digit' or e[0]=='alpha':
                end_q.enqueue(e)
            elif e[0]=='parenB':
                oper_stack.push(e)
            elif e[0]=='parenE':
                if oper_stack.isEmpty():
                    raise AssertionError("Error 3: Mismatched parenthesis")
                f=oper_stack.pop()
                while f[0]!='parenB':
                    end_q.enqueue(f)
                    if oper_stack.isEmpty():
                        raise AssertionError("Error 3: Mismatched Parenthesis")
                    f=oper_stack.pop()
            elif e[0]=='operator':
                if oper_stack.isEmpty():
                    oper_stack.push(e)
                else:
                    if oper_stack.peek()[0]!='operator' or Parser.get_value(e[1])>Parser.get_value(oper_stack.peek()[1]):
                        oper_stack.push(e)
                    else:
                        while not oper_stack.isEmpty() and oper_stack.peek()[0]=='operator' and Parser.get_value(e[1])<=Parser.get_value(oper_stack.peek()[1]):
                            end_q.enqueue(oper_stack.pop())
                        oper_stack.push(e)
            elif e[0]=='funcB':
                oper_stack.push(e)
                end_q.enqueue(e)
            elif e[0]=='funcD':
                if oper_stack.isEmpty():
                    raise AssertionError("Error 3: Mismatched parenthesis")
                f=oper_stack.pop()
                while f[0]!='funcB' and f[0]!='funcD':
                    end_q.enqueue(f)
                    if oper_stack.isEmpty():
                        raise AssertionError("Error 3: Mismatched parenthesis")
                    f=oper_stack.pop()
                end_q.enqueue(e)
                oper_stack.push(e)
            elif e[0]=='funcE':
                if oper_stack.isEmpty():
                    raise AssertionError("Error 3: Mismatched parenthesis")
                f=oper_stack.pop()
                while f[0]!='funcB' and f[0]!='funcD':
                    end_q.enqueue(f)
                    if oper_stack.isEmpty():
                        raise AssertionError("Error 3: Mismatched parenthesis")
                    f=oper_stack.pop()
                end_q.enqueue(e)
            else:
                raise AssertionError("Error 1: Unknown character")
        while not oper_stack.isEmpty():
            f=oper_stack.pop()
            if f[0]=='parenB' or f[0]=='funcB':
                raise AssertionError("Error 3: Mismatched parenthesis")
            end_q.enqueue(f)
        return end_q
    
    @staticmethod
    def convert_list_to_node(e: list):
        if e[0]=='digit':
            l=model.expression.Int(int(e[1]))
        elif e[0]=='alpha':
            l=model.expression.Var(e[1])
        elif e[0]=='operator':
            l=model.expression.Operator(e[1])
        elif e[0]=='funcE':
            l=model.expression.Function(e[1])
        else:
            raise AssertionError("Error 1b: Unknown character")
        return l
    
    @staticmethod
    def get_expr_tree(q: Queue)->TreePath:
        base_tree_node=None
        d=Queue.toDequeue(q)
        if not d.isEmpty():
            current_branch=Stack()
            n=None
            
            e=d.pop()
            base_tree_node=Parser.convert_list_to_node(e)
            tree_pointer=base_tree_node
            current_branch.push(tree_pointer)
            #print('221:func_stack pushed '+str(tree_pointer))
            #print(current_branch)
            while not d.isEmpty():
                e=d.pop()
                if e[0]=='operator' or e[0]=='funcE':
                    n=Parser.convert_list_to_node(e)
                    while type_as_str(tree_pointer)=='Operator' and len(tree_pointer.children)>=2 or type_as_str(tree_pointer)=='Function' and len(tree_pointer.children)>=function_database.get_function(tree_pointer.name).argcount:
                        temp=current_branch.pop()
                        #print('229:func_stack popped '+str(temp))
                        #print(current_branch)
                        tree_pointer=temp
                        
                    current_branch.push(n)
                    #print('234:func_stack pushed '+str(n))
                    #print(current_branch)
                    tree_pointer.add_child(n)
                    #print('237:'+str(tree_pointer)+' adds '+str(n))
                    tree_pointer=n
                elif e[0]=='funcD' or e[0]=='funcB':
                    while e[1]!=tree_pointer.name:
                        temp=current_branch.pop()
                        #print('242:func_stack popped '+str(temp))
                        #print(current_branch)
                        '''if len(tree_pointer.children)>=function_database.get_function(tree_pointer.get_kind()).argcount:
                            temp.add_child(tree_pointer)
                        print('245:'+str(temp)+' adds '+str(tree_pointer))'''
                        tree_pointer=temp
                    if e[0]=='funcD':
                        current_branch.push(tree_pointer)
                        #print('250:func_stack pushed '+str(temp))
                else:
                    while type_as_str(tree_pointer)=='Operator' and len(tree_pointer.children)>=2 or type_as_str(tree_pointer)=='Function' and len(tree_pointer.children)>=function_database.get_function(tree_pointer.name).argcount:
                        temp=current_branch.pop()
                        #print('254:func_stack popped '+str(temp))
                        #print(current_branch)
                        tree_pointer=temp
                        #print(tree_pointer)
                    n=Parser.convert_list_to_node(e)
                    tree_pointer.add_child(n)
                    #print('260:'+str(tree_pointer)+' adds '+str(n))
        #print(tree_pointer)
                
        return ExprTree(base_tree_node)
    
    def check(self)->None:
        for node in self._result.get_all_nodes():
            if type_as_str(node)=='Operator' and len(node.children)!=2 or type_as_str(node)=='Function' and len(node.children)!=function_database.get_function(node.name).argcount:
                raise AssertionError('Error 4: Invalid User Input')
    
    def output(self)->TreePath:
        self.check()
        return self._result
    
    def _modify_raw_str(self,raw:str)->str:
        for i in range(len(raw)-1):
            if raw[i]=='-' and raw[i]==raw[i+1]:
                j=i+1
                while raw[j]=='-':
                    j+=1
                if (j-i)%2==0:
                    raw=raw[:i]+"+"+raw[j-1:]
                else:
                    raw=raw[:i]+"-"+raw[j-1:]
                i-=1
        for i in range(len(raw)):
            if raw[i]=='-' and i>0 and i<len(raw) and raw[i+1].isdigit() and not Parser.is_binary_operator(raw[i-1]) and not Parser.is_separator(raw[i-1]):
                j=i+1
                while j<len(raw) and raw[j].isdigit():
                    j+=1
                raw=raw[:i]+'+('+raw[i:j]+')'+raw[j:]
        return raw
                
class RParser():
    make_pretty=True
    def __init__(self,raw:TreePath,const_dict:dict={},var_dict:dict={}):
        self._name_lookup=[]
        self.const_dict=const_dict
        self.var_dict=var_dict
        self._result=self.convert_to_str(raw.base)
        
    def convert_to_str(self,base_node)->str:
        if base_node==None:
            return "None"
        elif len(base_node.children)==0:
            if type(base_node) is model.expression.Var or type(base_node) is model.expression.Constant or type(base_node) is model.expression.ImmutableConst:
                self._name_lookup.append(base_node.name)
                return base_node.name
            elif type(base_node) is model.expression.Int or type(base_node) is model.expression.Fraction:
                return base_node.value
            else:
                raise AssertionError("Error 8: Unknown obj of type {}".format(type(base_node)))
        else:
            if type(base_node) is model.expression.Function:
                return "{name}({args})".format(name=base_node.name,args=";".join([self.convert_to_str(child) for child in base_node.args]))
            elif type(base_node) is model.expression.Operator:
                return "({l_arg}{name}{r_arg})".format(name=base_node.name,l_arg=self.convert_to_str(base_node[0]),r_arg=self.convert_to_str(base_node[1]))
            else:
                raise AssertionError("Error 8: Unknown obj of type {}".format(type(base_node)))
        
    def include(self,lookup:list,const_dict:dict,var_dict:dict):
        def _format_add(k:str,v:ExprTree,head_note=""):
            if RParser.make_pretty:
                return "{head_note} {key}={value}".format(key=k,value=self.pretty(self.convert_to_str(v)),head_note=head_note)
            else:
                return "{head_note} {key}={value}".format(key=k,value=self.convert_to_str(v),head_note=head_note)
        result="   "
        for e in lookup:
            if e in const_dict.keys():
                result+=_format_add(e,const_dict[e],"c:")+", "
            elif e in var_dict.keys():
                result+=_format_add(e,var_dict[e],"v:")+", "
        return ";"+result[:-2] if len(result)!=3 else ""
    
    def output(self)->str:
        if RParser.make_pretty:
            self._result=self.pretty(self._result)+self.include(self._name_lookup,self.var_dict,self.const_dict)
            return self._result
        else:
            self._result+=self.include(self._name_lookup,self.var_dict,self.const_dict)
            return self._result
    @staticmethod
    def _add_padding(res):
        for i in range(len(res)-2,0,-1):
            if res[i]=='-' and res[i+1].isdigit() and i>0 and (res[i-1].isdigit() or res[i-1].isalpha() or res[i-1]==')'):
                res=res[:i]+'+'+res[i:]
            elif res[i]=='-' and res[i+1].isalpha() and (i==0 or i>0 and (Parser.is_binary_operator(res[i-1]) or Parser.is_separator(res[i-1]) and res[i-1]!=')')):
                res=res[:i]+'(-1)*'+res[i+1:]
            elif res[i]=='-' and res[i+1].isalpha():
                res=res[:i]+'+(-1)*'+res[i+1:]
        return res
    
    def pretty(self,s:str):
        #remove excess parenthesis
        def _checkplusmin(res):
            for i in range(len(res)-2,0,-1):
                if res[i]=="+" and res[i+1]=="-":
                    res=res[:i]+res[i+1:]
                    i-=1
                elif res[i]=="-" and res[i+1]=="-":
                    res=res[:i]+"+"+res[i+2:]
                    i-=1
            return res
        res=s
        if res[0]=="(" and res[-1]==")":
            res=res[1:-1]
        
        
        res=RParser._add_padding(res)
        #print(res+'\n'*5)
        st=Stack()
        for i in range(len(res)-1,-1,-1):
            if res[i]==")":
                st.push([i])
                #print(st)
            else:
                if res[i]=="(":
                    #print(st)
                    current=st.pop()
                    #print(i,current,len(res),res[:i]+' {'+res[i:i+1]+'} '+res[i+1:current[0]]+' {'+res[current[0]:current[0]+1]+'} '+res[current[0]+1:])
                    if i==0 or i>0 and not res[i-1].isalpha() and not res[i-1]==';':
                        #print('initiate cutting1',res[:i]+' ['+res[i:i+1]+'] '+res[i+1:])
                        prev_oper=""
                        is_right=False
                        j=i-1
                        while prev_oper=="" and j>=0 and not (res[j]!=')' and Parser.is_separator(res[j])):
                            if Parser.is_binary_operator(res[j]) and (res[j]!='-' or not res[j+1].isdigit()):
                                prev_oper=res[j]
                            j-=1
                        if prev_oper!="":
                            '''print('left results:')
                            if j>=0:
                                print('\t',prev_oper=="", j>=0, not (res[j]!=')' and Parser.is_separator(res[j])))
                                print('\t','*',prev_oper)
                            else:
                                print('\t',prev_oper=="", j>=0, '-n/a-')
                                print('\t','*',prev_oper)
                        '''
                        if prev_oper=="":
                            is_right=True
                            j=current[0]+1
                            while prev_oper=="" and j<len(res) and not (res[j]!='(' and Parser.is_separator(res[j])):
                                if Parser.is_binary_operator(res[j]) and (res[j]!='-' or not res[j+1].isdigit()):
                                    prev_oper=res[j]
                                j+=1
                            '''print('right results:')
                            if j<len(res):
                                print('\t',prev_oper=="", j<len(res), not (res[j]!=')' and Parser.is_separator(res[j])))
                                print('\t','*',prev_oper)
                            else:
                                print('\t',prev_oper=="", j<len(res), '-n/a-')
                                print('\t','*',prev_oper)
                        print('check',i,current[0],prev_oper)
                        print('check2',i,current[0],prev_oper,current[1],is_right,current[0]=='/')'''
                        if prev_oper!='' and ((is_right and current[0]=='/' or not is_right and prev_oper=='/') and Parser.get_value(prev_oper)<Parser.get_value(current[1]) or (not(is_right and current[0]=='/' or not is_right and prev_oper=='/') ) and Parser.get_value(prev_oper)<=Parser.get_value(current[1])):
                            #print('cutting1',res[:i]+' ['+res[i:i+1]+'] '+res[i+1:current[0]]+' ['+res[current[0]:current[0]+1]+'] '+res[current[0]+1:])
                            res=res[:i]+res[i+1:current[0]]+res[current[0]+1:]
                            
                            temp_s=Stack()
                            while not st.isEmpty():
                                e=st.pop()
                                e[0]-=2
                                temp_s.push(e)
                            
                            while not temp_s.isEmpty():
                                st.push(temp_s.pop())
                                
                    else:
                        if res[i-1].isalpha() and res[i+1]=='(':
                            #print('initiate cutting2',i+1,res[:i]+' ['+res[i:i+2]+'] '+res[i+2:])
                            j=i+2
                            temp_s=Stack()
                            while res[j]!=')' or not Parser.is_separator(res[j+1]) or not temp_s.isEmpty():
                                #print(j,res[j],res[j+1])
                                if res[j]=='(':
                                    #print('pushed at',j)
                                    temp_s.push(j)
                                elif res[j]==')':
                                    #print('popped at',j)
                                    temp_s.pop()
                                j+=1
                            #print('cutting2',i+1,j,res[:i+1]+' ['+res[i]+'] '+res[i+2:j]+' ['+res[j]+'] '+res[j+1:])
                            res=res[:i+1]+res[i+2:j]+res[j+1:]
                            
                            temp_s=Stack()
                            while not st.isEmpty():
                                e=st.pop()
                                e[0]-=2
                                temp_s.push(e)
                            
                            while not temp_s.isEmpty():
                                st.push(temp_s.pop())
                        elif res[i-1]==';':
                            #print('initiate cutting3',i,res[:i]+' ['+res[i:i+1]+' ]'+res[i+1:])
                            j=i+1
                            temp_s=Stack()
                            while res[j]!=')' or not Parser.is_separator(res[j+1]) or not temp_s.isEmpty():
                                #print(j,res[j],res[j+1])
                                if res[j]=='(':
                                    #print('pushed at',j)
                                    temp_s.push(j)
                                elif res[j]==')':
                                    #print('popped at',j)
                                    temp_s.pop()
                                j+=1
                            #print('cutting3',i,j,res[:i]+' ['+res[i]+'] '+res[i+1:j]+' ['+res[j]+'] '+res[j+1:])
                            res=res[:i]+res[i+1:j]+res[j+1:]
                            
                            temp_s=Stack()
                            while not st.isEmpty():
                                e=st.pop()
                                e[0]-=2
                                temp_s.push(e)
                            
                            while not temp_s.isEmpty():
                                st.push(temp_s.pop())
                else:
                    if st.size()!=0 and Parser.is_binary_operator(res[i]) and (res[i]!='-' or not res[i+1].isdigit()):
                        st.peek().append(res[i])
                        
        #print('\n\n\nresult',res)
        res= _checkplusmin(res)
        
        #add parenthesis for negative numbers and exponents; also re-adds plus operator
        
        for i in range(len(res)-2):
            if res[i]=='-' and res[i+1].isdigit() and i+2<len(res):
                j=i+2
                while j<len(res) and res[j].isdigit():
                    j+=1
                if j<len(res) and res[j]=='^':
                    res=res[:i]+"("+res[i:j]+")"+res[j:]
                    if i-1>=0 and not Parser.is_binary_operator(res[i-1]):
                        res=res[:i]+"+"+res[i:]
                i=j+1
                
        #rearranges terms putting numbers in the front and variables/constants next followed by other expressions (order of sort is numbers, then letters, then by how long each substring is)
        
        
        def _sort_terms(res:str,f:callable):
            term=""
            s=Stack()
            terms=[]
            temp=Stack()
            
            for i in range(len(res)):
                #print(res[:i]+' { '+res[i:i+1]+' } '+res[i+1:],terms,term)
                if res[i]=='(':
                    temp.push(term+res[i])
                    temp.push(terms)
                    term=""
                    terms=[]
                elif res[i]==';':
                    terms.append(term)
                    temp.push(res[i])
                    temp.push(terms)
                    term=""
                    terms=[]
                elif res[i]==')':
                    is_done=False
                    if temp.peek(1)[-1]=='(':
                        is_done=True
                    terms.append(term)
                    e=temp.pop()
                    term=""
                    term_0=temp.pop()
                    terms.sort(key=f)
                    for j in range(len(terms)):
                        term_0+=terms[j]+'+'
                    term_0=term_0[:-1]
                    terms=e
                    while not is_done:
                        if temp.peek(1)[-1]=='(':
                            is_done=True
                        e=temp.pop()
                        term_i=temp.pop()
                        terms.sort(key=f)
                        for j in range(len(terms)):
                            term_i+=terms[j]+'+'
                        term_i=term_i[:-1]
                        term_0=term_i+term_0
                        terms=e
                    term=term_0+res[i]
                elif Parser.is_binary_operator(res[i]):
                    if res[i]=='-' and (res[i+1].isdigit() or res[i+1].isalpha()) and i>=0 and (res[i-1].isdigit() or res[i-1].isalpha() or res[i-1]==')'):
                        if len(term)!=0:
                            terms.append(term)
                        term=res[i]
                    elif res[i]=='-' and (res[i+1].isdigit() or res[i+1].isalpha()):
                        term+=res[i]
                    elif Parser.get_value(res[i])==Parser.get_value('+'):
                        if len(term)!=0:
                            terms.append(term)
                        term=""
                    else:
                        term+=res[i]
                else:
                    term+=res[i]
                #print(term,terms)
            terms.append(term)
            
            res=""
            #print(terms)
            terms.sort(key=f)
            for i in range(len(terms)):
                res+=terms[i]+'+'
            res=res[:-1]
            #print(res)
            
            return res
        
        def _order_terms(res:str,f:callable):
            singles=[]
            single=""
            result=""
            s=Stack()
            for i in range(len(res)):
                #print(res[:i]+" { "+res[i:i+1]+" } "+res[i+1:],singles,'"'+single+'"',' | ',result,' | ',s)
                if res[i]=='(':
                    s.push(single+res[i])
                    s.push(singles)
                    s.push(result)
                    single=''
                    singles=[]
                    result=''
                elif res[i]==')':
                    singles.append(single)
                    singles.sort(key=f)
                    temp2=s.pop()
                    temp=s.pop()
                    temp3=s.pop()
                    result=temp3+result
                    #print('*',single,singles,temp,result)
                    for e in singles:
                        if (result=="" or False) and len(e)>0 and e[0]=="/":
                            result+="1"
                        elif len(e)>0 and e[0]=="/" and result[-1]=='*':
                            result=result[:-1]
                        result+=e+"*"
                    result=result[:-1]+res[i]
                    singles=temp
                    single=result
                    result=temp2
                    #print('*',single,singles,result)
                elif Parser.is_separator(res[i]) or Parser.is_binary_operator(res[i]) and (res[i]=='+' or res[i]=='-' and (res[i+1].isdigit() or res[i+1].isalpha()) and i>=0 and (res[i-1].isdigit() or res[i-1].isalpha() or res[i-1]==')')):
                    singles.append(single)
                    singles.sort(key=f)
                    for e in singles:
                        if (result=="" or False) and len(e)>0 and e[0]=="/":
                            result+="1"
                        elif len(e)>0 and e[0]=="/" and result[-1]=='*':
                            result=result[:-1]
                        result+=e+"*"
                    result=result[:-1]+res[i]
                    singles=[]
                    single=""
                elif res[i]=="/":
                    singles.append(single)
                    single="/"
                elif res[i]=="*":
                    singles.append(single)
                    single=""
                else:
                    single+=res[i]
            singles.append(single)
            for e in singles:
                if result=="" and len(e)>0 and e[0]=="/":
                    result+="1"
                elif len(e)>0 and e[0]=="/" and result[-1]=='*':
                    result=result[:-1]
                result+=e+"*"
            result=result[:-1]
            return result
        
        def index_string(s:str):
            is_inverse=False
            if len(s)>0 and s[0]=='/': is_inverse=True
            for i in range(len(s)-1,-1,-1):
                if not s[i].isalnum():
                    s=s[:i]+s[i+1:]
            if s.isnumeric() and not is_inverse:
                s="?"*len(s)+s
            elif s.isnumeric() and is_inverse:
                s="@"*len(s)+s
            elif s.isalpha() and not is_inverse:
                s="|"*len(s)+s
            elif s.isalpha() and is_inverse:
                s="|"*(2*len(s))+s
            else:
                s="~"*len(s)+s
            return s
        res=_order_terms(res,lambda x: index_string(x))
        #print(res)
        #res=_sort_terms(res,lambda x: sum([ord(x[i])**-i for i in range(len(x))]))
        res=_sort_terms(res,lambda x: len(x))
        return res
        
if __name__=='__main__':
    test0="1"
    test1="-52"
    test2="3-4"
    test3="18-2*4"
    test4="(2-7)/(6+2)"
    test5="3-(-2)*5"
    test6="x+4"
    test7="exp(x)"
    test8="1+ln(4-3*1)"
    test9="(x^5-2*sqrt(1-x^4)*F(asin(x);-1)-x)/(3*sqrt(x^4-1))"
    test10="f-2*h"
    test11="1/(n-1)^2*(-1)^n"
    test12="(-2)^(2^((-2)^(-1*x)))"
    test13="x*14/5+x*y*2*z/7*6*n-2/9+asin(x)+y+asin(y)+(-1)+(-1)^n+(x-4*y+3/5)^3"
    #test14="F(asin(x);sqrt(x))"
    test14="x*F(asin(x^2*y)*y+x^2*y-1/2;-1*sqrt(-1*x^2+1)+3/4)*-1*y+x*y/2"
    test15="x*Fh((3^4-1)/2;(3^4+1)/2;(3*2*4-1*1)/(2*2)+1/2;1/4-z*1/4+z^2)-x*1/2-4"
    test16="x*Fh(1;-1;x^2*y;F(asin(x^2*y);(2-4)/3))"
    
    p0=Parser(test0)
    p1=Parser(test1)
    p2=Parser(test2)
    p3=Parser(test3)
    p4=Parser(test4)
    p5=Parser(test5)
    p6=Parser(test6)
    p7=Parser(test7)
    p8=Parser(test8)
    p9=Parser(test9)
    p10=Parser(test10)
    p11=Parser(test11)
    p12=Parser(test12)
    p13=Parser(test13)
    p14=Parser(test14)
    p15=Parser(test15)
    p16=Parser(test16)
    
    #print(p0.output())
    #print(p1.output())
    #print(p2.output())
    #print(p3.output())
    #print(p4.output())
    #print(p5.output())
    #print(p6.output())
    #print(p7.output())
    #print(p8.output())
    #print(p9.output())
    #print(p10.output())
    #print(p11.output())
    #print(p12.output())
    #print(p13.output())
    #print(p14.output())
    #print(p15.output())
    #print(p16.output())
    
    import ui.commands_database#for testing only
    r0=RParser(p0.output(),ui.commands_database.const_dict,ui.commands_database.var_dict)
    r1=RParser(p1.output(),ui.commands_database.const_dict,ui.commands_database.var_dict)
    r2=RParser(p2.output(),ui.commands_database.const_dict,ui.commands_database.var_dict)
    r3=RParser(p3.output(),ui.commands_database.const_dict,ui.commands_database.var_dict)
    r4=RParser(p4.output(),ui.commands_database.const_dict,ui.commands_database.var_dict)
    r5=RParser(p5.output(),ui.commands_database.const_dict,ui.commands_database.var_dict)
    r6=RParser(p6.output(),ui.commands_database.const_dict,ui.commands_database.var_dict)
    r7=RParser(p7.output(),ui.commands_database.const_dict,ui.commands_database.var_dict)
    r8=RParser(p8.output(),ui.commands_database.const_dict,ui.commands_database.var_dict)
    r9=RParser(p9.output(),ui.commands_database.const_dict,ui.commands_database.var_dict)
    r10=RParser(p10.output(),ui.commands_database.const_dict,ui.commands_database.var_dict)
    r11=RParser(p11.output(),ui.commands_database.const_dict,ui.commands_database.var_dict)
    r12=RParser(p12.output(),ui.commands_database.const_dict,ui.commands_database.var_dict)
    r13=RParser(p13.output(),ui.commands_database.const_dict,ui.commands_database.var_dict)
    r14=RParser(p14.output(),ui.commands_database.const_dict,ui.commands_database.var_dict)
    r15=RParser(p15.output(),ui.commands_database.const_dict,ui.commands_database.var_dict)
    r16=RParser(p16.output(),ui.commands_database.const_dict,ui.commands_database.var_dict)
    
    for i in range(2):
        if i%2==0:
            print('raw text')
            RParser.make_pretty=False
        if i%2==1:
            print('pretty text')
            RParser.make_pretty=True
        '''print()
        print(r0.output())
        print(r1.output())
        print(r2.output())
        print(r3.output())'''
        #print(r4.output())
        '''print(r5.output())
        print(r6.output())
        print(r7.output())
        print(r8.output())'''
        #print(r9.output())
        #print(r10.output())
        print(r11.output())
        print(r12.output())
        print(r13.output())
        print(r14.output())
        print(r15.output())
        print(r16.output())
    