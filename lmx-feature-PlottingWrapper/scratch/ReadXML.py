# script for reading xml files


# standard imports
import numpy as np


def readXML(fname, xml_user_gatewidths, user_gatewidth_list):
    
    filedata = []
    feynman_lines = []
    gatewidths = []
    feynman_data = []
    
    # opens the file and gets all lines in the file
    with open(fname, 'r') as f:
        for line in f:
            filedata.append(line)
    
    # finds the part of the file with the feynman data
    for line in filedata:
        if '</feynman>' in line:
            feynman_lines.append(line)
    
    # gets gate-width and feynman histogram data
    for element in feynman_lines:
    
        temp = element.split('gatewidth="')
        temp2 = temp[1]
        if " mask" in temp2:
            temp3 = temp2.split('" mask')
        else:
            temp3 = temp2.split('">')
        current_gatewidth = int(temp3[0])
        
        if (xml_user_gatewidths == True and current_gatewidth in user_gatewidth_list) or xml_user_gatewidths != True:
            
            if len(gatewidths) == 0 or current_gatewidth > np.max(gatewidths):
            
                gatewidths.append(current_gatewidth)
                
                temp4 = element.split('>')
                temp5 = temp4[1]
                temp6 = temp5.split('</feynman>')
                temp7 = temp6[0]
                temp8 = temp7.split(' ')
                current_feynman_data = temp8[:-1]
                current_feynman_data = [int(i) for i in current_feynman_data]
                feynman_data.append(current_feynman_data)
                
    return gatewidths, feynman_data