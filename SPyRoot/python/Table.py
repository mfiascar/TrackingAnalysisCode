
import sys

from SObject import SObject
from collections import defaultdict

class Table(SObject):
    def __init__(self,name=None,rows=1,cols=1):
        self.name=name
        self.data=defaultdict(str)
        if type(rows)==int:
            rows=range(1,rows+1)
        else:
            for r in rows:
                self.data[r,'__ROW__']=r
            if type(cols)!=int:
                cols=['__ROW__']+list(cols)
        if type(cols)==int:
            cols=[chr(ord('A')+ii) for ii in range(cols)]
            if self.data:
                cols=['__ROW__']+cols
        else:
            rows=['__COL__']+list(rows)
            for c in cols:
                if c=='__ROW__': continue
                self.data['__COL__',c]=c
        self.rows=tuple(rows)
        self.cols=tuple(cols)

        self.listPickleVars = [
            'name',
            'data',
            'cols',
            'rows',
            ]

    def __setitem__(self,loc,value):
        self.data[loc]=value

    def __getitem__(self,loc):
        return self.data[loc]

    def AddRow(self):
        num=len(self.rows)
        self.rows+=(num,)
        return num

    def GetRows(self):
        return list(self.rows)

    def GetCols(self):
        return list(self.cols)

    def Print(self,file=None,maxCols=8,longTable=False, htmlTableHeader=''):
        longfoot=''
        beg=''
        sep=' '
        endl='\n'
        header=lambda x : ''
        tail=''
        tableSep='\n'
        if not file:
            o=sys.stdout
        else:
            o=open(file,'w')
            if file.endswith('.tex'):
                texTable='tabular'
                if longTable:
                    texTable='longtable'
                    longfoot='\\endhead\n'
                sep=' & '
                endl=' \\\\ \n'
                def header(cols):
                    head='\\begin{'+texTable+'}'
                    if cols[0]=='__ROW__':
                        head+='{l'+'r'*(len(cols)-1)+'}\n'
                    else:
                        head+='{'+'r'*len(cols)+'}\n'
                    return head
                tail='\\end{'+texTable+'}\n'
                tableSep='\\vspace{2ex}\n'
            elif file.endswith('.html') :
                beg='<tr><td>'
                sep=' </td><td> '
                endl='</td></tr>\n'
                def header(cols):
                    head='<table %s>\n' % htmlTableHeader
                    return head
                tail='</table>\n'
                tableSep='<p>\n'

                
        mycols=list(self.cols)
        while mycols:
            cols=mycols[:maxCols]
            o.write(header(cols))
            for rr in self.rows:
                colList=['%-10s ' % str(self.data[rr,cc]) for cc in cols]
                o.write(beg+sep.join(colList)+endl)
                if rr==self.rows[0]:
                    o.write(longfoot)
            o.write(tail)
            if mycols[0]=='__ROW__':
                mycols=mycols[:1]+mycols[maxCols:]
                if len(mycols)==1: mycols=[]
            else:
                mycols=mycols[maxCols:]
            if mycols: o.write(tableSep)
        if file:
            o.close()
