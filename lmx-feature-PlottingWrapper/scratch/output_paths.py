### script for setting up input paths


# standard imports
import os
from time import gmtime, strftime

# local imports

def output_paths(save_path,default_dir,plot_histograms, plot_individual_files, plot_channels, output_csv, files, combine_Y2_rate_results):
    
    """ Sets up initial output paths """
    
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    output_dir = os.getcwd()
    save_path = output_dir+'/'+save_path
    print('Directory of output files ',save_path)
    save_path = save_path+'/'
    os.chdir(default_dir)
    if plot_histograms == True or plot_individual_files == True or plot_channels == True or output_csv == True:
        if not os.path.exists(save_path+'\Individual_Files'):
            os.makedirs(save_path+'\Individual_Files')
    if len(files) > 1:
        if not os.path.exists(save_path+'\All_Files'):
            os.makedirs(save_path+'\All_Files')
        if combine_Y2_rate_results == True:
            if not os.path.exists(save_path+'\Combined'):
                os.makedirs(save_path+'\Combined')
    
    return output_dir, save_path


def output_subdirectory_paths(output_nested_subdirectories, save_path, post_script, post_script_not_nested, current_file, add_current_file=False, make_dirs=False):
    
    """ Sets up output subdirectories and save path """
    
    if output_nested_subdirectories == True:
        if make_dirs == True:
            if not os.path.exists(save_path+post_script):
                os.makedirs(save_path+post_script)
        if add_current_file == True:
            current_save_path = save_path+post_script+post_script_not_nested+current_file
        else:
            current_save_path = save_path+post_script+post_script_not_nested
    else:
        if add_current_file == True:
            current_save_path = save_path+post_script_not_nested+current_file
        else:
            current_save_path = save_path+post_script_not_nested
            
    return current_save_path

