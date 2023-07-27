# script for summing Feynman histograms


# standard imports
import numpy as np


def histogram_sum(histogram_x_all_files, histogram_y_all_files):
    
    histogram_y_transposed = np.array(histogram_y_all_files).T.tolist()
    
    histogram_y_sum_list = []
    for element in histogram_y_transposed:

        sub_len_list = []    
        for sub_list in element:
            sub_len_list.append(len(sub_list))
        sub_max_len = np.max(sub_len_list)
        
        sub_sum_list = [0 for i in range(sub_max_len)]
        
        for sub_list in element:
            for i in range(0,len(sub_list)):
                sub_sum_list[i] += sub_list[i]
                
        histogram_y_sum_list.append(sub_sum_list)

    histogram_x_sum_list = []
    for element in histogram_y_sum_list:
        x_single_list = []
        for i in range(0,len(element)):
            x_single_list.append(i)
        histogram_x_sum_list.append(x_single_list)
    
    return histogram_x_sum_list, histogram_y_sum_list
    
    