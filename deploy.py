#deploy.py
#

from clint.textui import puts, colored, columns
import shutil
import fabric
import boto
import numpy as np

def make_text_menu(dmenu):
    COLW = 76
    COLH = 24
    
    assert isinstance(dmenu, dict)
    
    if dmenu['order']:
        colnames = dmenu['order']
    else:
        colnames = dmenu.keys()
    
    #Find each maximum column width by longest string
    colwidths = [max(len(max(dmenu[key]))+1, len(key)+1) for key in colnames]
    
    #Evenly distribute space to all columns
    mincolwidth = int(np.floor(COLW/len(colwidths)))
    
    #If bigger than window, keep those less than mincolwidth, long strings to 0 for placeholder
    if sum(colwidths) > COLW:
        colwidths = [colwidth if colwidth < mincolwidth else 0 for colwidth in colwidths]
    
    #Find the long ones
    ind, = np.where(np.array(colwidths)==0)
    
    #Split remaining space between long string columns
    if len(ind):
        maxwidth = int(np.floor((COLW-sum(colwidths))/len(ind)))
        colwidths = [colwidth if colwidth else maxwidth for colwidth in colwidths]
    
    #put headers
    cols = [[(colored.red(colname)), colwidth] for colname, colwidth in zip(colnames,colwidths)] 
    puts(columns(*cols))
    
    #loop through choices and print to console
    for i in range(len(dmenu[colnames[0]])):
        cols =[[dmenu[key][i], colwidth] for key, colwidth in zip(colnames,colwidths)]
        puts(columns(*cols))
        

if __name__ == '__main__':
    test_dict = {'order': ['id','a', 'b', 'lorem', 'lorem2'],'id': ['1','2'], 'a': ['test1', 'test2'], 'b': ['test11', 'test112'], 'lorem': ['Lorem ipsum dolor sit amet, consehdfhdfhdfhdfhdfhctetur adi pisicing elit, sed do eiusmod tempor incididunt ut labore', '1'], 'lorem2': ['Lorem ipsum dolor sit amet, consehdfhdfhdfhdfhdfhctetur adi pisicin', '2']}
    make_text_menu(test_dict)
        
    

