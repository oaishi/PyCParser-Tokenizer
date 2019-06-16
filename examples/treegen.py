#!/usr/bin/env python
# coding: utf-8

# In[17]:


from __future__ import print_function
import sys
import re
#pip install anytree
from anytree import Node, RenderTree
from anytree.exporter import DictExporter
from collections import OrderedDict
from pycparser import c_parser, c_ast , parse_file
# This is not required if you've installed pycparser into
# your site-packages/ with setup.py
#
sys.path.extend(['.', '..'])
fakeheaderpath = r'D:\Python\Lib\site-packages\pycparser\utils\fake_libc_include'
variable_list = []
scope = 1
scopecount = 1

root = Node('FileAST ,  < ' + str(scopecount) + ' > >')
required_attr = ['names', 'type' , 'op' , 'value' , 'declname', 'name']
useless_attr = ['dim_quals', 'quals', 'storage', 'funcspec']

id_list = ['CHAR', 'DOUBLE', 'INT', 'LONG', 'SHORT', 'SIGNED','UNSIGNED',  '__INT128'] # 'STRUCT' # 'VOID'


def show(self, buf=sys.stdout, offset=0, attrnames=False, nodenames=True, showcoord=False, _my_node_name=None , parent_name= None):
        lead = ' ' * offset
        
        if nodenames and _my_node_name is not None: 
            buf.write(lead + self.__class__.__name__+ ' < ' + _my_node_name + ' >: ')
        else:
            buf.write(lead + self.__class__.__name__+ ':  ')
            
        if "Compound" in self.__class__.__name__:
            global scope
            scope += 1
            # ambigious

        if self.attr_names:
            if attrnames:
                nvlist = [(n, getattr(self,n)) for n in self.attr_names]
                attrstr = ', '.join('%s=%s' % nv for nv in nvlist)
                 
                #if "TypeDecl" in self.__class__.__name__ and "FuncDecl" not in parent_name:
                 #   varname = getattr(self, 'declname', 'none')
                  #  typo = ''
                   # for (child_name, child) in self.children():
                    #    typo = getattr(child,'names', 'none')
                    #temp = [varname, typo,scope]
                    #if varname is not None:
                     #   variable_list.append(temp)
            else:
                vlist = [getattr(self, n) for n in self.attr_names]
                attrstr = ', '.join('%s' % v for v in vlist)
            buf.write(attrstr)

        if showcoord:
            buf.write(' (at %s)' % self.coord)
        buf.write('\n')

        for (child_name, child) in self.children():
            show(child,
                buf,
                offset=offset + 2,
                attrnames=attrnames,
                nodenames=nodenames,
                showcoord=showcoord,
                _my_node_name=child_name,
                parent_name=self.__class__.__name__)
# In[88]:

def treegen(self, root1, _my_node_name=None , parent_name= None , marker= 1):
    
        attrstr = ''

        if self.attr_names:
                        
                nvlist = [(n, getattr(self,n)) for n in self.attr_names if n not in useless_attr]
                attrstr = ' ,'.join(' %s="%s"' % nv for nv in nvlist)

        #new scope found,used for scope information
        if "Compound" in self.__class__.__name__:
            global scopecount
            scopecount += 1
            attrstr = ' < ' + str(scopecount) + ' >'


        if parent_name is not None:
            if marker:
                parent_n = Node('< ' + self.__class__.__name__ + ' , '+ attrstr +' >', parent=root1)
            else:
                parent_n = Node('< ' + self.__class__.__name__ , parent=root1)
            root1 = parent_n

        #if "IdentifierType" in self.__class__.__name__: ##scope informaton gather and f token rename
         #   str_tok = str(parent_n.parent)[7:][:-3]
          #  ancestors = str_tok.split('>/<')
          #  print(ancestors[-2:])
          #  scopelist = [s for s in ancestors if 'Compound' in s or 'FileAST' in s]
          #  print(scopelist[-1:])
          #  text = str(scopelist[-1:])
            ###parent_n.name = 'bingo!' ##renaming!!!
          #  try:
          #      found = re.search('<(.+?)>', text).group(1)
          #      print(found)
          #   except AttributeError:
          #      found = ''  # apply your error handling


        ##leftovers : name extraction and symboltablestack and tokenstack manipulation
        ##for ID and identifiertype in self._class_.__name__ rename , rename the node as well

        for (child_name, child) in self.children():
            treegen(child,root1,
                _my_node_name=child_name,
                parent_name = self.__class__.__name__)

