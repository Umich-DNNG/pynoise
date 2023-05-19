### script for modifying PlotWrapper.py files


# standard imports
import os
import numpy as np

# local imports


# begin user specifications

starting_script_name = 'PlotWrapper_NeSO_split.py'
lines_to_modify = [57,197,198]
new_values = [[r'\\slip.lanl.gov\NCERC\Data\Hand-stacking Data\2019 03 05 NeSO\split files\offset\017. Np+0.6Ni - Benchmark (2 NoMADs)', r'\\slip.lanl.gov\NCERC\Data\Hand-stacking Data\2019 03 05 NeSO\split files\offset\031. Np+1.1Ni - Benchmark 03.18-19 (2 NoMADs)', r'\\slip.lanl.gov\NCERC\Data\Hand-stacking Data\2019 03 05 NeSO\split files\offset\019. Np+1.6Ni - Benchmark (2 NoMADs)', r'\\slip.lanl.gov\NCERC\Data\Hand-stacking Data\2019 03 05 NeSO\split files\offset\020. Np+2.1Ni - Benchmark (2 NoMADs)', r'\\slip.lanl.gov\NCERC\Data\Hand-stacking Data\2019 03 05 NeSO\split files\offset\023. Np+2.6Ni - Benchmark (2 NoMADs)', r'\\slip.lanl.gov\NCERC\Data\Hand-stacking Data\2019 03 05 NeSO\split files\offset\022. Np+3.1Ni - Benchmark (2 NoMADs)', r'\\slip.lanl.gov\NCERC\Data\Hand-stacking Data\2019 03 05 NeSO\split files\offset\024. Np+3.6Ni - Benchmark (2 NoMADs)'], [0.042703522,0.043267782, 0.044224495, 0.044693265, 0.045214503, 0.045703521, 0.046175178], [0.000427095, 0.000432737, 0.000442304, 0.000447052, 0.000452204, 0.000457154, 0.000461791]]
# add a True for each list that contains a path
path_locations = [True, False, False]
batch_filename = 'batch.bat'
output_prompt_to_text = True

# example
#starting_script_name = 'PlotWrapper_20230308_NeSO_1.1Ni.py'
#lines_to_modify = [195,196]
#new_values = [[1,2,3],[4,5,6]]
# add a True for each list that contains a path
#path_locations = [True, False, False]
#batch_filename = 'batch.bat'
#output_prompt_to_text = True

# end user specifications



# checks
if len(lines_to_modify) != len(new_values):
    sys.exit('Exit: lines_to_modify and new_values must have the same length.')
if not all(len(l) == len(new_values[0]) for l in new_values):
    sys.exit('Exit: all sublists within new_values must have the same length.')

default_dir = os.getcwd()
print('Directory of python script ',default_dir)

os.chdir(default_dir)
save_path = default_dir+'/'
    
with open(starting_script_name, 'r') as file:
    read_data = file.readlines()


new_values_transposed = np.array(new_values).T.tolist()

script_names = []

for i in range(0,len(new_values_transposed)):
    
    current_new_values = new_values_transposed[i]
    
    for j in range(0,len(new_values_transposed[0])):
        
        line_number = lines_to_modify[j]-1
        is_path = path_locations[j]
            
        modify_line = read_data[line_number]
        modify_line = modify_line.split('=')
        modify_line_pre = modify_line[0]
        modify_line_post = modify_line[1]
        modify_line_post = modify_line[1:]
        if is_path == True:
            modify_line = modify_line_pre+"= r'"+str(current_new_values[j])+"'\n"
        else:
            modify_line = modify_line_pre+'= '+str(current_new_values[j])+'\n'
        
        read_data[line_number] = modify_line
    
    script_name = starting_script_name[:-3]+'_'+str(i+1)+'.py'
    with open(script_name, 'w') as file:
        file.writelines(read_data)
        
    script_names.append(script_name)

# write batch file
with open(batch_filename, 'w') as file:
    for script_name in script_names:
        if output_prompt_to_text == True:
            file.writelines('python '+script_name+' > '+script_name+'.txt\n')
        else:
            file.writelines('python '+script_name+'\n')

print('Script complete.')