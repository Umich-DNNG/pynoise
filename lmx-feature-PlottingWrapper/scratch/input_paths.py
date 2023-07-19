### script for setting up input paths




# standard imports
import glob
import sys

# local imports

def input_paths(input_type,filepath):
    fname, f_and_p_name, files = ([] for i in range(3))
    if input_type == '.lmx':
        search_ext = '*.lmx'
    elif input_type == '.xml':
        search_ext = '*.xml'
    elif input_type == '.csv':
        search_ext = '*.csv'
    for filename in glob.glob(search_ext):
        f_and_p_name.append(filepath+'/'+filename)
        files.append(filename)
        
    return files

def input_paths_w_bkg(input_type,filepath,bkg_subtract_fname):
    fname, f_and_p_name, files = ([] for i in range(3))
    bkg_file = ''
    if input_type == '.lmx':
        search_ext = '*.lmx'
    elif input_type == '.xml':
        search_ext = '*.xml'
    elif input_type == '.csv':
        search_ext = '*.csv'
    for filename in glob.glob(search_ext):
        if filename != bkg_subtract_fname:
            f_and_p_name.append(filepath+'/'+filename)
            files.append(filename)
        else: 
            bkg_file = filename
      
    if bkg_file == '':
        sys.exit('Exit: perform_bkg_subtract_rates is set to True, but bkg_subtract_fname was not located.')
        
    return files, bkg_file