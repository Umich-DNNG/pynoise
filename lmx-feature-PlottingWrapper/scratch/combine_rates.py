# script for computing weighted averages, combined uncertainties, etc.


# standard imports
import numpy as np
# import csv
# import sys

#local imports
# from plot_gatewidth import *


def combine_rates(data_list, unc_list):
    
    """ Script for computing weighted averages, combined uncertainties, etc.
    Both data_list and unc_list are assumed to be a list of lists (file outer list, gate-width inner list)."""
    
    w_avg = []
    w_unc = []
    w_sd = []
    w_unc_avg = []

    data_transposed = np.array(data_list).T.tolist()
    unc_transposed = np.array(unc_list).T.tolist()


    for i in range(0,len(data_transposed)):
        
        data_file = data_transposed[i]
        unc_file = unc_transposed[i]
        
        temp_unc = []
        temp_avg = []
        for j in range(0,len(data_file)):
            temp_unc.append(1/unc_file[j]**2)
            temp_avg.append(data_file[j]/unc_file[j]**2)
        
        w_avg.append(sum(temp_avg)/sum(temp_unc))
        w_unc.append((1/sum(temp_unc))**0.5)
        # not entirely sure if ddof=1 should be used or not. this forces it to match Excel stdev function
        w_sd.append(np.std(data_file, ddof=1))
        w_unc_avg.append(np.mean(unc_file))
    
    return w_avg, w_unc, w_sd, w_unc_avg
