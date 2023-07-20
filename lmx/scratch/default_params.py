### script for setting default parameters of PlotWrapper.py
### each default is a tuple with length 3: 0 is the parameter name, 1 is the default value, 2 is the example which is commented out



import os
import shutil
from time import gmtime, strftime

## local imports
from script_backup import *


################################################################################
# begin user specifications

starting_script_name = 'PlotWrapper.py'

default_param_tuple = (('filepath',"filepath = ''","#Example: filepath = r'X:\Scratch\Hutchinson\FAUSTlmxModified\FAUST\lmx\scratch\input\SCRAP_bare\split'"),('save_path',"save_path = 'output'",None),('output_nested_subdirectories',"output_nested_subdirectories = True",None),('file_descriptions',"file_descriptions = ()","#Example: file_descriptions = ('Config 1','Config 2','Config 3')"),('calculation_type',"calculation_type = ''", None),('plot_histograms','plot_histograms = False',None),('plot_individual_files','plot_individual_files = False',None),('plot_all_files_vs_gw','plot_all_files_vs_gw = False',None),('plot_all_files_vs_con','plot_all_files_vs_con = False',None),('plot_channels','plot_channels = False',None),('perform_Rossi','perform_Rossi = False',None),('read_header','read_header = False', None),('combine_Y2_rate_results','combine_Y2_rate_results = False',None),('combine_statistical_plots','combine_statistical_plots = False', None),('sum_Feynman_histograms','sum_Feynman_histograms = False',None),('compare_combine_Y2_rate_results_and_Feynman_sum','compare_combine_Y2_rate_results_and_Feynman_sum = False',None),('combine_Y2_rate_results_filepath',"combine_Y2_rate_results_filepath = ''",None),('sum_histogram_filepath',"sum_histogram_filepath = ''",None),('compare_individual_file_and_combine_Y2_rate_results_and_Feynman_sum','compare_individual_file_and_combine_Y2_rate_results_and_Feynman_sum = False',None),('individual_filepath_and_filename',"individual_filepath_and_filename = ''",None),('output_csv',"output_csv = True",None),('histogram_match_axis','histogram_match_axis = False',None),('histogram_normalize','histogram_normalize = False',None),('plot_sum_and_individual_histogram','plot_sum_and_individual_histogram = False',None),('perform_Y2_single_fit','perform_Y2_single_fit = False',None),('perform_Y2_double_fit','perform_Y2_double_fit = False',None),('xml_user_gatewidths','xml_user_gatewidths = False',None),('user_gatewidths_plot_all_files_vs_con','user_gatewidths_plot_all_files_vs_con = True',None),('perform_Rossi_fits','perform_Rossi_fits = False',None),('Rossi_reset_time','Rossi_reset_time=1000000',None),('Rossi_bin_num','Rossi_bin_num=100',None),('des_on_vs_config','des_on_vs_config = False',None),('marker_size','marker_size = 2',None),('yaxis_log','yaxis_log = False',None),('plot_titles','plot_titles = False',None),('use_title','use_title = True',None),('title_prefix',"title_prefix = 'NOMAD'",None),('backup_script','backup_script = True',None),('include_stats_reduced_moments','include_stats_reduced_moments = True',None),('include_stats_moments','include_stats_moments = True',None),('include_stats_rates','include_stats_rates = True',None),('exit_on_FIFO','exit_on_FIFO = False',None),('plot_time_vs_events','plot_time_vs_events = False',None),('use_user_specified_lifetime','use_user_specified_lifetime = False',None),('user_lifetime','user_lifetime = 40.8e-6',None),('user_lifetime_unc','user_lifetime_unc = 0',None),('perform_bkg_subtract_rates','perform_bkg_subtract_rates = False',None),('bkg_subtract_fname',"bkg_subtract_fname = ''",None),('channel_display',"channel_display = ''",None),('Y2_fit_randomized_data','Y2_fit_randomized_data = False',None),('Y2_fit_randomized_data_number_points',"Y2_fit_randomized_data_number_points = 'automatic'",None),('Y2_fit_randomized_data_number_fits','Y2_fit_randomized_data_number_fits = 10000',None))
input_type_default = ('input_type',"input_type = '.xml'","#Example: input_type = '.lmx'","#Example: input_type = '.csv'")
gatewidth_list_default = ('gatewidth_list', 'gatewidth_list = [256000, 2048000]')
start_string = '# begin user specifications'
end_string = '# end user specifications'

# end user specifications
################################################################################




default_dir = os.getcwd()
print('Directory of python script ',default_dir)
save_path = default_dir+'/'

script_backup(save_path, starting_script_name, '_'+strftime("%Y_%m_%d_%H%M%S", gmtime()), '.py')


with open(starting_script_name, 'r') as file:
    read_data = file.readlines()
    
   
for j in range(0,len(read_data)):
    if start_string in read_data[j]:
        start_index = j
    if end_string in read_data[j]:
        end_index = j


modified_line_count = 0

for j in range(start_index,end_index):
    line = read_data[j]
    for k in range(0,len(default_param_tuple)):
        current_tuple = default_param_tuple[k]
        if line[0:10] != '#Example: ':
            if '=' in line:
                if current_tuple[0] == line[:line.index('=')-1]:
                    read_data[j] = current_tuple[1]+'\n'
                    modified_line_count += 1

print('Sub 1',modified_line_count,len(default_param_tuple))
    
expected_line_count = len(default_param_tuple)

for j in range(start_index,end_index):
    line = read_data[j]
    for k in range(0,len(default_param_tuple)):
        current_tuple = default_param_tuple[k]
        if current_tuple[2] != None:
            if line[0:10] == '#Example: ':
                if current_tuple[0] in line:
                    read_data[j] = current_tuple[2]+'\n'
                    modified_line_count += 1
                    expected_line_count += 1
                    
print('Sub 2',modified_line_count,expected_line_count)                    

for j in range(start_index,end_index):
    line = read_data[j]
    if line[0:10] != '#Example: ':
        if '=' in line:
            if input_type_default[0] == line[:line.index('=')-1]:
                read_data[j] = input_type_default[1]+'\n'
                read_data[j+1] = input_type_default[2]+'\n'
                read_data[j+2] = input_type_default[3]+'\n'
                modified_line_count += 3
                

print('Sub 3',modified_line_count,expected_line_count+3)

for j in range(start_index,end_index):
    line = read_data[j]
    if line[0:10] != '#Example: ':
        if '=' in line:
            if gatewidth_list_default[0] == line[:line.index('=')-1]:
                read_data[j] = gatewidth_list_default[1]+'\n'
                modified_line_count += 1
                
print('Sub 4',modified_line_count,expected_line_count+4)

os.remove(starting_script_name)
    
with open(starting_script_name, 'w') as file:
    file.writelines(read_data)
