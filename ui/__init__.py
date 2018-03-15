

class ParsingError(AssertionError):
    def __init__(self,msg=""):
        if msg=="":
            super(ParsingError,self).__init__()
        else:
            super(ParsingError,self).__init__(msg)

if __name__=='__main__':
    import sys
    import traceback
    import ui.parser as parser
    import ui.commands_database
    s=input(':')
    while not s=='~':
        def _only_one_char(string,char):
            return char in s and not char in s[s.index(char)+1:]
        def _parse_tree(s,index):
            try:
                return parser.Parser(s[index]).output()
                #print(p.output())
            except BaseException as E:
                print(sys.exc_info())
                #print(traceback.format_exc())
        
        try:
            if '=' in s or '<' in s or '>' in s:
                if _only_one_char(s,'<') and _only_one_char(s,'=') and s.index('<')+1==s.index('='):
                    s='le '+s[:s.index('<')]+s[s.index('=')+1:]
                elif _only_one_char(s,'>') and _only_one_char(s,'=') and s.index('>')+1==s.index('='):
                    s='ge '+s[:s.index('>')]+s[s.index('=')+1:]
                elif _only_one_char(s,'='):
                    s='eq '+s[:s.index('=')]+s[s.index('=')+1:]
                elif _only_one_char(s,'<'):
                    s='lt '+s[:s.index('=')]+s[s.index('=')+1:]
                elif _only_one_char(s,'>'):
                    s='gt '+s[:s.index('=')]+s[s.index('=')+1:]
                else:
                    raise ParsingError("Error 1: Incorrect usage of inequality/equality signs")
            s_list=s.split(' ')
            cmd=None
            if s_list[0] in ui.commands_database.database.keys():
                cmd=ui.commands_database.interface(s_list[0])
                try:
                    if cmd.get_arg_count()==2 and len(s_list)==3:
                        print(s_list[2])
                        print('***',_parse_tree(s_list,2))
                        res=cmd(s_list[1],_parse_tree(s_list,2))
                    elif cmd.get_arg_count()==1 and len(s_list)==2:
                        res=cmd(s_list[1])
                    else:
                        raise AttributeError("Incorrect number of parameters")
                except (IndexError,KeyError,AttributeError):
                    print(sys.exc_info()[0])
                    print(sys.exc_info()[1])
                    print(traceback.print_tb(sys.exc_info()[2]))
                else:
                    if res!=None:
                        print(res)
                    else:
                        print()
            else:
                raise SyntaxError("Command not found")
        except (AssertionError,ParsingError,SyntaxError):
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])
            print(traceback.print_tb(sys.exc_info()[2]))
        
        s=input(':')
    