### script for making "batch" PlotWrapper.py files


# standard imports
import os
import shutil

# local imports
from script_backup import *


# begin user specifications

starting_script_name = 'PlotWrapper_20230308_NeSO_1.1Ni.py'
root_filepath = r'\\slip.lanl.gov\NCERC\Data\Hand-stacking Data\2019 03 05 NeSO\001-008  Benchmark Cf N2-515 (2 NoMADs)'
parameter_to_modify = 'filepath = '
batch_filename = 'batch.bat'
output_prompt_to_text = True
# Note that this will run in parallel. This could utilize a lot of CPU!
run_in_parallel = False

# default user specifications
#starting_script_name = 'PlotWrapper.py'
#root_filepath = r''
#parameter_to_modify = 'filepath = '
#batch_filename = 'batch.bat'
#output_prompt_to_text = True

# end user specifications



default_dir = os.getcwd()
print('Directory of python script ',default_dir)
os.chdir(root_filepath)
print('Directory of input files ',root_filepath)

# getting subdirectories
sub_directory_list = [d for d in next(os.walk(root_filepath))[1]]
sub_directory_path = []
for element in sub_directory_list:
    sub_directory_path.append(root_filepath+'/'+element)

os.chdir(default_dir)
save_path = default_dir+'/'

# creating script backups
script_names = []
for i in range(0,len(sub_directory_list)):
    
    script_backup(save_path, starting_script_name, '_'+str(i), '.py')    
    script_names.append(starting_script_name[:-3]+'_'+str(i)+'.py')

# modify path in script
for i in range(0,len(script_names)):
    fname = script_names[i]
    modify_line = parameter_to_modify+"r'"+sub_directory_path[i]+"'\n"
    
    with open(fname, 'r') as file:
        read_data = file.readlines()
    
    modified_line_count = 0
    
    for j in range(0,len(read_data)):
        line = read_data[j]
        if parameter_to_modify in line and line[0] != '#':
            read_data[j] = modify_line
            modified_line_count += 1
    
    
        
    print(fname,' had ',modified_line_count,' line(s) modified.')
    
    with open(fname, 'w') as file:
        file.writelines(read_data)

# write batch file
with open(batch_filename, 'w') as file:
    for script_name in script_names:
        if output_prompt_to_text == True:
            if run_in_parallel == True:
                file.writelines('start /b python '+script_name+' > '+script_name+'.txt\n')
            else:
                file.writelines('python '+script_name+' > '+script_name+'.txt\n')
        else:
            if run_in_parallel == True:
                file.writelines('start /b python '+script_name+'\n')
            else:
                file.writelines('python '+script_name+'\n')