def token_to_code(tokenstack):
    code = ''
    prev = None
    for a in tokenstack:
        if prev is not None:
            if prev.lineno != a.lineno:
                code += '\n'
        code += a.value + ' '
        prev = a
    print(code)

def print_token(tokenstack):

    str = ''
    for a in tokenstack:  # tokenlist printing
        # 'LexToken(%s,%r,%d,%d)' % (self.type, self.value, self.lineno, self.lexpos) ply/lex.py
        # print(str(a))
        str += '  ' + '< ' + a.type + ',' + a.value + ' >'
    print(str)

def print_Tree(root):
    for pre, fill, node in RenderTree(root):
        print("%s%s" % (pre, node.name))

    # leaves = root.leaves
    # for i in range(len(leaves)):
    #    print('next one')
    #    print(leaves[i])

def token_manipulation(tokenstack):
    declarelist = []
    formallist = {}
    map1 = {}
    currentscope=1
    declarelist.append(map1)

    prevtoken = '' # need to have the following one to track functions . function parameters ???

    flag = 0
    for iter in range(len(tokenstack)):
        a=tokenstack[iter]
        if a.type == 'ID':
            if prevtoken != '': #declaration

                tokenstack[iter].type = "ID_"+ prevtoken
                if flag == 0:
                    declarelist[currentscope-1][a.value] = prevtoken
                    print(declarelist)
                    if tokenstack[iter + 1].type == 'LPAREN':
                        formallist = {}
                        flag = 1
                else:
                    formallist[a.value] = prevtoken
                    print(formallist)

            else: ## token rename
                searchfurther = 0

                try:
                    found = declarelist[currentscope-1][a.value]
                    print(a.value + " - "+ found)
                    tokenstack[iter].type = "ID_" + found
                    print(a.value + " - " + found + " - "+ tokenstack[iter].type)
                except KeyError:
                    searchfurther = 1

                if searchfurther == 1:
                    try:
                        found = declarelist[currentscope - 1][a.value]
                        print(a.value + " - " + found)
                        tokenstack[iter].type = "ID_" + found
                        print(a.value + " - " + found + " - " + tokenstack[iter].type)
                        searchfurther = 0
                    except KeyError:
                        searchfurther = 1

                for i in range(1,currentscope-1):
                    if searchfurther == 1:
                        try:
                            found = declarelist[i - 1][a.value]
                            print(a.value + " - " + found)
                            tokenstack[iter].type = "ID_" + found
                            print(a.value + " - " + found + " - " + tokenstack[iter].type)
                            searchfurther = 0
                            break
                        except KeyError:
                            searchfurther = 1


        if a.type != 'ID' or a.type != 'COMMA':
            prevtoken = ''

        if a.type == 'RPAREN':
            flag = 0

        if a.type in id_list:
            prevtoken = a.type

        if a.type == 'LBRACE':
            currentscope += 1
            map1 = {}
            declarelist.append(map1)

        if a.type == 'RBRACE':
            currentscope -= 1
            declarelist.pop()
            formallist = {}


    #try:
     #   found = map[1]['key1']
      #  print(found)
    #except KeyError:
     #   found = ''  # apply your error handling

# parse_file -> _init_.py
# from there c_parser.py in line 152
# from there yacc.py in line 328
ast, tokenstack, symboltablestack = parse_file(r'F:\machine learning\pycparser-master\pycparser-master\examples\c_files\test.c')
#treegen(ast, root)
#print_Tree(root)
token_manipulation(tokenstack)
print_token(tokenstack)
#token_to_code(tokenstack)
#print(symboltablestack)
#print(symboltablestack['ID'])
# In[33]:
#parser = c_parser.CParser()
#ast = parser.parse(text, filename='<none>')
#ast = parser.parse(text, filename='<none>')
#ast = parse_file(r'F:\machine learning\pycparser-master\pycparser-master\examples\c_files\test.c')
#show(ast,attrnames=True, nodenames=True, showcoord=True, _my_node_name=None)
#print(variable_list)
