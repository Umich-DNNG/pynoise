### script for setting up input paths


# standard imports
import glob

# local imports

def input_paths(input_type,filepath):
    fname, f_and_p_name, files  = ([] for i in range(3))
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