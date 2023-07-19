# script for summing Feynman histograms


# standard imports
import csv
import sys

#local imports
from plot_gatewidth import *


def list_difference(list1,list2,percent_difference=False):
    
    if len(list1) != len(list2):
        sys.exit('Exit: combine results and sum histogram results must have the same gate-widths.')
        
    difference_list = []
    
    for i in range(0,len(list1)):
        if percent_difference == True:
            if list1[i] != 0:
                difference_list.append(100*(list1[i] - list2[i])/list1[i])
            else:
                difference_list.append(0)
        else:
            difference_list.append(list1[i] - list2[i])
    
    return difference_list

def combine_prepare(combine_Y2_rate_results_filepath, current_save_path, calculation_type, perform_Y2_single_fit, perform_Y2_double_fit, use_user_specified_lifetime):
    
    # reads combine file
    combine_f = open(combine_Y2_rate_results_filepath+'/Combined_rates.csv')

    csv_f = csv.reader(combine_f)
    
    combine_file_gatewidth_list = []
    combine_file_Y1_combined = []
    combine_file_Y1_combined_unc = []
    combine_file_Y1_combined_sd = []
    combine_file_Y1_individual_unc_avg = []
    combine_file_Y2_combined = []
    combine_file_Y2_combined_unc = []
    combine_file_Y2_combined_sd = []
    combine_file_Y2_individual_unc_avg = []
    combine_file_R1_combined = []
    combine_file_R1_combined_unc = []
    combine_file_R1_combined_sd = []
    combine_file_R1_individual_unc_avg = []
    combine_file_R2_single_Y2_decay_combined = []
    combine_file_R2_single_Y2_decay_combined_unc = []
    combine_file_R2_single_Y2_decay_combined_sd = []
    combine_file_R2_single_Y2_decay_individual_unc_avg = []
    combine_file_R2_double1_Y2_decay_combined = []
    combine_file_R2_double1_Y2_decay_combined_unc = []
    combine_file_R2_double1_Y2_decay_combined_sd = []
    combine_file_R2_double1_Y2_decay_individual_unc_avg = []
    combine_file_R2_double2_Y2_decay_combined = []
    combine_file_R2_double2_Y2_decay_combined_unc = []
    combine_file_R2_double2_Y2_decay_combined_sd = []
    combine_file_R2_double2_Y2_decay_individual_unc_avg = []
    combine_file_R2_double_both_Y2_decay_combined = []
    combine_file_R2_double_both_Y2_decay_combined_unc = []
    combine_file_R2_double_both_Y2_decay_combined_sd = []
    combine_file_R2_double_both_Y2_decay_individual_unc_avg = []
    combine_file_R2_user_lifetime_combined = []
    combine_file_R2_user_lifetime_combined_unc = []
    combine_file_R2_user_lifetime_combined_sd = []
    combine_file_R2_user_lifetime_individual_unc_avg = []
    combine_file_Ym_combined = []
    combine_file_Ym_combined_unc = []
    combine_file_Ym_combined_sd = []
    combine_file_Ym_individual_unc_avg = []
    combine_file_calc_eff_kn_combined = []
    combine_file_calc_eff_kn_combined_unc = []
    combine_file_calc_eff_kn_combined_sd = []
    combine_file_calc_eff_kn_individual_unc_avg = []
    combine_file_Ml_combined_Y2single = []
    combine_file_Ml_combined_unc_Y2single = []
    combine_file_Ml_combined_sd_Y2single = []
    combine_file_Ml_individual_unc_avg_Y2single = []
    combine_file_Mt_combined_Y2single = []
    combine_file_Mt_combined_unc_Y2single = []
    combine_file_Mt_combined_sd_Y2single = []
    combine_file_Mt_individual_unc_avg_Y2single = []
    combine_file_Fs_combined_Y2single = []
    combine_file_Fs_combined_unc_Y2single = []
    combine_file_Fs_combined_sd_Y2single = []
    combine_file_Fs_individual_unc_avg_Y2single = []
    combine_file_kp_combined_Y2single = []
    combine_file_kp_combined_unc_Y2single = []
    combine_file_kp_combined_sd_Y2single = []
    combine_file_kp_individual_unc_avg_Y2single = []
    combine_file_keff_combined_Y2single = []
    combine_file_keff_combined_unc_Y2single = []
    combine_file_keff_combined_sd_Y2single = []
    combine_file_keff_individual_unc_avg_Y2single = []
    combine_file_Ml_combined_Y2double1 = []
    combine_file_Ml_combined_unc_Y2double1 = []
    combine_file_Ml_combined_sd_Y2double1 = []
    combine_file_Ml_individual_unc_avg_Y2double1 = []
    combine_file_Mt_combined_Y2double1 = []
    combine_file_Mt_combined_unc_Y2double1 = []
    combine_file_Mt_combined_sd_Y2double1 = []
    combine_file_Mt_individual_unc_avg_Y2double1 = []
    combine_file_Fs_combined_Y2double1 = []
    combine_file_Fs_combined_unc_Y2double1 = []
    combine_file_Fs_combined_sd_Y2double1 = []
    combine_file_Fs_individual_unc_avg_Y2double1 = []
    combine_file_kp_combined_Y2double1 = []
    combine_file_kp_combined_unc_Y2double1 = []
    combine_file_kp_combined_sd_Y2double1 = []
    combine_file_kp_individual_unc_avg_Y2double1 = []
    combine_file_keff_combined_Y2double1 = []
    combine_file_keff_combined_unc_Y2double1 = []
    combine_file_keff_combined_sd_Y2double1 = []
    combine_file_keff_individual_unc_avg_Y2double1 = []
    combine_file_Ml_combined_Y2double2 = []
    combine_file_Ml_combined_unc_Y2double2 = []
    combine_file_Ml_combined_sd_Y2double2 = []
    combine_file_Ml_individual_unc_avg_Y2double2 = []
    combine_file_Mt_combined_Y2double2 = []
    combine_file_Mt_combined_unc_Y2double2 = []
    combine_file_Mt_combined_sd_Y2double2 = []
    combine_file_Mt_individual_unc_avg_Y2double2 = []
    combine_file_Fs_combined_Y2double2 = []
    combine_file_Fs_combined_unc_Y2double2 = []
    combine_file_Fs_combined_sd_Y2double2 = []
    combine_file_Fs_individual_unc_avg_Y2double2 = []
    combine_file_kp_combined_Y2double2 = []
    combine_file_kp_combined_unc_Y2double2 = []
    combine_file_kp_combined_sd_Y2double2 = []
    combine_file_kp_individual_unc_avg_Y2double2 = []
    combine_file_keff_combined_Y2double2 = []
    combine_file_keff_combined_unc_Y2double2 = []
    combine_file_keff_combined_sd_Y2double2 = []
    combine_file_keff_individual_unc_avg_Y2double2 = []
    combine_file_Ml_combined_Y2double_both = []
    combine_file_Ml_combined_unc_Y2double_both = []
    combine_file_Ml_combined_sd_Y2double_both = []
    combine_file_Ml_individual_unc_avg_Y2double_both = []
    combine_file_Mt_combined_Y2double_both = []
    combine_file_Mt_combined_unc_Y2double_both = []
    combine_file_Mt_combined_sd_Y2double_both = []
    combine_file_Mt_individual_unc_avg_Y2double_both = []
    combine_file_Fs_combined_Y2double_both = []
    combine_file_Fs_combined_unc_Y2double_both = []
    combine_file_Fs_combined_sd_Y2double_both = []
    combine_file_Fs_individual_unc_avg_Y2double_both = []
    combine_file_kp_combined_Y2double_both = []
    combine_file_kp_combined_unc_Y2double_both = []
    combine_file_kp_combined_sd_Y2double_both = []
    combine_file_kp_individual_unc_avg_Y2double_both = []
    combine_file_keff_combined_Y2double_both = []
    combine_file_keff_combined_unc_Y2double_both = []
    combine_file_keff_combined_sd_Y2double_both = []
    combine_file_keff_individual_unc_avg_Y2double_both = []
    combine_file_Ml_combined_Y2user_lifetime = []
    combine_file_Ml_combined_unc_Y2user_lifetime = []
    combine_file_Ml_combined_sd_Y2user_lifetime = []
    combine_file_Ml_individual_unc_avg_Y2user_lifetime = []
    combine_file_Mt_combined_Y2user_lifetime = []
    combine_file_Mt_combined_unc_Y2user_lifetime = []
    combine_file_Mt_combined_sd_Y2user_lifetime = []
    combine_file_Mt_individual_unc_avg_Y2user_lifetime = []
    combine_file_Fs_combined_Y2user_lifetime = []
    combine_file_Fs_combined_unc_Y2user_lifetime = []
    combine_file_Fs_combined_sd_Y2user_lifetime = []
    combine_file_Fs_individual_unc_avg_Y2user_lifetime = []
    combine_file_kp_combined_Y2user_lifetime = []
    combine_file_kp_combined_unc_Y2user_lifetime = []
    combine_file_kp_combined_sd_Y2user_lifetime = []
    combine_file_kp_individual_unc_avg_Y2user_lifetime = []
    combine_file_keff_combined_Y2user_lifetime = []
    combine_file_keff_combined_unc_Y2user_lifetime = []
    combine_file_keff_combined_sd_Y2user_lifetime = []
    combine_file_keff_individual_unc_avg_Y2user_lifetime = []
 
    # reads in csv and gets the columns
    for row in csv_f:
        combine_file_gatewidth_list.append(row[0])
        combine_file_Y1_combined.append(row[1])
        combine_file_Y1_combined_unc.append(row[2])
        combine_file_Y1_combined_sd.append(row[3])
        combine_file_Y1_individual_unc_avg.append(row[4])
        combine_file_Y2_combined.append(row[5])
        combine_file_Y2_combined_unc.append(row[6])
        combine_file_Y2_combined_sd.append(row[7])
        combine_file_Y2_individual_unc_avg.append(row[8])
        combine_file_R1_combined.append(row[9])
        combine_file_R1_combined_unc.append(row[10])
        combine_file_R1_combined_sd.append(row[11])
        combine_file_R1_individual_unc_avg.append(row[12])
        combine_file_R2_single_Y2_decay_combined.append(row[13])
        combine_file_R2_single_Y2_decay_combined_unc.append(row[14])
        combine_file_R2_single_Y2_decay_combined_sd.append(row[15])
        combine_file_R2_single_Y2_decay_individual_unc_avg.append(row[16])
        combine_file_R2_double1_Y2_decay_combined.append(row[17])
        combine_file_R2_double1_Y2_decay_combined_unc.append(row[18])
        combine_file_R2_double1_Y2_decay_combined_sd.append(row[19])
        combine_file_R2_double1_Y2_decay_individual_unc_avg.append(row[20])
        combine_file_R2_double2_Y2_decay_combined.append(row[21])
        combine_file_R2_double2_Y2_decay_combined_unc.append(row[22])
        combine_file_R2_double2_Y2_decay_combined_sd.append(row[23])
        combine_file_R2_double2_Y2_decay_individual_unc_avg.append(row[24])
        combine_file_R2_double_both_Y2_decay_combined.append(row[25])
        combine_file_R2_double_both_Y2_decay_combined_unc.append(row[26])
        combine_file_R2_double_both_Y2_decay_combined_sd.append(row[27])
        combine_file_R2_double_both_Y2_decay_individual_unc_avg.append(row[28])
        combine_file_R2_user_lifetime_combined.append(row[29])
        combine_file_R2_user_lifetime_combined_unc.append(row[30])
        combine_file_R2_user_lifetime_combined_sd.append(row[31])
        combine_file_R2_user_lifetime_individual_unc_avg.append(row[32])
        combine_file_Ym_combined.append(row[33])
        combine_file_Ym_combined_unc.append(row[34])
        combine_file_Ym_combined_sd.append(row[35])
        combine_file_Ym_individual_unc_avg.append(row[36])
        if calculation_type == 'Cf':
            combine_file_calc_eff_kn_combined.append(row[37])
            combine_file_calc_eff_kn_combined_unc.append(row[38])
            combine_file_calc_eff_kn_combined_sd.append(row[39])
            combine_file_calc_eff_kn_individual_unc_avg.append(row[40])
        elif calculation_type == 'Multiplicity':
            if perform_Y2_single_fit == True:
                combine_file_Ml_combined_Y2single.append(row[37])
                combine_file_Ml_combined_unc_Y2single.append(row[38])
                combine_file_Ml_combined_sd_Y2single.append(row[39])
                combine_file_Ml_individual_unc_avg_Y2single.append(row[40])
                combine_file_Fs_combined_Y2single.append(row[41])
                combine_file_Fs_combined_unc_Y2single.append(row[42])
                combine_file_Fs_combined_sd_Y2single.append(row[43])
                combine_file_Fs_individual_unc_avg_Y2single.append(row[44])
                combine_file_Mt_combined_Y2single.append(row[45])
                combine_file_Mt_combined_unc_Y2single.append(row[46])
                combine_file_Mt_combined_sd_Y2single.append(row[47])
                combine_file_Mt_individual_unc_avg_Y2single.append(row[48])
                combine_file_kp_combined_Y2single.append(row[49])
                combine_file_kp_combined_unc_Y2single.append(row[50])
                combine_file_kp_combined_sd_Y2single.append(row[51])
                combine_file_kp_individual_unc_avg_Y2single.append(row[52])
                combine_file_keff_combined_Y2single.append(row[53])
                combine_file_keff_combined_unc_Y2single.append(row[54])
                combine_file_keff_combined_sd_Y2single.append(row[55])
                combine_file_keff_individual_unc_avg_Y2single.append(row[56])
            if perform_Y2_double_fit == True:
                if perform_Y2_single_fit == True:
                    start_column = 57
                else:
                    start_column = 37
                combine_file_Ml_combined_Y2double1.append(row[start_column])
                combine_file_Ml_combined_unc_Y2double1.append(row[start_column+1])
                combine_file_Ml_combined_sd_Y2double1.append(row[start_column+2])
                combine_file_Ml_individual_unc_avg_Y2double1.append(row[start_column+3])
                combine_file_Fs_combined_Y2double1.append(row[start_column+4])
                combine_file_Fs_combined_unc_Y2double1.append(row[start_column+5])
                combine_file_Fs_combined_sd_Y2double1.append(row[start_column+6])
                combine_file_Fs_individual_unc_avg_Y2double1.append(row[start_column+7])
                combine_file_Mt_combined_Y2double1.append(row[start_column+8])
                combine_file_Mt_combined_unc_Y2double1.append(row[start_column+9])
                combine_file_Mt_combined_sd_Y2double1.append(row[start_column+10])
                combine_file_Mt_individual_unc_avg_Y2double1.append(row[start_column+11])
                combine_file_kp_combined_Y2double1.append(row[start_column+12])
                combine_file_kp_combined_unc_Y2double1.append(row[start_column+13])
                combine_file_kp_combined_sd_Y2double1.append(row[start_column+14])
                combine_file_kp_individual_unc_avg_Y2double1.append(row[start_column+15])
                combine_file_keff_combined_Y2double1.append(row[start_column+16])
                combine_file_keff_combined_unc_Y2double1.append(row[start_column+17])
                combine_file_keff_combined_sd_Y2double1.append(row[start_column+18])
                combine_file_keff_individual_unc_avg_Y2double1.append(row[start_column+19])
                combine_file_Ml_combined_Y2double2.append(row[start_column+20])
                combine_file_Ml_combined_unc_Y2double2.append(row[start_column+21])
                combine_file_Ml_combined_sd_Y2double2.append(row[start_column+22])
                combine_file_Ml_individual_unc_avg_Y2double2.append(row[start_column+23])
                combine_file_Fs_combined_Y2double2.append(row[start_column+24])
                combine_file_Fs_combined_unc_Y2double2.append(row[start_column+25])
                combine_file_Fs_combined_sd_Y2double2.append(row[start_column+26])
                combine_file_Fs_individual_unc_avg_Y2double2.append(row[start_column+27])
                combine_file_Mt_combined_Y2double2.append(row[start_column+28])
                combine_file_Mt_combined_unc_Y2double2.append(row[start_column+29])
                combine_file_Mt_combined_sd_Y2double2.append(row[start_column+30])
                combine_file_Mt_individual_unc_avg_Y2double2.append(row[start_column+31])
                combine_file_kp_combined_Y2double2.append(row[start_column+32])
                combine_file_kp_combined_unc_Y2double2.append(row[start_column+33])
                combine_file_kp_combined_sd_Y2double2.append(row[start_column+34])
                combine_file_kp_individual_unc_avg_Y2double2.append(row[start_column+35])
                combine_file_keff_combined_Y2double2.append(row[start_column+36])
                combine_file_keff_combined_unc_Y2double2.append(row[start_column+37])
                combine_file_keff_combined_sd_Y2double2.append(row[start_column+38])
                combine_file_keff_individual_unc_avg_Y2double2.append(row[start_column+39])
                combine_file_Ml_combined_Y2double_both.append(row[start_column+40])
                combine_file_Ml_combined_unc_Y2double_both.append(row[start_column+41])
                combine_file_Ml_combined_sd_Y2double_both.append(row[start_column+42])
                combine_file_Ml_individual_unc_avg_Y2double_both.append(row[start_column+43])
                combine_file_Fs_combined_Y2double_both.append(row[start_column+44])
                combine_file_Fs_combined_unc_Y2double_both.append(row[start_column+45])
                combine_file_Fs_combined_sd_Y2double_both.append(row[start_column+46])
                combine_file_Fs_individual_unc_avg_Y2double_both.append(row[start_column+47])
                combine_file_Mt_combined_Y2double_both.append(row[start_column+48])
                combine_file_Mt_combined_unc_Y2double_both.append(row[start_column+49])
                combine_file_Mt_combined_sd_Y2double_both.append(row[start_column+50])
                combine_file_Mt_individual_unc_avg_Y2double_both.append(row[start_column+51])
                combine_file_kp_combined_Y2double_both.append(row[start_column+52])
                combine_file_kp_combined_unc_Y2double_both.append(row[start_column+53])
                combine_file_kp_combined_sd_Y2double_both.append(row[start_column+54])
                combine_file_kp_individual_unc_avg_Y2double_both.append(row[start_column+55])
                combine_file_keff_combined_Y2double_both.append(row[start_column+56])
                combine_file_keff_combined_unc_Y2double_both.append(row[start_column+57])
                combine_file_keff_combined_sd_Y2double_both.append(row[start_column+58])
                combine_file_keff_individual_unc_avg_Y2double_both.append(row[start_column+59])
            if use_user_specified_lifetime == True:
                if perform_Y2_single_fit == True and perform_Y2_double_fit == True:
                    start_column = 117
                elif perform_Y2_single_fit == True:
                    start_column = 57
                elif perform_Y2_double_fit == True:
                    start_column = 97
                else:
                    start_column = 37
                combine_file_Ml_combined_Y2user_lifetime.append(row[start_column])
                combine_file_Ml_combined_unc_Y2user_lifetime.append(row[start_column+1])
                combine_file_Ml_combined_sd_Y2user_lifetime.append(row[start_column+2])
                combine_file_Ml_individual_unc_avg_Y2user_lifetime.append(row[start_column+3])
                combine_file_Fs_combined_Y2user_lifetime.append(row[start_column+4])
                combine_file_Fs_combined_unc_Y2user_lifetime.append(row[start_column+5])
                combine_file_Fs_combined_sd_Y2user_lifetime.append(row[start_column+6])
                combine_file_Fs_individual_unc_avg_Y2user_lifetime.append(row[start_column+7])
                combine_file_Mt_combined_Y2user_lifetime.append(row[start_column+8])
                combine_file_Mt_combined_unc_Y2user_lifetime.append(row[start_column+9])
                combine_file_Mt_combined_sd_Y2user_lifetime.append(row[start_column+10])
                combine_file_Mt_individual_unc_avg_Y2user_lifetime.append(row[start_column+11])
                combine_file_kp_combined_Y2user_lifetime.append(row[start_column+12])
                combine_file_kp_combined_unc_Y2user_lifetime.append(row[start_column+13])
                combine_file_kp_combined_sd_Y2user_lifetime.append(row[start_column+14])
                combine_file_kp_individual_unc_avg_Y2user_lifetime.append(row[start_column+15])
                combine_file_keff_combined_Y2user_lifetime.append(row[start_column+16])
                combine_file_keff_combined_unc_Y2user_lifetime.append(row[start_column+17])
                combine_file_keff_combined_sd_Y2user_lifetime.append(row[start_column+18])
                combine_file_keff_individual_unc_avg_Y2user_lifetime.append(row[start_column+19])
    
    # delete first row from list  
    del combine_file_gatewidth_list[0]
    del combine_file_Y1_combined[0]
    del combine_file_Y1_combined_unc[0]
    del combine_file_Y1_combined_sd[0]
    del combine_file_Y1_individual_unc_avg[0]
    del combine_file_Y2_combined[0]
    del combine_file_Y2_combined_unc[0]
    del combine_file_Y2_combined_sd[0]
    del combine_file_Y2_individual_unc_avg[0]
    del combine_file_R1_combined[0]
    del combine_file_R1_combined_unc[0]
    del combine_file_R1_combined_sd[0]
    del combine_file_R1_individual_unc_avg[0]
    del combine_file_R2_single_Y2_decay_combined[0]
    del combine_file_R2_single_Y2_decay_combined_unc[0]
    del combine_file_R2_single_Y2_decay_combined_sd[0]
    del combine_file_R2_single_Y2_decay_individual_unc_avg[0]
    del combine_file_R2_double1_Y2_decay_combined[0]
    del combine_file_R2_double1_Y2_decay_combined_unc[0]
    del combine_file_R2_double1_Y2_decay_combined_sd[0]
    del combine_file_R2_double1_Y2_decay_individual_unc_avg[0]
    del combine_file_R2_double2_Y2_decay_combined[0]
    del combine_file_R2_double2_Y2_decay_combined_unc[0]
    del combine_file_R2_double2_Y2_decay_combined_sd[0]
    del combine_file_R2_double2_Y2_decay_individual_unc_avg[0]
    del combine_file_R2_double_both_Y2_decay_combined[0]
    del combine_file_R2_double_both_Y2_decay_combined_unc[0]
    del combine_file_R2_double_both_Y2_decay_combined_sd[0]
    del combine_file_R2_double_both_Y2_decay_individual_unc_avg[0]
    del combine_file_R2_user_lifetime_combined[0]
    del combine_file_R2_user_lifetime_combined_unc[0]
    del combine_file_R2_user_lifetime_combined_sd[0]
    del combine_file_R2_user_lifetime_individual_unc_avg[0]
    del combine_file_Ym_combined[0]
    del combine_file_Ym_combined_unc[0]
    del combine_file_Ym_combined_sd[0]
    del combine_file_Ym_individual_unc_avg[0]
    if calculation_type == 'Cf':
        del combine_file_calc_eff_kn_combined[0]
        del combine_file_calc_eff_kn_combined_unc[0]
        del combine_file_calc_eff_kn_combined_sd[0]
        del combine_file_calc_eff_kn_individual_unc_avg[0]
    elif calculation_type == 'Multiplicity':
        if perform_Y2_single_fit == True:
            del combine_file_Ml_combined_Y2single[0]
            del combine_file_Ml_combined_unc_Y2single[0]
            del combine_file_Ml_combined_sd_Y2single[0]
            del combine_file_Ml_individual_unc_avg_Y2single[0]
            del combine_file_Mt_combined_Y2single[0]
            del combine_file_Mt_combined_unc_Y2single[0]
            del combine_file_Mt_combined_sd_Y2single[0]
            del combine_file_Mt_individual_unc_avg_Y2single[0]
            del combine_file_Fs_combined_Y2single[0]
            del combine_file_Fs_combined_unc_Y2single[0]
            del combine_file_Fs_combined_sd_Y2single[0]
            del combine_file_Fs_individual_unc_avg_Y2single[0]
            del combine_file_kp_combined_Y2single[0]
            del combine_file_kp_combined_unc_Y2single[0]
            del combine_file_kp_combined_sd_Y2single[0]
            del combine_file_kp_individual_unc_avg_Y2single[0]
            del combine_file_keff_combined_Y2single[0]
            del combine_file_keff_combined_unc_Y2single[0]
            del combine_file_keff_combined_sd_Y2single[0]
            del combine_file_keff_individual_unc_avg_Y2single[0]
        if perform_Y2_double_fit == True:
            del combine_file_Ml_combined_Y2double1[0]
            del combine_file_Ml_combined_unc_Y2double1[0]
            del combine_file_Ml_combined_sd_Y2double1[0]
            del combine_file_Ml_individual_unc_avg_Y2double1[0]
            del combine_file_Mt_combined_Y2double1[0]
            del combine_file_Mt_combined_unc_Y2double1[0]
            del combine_file_Mt_combined_sd_Y2double1[0]
            del combine_file_Mt_individual_unc_avg_Y2double1[0]
            del combine_file_Fs_combined_Y2double1[0]
            del combine_file_Fs_combined_unc_Y2double1[0]
            del combine_file_Fs_combined_sd_Y2double1[0]
            del combine_file_Fs_individual_unc_avg_Y2double1[0]
            del combine_file_kp_combined_Y2double1[0]
            del combine_file_kp_combined_unc_Y2double1[0]
            del combine_file_kp_combined_sd_Y2double1[0]
            del combine_file_kp_individual_unc_avg_Y2double1[0]
            del combine_file_keff_combined_Y2double1[0]
            del combine_file_keff_combined_unc_Y2double1[0]
            del combine_file_keff_combined_sd_Y2double1[0]
            del combine_file_keff_individual_unc_avg_Y2double1[0]
            del combine_file_Ml_combined_Y2double2[0]
            del combine_file_Ml_combined_unc_Y2double2[0]
            del combine_file_Ml_combined_sd_Y2double2[0]
            del combine_file_Ml_individual_unc_avg_Y2double2[0]
            del combine_file_Mt_combined_Y2double2[0]
            del combine_file_Mt_combined_unc_Y2double2[0]
            del combine_file_Mt_combined_sd_Y2double2[0]
            del combine_file_Mt_individual_unc_avg_Y2double2[0]
            del combine_file_Fs_combined_Y2double2[0]
            del combine_file_Fs_combined_unc_Y2double2[0]
            del combine_file_Fs_combined_sd_Y2double2[0]
            del combine_file_Fs_individual_unc_avg_Y2double2[0]
            del combine_file_kp_combined_Y2double2[0]
            del combine_file_kp_combined_unc_Y2double2[0]
            del combine_file_kp_combined_sd_Y2double2[0]
            del combine_file_kp_individual_unc_avg_Y2double2[0]
            del combine_file_keff_combined_Y2double2[0]
            del combine_file_keff_combined_unc_Y2double2[0]
            del combine_file_keff_combined_sd_Y2double2[0]
            del combine_file_keff_individual_unc_avg_Y2double2[0]
            del combine_file_Ml_combined_Y2double_both[0]
            del combine_file_Ml_combined_unc_Y2double_both[0]
            del combine_file_Ml_combined_sd_Y2double_both[0]
            del combine_file_Ml_individual_unc_avg_Y2double_both[0]
            del combine_file_Mt_combined_Y2double_both[0]
            del combine_file_Mt_combined_unc_Y2double_both[0]
            del combine_file_Mt_combined_sd_Y2double_both[0]
            del combine_file_Mt_individual_unc_avg_Y2double_both[0]
            del combine_file_Fs_combined_Y2double_both[0]
            del combine_file_Fs_combined_unc_Y2double_both[0]
            del combine_file_Fs_combined_sd_Y2double_both[0]
            del combine_file_Fs_individual_unc_avg_Y2double_both[0]
            del combine_file_kp_combined_Y2double_both[0]
            del combine_file_kp_combined_unc_Y2double_both[0]
            del combine_file_kp_combined_sd_Y2double_both[0]
            del combine_file_kp_individual_unc_avg_Y2double_both[0]
            del combine_file_keff_combined_Y2double_both[0]
            del combine_file_keff_combined_unc_Y2double_both[0]
            del combine_file_keff_combined_sd_Y2double_both[0]
            del combine_file_keff_individual_unc_avg_Y2double_both[0]
        if use_user_specified_lifetime == True:
            del combine_file_Ml_combined_Y2user_lifetime[0]
            del combine_file_Ml_combined_unc_Y2user_lifetime[0]
            del combine_file_Ml_combined_sd_Y2user_lifetime[0]
            del combine_file_Ml_individual_unc_avg_Y2user_lifetime[0]
            del combine_file_Mt_combined_Y2user_lifetime[0]
            del combine_file_Mt_combined_unc_Y2user_lifetime[0]
            del combine_file_Mt_combined_sd_Y2user_lifetime[0]
            del combine_file_Mt_individual_unc_avg_Y2user_lifetime[0]
            del combine_file_Fs_combined_Y2user_lifetime[0]
            del combine_file_Fs_combined_unc_Y2user_lifetime[0]
            del combine_file_Fs_combined_sd_Y2user_lifetime[0]
            del combine_file_Fs_individual_unc_avg_Y2user_lifetime[0]
            del combine_file_kp_combined_Y2user_lifetime[0]
            del combine_file_kp_combined_unc_Y2user_lifetime[0]
            del combine_file_kp_combined_sd_Y2user_lifetime[0]
            del combine_file_kp_individual_unc_avg_Y2user_lifetime[0]
            del combine_file_keff_combined_Y2user_lifetime[0]
            del combine_file_keff_combined_unc_Y2user_lifetime[0]
            del combine_file_keff_combined_sd_Y2user_lifetime[0]
            del combine_file_keff_individual_unc_avg_Y2user_lifetime[0]
    
    
    # converts to correct type
    for i in range(0,len(combine_file_gatewidth_list)):
        try:
            combine_file_gatewidth_list[i] = int(combine_file_gatewidth_list[i])
        except:
            ValueError
        try:
            combine_file_Y1_combined[i] = float(combine_file_Y1_combined[i])
            combine_file_Y1_combined_unc[i] = float(combine_file_Y1_combined_unc[i])
            combine_file_Y1_combined_sd[i] = float(combine_file_Y1_combined_sd[i])
            combine_file_Y1_individual_unc_avg[i] = float(combine_file_Y1_individual_unc_avg[i])
        except:
            ValueError
        try:
            combine_file_Y2_combined[i] = float(combine_file_Y2_combined[i])
            combine_file_Y2_combined_unc[i] = float(combine_file_Y2_combined_unc[i])
            combine_file_Y2_combined_sd[i] = float(combine_file_Y2_combined_sd[i])
            combine_file_Y2_individual_unc_avg[i] = float(combine_file_Y2_individual_unc_avg[i])
        except:
            ValueError
        try:
            combine_file_R1_combined[i] = float(combine_file_R1_combined[i])
            combine_file_R1_combined_unc[i] = float(combine_file_R1_combined_unc[i])
            combine_file_R1_combined_sd[i] = float(combine_file_R1_combined_sd[i])
            combine_file_R1_individual_unc_avg[i] = float(combine_file_R1_individual_unc_avg[i])
        except:
            ValueError
        try:
            combine_file_R2_single_Y2_decay_combined[i] = float(combine_file_R2_single_Y2_decay_combined[i])
            combine_file_R2_single_Y2_decay_combined_unc[i] = float(combine_file_R2_single_Y2_decay_combined_unc[i])
            combine_file_R2_single_Y2_decay_combined_sd[i] = float(combine_file_R2_single_Y2_decay_combined_sd[i])
            combine_file_R2_single_Y2_decay_individual_unc_avg[i] = float(combine_file_R2_single_Y2_decay_individual_unc_avg[i])
        except:
            ValueError
        try:
            combine_file_R2_double1_Y2_decay_combined[i] = float(combine_file_R2_double1_Y2_decay_combined[i])
            combine_file_R2_double1_Y2_decay_combined_unc[i] = float(combine_file_R2_double1_Y2_decay_combined_unc[i])
            combine_file_R2_double1_Y2_decay_combined_sd[i] = float(combine_file_R2_double1_Y2_decay_combined_sd[i])
            combine_file_R2_double1_Y2_decay_individual_unc_avg[i] = float(combine_file_R2_double1_Y2_decay_individual_unc_avg[i])
        except:
            ValueError
        try:
            combine_file_R2_double2_Y2_decay_combined[i] = float(combine_file_R2_double2_Y2_decay_combined[i])
            combine_file_R2_double2_Y2_decay_combined_unc[i] = float(combine_file_R2_double2_Y2_decay_combined_unc[i])
            combine_file_R2_double2_Y2_decay_combined_sd[i] = float(combine_file_R2_double2_Y2_decay_combined_sd[i])
            combine_file_R2_double2_Y2_decay_individual_unc_avg[i] = float(combine_file_R2_double2_Y2_decay_individual_unc_avg[i])
        except:
            ValueError
        try:
            combine_file_R2_double_both_Y2_decay_combined[i] = float(combine_file_R2_double_both_Y2_decay_combined[i])
            combine_file_R2_double_both_Y2_decay_combined_unc[i] = float(combine_file_R2_double_both_Y2_decay_combined_unc[i])
            combine_file_R2_double_both_Y2_decay_combined_sd[i] = float(combine_file_R2_double_both_Y2_decay_combined_sd[i])
            combine_file_R2_double_both_Y2_decay_individual_unc_avg[i] = float(combine_file_R2_double_both_Y2_decay_individual_unc_avg[i])
        except:
            ValueError
        try:
            combine_file_R2_user_lifetime_combined[i] = float(combine_file_R2_user_lifetime_combined[i])
            combine_file_R2_user_lifetime_combined_unc[i] = float(combine_file_R2_user_lifetime_combined_unc[i])
            combine_file_R2_user_lifetime_combined_sd[i] = float(combine_file_R2_user_lifetime_combined_sd[i])
            combine_file_R2_user_lifetime_individual_unc_avg[i] = float(combine_file_R2_user_lifetime_individual_unc_avg[i])
        except:
            ValueError
        try:
            combine_file_Ym_combined[i] = float(combine_file_Ym_combined[i])
            combine_file_Ym_combined_unc[i] = float(combine_file_Ym_combined_unc[i])
            combine_file_Ym_combined_sd[i] = float(combine_file_Ym_combined_sd[i])
            combine_file_Ym_individual_unc_avg[i] = float(combine_file_Ym_individual_unc_avg[i])
        except:
            ValueError
        if calculation_type == 'Cf':
            try:
                combine_file_calc_eff_kn_combined[i] = float(combine_file_calc_eff_kn_combined[i])
                combine_file_calc_eff_kn_combined_unc[i] = float(combine_file_calc_eff_kn_combined_unc[i])
                combine_file_calc_eff_kn_combined_sd[i] = float(combine_file_calc_eff_kn_combined_sd[i])
                combine_file_calc_eff_kn_individual_unc_avg[i] = float(combine_file_calc_eff_kn_individual_unc_avg[i])
            except:
                ValueError
        elif calculation_type == 'Multiplicity':
            try:
                combine_file_Ml_combined_Y2single[i] = float(combine_file_Ml_combined_Y2single[i])
                combine_file_Ml_combined_unc_Y2single[i] = float(combine_file_Ml_combined_unc_Y2single[i])    
                combine_file_Mt_combined_Y2single[i] = float(combine_file_Mt_combined_Y2single[i])
                combine_file_Mt_combined_unc_Y2single[i] = float(combine_file_Mt_combined_unc_Y2single[i])  
                combine_file_Fs_combined_Y2single[i] = float(combine_file_Fs_combined_Y2single[i])
                combine_file_Fs_combined_unc_Y2single[i] = float(combine_file_Fs_combined_unc_Y2single[i])
                combine_file_kp_combined_Y2single[i] = float(combine_file_kp_combined_Y2single[i])
                combine_file_kp_combined_unc_Y2single[i] = float(combine_file_kp_combined_unc_Y2single[i])
                combine_file_keff_combined_Y2single[i] = float(combine_file_keff_combined_Y2single[i])
                combine_file_keff_combined_unc_Y2single[i] = float(combine_file_keff_combined_unc_Y2single[i])
                combine_file_Ml_combined_Y2double1[i] = float(combine_file_Ml_combined_Y2double1[i])
                combine_file_Ml_combined_unc_Y2double1[i] = float(combine_file_Ml_combined_unc_Y2double1[i])
                combine_file_Mt_combined_Y2double1[i] = float(combine_file_Mt_combined_Y2double1[i])
                combine_file_Mt_combined_unc_Y2double1[i] = float(combine_file_Mt_combined_unc_Y2double1[i])
                combine_file_Fs_combined_Y2double1[i] = float(combine_file_Fs_combined_Y2double1[i])
                combine_file_Fs_combined_unc_Y2double1[i] = float(combine_file_Fs_combined_unc_Y2double1[i])
                combine_file_kp_combined_Y2double1[i] = float(combine_file_kp_combined_Y2double1[i])
                combine_file_kp_combined_unc_Y2double1[i] = float(combine_file_kp_combined_unc_Y2double1[i])
                combine_file_keff_combined_Y2double1[i] = float(combine_file_keff_combined_Y2double1[i])
                combine_file_keff_combined_unc_Y2double1[i] = float(combine_file_keff_combined_unc_Y2double1[i])
                combine_file_Ml_combined_Y2double2[i] = float(combine_file_Ml_combined_Y2double2[i])
                combine_file_Ml_combined_unc_Y2double2[i] = float(combine_file_Ml_combined_unc_Y2double2[i])
                combine_file_Mt_combined_Y2double2[i] = float(combine_file_Mt_combined_Y2double2[i])
                combine_file_Mt_combined_unc_Y2double2[i] = float(combine_file_Mt_combined_unc_Y2double2[i])
                combine_file_Fs_combined_Y2double2[i] = float(combine_file_Fs_combined_Y2double2[i])
                combine_file_Fs_combined_unc_Y2double2[i] = float(combine_file_Fs_combined_unc_Y2double2[i])
                combine_file_kp_combined_Y2double2[i] = float(combine_file_kp_combined_Y2double2[i])
                combine_file_kp_combined_unc_Y2double2[i] = float(combine_file_kp_combined_unc_Y2double2[i])
                combine_file_keff_combined_Y2double2[i] = float(combine_file_keff_combined_Y2double2[i])
                combine_file_keff_combined_unc_Y2double2[i] = float(combine_file_keff_combined_unc_Y2double2[i])
                combine_file_Ml_combined_Y2double_both[i] = float(combine_file_Ml_combined_Y2double_both[i])
                combine_file_Ml_combined_unc_Y2double_both[i] = float(combine_file_Ml_combined_unc_Y2double_both[i])
                combine_file_Mt_combined_Y2double_both[i] = float(combine_file_Mt_combined_Y2double_both[i])
                combine_file_Mt_combined_unc_Y2double_both[i] = float(combine_file_Mt_combined_unc_Y2double_both[i])
                combine_file_Fs_combined_Y2double_both[i] = float(combine_file_Fs_combined_Y2double_both[i])
                combine_file_Fs_combined_unc_Y2double_both[i] = float(combine_file_Fs_combined_unc_Y2double_both[i])
                combine_file_kp_combined_Y2double_both[i] = float(combine_file_kp_combined_Y2double_both[i])
                combine_file_kp_combined_unc_Y2double_both[i] = float(combine_file_kp_combined_unc_Y2double_both[i])
                combine_file_keff_combined_Y2double_both[i] = float(combine_file_keff_combined_Y2double_both[i])
                combine_file_keff_combined_unc_Y2double_both[i] = float(combine_file_keff_combined_unc_Y2double_both[i])
                combine_file_Ml_combined_Y2user_lifetime[i] = float(combine_file_Ml_combined_Y2user_lifetime[i])
                combine_file_Ml_combined_unc_Y2user_lifetime[i] = float(combine_file_Ml_combined_unc_Y2user_lifetime[i])
                combine_file_Mt_combined_Y2user_lifetime[i] = float(combine_file_Mt_combined_Y2user_lifetime[i])
                combine_file_Mt_combined_unc_Y2user_lifetime[i] = float(combine_file_Mt_combined_unc_Y2user_lifetime[i])
                combine_file_Fs_combined_Y2user_lifetime[i] = float(combine_file_Fs_combined_Y2user_lifetime[i])
                combine_file_Fs_combined_unc_Y2user_lifetime[i] = float(combine_file_Fs_combined_unc_Y2user_lifetime[i])
                combine_file_kp_combined_Y2user_lifetime[i] = float(combine_file_kp_combined_Y2user_lifetime[i])
                combine_file_kp_combined_unc_Y2user_lifetime[i] = float(combine_file_kp_combined_unc_Y2user_lifetime[i])
                combine_file_keff_combined_Y2user_lifetime[i] = float(combine_file_keff_combined_Y2user_lifetime[i])
                combine_file_keff_combined_unc_Y2user_lifetime[i] = float(combine_file_keff_combined_unc_Y2user_lifetime[i])
            except:
                ValueError
            try:
                combine_file_Ml_combined_sd_Y2single[i] = float(combine_file_Ml_combined_sd_Y2single[i])
                combine_file_Ml_individual_unc_avg_Y2single[i] = float(combine_file_Ml_individual_unc_avg_Y2single[i])
                combine_file_Mt_combined_sd_Y2single[i] = float(combine_file_Mt_combined_sd_Y2single[i])
                combine_file_Mt_individual_unc_avg_Y2single[i] = float(combine_file_Mt_individual_unc_avg_Y2single[i])
                combine_file_Fs_combined_sd_Y2single[i] = float(combine_file_Fs_combined_sd_Y2single[i])
                combine_file_Fs_individual_unc_avg_Y2single[i] = float(combine_file_Fs_individual_unc_avg_Y2single[i])
                combine_file_kp_combined_sd_Y2single[i] = float(combine_file_kp_combined_sd_Y2single[i])
                combine_file_kp_individual_unc_avg_Y2single[i] = float(combine_file_kp_individual_unc_avg_Y2single[i])
                combine_file_keff_combined_sd_Y2single[i] = float(combine_file_keff_combined_sd_Y2single[i])
                combine_file_keff_individual_unc_avg_Y2single[i] = float(combine_file_keff_individual_unc_avg_Y2single[i])
                combine_file_Ml_combined_sd_Y2double1[i] = float(combine_file_Ml_combined_sd_Y2double1[i])
                combine_file_Ml_individual_unc_avg_Y2double1[i] = float(combine_file_Ml_individual_unc_avg_Y2double1[i])
                combine_file_Mt_combined_sd_Y2double1[i] = float(combine_file_Mt_combined_sd_Y2double1[i])
                combine_file_Mt_individual_unc_avg_Y2double1[i] = float(combine_file_Mt_individual_unc_avg_Y2double1[i])
                combine_file_Fs_combined_sd_Y2double1[i] = float(combine_file_Fs_combined_sd_Y2double1[i])
                combine_file_Fs_individual_unc_avg_Y2double1[i] = float(combine_file_Fs_individual_unc_avg_Y2double1[i])
                combine_file_kp_combined_sd_Y2double1[i] = float(combine_file_kp_combined_sd_Y2double1[i])
                combine_file_kp_individual_unc_avg_Y2double1[i] = float(combine_file_kp_individual_unc_avg_Y2double1[i])
                combine_file_keff_combined_sd_Y2double1[i] = float(combine_file_keff_combined_sd_Y2double1[i])
                combine_file_keff_individual_unc_avg_Y2double1[i] = float(combine_file_keff_individual_unc_avg_Y2double1[i])
                combine_file_Ml_combined_sd_Y2double2[i] = float(combine_file_Ml_combined_sd_Y2double2[i])
                combine_file_Ml_individual_unc_avg_Y2double2[i] = float(combine_file_Ml_individual_unc_avg_Y2double2[i])
                combine_file_Mt_combined_sd_Y2double2[i] = float(combine_file_Mt_combined_sd_Y2double2[i])
                combine_file_Mt_individual_unc_avg_Y2double2[i] = float(combine_file_Mt_individual_unc_avg_Y2double2[i])
                combine_file_Fs_combined_sd_Y2double2[i] = float(combine_file_Fs_combined_sd_Y2double2[i])
                combine_file_Fs_individual_unc_avg_Y2double2[i] = float(combine_file_Fs_individual_unc_avg_Y2double2[i])
                combine_file_kp_combined_sd_Y2double2[i] = float(combine_file_kp_combined_sd_Y2double2[i])
                combine_file_kp_individual_unc_avg_Y2double2[i] = float(combine_file_kp_individual_unc_avg_Y2double2[i])
                combine_file_keff_combined_sd_Y2double2[i] = float(combine_file_keff_combined_sd_Y2double2[i])
                combine_file_keff_individual_unc_avg_Y2double2[i] = float(combine_file_keff_individual_unc_avg_Y2double2[i])
                combine_file_Ml_combined_sd_Y2double_both[i] = float(combine_file_Ml_combined_sd_Y2double_both[i])
                combine_file_Ml_individual_unc_avg_Y2double_both[i] = float(combine_file_Ml_individual_unc_avg_Y2double_both[i])
                combine_file_Mt_combined_sd_Y2double_both[i] = float(combine_file_Mt_combined_sd_Y2double_both[i])
                combine_file_Mt_individual_unc_avg_Y2double_both[i] = float(combine_file_Mt_individual_unc_avg_Y2double_both[i])
                combine_file_Fs_combined_sd_Y2double_both[i] = float(combine_file_Fs_combined_sd_Y2double_both[i])
                combine_file_Fs_individual_unc_avg_Y2double_both[i] = float(combine_file_Fs_individual_unc_avg_Y2double_both[i])
                combine_file_kp_combined_sd_Y2double_both[i] = float(combine_file_kp_combined_sd_Y2double_both[i])
                combine_file_kp_individual_unc_avg_Y2double_both[i] = float(combine_file_kp_individual_unc_avg_Y2double_both[i])
                combine_file_keff_combined_sd_Y2double_both[i] = float(combine_file_keff_combined_sd_Y2double_both[i])
                combine_file_keff_individual_unc_avg_Y2double_both[i] = float(combine_file_keff_individual_unc_avg_Y2double_both[i])
                combine_file_Ml_combined_sd_Y2user_lifetime[i] = float(combine_file_Ml_combined_sd_Y2user_lifetime[i])
                combine_file_Ml_individual_unc_avg_Y2user_lifetime[i] = float(combine_file_Ml_individual_unc_avg_Y2user_lifetime[i])
                combine_file_Mt_combined_sd_Y2user_lifetime[i] = float(combine_file_Mt_combined_sd_Y2user_lifetime[i])
                combine_file_Mt_individual_unc_avg_Y2user_lifetime[i] = float(combine_file_Mt_individual_unc_avg_Y2user_lifetime[i])
                combine_file_Fs_combined_sd_Y2user_lifetime[i] = float(combine_file_Fs_combined_sd_Y2user_lifetime[i])
                combine_file_Fs_individual_unc_avg_Y2user_lifetime[i] = float(combine_file_Fs_individual_unc_avg_Y2user_lifetime[i])
                combine_file_kp_combined_sd_Y2user_lifetime[i] = float(combine_file_kp_combined_sd_Y2user_lifetime[i])
                combine_file_kp_individual_unc_avg_Y2user_lifetime[i] = float(combine_file_kp_individual_unc_avg_Y2user_lifetime[i])
                combine_file_keff_combined_sd_Y2user_lifetime[i] = float(combine_file_keff_combined_sd_Y2user_lifetime[i])
                combine_file_keff_individual_unc_avg_Y2user_lifetime[i] = float(combine_file_keff_individual_unc_avg_Y2user_lifetime[i])
            except:
                ValueError

    return combine_file_gatewidth_list, combine_file_Y1_combined, combine_file_Y1_combined_unc, combine_file_Y1_combined_sd, combine_file_Y1_individual_unc_avg, combine_file_Y2_combined, combine_file_Y2_combined_unc, combine_file_Y2_combined_sd, combine_file_Y2_individual_unc_avg, combine_file_R1_combined, combine_file_R1_combined_unc, combine_file_R1_combined_sd, combine_file_R1_individual_unc_avg, combine_file_R2_single_Y2_decay_combined, combine_file_R2_single_Y2_decay_combined_unc, combine_file_R2_single_Y2_decay_combined_sd, combine_file_R2_single_Y2_decay_individual_unc_avg, combine_file_R2_double1_Y2_decay_combined, combine_file_R2_double1_Y2_decay_combined_unc, combine_file_R2_double1_Y2_decay_combined_sd, combine_file_R2_double1_Y2_decay_individual_unc_avg, combine_file_R2_double2_Y2_decay_combined, combine_file_R2_double2_Y2_decay_combined_unc, combine_file_R2_double2_Y2_decay_combined_sd, combine_file_R2_double2_Y2_decay_individual_unc_avg, combine_file_R2_double_both_Y2_decay_combined, combine_file_R2_double_both_Y2_decay_combined_unc, combine_file_R2_double_both_Y2_decay_combined_sd, combine_file_R2_double_both_Y2_decay_individual_unc_avg, combine_file_R2_user_lifetime_combined, combine_file_R2_user_lifetime_combined_unc, combine_file_R2_user_lifetime_combined_sd, combine_file_R2_user_lifetime_individual_unc_avg, combine_file_Ym_combined, combine_file_Ym_combined_unc, combine_file_Ym_combined_sd, combine_file_Ym_individual_unc_avg, combine_file_calc_eff_kn_combined, combine_file_calc_eff_kn_combined_unc, combine_file_calc_eff_kn_combined_sd, combine_file_calc_eff_kn_individual_unc_avg, combine_file_Ml_combined_Y2single, combine_file_Ml_combined_unc_Y2single, combine_file_Ml_combined_sd_Y2single, combine_file_Ml_individual_unc_avg_Y2single, combine_file_Mt_combined_Y2single, combine_file_Mt_combined_unc_Y2single, combine_file_Mt_combined_sd_Y2single, combine_file_Mt_individual_unc_avg_Y2single, combine_file_Fs_combined_Y2single, combine_file_Fs_combined_unc_Y2single, combine_file_Fs_combined_sd_Y2single, combine_file_Fs_individual_unc_avg_Y2single, combine_file_kp_combined_Y2single, combine_file_kp_combined_unc_Y2single, combine_file_kp_combined_sd_Y2single, combine_file_kp_individual_unc_avg_Y2single, combine_file_keff_combined_Y2single, combine_file_keff_combined_unc_Y2single, combine_file_keff_combined_sd_Y2single, combine_file_keff_individual_unc_avg_Y2single, combine_file_Ml_combined_Y2double1, combine_file_Ml_combined_unc_Y2double1, combine_file_Ml_combined_sd_Y2double1, combine_file_Ml_individual_unc_avg_Y2double1, combine_file_Mt_combined_Y2double1, combine_file_Mt_combined_unc_Y2double1, combine_file_Mt_combined_sd_Y2double1, combine_file_Mt_individual_unc_avg_Y2double1, combine_file_Fs_combined_Y2double1, combine_file_Fs_combined_unc_Y2double1, combine_file_Fs_combined_sd_Y2double1, combine_file_Fs_individual_unc_avg_Y2double1, combine_file_kp_combined_Y2double1, combine_file_kp_combined_unc_Y2double1, combine_file_kp_combined_sd_Y2double1, combine_file_kp_individual_unc_avg_Y2double1, combine_file_keff_combined_Y2double1, combine_file_keff_combined_unc_Y2double1, combine_file_keff_combined_sd_Y2double1, combine_file_keff_individual_unc_avg_Y2double1, combine_file_Ml_combined_Y2double2, combine_file_Ml_combined_unc_Y2double2, combine_file_Ml_combined_sd_Y2double2, combine_file_Ml_individual_unc_avg_Y2double2, combine_file_Mt_combined_Y2double2, combine_file_Mt_combined_unc_Y2double2, combine_file_Mt_combined_sd_Y2double2, combine_file_Mt_individual_unc_avg_Y2double2, combine_file_Fs_combined_Y2double2, combine_file_Fs_combined_unc_Y2double2, combine_file_Fs_combined_sd_Y2double2, combine_file_Fs_individual_unc_avg_Y2double2, combine_file_kp_combined_Y2double2, combine_file_kp_combined_unc_Y2double2, combine_file_kp_combined_sd_Y2double2, combine_file_kp_individual_unc_avg_Y2double2, combine_file_keff_combined_Y2double2, combine_file_keff_combined_unc_Y2double2, combine_file_keff_combined_sd_Y2double2, combine_file_keff_individual_unc_avg_Y2double2, combine_file_Ml_combined_Y2double_both, combine_file_Ml_combined_unc_Y2double_both, combine_file_Ml_combined_sd_Y2double_both, combine_file_Ml_individual_unc_avg_Y2double_both, combine_file_Mt_combined_Y2double_both, combine_file_Mt_combined_unc_Y2double_both, combine_file_Mt_combined_sd_Y2double_both, combine_file_Mt_individual_unc_avg_Y2double_both, combine_file_Fs_combined_Y2double_both, combine_file_Fs_combined_unc_Y2double_both, combine_file_Fs_combined_sd_Y2double_both, combine_file_Fs_individual_unc_avg_Y2double_both, combine_file_kp_combined_Y2double_both, combine_file_kp_combined_unc_Y2double_both, combine_file_kp_combined_sd_Y2double_both, combine_file_kp_individual_unc_avg_Y2double_both, combine_file_keff_combined_Y2double_both, combine_file_keff_combined_unc_Y2double_both, combine_file_keff_combined_sd_Y2double_both, combine_file_keff_individual_unc_avg_Y2double_both, combine_file_Ml_combined_Y2user_lifetime, combine_file_Ml_combined_unc_Y2user_lifetime, combine_file_Ml_combined_sd_Y2user_lifetime, combine_file_Ml_individual_unc_avg_Y2user_lifetime, combine_file_Mt_combined_Y2user_lifetime, combine_file_Mt_combined_unc_Y2user_lifetime, combine_file_Mt_combined_sd_Y2user_lifetime, combine_file_Mt_individual_unc_avg_Y2user_lifetime, combine_file_Fs_combined_Y2user_lifetime, combine_file_Fs_combined_unc_Y2user_lifetime, combine_file_Fs_combined_sd_Y2user_lifetime, combine_file_Fs_individual_unc_avg_Y2user_lifetime, combine_file_kp_combined_Y2user_lifetime, combine_file_kp_combined_unc_Y2user_lifetime, combine_file_kp_combined_sd_Y2user_lifetime, combine_file_kp_individual_unc_avg_Y2user_lifetime, combine_file_keff_combined_Y2user_lifetime, combine_file_keff_combined_unc_Y2user_lifetime, combine_file_keff_combined_sd_Y2user_lifetime, combine_file_keff_individual_unc_avg_Y2user_lifetime


def sum_prepare(sum_histogram_filepath, current_save_path, calculation_type, perform_Y2_single_fit, perform_Y2_double_fit, use_user_specified_lifetime, sumfile=True):
    
    # reads sum file
    if sumfile == True:
        sum_f = open(sum_histogram_filepath+'/Histogram_Sum_Rates.csv')
    else:
        sum_f = open(sum_histogram_filepath)

    csv_sum_f = csv.reader(sum_f)
    
    sum_file_gatewidth_list = []
    sum_file_first_reduced_factorial_moment_sum_list = []
    sum_file_second_reduced_factorial_moment_sum_list = []
    sum_file_third_reduced_factorial_moment_sum_list = []
    sum_file_fourth_reduced_factorial_moment_sum_list = []
    sum_file_first_factorial_moment_sum_list = []
    sum_file_second_factorial_moment_sum_list = []
    sum_file_third_factorial_moment_sum_list = []
    sum_file_fourth_factorial_moment_sum_list = []
    sum_file_Y1_sum_list = []
    sum_file_dY1_sum_list = []
    sum_file_Y2_sum_list = []
    sum_file_dY2_sum_list = []
    sum_file_R1_sum_list = []
    sum_file_dR1_sum_list = []
    sum_file_fit1log_A = []
    sum_file_fit1log_A_unc = []
    sum_file_fit1log_B = []
    sum_file_fit1log_B_unc = []
    sum_file_fit1log_det_lifetime = []
    sum_file_fit1log_det_lifetime_unc = []
    sum_file_omega2_single_results = []
    sum_file_R2_single_Y2_decay = []
    sum_file_R2_unc_single_Y2_decay = []
    sum_file_fit2log_A = []
    sum_file_fit2log_A_unc = []
    sum_file_fit2log_B = []
    sum_file_fit2log_B_unc = []
    sum_file_fit2log_C = []
    sum_file_fit2log_C_unc = []
    sum_file_fit2log_D = []
    sum_file_fit2log_D_unc = []
    sum_file_fit2log_det_lifetime1 = []
    sum_file_fit2log_det_lifetime1_unc = []
    sum_file_fit2log_det_lifetime2 = []
    sum_file_fit2log_det_lifetime2_unc = []
    sum_file_omega2_double1_results = []
    sum_file_R2_double1_Y2_decay = []
    sum_file_R2_unc_double1_Y2_decay = []
    sum_file_omega2_double2_results = []
    sum_file_R2_double2_Y2_decay = []
    sum_file_R2_unc_double2_Y2_decay = []
    sum_file_R2_double_both_Y2_decay = []
    sum_file_R2_unc_double_both_Y2_decay = []
    sum_file_omega2_lifetime_user_results = []
    sum_file_R2_user_lifetime = []
    sum_file_R2_unc_user_lifetime = []
    sum_file_Ym_list = []
    sum_file_dYm_list = []
    sum_file_calc_eff_kn_sum_list = []
    sum_file_calc_eff_unc_kn_sum_list = []
    sum_file_Ml_Y2single_sum_list = []
    sum_file_dMl_Y2single_sum_list = []
    sum_file_Mt_Y2single_sum_list = []
    sum_file_dMt_Y2single_sum_list = []
    sum_file_Fs_Y2single_sum_list = []
    sum_file_dFs_Y2single_sum_list = []
    sum_file_kp_Y2single_sum_list = []
    sum_file_dkp_Y2single_sum_list = []
    sum_file_keff_Y2single_sum_list = []
    sum_file_dkeff_Y2single_sum_list = []
    sum_file_Ml_Y2double1_sum_list = []
    sum_file_dMl_Y2double1_sum_list = []
    sum_file_Mt_Y2double1_sum_list = []
    sum_file_dMt_Y2double1_sum_list = []
    sum_file_Fs_Y2double1_sum_list = []
    sum_file_dFs_Y2double1_sum_list = []
    sum_file_kp_Y2double1_sum_list = []
    sum_file_dkp_Y2double1_sum_list = []
    sum_file_keff_Y2double1_sum_list = []
    sum_file_dkeff_Y2double1_sum_list = []
    sum_file_Ml_Y2double2_sum_list = []
    sum_file_dMl_Y2double2_sum_list = []
    sum_file_Mt_Y2double2_sum_list = []
    sum_file_dMt_Y2double2_sum_list = []
    sum_file_Fs_Y2double2_sum_list = []
    sum_file_dFs_Y2double2_sum_list = []
    sum_file_kp_Y2double2_sum_list = []
    sum_file_dkp_Y2double2_sum_list = []
    sum_file_keff_Y2double2_sum_list = []
    sum_file_dkeff_Y2double2_sum_list = []
    sum_file_Ml_Y2double_both_sum_list = []
    sum_file_dMl_Y2double_both_sum_list = []
    sum_file_Mt_Y2double_both_sum_list = []
    sum_file_dMt_Y2double_both_sum_list = []
    sum_file_Fs_Y2double_both_sum_list = []
    sum_file_dFs_Y2double_both_sum_list = []
    sum_file_kp_Y2double_both_sum_list = []
    sum_file_dkp_Y2double_both_sum_list = []
    sum_file_keff_Y2double_both_sum_list = []
    sum_file_dkeff_Y2double_both_sum_list = []
    sum_file_Ml_Y2user_lifetime_sum_list = []
    sum_file_dMl_Y2user_lifetime_sum_list = []
    sum_file_Mt_Y2user_lifetime_sum_list = []
    sum_file_dMt_Y2user_lifetime_sum_list = []
    sum_file_Fs_Y2user_lifetime_sum_list = []
    sum_file_dFs_Y2user_lifetime_sum_list = []
    sum_file_kp_Y2user_lifetime_sum_list = []
    sum_file_dkp_Y2user_lifetime_sum_list = []
    sum_file_keff_Y2user_lifetime_sum_list = []
    sum_file_dkeff_Y2user_lifetime_sum_list = []
    
    # reads in csv and gets the columns
    for row in csv_sum_f:
        
        sum_file_gatewidth_list.append(row[0])
        sum_file_first_reduced_factorial_moment_sum_list.append(row[1])
        sum_file_second_reduced_factorial_moment_sum_list.append(row[2])
        sum_file_third_reduced_factorial_moment_sum_list.append(row[3])
        sum_file_fourth_reduced_factorial_moment_sum_list.append(row[4])
        sum_file_first_factorial_moment_sum_list.append(row[5])
        sum_file_second_factorial_moment_sum_list.append(row[6])
        sum_file_third_factorial_moment_sum_list.append(row[7])
        sum_file_fourth_factorial_moment_sum_list.append(row[8])
        sum_file_Y1_sum_list.append(row[9])
        sum_file_dY1_sum_list.append(row[10])
        sum_file_Y2_sum_list.append(row[11])
        sum_file_dY2_sum_list.append(row[12])
        sum_file_R1_sum_list.append(row[13])
        sum_file_dR1_sum_list.append(row[14])
        sum_file_fit1log_A.append(row[15])
        sum_file_fit1log_A_unc.append(row[16])
        sum_file_fit1log_B.append(row[17])
        sum_file_fit1log_B_unc.append(row[18])
        sum_file_fit1log_det_lifetime.append(row[19])
        sum_file_fit1log_det_lifetime_unc.append(row[20])
        sum_file_omega2_single_results.append(row[21])
        sum_file_R2_single_Y2_decay.append(row[22])
        sum_file_R2_unc_single_Y2_decay.append(row[23])
        sum_file_fit2log_A.append(row[24])
        sum_file_fit2log_A_unc.append(row[25])
        sum_file_fit2log_B.append(row[26])
        sum_file_fit2log_B_unc.append(row[27])
        sum_file_fit2log_C.append(row[28])
        sum_file_fit2log_C_unc.append(row[29])
        sum_file_fit2log_D.append(row[30])
        sum_file_fit2log_D_unc.append(row[31])
        sum_file_fit2log_det_lifetime1.append(row[32])
        sum_file_fit2log_det_lifetime1_unc.append(row[33])
        sum_file_fit2log_det_lifetime2.append(row[34])
        sum_file_fit2log_det_lifetime2_unc.append(row[35])
        sum_file_omega2_double1_results.append(row[36])
        sum_file_R2_double1_Y2_decay.append(row[37])
        sum_file_R2_unc_double1_Y2_decay.append(row[38])
        sum_file_omega2_double2_results.append(row[39])
        sum_file_R2_double2_Y2_decay.append(row[40])
        sum_file_R2_unc_double2_Y2_decay.append(row[41])
        sum_file_R2_double_both_Y2_decay.append(row[42])
        sum_file_R2_unc_double_both_Y2_decay.append(row[43])
        sum_file_omega2_lifetime_user_results.append(row[44])
        sum_file_R2_user_lifetime.append(row[45])
        sum_file_R2_unc_user_lifetime.append(row[46])
        sum_file_Ym_list.append(row[47])
        sum_file_dYm_list.append(row[48])
        if calculation_type == 'Cf':
            sum_file_calc_eff_kn_sum_list.append(row[49])
            sum_file_calc_eff_unc_kn_sum_list.append(row[50])
        elif calculation_type == 'Multiplicity':
            if perform_Y2_single_fit == True:
                sum_file_Ml_Y2single_sum_list.append(row[49])
                sum_file_dMl_Y2single_sum_list.append(row[50])
                sum_file_Fs_Y2single_sum_list.append(row[51])
                sum_file_dFs_Y2single_sum_list.append(row[52])
                sum_file_Mt_Y2single_sum_list.append(row[53])
                sum_file_dMt_Y2single_sum_list.append(row[54])
                sum_file_kp_Y2single_sum_list.append(row[55])
                sum_file_dkp_Y2single_sum_list.append(row[56])
                sum_file_keff_Y2single_sum_list.append(row[57])
                sum_file_dkeff_Y2single_sum_list.append(row[58])
            if perform_Y2_double_fit == True:
                if perform_Y2_single_fit == True:
                    start_column = 59
                else:
                    start_column = 49
                sum_file_Ml_Y2double1_sum_list.append(row[start_column])
                sum_file_dMl_Y2double1_sum_list.append(row[start_column+1])
                sum_file_Fs_Y2double1_sum_list.append(row[start_column+2])
                sum_file_dFs_Y2double1_sum_list.append(row[start_column+3])
                sum_file_Mt_Y2double1_sum_list.append(row[start_column+4])
                sum_file_dMt_Y2double1_sum_list.append(row[start_column+5])
                sum_file_kp_Y2double1_sum_list.append(row[start_column+6])
                sum_file_dkp_Y2double1_sum_list.append(row[start_column+7])
                sum_file_keff_Y2double1_sum_list.append(row[start_column+8])
                sum_file_dkeff_Y2double1_sum_list.append(row[start_column+9])
                sum_file_Ml_Y2double2_sum_list.append(row[start_column+10])
                sum_file_dMl_Y2double2_sum_list.append(row[start_column+11])
                sum_file_Fs_Y2double2_sum_list.append(row[start_column+12])
                sum_file_dFs_Y2double2_sum_list.append(row[start_column+13])
                sum_file_Mt_Y2double2_sum_list.append(row[start_column+14])
                sum_file_dMt_Y2double2_sum_list.append(row[start_column+15])
                sum_file_kp_Y2double2_sum_list.append(row[start_column+16])
                sum_file_dkp_Y2double2_sum_list.append(row[start_column+17])
                sum_file_keff_Y2double2_sum_list.append(row[start_column+18])
                sum_file_dkeff_Y2double2_sum_list.append(row[start_column+19])
                sum_file_Ml_Y2double_both_sum_list.append(row[start_column+20])
                sum_file_dMl_Y2double_both_sum_list.append(row[start_column+21])
                sum_file_Fs_Y2double_both_sum_list.append(row[start_column+22])
                sum_file_dFs_Y2double_both_sum_list.append(row[start_column+23])
                sum_file_Mt_Y2double_both_sum_list.append(row[start_column+24])
                sum_file_dMt_Y2double_both_sum_list.append(row[start_column+25])
                sum_file_kp_Y2double_both_sum_list.append(row[start_column+26])
                sum_file_dkp_Y2double_both_sum_list.append(row[start_column+27])
                sum_file_keff_Y2double_both_sum_list.append(row[start_column+28])
                sum_file_dkeff_Y2double_both_sum_list.append(row[start_column+29])
            if use_user_specified_lifetime == True:
                if perform_Y2_single_fit == True and perform_Y2_double_fit == True:
                    start_column = 89
                elif perform_Y2_single_fit == True:
                    start_column = 59
                elif perform_Y2_double_fit == True:
                    start_column = 79
                else:
                    start_column = 49
                sum_file_Ml_Y2user_lifetime_sum_list.append(row[start_column])
                sum_file_dMl_Y2user_lifetime_sum_list.append(row[start_column+1])
                sum_file_Fs_Y2user_lifetime_sum_list.append(row[start_column+2])
                sum_file_dFs_Y2user_lifetime_sum_list.append(row[start_column+3])
                sum_file_Mt_Y2user_lifetime_sum_list.append(row[start_column+4])
                sum_file_dMt_Y2user_lifetime_sum_list.append(row[start_column+5])
                sum_file_kp_Y2user_lifetime_sum_list.append(row[start_column+6])
                sum_file_dkp_Y2user_lifetime_sum_list.append(row[start_column+7])
                sum_file_keff_Y2user_lifetime_sum_list.append(row[start_column+8])
                sum_file_dkeff_Y2user_lifetime_sum_list.append(row[start_column+9])
        
    
    # delete first row from list  
    del sum_file_gatewidth_list[0]
    del sum_file_first_reduced_factorial_moment_sum_list[0]
    del sum_file_second_reduced_factorial_moment_sum_list[0]
    del sum_file_third_reduced_factorial_moment_sum_list[0]
    del sum_file_fourth_reduced_factorial_moment_sum_list[0]
    del sum_file_first_factorial_moment_sum_list[0]
    del sum_file_second_factorial_moment_sum_list[0]
    del sum_file_third_factorial_moment_sum_list[0]
    del sum_file_fourth_factorial_moment_sum_list[0]
    del sum_file_Y1_sum_list[0]
    del sum_file_dY1_sum_list[0]
    del sum_file_Y2_sum_list[0]
    del sum_file_dY2_sum_list[0]
    del sum_file_R1_sum_list[0]
    del sum_file_dR1_sum_list[0]
    del sum_file_fit1log_A[0]
    del sum_file_fit1log_A_unc[0]
    del sum_file_fit1log_B[0]
    del sum_file_fit1log_B_unc[0]
    del sum_file_fit1log_det_lifetime[0]
    del sum_file_fit1log_det_lifetime_unc[0]
    del sum_file_omega2_single_results[0]
    del sum_file_R2_single_Y2_decay[0]
    del sum_file_R2_unc_single_Y2_decay[0]
    del sum_file_fit2log_A[0]
    del sum_file_fit2log_A_unc[0]
    del sum_file_fit2log_B[0]
    del sum_file_fit2log_B_unc[0]
    del sum_file_fit2log_C[0]
    del sum_file_fit2log_C_unc[0]
    del sum_file_fit2log_D[0]
    del sum_file_fit2log_D_unc[0]
    del sum_file_fit2log_det_lifetime1[0]
    del sum_file_fit2log_det_lifetime1_unc[0]
    del sum_file_fit2log_det_lifetime2[0]
    del sum_file_fit2log_det_lifetime2_unc[0]
    del sum_file_omega2_double1_results[0]
    del sum_file_R2_double1_Y2_decay[0]
    del sum_file_R2_unc_double1_Y2_decay[0]
    del sum_file_omega2_double2_results[0]
    del sum_file_R2_double2_Y2_decay[0]
    del sum_file_R2_unc_double2_Y2_decay[0]
    del sum_file_R2_double_both_Y2_decay[0]
    del sum_file_R2_unc_double_both_Y2_decay[0]
    del sum_file_omega2_lifetime_user_results[0]
    del sum_file_R2_user_lifetime[0]
    del sum_file_R2_unc_user_lifetime[0]
    del sum_file_Ym_list[0]
    del sum_file_dYm_list[0]
    if calculation_type == 'Cf':
        del sum_file_calc_eff_kn_sum_list[0]
        del sum_file_calc_eff_unc_kn_sum_list[0]
    elif calculation_type == 'Multiplicity':
        if perform_Y2_single_fit == True:
            del sum_file_Ml_Y2single_sum_list[0]
            del sum_file_dMl_Y2single_sum_list[0]
            del sum_file_Mt_Y2single_sum_list[0]
            del sum_file_dMt_Y2single_sum_list[0]
            del sum_file_Fs_Y2single_sum_list[0]
            del sum_file_dFs_Y2single_sum_list[0]
            del sum_file_kp_Y2single_sum_list[0]
            del sum_file_dkp_Y2single_sum_list[0]
            del sum_file_keff_Y2single_sum_list[0]
            del sum_file_dkeff_Y2single_sum_list[0]
        if perform_Y2_double_fit == True:
            del sum_file_Ml_Y2double1_sum_list[0]
            del sum_file_dMl_Y2double1_sum_list[0]
            del sum_file_Mt_Y2double1_sum_list[0]
            del sum_file_dMt_Y2double1_sum_list[0]
            del sum_file_Fs_Y2double1_sum_list[0]
            del sum_file_dFs_Y2double1_sum_list[0]
            del sum_file_kp_Y2double1_sum_list[0]
            del sum_file_dkp_Y2double1_sum_list[0]
            del sum_file_keff_Y2double1_sum_list[0]
            del sum_file_dkeff_Y2double1_sum_list[0]
            del sum_file_Ml_Y2double2_sum_list[0]
            del sum_file_dMl_Y2double2_sum_list[0]
            del sum_file_Mt_Y2double2_sum_list[0]
            del sum_file_dMt_Y2double2_sum_list[0]
            del sum_file_Fs_Y2double2_sum_list[0]
            del sum_file_dFs_Y2double2_sum_list[0]
            del sum_file_kp_Y2double2_sum_list[0]
            del sum_file_dkp_Y2double2_sum_list[0]
            del sum_file_keff_Y2double2_sum_list[0]
            del sum_file_dkeff_Y2double2_sum_list[0]
            del sum_file_Ml_Y2double_both_sum_list[0]
            del sum_file_dMl_Y2double_both_sum_list[0]
            del sum_file_Mt_Y2double_both_sum_list[0]
            del sum_file_dMt_Y2double_both_sum_list[0]
            del sum_file_Fs_Y2double_both_sum_list[0]
            del sum_file_dFs_Y2double_both_sum_list[0]
            del sum_file_kp_Y2double_both_sum_list[0]
            del sum_file_dkp_Y2double_both_sum_list[0]
            del sum_file_keff_Y2double_both_sum_list[0]
            del sum_file_dkeff_Y2double_both_sum_list[0]
        if use_user_specified_lifetime == True:
            del sum_file_Ml_Y2user_lifetime_sum_list[0]
            del sum_file_dMl_Y2user_lifetime_sum_list[0]
            del sum_file_Mt_Y2user_lifetime_sum_list[0]
            del sum_file_dMt_Y2user_lifetime_sum_list[0]
            del sum_file_Fs_Y2user_lifetime_sum_list[0]
            del sum_file_dFs_Y2user_lifetime_sum_list[0]
            del sum_file_kp_Y2user_lifetime_sum_list[0]
            del sum_file_dkp_Y2user_lifetime_sum_list[0]
            del sum_file_keff_Y2user_lifetime_sum_list[0]
            del sum_file_dkeff_Y2user_lifetime_sum_list[0]
    
    # converts to correct type
    for i in range(0,len(sum_file_gatewidth_list)):
        try:
            sum_file_gatewidth_list[i] = int(sum_file_gatewidth_list[i])
        except:
            ValueError
        try:
            sum_file_first_reduced_factorial_moment_sum_list[i] = float(sum_file_first_reduced_factorial_moment_sum_list[i])
            sum_file_second_reduced_factorial_moment_sum_list[i] = float(sum_file_second_reduced_factorial_moment_sum_list[i])
            sum_file_third_reduced_factorial_moment_sum_list[i] = float(sum_file_third_reduced_factorial_moment_sum_list[i])
            sum_file_fourth_reduced_factorial_moment_sum_list[i] = float(sum_file_fourth_reduced_factorial_moment_sum_list[i])
        except:
            ValueError
        try:
            sum_file_first_factorial_moment_sum_list[i] = float(sum_file_first_factorial_moment_sum_list[i])
            sum_file_second_factorial_moment_sum_list[i] = float(sum_file_second_factorial_moment_sum_list[i])
            sum_file_third_factorial_moment_sum_list[i] = float(sum_file_third_factorial_moment_sum_list[i])
            sum_file_fourth_factorial_moment_sum_list[i] = float(sum_file_fourth_factorial_moment_sum_list[i])
        except:
            ValueError
        try:
            sum_file_Y1_sum_list[i] = float(sum_file_Y1_sum_list[i])
            sum_file_dY1_sum_list[i] = float(sum_file_dY1_sum_list[i])
        except:
            ValueError
        try:
            sum_file_Y2_sum_list[i] = float(sum_file_Y2_sum_list[i])
            sum_file_dY2_sum_list[i] = float(sum_file_dY2_sum_list[i])
        except:
            ValueError
        try:
            sum_file_R1_sum_list[i] = float(sum_file_R1_sum_list[i])
            sum_file_dR1_sum_list[i] = float(sum_file_dR1_sum_list[i])
        except:
            ValueError
        try:
            sum_file_fit1log_A[i] = float(sum_file_fit1log_A[i])
            sum_file_fit1log_A_unc[i] = float(sum_file_fit1log_A_unc[i])
            sum_file_fit1log_B[i] = float(sum_file_fit1log_B[i])
            sum_file_fit1log_B_unc[i] = float(sum_file_fit1log_B_unc[i])
            sum_file_fit1log_det_lifetime[i] = float(sum_file_fit1log_det_lifetime[i])
            sum_file_fit1log_det_lifetime_unc[i] = float(sum_file_fit1log_det_lifetime_unc[i])
            sum_file_omega2_single_results[i] = float(sum_file_omega2_single_results[i])
            sum_file_R2_single_Y2_decay[i] = float(sum_file_R2_single_Y2_decay[i])
            sum_file_R2_unc_single_Y2_decay[i] = float(sum_file_R2_unc_single_Y2_decay[i])
        except:
            ValueError
        try:
            sum_file_fit2log_A[i] = float(sum_file_fit2log_A[i])
            sum_file_fit2log_A_unc[i] = float(sum_file_fit2log_A_unc[i])
            sum_file_fit2log_B[i] = float(sum_file_fit2log_B[i])
            sum_file_fit2log_B_unc[i] = float(sum_file_fit2log_B_unc[i])
            sum_file_fit2log_C[i] = float(sum_file_fit2log_C[i])
            sum_file_fit2log_C_unc[i] = float(sum_file_fit2log_C_unc[i])
            sum_file_fit2log_D[i] = float(sum_file_fit2log_D[i])
            sum_file_fit2log_D_unc[i] = float(sum_file_fit2log_D_unc[i])
            sum_file_fit2log_det_lifetime1[i] = float(sum_file_fit2log_det_lifetime1[i])
            sum_file_fit2log_det_lifetime1_unc[i] = float(sum_file_fit2log_det_lifetime1_unc[i])
            sum_file_fit2log_det_lifetime2[i] = float(sum_file_fit2log_det_lifetime2[i])
            sum_file_fit2log_det_lifetime2_unc[i] = float(sum_file_fit2log_det_lifetime2_unc[i])
            sum_file_omega2_double1_results[i] = float(sum_file_omega2_double1_results[i])
            sum_file_R2_double1_Y2_decay[i] = float(sum_file_R2_double1_Y2_decay[i])
            sum_file_R2_unc_double1_Y2_decay[i] = float(sum_file_R2_unc_double1_Y2_decay[i])
            sum_file_omega2_double2_results[i] = float(sum_file_omega2_double2_results[i])
            sum_file_R2_double2_Y2_decay[i] = float(sum_file_R2_double2_Y2_decay[i])
            sum_file_R2_unc_double2_Y2_decay[i] = float(sum_file_R2_unc_double2_Y2_decay[i])
            sum_file_R2_double_both_Y2_decay[i] = float(sum_file_R2_double_both_Y2_decay[i])
            sum_file_R2_unc_double_both_Y2_decay[i] = float(sum_file_R2_unc_double_both_Y2_decay[i])
        except:
            ValueError
        try:
            sum_file_omega2_lifetime_user_results[i] = float(sum_file_omega2_lifetime_user_results[i])
            sum_file_R2_user_lifetime[i] = float(sum_file_R2_user_lifetime[i])
            sum_file_R2_unc_user_lifetime[i] = float(sum_file_R2_unc_user_lifetime[i])
        except:
            ValueError
        try:
            sum_file_Ym_list[i] = float(sum_file_Ym_list[i])
            sum_file_dYm_list[i] = float(sum_file_dYm_list[i])
        except:
            ValueError
        if calculation_type == 'Cf':
            try:
                sum_file_calc_eff_kn_sum_list[i] = float(sum_file_calc_eff_kn_sum_list[i])
                sum_file_calc_eff_unc_kn_sum_list[i] = float(sum_file_calc_eff_unc_kn_sum_list[i])
            except:
                ValueError
        elif calculation_type == 'Multiplicity':
            if perform_Y2_single_fit == True:
                try:
                    sum_file_Ml_Y2single_sum_list[i] = float(sum_file_Ml_Y2single_sum_list[i])
                    sum_file_dMl_Y2single_sum_list[i] = float(sum_file_dMl_Y2single_sum_list[i])
                    sum_file_Mt_Y2single_sum_list[i] = float(sum_file_Mt_Y2single_sum_list[i])
                    sum_file_dMt_Y2single_sum_list[i] = float(sum_file_dMt_Y2single_sum_list[i])
                    sum_file_Fs_Y2single_sum_list[i] = float(sum_file_Fs_Y2single_sum_list[i])
                    sum_file_dFs_Y2single_sum_list[i] = float(sum_file_dFs_Y2single_sum_list[i])
                    sum_file_kp_Y2single_sum_list[i] = float(sum_file_kp_Y2single_sum_list[i])
                    sum_file_dkp_Y2single_sum_list[i] = float(sum_file_dkp_Y2single_sum_list[i])
                    sum_file_keff_Y2single_sum_list[i] = float(sum_file_keff_Y2single_sum_list[i])
                    sum_file_dkeff_Y2single_sum_list[i] = float(sum_file_dkeff_Y2single_sum_list[i])
                except:
                    ValueError
            if perform_Y2_double_fit == True:
                try:
                    sum_file_Ml_Y2double1_sum_list[i] = float(sum_file_Ml_Y2double1_sum_list[i])
                    sum_file_dMl_Y2double1_sum_list[i] = float(sum_file_dMl_Y2double1_sum_list[i])
                    sum_file_Mt_Y2double1_sum_list[i] = float(sum_file_Mt_Y2double1_sum_list[i])
                    sum_file_dMt_Y2double1_sum_list[i] = float(sum_file_dMt_Y2double1_sum_list[i])
                    sum_file_Fs_Y2double1_sum_list[i] = float(sum_file_Fs_Y2double1_sum_list[i])
                    sum_file_dFs_Y2double1_sum_list[i] = float(sum_file_dFs_Y2double1_sum_list[i])
                    sum_file_kp_Y2double1_sum_list[i] = float(sum_file_kp_Y2double1_sum_list[i])
                    sum_file_dkp_Y2double1_sum_list[i] = float(sum_file_dkp_Y2double1_sum_list[i])
                    sum_file_keff_Y2double1_sum_list[i] = float(sum_file_keff_Y2double1_sum_list[i])
                    sum_file_dkeff_Y2double1_sum_list[i] = float(sum_file_dkeff_Y2double1_sum_list[i])
                    sum_file_Ml_Y2double2_sum_list[i] = float(sum_file_Ml_Y2double2_sum_list[i])
                    sum_file_dMl_Y2double2_sum_list[i] = float(sum_file_dMl_Y2double2_sum_list[i])
                    sum_file_Mt_Y2double2_sum_list[i] = float(sum_file_Mt_Y2double2_sum_list[i])
                    sum_file_dMt_Y2double2_sum_list[i] = float(sum_file_dMt_Y2double2_sum_list[i])
                    sum_file_Fs_Y2double2_sum_list[i] = float(sum_file_Fs_Y2double2_sum_list[i])
                    sum_file_dFs_Y2double2_sum_list[i] = float(sum_file_dFs_Y2double2_sum_list[i])
                    sum_file_kp_Y2double2_sum_list[i] = float(sum_file_kp_Y2double2_sum_list[i])
                    sum_file_dkp_Y2double2_sum_list[i] = float(sum_file_dkp_Y2double2_sum_list[i])
                    sum_file_keff_Y2double2_sum_list[i] = float(sum_file_keff_Y2double2_sum_list[i])
                    sum_file_dkeff_Y2double2_sum_list[i] = float(sum_file_dkeff_Y2double2_sum_list[i])
                    sum_file_Ml_Y2double_both_sum_list[i] = float(sum_file_Ml_Y2double_both_sum_list[i])
                    sum_file_dMl_Y2double_both_sum_list[i] = float(sum_file_dMl_Y2double_both_sum_list[i])
                    sum_file_Mt_Y2double_both_sum_list[i] = float(sum_file_Mt_Y2double_both_sum_list[i])
                    sum_file_dMt_Y2double_both_sum_list[i] = float(sum_file_dMt_Y2double_both_sum_list[i])
                    sum_file_Fs_Y2double_both_sum_list[i] = float(sum_file_Fs_Y2double_both_sum_list[i])
                    sum_file_dFs_Y2double_both_sum_list[i] = float(sum_file_dFs_Y2double_both_sum_list[i])
                    sum_file_kp_Y2double_both_sum_list[i] = float(sum_file_kp_Y2double_both_sum_list[i])
                    sum_file_dkp_Y2double_both_sum_list[i] = float(sum_file_dkp_Y2double_both_sum_list[i])
                    sum_file_keff_Y2double_both_sum_list[i] = float(sum_file_keff_Y2double_both_sum_list[i])
                    sum_file_dkeff_Y2double_both_sum_list[i] = float(sum_file_dkeff_Y2double_both_sum_list[i])
                except:
                    ValueError
            if use_user_specified_lifetime == True:
                try:
                    sum_file_Ml_Y2user_lifetime_sum_list[i] = float(sum_file_Ml_Y2user_lifetime_sum_list[i])
                    sum_file_dMl_Y2user_lifetime_sum_list[i] = float(sum_file_dMl_Y2user_lifetime_sum_list[i])
                    sum_file_Mt_Y2user_lifetime_sum_list[i] = float(sum_file_Mt_Y2user_lifetime_sum_list[i])
                    sum_file_dMt_Y2user_lifetime_sum_list[i] = float(sum_file_dMt_Y2user_lifetime_sum_list[i])
                    sum_file_Fs_Y2user_lifetime_sum_list[i] = float(sum_file_Fs_Y2user_lifetime_sum_list[i])
                    sum_file_dFs_Y2user_lifetime_sum_list[i] = float(sum_file_dFs_Y2user_lifetime_sum_list[i])
                    sum_file_kp_Y2user_lifetime_sum_list[i] = float(sum_file_kp_Y2user_lifetime_sum_list[i])
                    sum_file_dkp_Y2user_lifetime_sum_list[i] = float(sum_file_dkp_Y2user_lifetime_sum_list[i])
                    sum_file_keff_Y2user_lifetime_sum_list[i] = float(sum_file_keff_Y2user_lifetime_sum_list[i])
                    sum_file_dkeff_Y2user_lifetime_sum_lis[i] = float(sum_file_dkeff_Y2user_lifetime_sum_lis[i])
                except:
                    ValueError
    
    return sum_file_gatewidth_list, sum_file_first_reduced_factorial_moment_sum_list, sum_file_second_reduced_factorial_moment_sum_list, sum_file_third_reduced_factorial_moment_sum_list, sum_file_fourth_reduced_factorial_moment_sum_list, sum_file_first_factorial_moment_sum_list, sum_file_second_factorial_moment_sum_list, sum_file_third_factorial_moment_sum_list, sum_file_fourth_factorial_moment_sum_list, sum_file_Y1_sum_list, sum_file_dY1_sum_list, sum_file_Y2_sum_list, sum_file_dY2_sum_list, sum_file_R1_sum_list, sum_file_dR1_sum_list, sum_file_fit1log_A, sum_file_fit1log_A_unc, sum_file_fit1log_B, sum_file_fit1log_B_unc, sum_file_fit1log_det_lifetime, sum_file_fit1log_det_lifetime_unc, sum_file_omega2_single_results, sum_file_R2_single_Y2_decay, sum_file_R2_unc_single_Y2_decay, sum_file_fit2log_A, sum_file_fit2log_A_unc, sum_file_fit2log_B, sum_file_fit2log_B_unc, sum_file_fit2log_C, sum_file_fit2log_C_unc, sum_file_fit2log_D, sum_file_fit2log_D_unc, sum_file_fit2log_det_lifetime1, sum_file_fit2log_det_lifetime1_unc, sum_file_fit2log_det_lifetime2, sum_file_fit2log_det_lifetime2_unc, sum_file_omega2_double1_results, sum_file_R2_double1_Y2_decay, sum_file_R2_unc_double1_Y2_decay, sum_file_omega2_double2_results, sum_file_R2_double2_Y2_decay, sum_file_R2_unc_double2_Y2_decay, sum_file_R2_double_both_Y2_decay, sum_file_R2_unc_double_both_Y2_decay, sum_file_omega2_lifetime_user_results, sum_file_R2_user_lifetime, sum_file_R2_unc_user_lifetime, sum_file_Ym_list, sum_file_dYm_list, sum_file_calc_eff_kn_sum_list, sum_file_calc_eff_unc_kn_sum_list, sum_file_Ml_Y2single_sum_list, sum_file_dMl_Y2single_sum_list, sum_file_Mt_Y2single_sum_list, sum_file_dMt_Y2single_sum_list, sum_file_Fs_Y2single_sum_list, sum_file_dFs_Y2single_sum_list, sum_file_kp_Y2single_sum_list, sum_file_dkp_Y2single_sum_list, sum_file_keff_Y2single_sum_list, sum_file_dkeff_Y2single_sum_list, sum_file_Ml_Y2double1_sum_list, sum_file_dMl_Y2double1_sum_list, sum_file_Mt_Y2double1_sum_list, sum_file_dMt_Y2double1_sum_list, sum_file_Fs_Y2double1_sum_list, sum_file_dFs_Y2double1_sum_list, sum_file_kp_Y2double1_sum_list, sum_file_dkp_Y2double1_sum_list, sum_file_keff_Y2double1_sum_list, sum_file_dkeff_Y2double1_sum_list, sum_file_Ml_Y2double2_sum_list, sum_file_dMl_Y2double2_sum_list, sum_file_Mt_Y2double2_sum_list, sum_file_dMt_Y2double2_sum_list, sum_file_Fs_Y2double2_sum_list, sum_file_dFs_Y2double2_sum_list, sum_file_kp_Y2double2_sum_list, sum_file_dkp_Y2double2_sum_list, sum_file_keff_Y2double2_sum_list, sum_file_dkeff_Y2double2_sum_list, sum_file_Ml_Y2double_both_sum_list, sum_file_dMl_Y2double_both_sum_list, sum_file_Mt_Y2double_both_sum_list, sum_file_dMt_Y2double_both_sum_list, sum_file_Fs_Y2double_both_sum_list, sum_file_dFs_Y2double_both_sum_list, sum_file_kp_Y2double_both_sum_list, sum_file_dkp_Y2double_both_sum_list, sum_file_keff_Y2double_both_sum_list, sum_file_dkeff_Y2double_both_sum_list, sum_file_Ml_Y2user_lifetime_sum_list, sum_file_dMl_Y2user_lifetime_sum_list, sum_file_Mt_Y2user_lifetime_sum_list, sum_file_dMt_Y2user_lifetime_sum_list, sum_file_Fs_Y2user_lifetime_sum_list, sum_file_dFs_Y2user_lifetime_sum_list, sum_file_kp_Y2user_lifetime_sum_list, sum_file_dkp_Y2user_lifetime_sum_list, sum_file_keff_Y2user_lifetime_sum_list, sum_file_dkeff_Y2user_lifetime_sum_list

    
def compare_combine_sum(combine_Y2_rate_results_filepath, sum_histogram_filepath,current_save_path, calculation_type, perform_Y2_single_fit, perform_Y2_double_fit, use_user_specified_lifetime):
    
    combine_file_gatewidth_list, combine_file_Y1_combined, combine_file_Y1_combined_unc, combine_file_Y1_combined_sd, combine_file_Y1_individual_unc_avg, combine_file_Y2_combined, combine_file_Y2_combined_unc, combine_file_Y2_combined_sd, combine_file_Y2_individual_unc_avg, combine_file_R1_combined, combine_file_R1_combined_unc, combine_file_R1_combined_sd, combine_file_R1_individual_unc_avg, combine_file_R2_single_Y2_decay_combined, combine_file_R2_single_Y2_decay_combined_unc, combine_file_R2_single_Y2_decay_combined_sd, combine_file_R2_single_Y2_decay_individual_unc_avg, combine_file_R2_double1_Y2_decay_combined, combine_file_R2_double1_Y2_decay_combined_unc, combine_file_R2_double1_Y2_decay_combined_sd, combine_file_R2_double1_Y2_decay_individual_unc_avg, combine_file_R2_double2_Y2_decay_combined, combine_file_R2_double2_Y2_decay_combined_unc, combine_file_R2_double2_Y2_decay_combined_sd, combine_file_R2_double2_Y2_decay_individual_unc_avg, combine_file_R2_double_both_Y2_decay_combined, combine_file_R2_double_both_Y2_decay_combined_unc, combine_file_R2_double_both_Y2_decay_combined_sd, combine_file_R2_double_both_Y2_decay_individual_unc_avg, combine_file_R2_user_lifetime_combined, combine_file_R2_user_lifetime_combined_unc, combine_file_R2_user_lifetime_combined_sd, combine_file_R2_user_lifetime_individual_unc_avg, combine_file_Ym_combined, combine_file_Ym_combined_unc, combine_file_Ym_combined_sd, combine_file_Ym_individual_unc_avg, combine_file_calc_eff_kn_combined, combine_file_calc_eff_kn_combined_unc, combine_file_calc_eff_kn_combined_sd, combine_file_calc_eff_kn_individual_unc_avg, combine_file_Ml_combined_Y2single, combine_file_Ml_combined_unc_Y2single, combine_file_Ml_combined_sd_Y2single, combine_file_Ml_individual_unc_avg_Y2single, combine_file_Mt_combined_Y2single, combine_file_Mt_combined_unc_Y2single, combine_file_Mt_combined_sd_Y2single, combine_file_Mt_individual_unc_avg_Y2single, combine_file_Fs_combined_Y2single, combine_file_Fs_combined_unc_Y2single, combine_file_Fs_combined_sd_Y2single, combine_file_Fs_individual_unc_avg_Y2single, combine_file_kp_combined_Y2single, combine_file_kp_combined_unc_Y2single, combine_file_kp_combined_sd_Y2single, combine_file_kp_individual_unc_avg_Y2single, combine_file_keff_combined_Y2single, combine_file_keff_combined_unc_Y2single, combine_file_keff_combined_sd_Y2single, combine_file_keff_individual_unc_avg_Y2single, combine_file_Ml_combined_Y2double1, combine_file_Ml_combined_unc_Y2double1, combine_file_Ml_combined_sd_Y2double1, combine_file_Ml_individual_unc_avg_Y2double1, combine_file_Mt_combined_Y2double1, combine_file_Mt_combined_unc_Y2double1, combine_file_Mt_combined_sd_Y2double1, combine_file_Mt_individual_unc_avg_Y2double1, combine_file_Fs_combined_Y2double1, combine_file_Fs_combined_unc_Y2double1, combine_file_Fs_combined_sd_Y2double1, combine_file_Fs_individual_unc_avg_Y2double1, combine_file_kp_combined_Y2double1, combine_file_kp_combined_unc_Y2double1, combine_file_kp_combined_sd_Y2double1, combine_file_kp_individual_unc_avg_Y2double1, combine_file_keff_combined_Y2double1, combine_file_keff_combined_unc_Y2double1, combine_file_keff_combined_sd_Y2double1, combine_file_keff_individual_unc_avg_Y2double1, combine_file_Ml_combined_Y2double2, combine_file_Ml_combined_unc_Y2double2, combine_file_Ml_combined_sd_Y2double2, combine_file_Ml_individual_unc_avg_Y2double2, combine_file_Mt_combined_Y2double2, combine_file_Mt_combined_unc_Y2double2, combine_file_Mt_combined_sd_Y2double2, combine_file_Mt_individual_unc_avg_Y2double2, combine_file_Fs_combined_Y2double2, combine_file_Fs_combined_unc_Y2double2, combine_file_Fs_combined_sd_Y2double2, combine_file_Fs_individual_unc_avg_Y2double2, combine_file_kp_combined_Y2double2, combine_file_kp_combined_unc_Y2double2, combine_file_kp_combined_sd_Y2double2, combine_file_kp_individual_unc_avg_Y2double2, combine_file_keff_combined_Y2double2, combine_file_keff_combined_unc_Y2double2, combine_file_keff_combined_sd_Y2double2, combine_file_keff_individual_unc_avg_Y2double2, combine_file_Ml_combined_Y2double_both, combine_file_Ml_combined_unc_Y2double_both, combine_file_Ml_combined_sd_Y2double_both, combine_file_Ml_individual_unc_avg_Y2double_both, combine_file_Mt_combined_Y2double_both, combine_file_Mt_combined_unc_Y2double_both, combine_file_Mt_combined_sd_Y2double_both, combine_file_Mt_individual_unc_avg_Y2double_both, combine_file_Fs_combined_Y2double_both, combine_file_Fs_combined_unc_Y2double_both, combine_file_Fs_combined_sd_Y2double_both, combine_file_Fs_individual_unc_avg_Y2double_both, combine_file_kp_combined_Y2double_both, combine_file_kp_combined_unc_Y2double_both, combine_file_kp_combined_sd_Y2double_both, combine_file_kp_individual_unc_avg_Y2double_both, combine_file_keff_combined_Y2double_both, combine_file_keff_combined_unc_Y2double_both, combine_file_keff_combined_sd_Y2double_both, combine_file_keff_individual_unc_avg_Y2double_both, combine_file_Ml_combined_Y2user_lifetime, combine_file_Ml_combined_unc_Y2user_lifetime, combine_file_Ml_combined_sd_Y2user_lifetime, combine_file_Ml_individual_unc_avg_Y2user_lifetime, combine_file_Mt_combined_Y2user_lifetime, combine_file_Mt_combined_unc_Y2user_lifetime, combine_file_Mt_combined_sd_Y2user_lifetime, combine_file_Mt_individual_unc_avg_Y2user_lifetime, combine_file_Fs_combined_Y2user_lifetime, combine_file_Fs_combined_unc_Y2user_lifetime, combine_file_Fs_combined_sd_Y2user_lifetime, combine_file_Fs_individual_unc_avg_Y2user_lifetime, combine_file_kp_combined_Y2user_lifetime, combine_file_kp_combined_unc_Y2user_lifetime, combine_file_kp_combined_sd_Y2user_lifetime, combine_file_kp_individual_unc_avg_Y2user_lifetime, combine_file_keff_combined_Y2user_lifetime, combine_file_keff_combined_unc_Y2user_lifetime, combine_file_keff_combined_sd_Y2user_lifetime, combine_file_keff_individual_unc_avg_Y2user_lifetime = combine_prepare(combine_Y2_rate_results_filepath, current_save_path, calculation_type, perform_Y2_single_fit, perform_Y2_double_fit, use_user_specified_lifetime)    
    
    sum_file_gatewidth_list, sum_file_first_reduced_factorial_moment_sum_list, sum_file_second_reduced_factorial_moment_sum_list, sum_file_third_reduced_factorial_moment_sum_list, sum_file_fourth_reduced_factorial_moment_sum_list, sum_file_first_factorial_moment_sum_list, sum_file_second_factorial_moment_sum_list, sum_file_third_factorial_moment_sum_list, sum_file_fourth_factorial_moment_sum_list, sum_file_Y1_sum_list, sum_file_dY1_sum_list, sum_file_Y2_sum_list, sum_file_dY2_sum_list, sum_file_R1_sum_list, sum_file_dR1_sum_list, sum_file_fit1log_A, sum_file_fit1log_A_unc, sum_file_fit1log_B, sum_file_fit1log_B_unc, sum_file_fit1log_det_lifetime, sum_file_fit1log_det_lifetime_unc, sum_file_omega2_single_results, sum_file_R2_single_Y2_decay, sum_file_R2_unc_single_Y2_decay, sum_file_fit2log_A, sum_file_fit2log_A_unc, sum_file_fit2log_B, sum_file_fit2log_B_unc, sum_file_fit2log_C, sum_file_fit2log_C_unc, sum_file_fit2log_D, sum_file_fit2log_D_unc, sum_file_fit2log_det_lifetime1, sum_file_fit2log_det_lifetime1_unc, sum_file_fit2log_det_lifetime2, sum_file_fit2log_det_lifetime2_unc, sum_file_omega2_double1_results, sum_file_R2_double1_Y2_decay, sum_file_R2_unc_double1_Y2_decay, sum_file_omega2_double2_results, sum_file_R2_double2_Y2_decay, sum_file_R2_unc_double2_Y2_decay, sum_file_R2_double_both_Y2_decay, sum_file_R2_unc_double_both_Y2_decay, sum_file_omega2_lifetime_user_results, sum_file_R2_user_lifetime, sum_file_R2_unc_user_lifetime, sum_file_Ym_list, sum_file_dYm_list, sum_file_calc_eff_kn_sum_list, sum_file_calc_eff_unc_kn_sum_list, sum_file_Ml_Y2single_sum_list, sum_file_dMl_Y2single_sum_list, sum_file_Mt_Y2single_sum_list, sum_file_dMt_Y2single_sum_list, sum_file_Fs_Y2single_sum_list, sum_file_dFs_Y2single_sum_list, sum_file_kp_Y2single_sum_list, sum_file_dkp_Y2single_sum_list, sum_file_keff_Y2single_sum_list, sum_file_dkeff_Y2single_sum_list, sum_file_Ml_Y2double1_sum_list, sum_file_dMl_Y2double1_sum_list, sum_file_Mt_Y2double1_sum_list, sum_file_dMt_Y2double1_sum_list, sum_file_Fs_Y2double1_sum_list, sum_file_dFs_Y2double1_sum_list, sum_file_kp_Y2double1_sum_list, sum_file_dkp_Y2double1_sum_list, sum_file_keff_Y2double1_sum_list, sum_file_dkeff_Y2double1_sum_list, sum_file_Ml_Y2double2_sum_list, sum_file_dMl_Y2double2_sum_list, sum_file_Mt_Y2double2_sum_list, sum_file_dMt_Y2double2_sum_list, sum_file_Fs_Y2double2_sum_list, sum_file_dFs_Y2double2_sum_list, sum_file_kp_Y2double2_sum_list, sum_file_dkp_Y2double2_sum_list, sum_file_keff_Y2double2_sum_list, sum_file_dkeff_Y2double2_sum_list, sum_file_Ml_Y2double_both_sum_list, sum_file_dMl_Y2double_both_sum_list, sum_file_Mt_Y2double_both_sum_list, sum_file_dMt_Y2double_both_sum_list, sum_file_Fs_Y2double_both_sum_list, sum_file_dFs_Y2double_both_sum_list, sum_file_kp_Y2double_both_sum_list, sum_file_dkp_Y2double_both_sum_list, sum_file_keff_Y2double_both_sum_list, sum_file_dkeff_Y2double_both_sum_list, sum_file_Ml_Y2user_lifetime_sum_list, sum_file_dMl_Y2user_lifetime_sum_list, sum_file_Mt_Y2user_lifetime_sum_list, sum_file_dMt_Y2user_lifetime_sum_list, sum_file_Fs_Y2user_lifetime_sum_list, sum_file_dFs_Y2user_lifetime_sum_list, sum_file_kp_Y2user_lifetime_sum_list, sum_file_dkp_Y2user_lifetime_sum_list, sum_file_keff_Y2user_lifetime_sum_list, sum_file_dkeff_Y2user_lifetime_sum_list = sum_prepare(sum_histogram_filepath, current_save_path, calculation_type, perform_Y2_single_fit, perform_Y2_double_fit, use_user_specified_lifetime)
    
    # generate plots
    gatewidth_compare = []
    Y1_compare = []
    dY1_compare = []
    R1_compare = []
    dR1_compare = []
    Y2_compare = []
    dY2_compare = []
    Ym_compare = []
    dYm_compare = []
    R2_single_Y2_compare = []
    dR2_single_Y2_compare = []
    R2_double1_Y2_compare = []
    dR2_double1_Y2_compare = []
    R2_double2_Y2_compare = []
    dR2_double2_Y2_compare = []
    R2_double_both_Y2_compare = []
    dR2_double_both_Y2_compare = []
    R2_user_lifetime_Y2_compare = []
    dR2_user_lifetime_Y2_compare = []
    calc_eff_kn_compare = []
    calc_eff_unc_kn_compare = []
    Ml_Y2single_compare = []
    dMl_Y2single_compare = []
    Mt_Y2single_compare = []
    dMt_Y2single_compare = []
    Fs_Y2single_compare = []
    dFs_Y2single_compare = []
    kp_Y2single_compare = []
    dkp_Y2single_compare = []
    keff_Y2single_compare = []
    dkeff_Y2single_compare = []
    Ml_Y2double1_compare = []
    dMl_Y2double1_compare = []
    Mt_Y2double1_compare = []
    dMt_Y2double1_compare = []
    Fs_Y2double1_compare = []
    dFs_Y2double1_compare = []
    kp_Y2double1_compare = []
    dkp_Y2double1_compare = []
    keff_Y2double1_compare = []
    dkeff_Y2double1_compare = []
    Ml_Y2double2_compare = []
    dMl_Y2double2_compare = []
    Mt_Y2double2_compare = []
    dMt_Y2double2_compare = []
    Fs_Y2double2_compare = []
    dFs_Y2double2_compare = []
    kp_Y2double2_compare = []
    dkp_Y2double2_compare = []
    keff_Y2double2_compare = []
    dkeff_Y2double2_compare = []
    Ml_Y2double_both_compare = []
    dMl_Y2double_both_compare = []
    Mt_Y2double_both_compare = []
    dMt_Y2double_both_compare = []
    Fs_Y2double_both_compare = []
    dFs_Y2double_both_compare = []
    kp_Y2double_both_compare = []
    dkp_Y2double_both_compare = []
    keff_Y2double_both_compare = []
    dkeff_Y2double_both_compare = []
    Ml_Y2user_lifetime_compare = []
    dMl_Y2user_lifetime_compare = []
    Mt_Y2user_lifetime_compare = []
    dMt_Y2user_lifetime_compare = []
    Fs_Y2user_lifetime_compare = []
    dFs_Y2user_lifetime_compare = []
    kp_Y2user_lifetime_compare = []
    dkp_Y2user_lifetime_compare = []
    keff_Y2user_lifetime_compare = []
    dkeff_Y2user_lifetime_compare = []
    
    Y1_difference = []
    dY1_difference = []
    R1_difference = []
    dR1_difference = []
    Y2_difference = []
    dY2_difference = []
    Ym_difference = []
    dYm_difference = []
    R2_single_Y2_difference = []
    dR2_single_Y2_difference = []
    R2_double1_Y2_difference = []
    dR2_double1_Y2_difference = []
    R2_double2_Y2_difference = []
    dR2_double2_Y2_difference = []
    R2_double_both_Y2_difference = []
    dR2_double_both_Y2_difference = []
    R2_user_lifetime_Y2_difference = []
    dR2_user_lifetime_Y2_difference = []
    calc_eff_kn_difference = []
    calc_eff_unc_kn_difference = []
    Ml_Y2single_difference = []
    dMl_Y2single_difference = []
    Mt_Y2single_difference = []
    dMt_Y2single_difference = []
    Fs_Y2single_difference = []
    dFs_Y2single_difference = []
    kp_Y2single_difference = []
    dkp_Y2single_difference = []
    keff_Y2single_difference = []
    dkeff_Y2single_difference = []
    Ml_Y2double1_difference = []
    dMl_Y2double1_difference = []
    Mt_Y2double1_difference = []
    dMt_Y2double1_difference = []
    Fs_Y2double1_difference = []
    dFs_Y2double1_difference = []
    kp_Y2double1_difference = []
    dkp_Y2double1_difference = []
    keff_Y2double1_difference = []
    dkeff_Y2double1_difference = []
    Ml_Y2double2_difference = []
    dMl_Y2double2_difference = []
    Mt_Y2double2_difference = []
    dMt_Y2double2_difference = []
    Fs_Y2double2_difference = []
    dFs_Y2double2_difference = []
    kp_Y2double2_difference = []
    dkp_Y2double2_difference = []
    keff_Y2double2_difference = []
    dkeff_Y2double2_difference = []
    Ml_Y2double_both_difference = []
    dMl_Y2double_both_difference = []
    Mt_Y2double_both_difference = []
    dMt_Y2double_both_difference = []
    Fs_Y2double_both_difference = []
    dFs_Y2double_both_difference = []
    kp_Y2double_both_difference = []
    dkp_Y2double_both_difference = []
    keff_Y2double_both_difference = []
    dkeff_Y2double_both_difference = []
    Ml_Y2user_lifetime_difference = []
    dMl_Y2user_lifetime_difference = []
    Mt_Y2user_lifetime_difference = []
    dMt_Y2user_lifetime_difference = []
    Fs_Y2user_lifetime_difference = []
    dFs_Y2user_lifetime_difference = []
    kp_Y2user_lifetime_difference = []
    dkp_Y2user_lifetime_difference = []
    keff_Y2user_lifetime_difference = []
    dkeff_Y2user_lifetime_difference = []
    
    if type(combine_file_gatewidth_list[0]) == int and type(combine_file_gatewidth_list[0]) == int:
        gatewidth_compare.append(combine_file_gatewidth_list)
        gatewidth_compare.append(sum_file_gatewidth_list)
        gatewidth_pass = True
    else:
        gatewidth_pass = False
    if type(combine_file_Y1_combined[0]) == float and type(sum_file_Y1_sum_list[0]) == float:
        Y1_compare.append(combine_file_Y1_combined)
        Y1_compare.append(sum_file_Y1_sum_list)
        Y1_difference = list_difference(combine_file_Y1_combined,sum_file_Y1_sum_list,percent_difference=True)
        Y1_pass = True
        dY1_compare.append(combine_file_Y1_combined_unc)
        dY1_compare.append(sum_file_dY1_sum_list)
        dY1_difference = list_difference(combine_file_Y1_combined_unc,sum_file_dY1_sum_list,percent_difference=True)
        dY1_pass = True
    else:
        Y1_pass = False
        dY1_pass = False
    if type(combine_file_R1_combined[0]) == float and type(sum_file_R1_sum_list[0]) == float:
        R1_compare.append(combine_file_R1_combined)
        R1_compare.append(sum_file_R1_sum_list)
        R1_difference = list_difference(combine_file_R1_combined, sum_file_R1_sum_list,percent_difference=True)
        R1_pass = True
        dR1_compare.append(combine_file_R1_combined_unc)
        dR1_compare.append(sum_file_dR1_sum_list)
        dR1_difference = list_difference(combine_file_R1_combined_unc, sum_file_dR1_sum_list,percent_difference=True)
        dR1_pass = True
    else:
        R1_pass = False
        dR1_pass = False
    if type(combine_file_Y2_combined[0]) == float and type(sum_file_Y2_sum_list[0]) == float:
        Y2_compare.append(combine_file_Y2_combined)
        Y2_compare.append(sum_file_Y2_sum_list)
        Y2_difference = list_difference(combine_file_Y2_combined, sum_file_Y2_sum_list,percent_difference=True)
        Y2_pass = True
        dY2_compare.append(combine_file_Y2_combined_unc)
        dY2_compare.append(sum_file_dY2_sum_list)
        dY2_difference = list_difference(combine_file_Y2_combined_unc, sum_file_dY2_sum_list,percent_difference=True)
        dY2_pass = True
    else:
        Y2_pass = False
        dY2_pass = False
    if type(combine_file_Ym_combined[0]) == float and type(sum_file_Ym_list[0]) == float:
        Ym_compare.append(combine_file_Ym_combined)
        Ym_compare.append(sum_file_Ym_list)
        Ym_difference = list_difference(combine_file_Ym_combined,sum_file_Ym_list,percent_difference=True)
        Ym_pass = True
        dYm_compare.append(combine_file_Ym_combined_unc)
        dYm_compare.append(sum_file_dYm_list)
        dYm_difference = list_difference(combine_file_Ym_combined_unc,sum_file_dYm_list,percent_difference=True)
        dYm_pass = True
    else:
        Ym_pass = False
        dYm_pass = False
    if type(combine_file_R2_single_Y2_decay_combined[0]) == float and type(sum_file_R2_single_Y2_decay[0]) == float:
        R2_single_Y2_compare.append(combine_file_R2_single_Y2_decay_combined)
        R2_single_Y2_compare.append(sum_file_R2_single_Y2_decay)
        R2_single_Y2_difference = list_difference(combine_file_R2_single_Y2_decay_combined, sum_file_R2_single_Y2_decay,percent_difference=True)
        R2_single_Y2_pass = True
        dR2_single_Y2_compare.append(combine_file_R2_single_Y2_decay_combined_unc)
        dR2_single_Y2_compare.append(sum_file_R2_unc_single_Y2_decay)
        dR2_single_Y2_difference = list_difference(combine_file_R2_single_Y2_decay_combined_unc, sum_file_R2_unc_single_Y2_decay,percent_difference=True)
        dR2_single_Y2_pass = True
    else:
        R2_single_Y2_pass = False
        dR2_single_Y2_pass = False
    if type(combine_file_R2_double1_Y2_decay_combined[0]) == float and type(sum_file_R2_double1_Y2_decay[0]) == float:
        R2_double1_Y2_compare.append(combine_file_R2_double1_Y2_decay_combined)
        R2_double1_Y2_compare.append(sum_file_R2_double1_Y2_decay)
        R2_double1_Y2_difference = list_difference(combine_file_R2_double1_Y2_decay_combined, sum_file_R2_double1_Y2_decay,percent_difference=True)
        R2_double1_Y2_pass = True
        dR2_double1_Y2_compare.append(combine_file_R2_double1_Y2_decay_combined_unc)
        dR2_double1_Y2_compare.append(sum_file_R2_unc_double1_Y2_decay)
        dR2_double1_Y2_difference = list_difference(combine_file_R2_double1_Y2_decay_combined_unc, sum_file_R2_unc_double1_Y2_decay,percent_difference=True)
        dR2_double1_Y2_pass = True
    else:
        R2_double1_Y2_pass = False
        dR2_double1_Y2_pass = False
    if type(combine_file_R2_double2_Y2_decay_combined[0]) == float and type(sum_file_R2_double2_Y2_decay[0]) == float:
        R2_double2_Y2_compare.append(combine_file_R2_double2_Y2_decay_combined)
        R2_double2_Y2_compare.append(sum_file_R2_double2_Y2_decay)
        R2_double2_Y2_difference = list_difference(combine_file_R2_double2_Y2_decay_combined, sum_file_R2_double2_Y2_decay,percent_difference=True)
        R2_double2_Y2_pass = True
        dR2_double2_Y2_compare.append(combine_file_R2_double2_Y2_decay_combined_unc)
        dR2_double2_Y2_compare.append(sum_file_R2_unc_double2_Y2_decay)
        dR2_double2_Y2_difference = list_difference(combine_file_R2_double2_Y2_decay_combined_unc, sum_file_R2_unc_double2_Y2_decay,percent_difference=True)
        dR2_double2_Y2_pass = True
    else:
        R2_double2_Y2_pass = False
        dR2_double2_Y2_pass = False
    if type(combine_file_R2_double_both_Y2_decay_combined[0]) == float and type(sum_file_R2_double_both_Y2_decay[0]) == float:
        R2_double_both_Y2_compare.append(combine_file_R2_double_both_Y2_decay_combined)
        R2_double_both_Y2_compare.append(sum_file_R2_double_both_Y2_decay)
        R2_double_both_Y2_difference = list_difference(combine_file_R2_double_both_Y2_decay_combined, sum_file_R2_double_both_Y2_decay,percent_difference=True)
        R2_double_both_Y2_pass = True
        dR2_double_both_Y2_compare.append(combine_file_R2_double_both_Y2_decay_combined_unc)
        dR2_double_both_Y2_compare.append(sum_file_R2_unc_double_both_Y2_decay)
        dR2_double_both_Y2_difference = list_difference(combine_file_R2_double_both_Y2_decay_combined_unc, sum_file_R2_unc_double_both_Y2_decay,percent_difference=True)
        dR2_double_both_Y2_pass = True
    else:
        R2_double_both_Y2_pass = False
        dR2_double_both_Y2_pass = False
    if type(combine_file_R2_user_lifetime_combined[0]) == float and type(sum_file_R2_user_lifetime[0]) == float:
        R2_user_lifetime_Y2_compare.append(combine_file_R2_user_lifetime_combined)
        R2_user_lifetime_Y2_compare.append(sum_file_R2_user_lifetime)
        R2_user_lifetime_Y2_difference = list_difference(combine_file_R2_user_lifetime_combined, sum_file_R2_user_lifetime,percent_difference=True)
        R2_user_lifetime_Y2_pass = True
        dR2_user_lifetime_Y2_compare.append(combine_file_R2_user_lifetime_combined_unc)
        dR2_user_lifetime_Y2_compare.append(sum_file_R2_unc_user_lifetime)
        dR2_user_lifetime_Y2_difference = list_difference(combine_file_R2_user_lifetime_combined_unc, sum_file_R2_unc_user_lifetime,percent_difference=True)
        dR2_user_lifetime_Y2_pass = True
    else:
        R2_user_lifetime_Y2_pass = False
        dR2_user_lifetime_Y2_pass = False
    if calculation_type == 'Cf' and type(combine_file_calc_eff_kn_combined[0]) == float and type(sum_file_calc_eff_kn_sum_list[0]) == float:
        calc_eff_kn_compare.append(combine_file_calc_eff_kn_combined)
        calc_eff_kn_compare.append(sum_file_calc_eff_kn_sum_list)
        calc_eff_kn_difference = list_difference(combine_file_calc_eff_kn_combined,sum_file_calc_eff_kn_sum_list,percent_difference=True)
        calc_eff_kn_pass = True
        calc_eff_unc_kn_compare.append(combine_file_calc_eff_kn_combined_unc)
        calc_eff_unc_kn_compare.append(sum_file_calc_eff_unc_kn_sum_list)
        calc_eff_unc_kn_difference = list_difference(combine_file_calc_eff_kn_combined_unc,sum_file_calc_eff_unc_kn_sum_list,percent_difference=True)
        calc_eff_unc_kn_pass = True
    else:
        calc_eff_kn_pass = False
        calc_eff_unc_kn_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_single_fit == True:
        Ml_Y2single_compare.append(combine_file_Ml_combined_Y2single)
        Ml_Y2single_compare.append(sum_file_Ml_Y2single_sum_list)
        Ml_Y2single_difference = list_difference(combine_file_Ml_combined_Y2single, sum_file_Ml_Y2single_sum_list, percent_difference=True)
        Ml_Y2single_pass = True
        dMl_Y2single_compare.append(combine_file_Ml_combined_unc_Y2single)
        dMl_Y2single_compare.append(sum_file_dMl_Y2single_sum_list)
        dMl_Y2single_difference = list_difference(combine_file_Ml_combined_unc_Y2single,sum_file_dMl_Y2single_sum_list,percent_difference=True)
        dMl_Y2single_pass = True
    else:
        Ml_Y2single_pass = False
        dMl_Y2single_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_single_fit == True:
        Mt_Y2single_compare.append(combine_file_Mt_combined_Y2single)
        Mt_Y2single_compare.append(sum_file_Mt_Y2single_sum_list)
        Mt_Y2single_difference = list_difference(combine_file_Mt_combined_Y2single, sum_file_Mt_Y2single_sum_list, percent_difference=True)
        Mt_Y2single_pass = True
        dMt_Y2single_compare.append(combine_file_Mt_combined_unc_Y2single)
        dMt_Y2single_compare.append(sum_file_dMt_Y2single_sum_list)
        dMt_Y2single_difference = list_difference(combine_file_Mt_combined_unc_Y2single,sum_file_dMt_Y2single_sum_list,percent_difference=True)
        dMt_Y2single_pass = True
    else:
        Mt_Y2single_pass = False
        dMt_Y2single_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_single_fit == True:
        Fs_Y2single_compare.append(combine_file_Fs_combined_Y2single)
        Fs_Y2single_compare.append(sum_file_Fs_Y2single_sum_list)
        Fs_Y2single_difference = list_difference(combine_file_Fs_combined_Y2single, sum_file_Fs_Y2single_sum_list, percent_difference=True)
        Fs_Y2single_pass = True
        dFs_Y2single_compare.append(combine_file_Fs_combined_unc_Y2single)
        dFs_Y2single_compare.append(sum_file_dFs_Y2single_sum_list)
        dFs_Y2single_difference = list_difference(combine_file_Fs_combined_unc_Y2single,sum_file_dFs_Y2single_sum_list,percent_difference=True)
        dFs_Y2single_pass = True
    else:
        Fs_Y2single_pass = False
        dFs_Y2single_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_single_fit == True:
        kp_Y2single_compare.append(combine_file_kp_combined_Y2single)
        kp_Y2single_compare.append(sum_file_kp_Y2single_sum_list)
        kp_Y2single_difference = list_difference(combine_file_kp_combined_Y2single, sum_file_kp_Y2single_sum_list, percent_difference=True)
        kp_Y2single_pass = True
        dkp_Y2single_compare.append(combine_file_kp_combined_unc_Y2single)
        dkp_Y2single_compare.append(sum_file_dkp_Y2single_sum_list)
        dkp_Y2single_difference = list_difference(combine_file_kp_combined_unc_Y2single,sum_file_dkp_Y2single_sum_list,percent_difference=True)
        dkp_Y2single_pass = True
    else:
        kp_Y2single_pass = False
        dkp_Y2single_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_single_fit == True:
        keff_Y2single_compare.append(combine_file_keff_combined_Y2single)
        keff_Y2single_compare.append(sum_file_keff_Y2single_sum_list)
        keff_Y2single_difference = list_difference(combine_file_keff_combined_Y2single, sum_file_keff_Y2single_sum_list, percent_difference=True)
        keff_Y2single_pass = True
        dkeff_Y2single_compare.append(combine_file_keff_combined_unc_Y2single)
        dkeff_Y2single_compare.append(sum_file_dkeff_Y2single_sum_list)
        dkeff_Y2single_difference = list_difference(combine_file_keff_combined_unc_Y2single,sum_file_dkeff_Y2single_sum_list,percent_difference=True)
        dkeff_Y2single_pass = True
    else:
        keff_Y2single_pass = False
        dkeff_Y2single_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        Ml_Y2double1_compare.append(combine_file_Ml_combined_Y2double1)
        Ml_Y2double1_compare.append(sum_file_Ml_Y2double1_sum_list)
        Ml_Y2double1_difference = list_difference(combine_file_Ml_combined_Y2double1, sum_file_Ml_Y2double1_sum_list, percent_difference=True)
        Ml_Y2double1_pass = True
        dMl_Y2double1_compare.append(combine_file_Ml_combined_unc_Y2double1)
        dMl_Y2double1_compare.append(sum_file_dMl_Y2double1_sum_list)
        dMl_Y2double1_difference = list_difference(combine_file_Ml_combined_unc_Y2double1,sum_file_dMl_Y2double1_sum_list,percent_difference=True)
        dMl_Y2double1_pass = True
    else:
        Ml_Y2double1_pass = False
        dMl_Y2double1_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        Mt_Y2double1_compare.append(combine_file_Mt_combined_Y2double1)
        Mt_Y2double1_compare.append(sum_file_Mt_Y2double1_sum_list)
        Mt_Y2double1_difference = list_difference(combine_file_Mt_combined_Y2double1, sum_file_Mt_Y2double1_sum_list, percent_difference=True)
        Mt_Y2double1_pass = True
        dMt_Y2double1_compare.append(combine_file_Mt_combined_unc_Y2double1)
        dMt_Y2double1_compare.append(sum_file_dMt_Y2double1_sum_list)
        dMt_Y2double1_difference = list_difference(combine_file_Mt_combined_unc_Y2double1,sum_file_dMt_Y2double1_sum_list,percent_difference=True)
        dMt_Y2double1_pass = True
    else:
        Mt_Y2double1_pass = False
        dMt_Y2double1_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        Fs_Y2double1_compare.append(combine_file_Fs_combined_Y2double1)
        Fs_Y2double1_compare.append(sum_file_Fs_Y2double1_sum_list)
        Fs_Y2double1_difference = list_difference(combine_file_Fs_combined_Y2double1, sum_file_Fs_Y2double1_sum_list, percent_difference=True)
        Fs_Y2double1_pass = True
        dFs_Y2double1_compare.append(combine_file_Fs_combined_unc_Y2double1)
        dFs_Y2double1_compare.append(sum_file_dFs_Y2double1_sum_list)
        dFs_Y2double1_difference = list_difference(combine_file_Fs_combined_unc_Y2double1,sum_file_dFs_Y2double1_sum_list,percent_difference=True)
        dFs_Y2double1_pass = True
    else:
        Fs_Y2double1_pass = False
        dFs_Y2double1_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        kp_Y2double1_compare.append(combine_file_kp_combined_Y2double1)
        kp_Y2double1_compare.append(sum_file_kp_Y2double1_sum_list)
        kp_Y2double1_difference = list_difference(combine_file_kp_combined_Y2double1, sum_file_kp_Y2double1_sum_list, percent_difference=True)
        kp_Y2double1_pass = True
        dkp_Y2double1_compare.append(combine_file_kp_combined_unc_Y2double1)
        dkp_Y2double1_compare.append(sum_file_dkp_Y2double1_sum_list)
        dkp_Y2double1_difference = list_difference(combine_file_kp_combined_unc_Y2double1,sum_file_dkp_Y2double1_sum_list,percent_difference=True)
        dkp_Y2double1_pass = True
    else:
        kp_Y2double1_pass = False
        dkp_Y2double1_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        keff_Y2double1_compare.append(combine_file_keff_combined_Y2double1)
        keff_Y2double1_compare.append(sum_file_keff_Y2double1_sum_list)
        keff_Y2double1_difference = list_difference(combine_file_keff_combined_Y2double1, sum_file_keff_Y2double1_sum_list, percent_difference=True)
        keff_Y2double1_pass = True
        dkeff_Y2double1_compare.append(combine_file_keff_combined_unc_Y2double1)
        dkeff_Y2double1_compare.append(sum_file_dkeff_Y2double1_sum_list)
        dkeff_Y2double1_difference = list_difference(combine_file_keff_combined_unc_Y2double1,sum_file_dkeff_Y2double1_sum_list,percent_difference=True)
        dkeff_Y2double1_pass = True
    else:
        keff_Y2double1_pass = False
        dkeff_Y2double1_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        Ml_Y2double2_compare.append(combine_file_Ml_combined_Y2double2)
        Ml_Y2double2_compare.append(sum_file_Ml_Y2double2_sum_list)
        Ml_Y2double2_difference = list_difference(combine_file_Ml_combined_Y2double2, sum_file_Ml_Y2double2_sum_list, percent_difference=True)
        Ml_Y2double2_pass = True
        dMl_Y2double2_compare.append(combine_file_Ml_combined_unc_Y2double2)
        dMl_Y2double2_compare.append(sum_file_dMl_Y2double2_sum_list)
        dMl_Y2double2_difference = list_difference(combine_file_Ml_combined_unc_Y2double2,sum_file_dMl_Y2double2_sum_list,percent_difference=True)
        dMl_Y2double2_pass = True
    else:
        Ml_Y2double2_pass = False
        dMl_Y2double2_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        Mt_Y2double2_compare.append(combine_file_Mt_combined_Y2double2)
        Mt_Y2double2_compare.append(sum_file_Mt_Y2double2_sum_list)
        Mt_Y2double2_difference = list_difference(combine_file_Mt_combined_Y2double2, sum_file_Mt_Y2double2_sum_list, percent_difference=True)
        Mt_Y2double2_pass = True
        dMt_Y2double2_compare.append(combine_file_Mt_combined_unc_Y2double2)
        dMt_Y2double2_compare.append(sum_file_dMt_Y2double2_sum_list)
        dMt_Y2double2_difference = list_difference(combine_file_Mt_combined_unc_Y2double2,sum_file_dMt_Y2double2_sum_list,percent_difference=True)
        dMt_Y2double2_pass = True
    else:
        Mt_Y2double2_pass = False
        dMt_Y2double2_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        Fs_Y2double2_compare.append(combine_file_Fs_combined_Y2double2)
        Fs_Y2double2_compare.append(sum_file_Fs_Y2double2_sum_list)
        Fs_Y2double2_difference = list_difference(combine_file_Fs_combined_Y2double2, sum_file_Fs_Y2double2_sum_list, percent_difference=True)
        Fs_Y2double2_pass = True
        dFs_Y2double2_compare.append(combine_file_Fs_combined_unc_Y2double2)
        dFs_Y2double2_compare.append(sum_file_dFs_Y2double2_sum_list)
        dFs_Y2double2_difference = list_difference(combine_file_Fs_combined_unc_Y2double2,sum_file_dFs_Y2double2_sum_list,percent_difference=True)
        dFs_Y2double2_pass = True
    else:
        Fs_Y2double2_pass = False
        dFs_Y2double2_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        kp_Y2double2_compare.append(combine_file_kp_combined_Y2double2)
        kp_Y2double2_compare.append(sum_file_kp_Y2double2_sum_list)
        kp_Y2double2_difference = list_difference(combine_file_kp_combined_Y2double2, sum_file_kp_Y2double2_sum_list, percent_difference=True)
        kp_Y2double2_pass = True
        dkp_Y2double2_compare.append(combine_file_kp_combined_unc_Y2double2)
        dkp_Y2double2_compare.append(sum_file_dkp_Y2double2_sum_list)
        dkp_Y2double2_difference = list_difference(combine_file_kp_combined_unc_Y2double2,sum_file_dkp_Y2double2_sum_list,percent_difference=True)
        dkp_Y2double2_pass = True
    else:
        kp_Y2double2_pass = False
        dkp_Y2double2_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        keff_Y2double2_compare.append(combine_file_keff_combined_Y2double2)
        keff_Y2double2_compare.append(sum_file_keff_Y2double2_sum_list)
        keff_Y2double2_difference = list_difference(combine_file_keff_combined_Y2double2, sum_file_keff_Y2double2_sum_list, percent_difference=True)
        keff_Y2double2_pass = True
        dkeff_Y2double2_compare.append(combine_file_keff_combined_unc_Y2double2)
        dkeff_Y2double2_compare.append(sum_file_dkeff_Y2double2_sum_list)
        dkeff_Y2double2_difference = list_difference(combine_file_keff_combined_unc_Y2double2,sum_file_dkeff_Y2double2_sum_list,percent_difference=True)
        dkeff_Y2double2_pass = True
    else:
        keff_Y2double2_pass = False
        dkeff_Y2double2_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        Ml_Y2double_both_compare.append(combine_file_Ml_combined_Y2double_both)
        Ml_Y2double_both_compare.append(sum_file_Ml_Y2double_both_sum_list)
        Ml_Y2double_both_difference = list_difference(combine_file_Ml_combined_Y2double_both, sum_file_Ml_Y2double_both_sum_list, percent_difference=True)
        Ml_Y2double_both_pass = True
        dMl_Y2double_both_compare.append(combine_file_Ml_combined_unc_Y2double_both)
        dMl_Y2double_both_compare.append(sum_file_dMl_Y2double_both_sum_list)
        dMl_Y2double_both_difference = list_difference(combine_file_Ml_combined_unc_Y2double_both,sum_file_dMl_Y2double_both_sum_list,percent_difference=True)
        dMl_Y2double_both_pass = True
    else:
        Ml_Y2double_both_pass = False
        dMl_Y2double_both_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        Mt_Y2double_both_compare.append(combine_file_Mt_combined_Y2double_both)
        Mt_Y2double_both_compare.append(sum_file_Mt_Y2double_both_sum_list)
        Mt_Y2double_both_difference = list_difference(combine_file_Mt_combined_Y2double_both, sum_file_Mt_Y2double_both_sum_list, percent_difference=True)
        Mt_Y2double_both_pass = True
        dMt_Y2double_both_compare.append(combine_file_Mt_combined_unc_Y2double_both)
        dMt_Y2double_both_compare.append(sum_file_dMt_Y2double_both_sum_list)
        dMt_Y2double_both_difference = list_difference(combine_file_Mt_combined_unc_Y2double_both,sum_file_dMt_Y2double_both_sum_list,percent_difference=True)
        dMt_Y2double_both_pass = True
    else:
        Mt_Y2double_both_pass = False
        dMt_Y2double_both_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        Fs_Y2double_both_compare.append(combine_file_Fs_combined_Y2double_both)
        Fs_Y2double_both_compare.append(sum_file_Fs_Y2double_both_sum_list)
        Fs_Y2double_both_difference = list_difference(combine_file_Fs_combined_Y2double_both, sum_file_Fs_Y2double_both_sum_list, percent_difference=True)
        Fs_Y2double_both_pass = True
        dFs_Y2double_both_compare.append(combine_file_Fs_combined_unc_Y2double_both)
        dFs_Y2double_both_compare.append(sum_file_dFs_Y2double_both_sum_list)
        dFs_Y2double_both_difference = list_difference(combine_file_Fs_combined_unc_Y2double_both,sum_file_dFs_Y2double_both_sum_list,percent_difference=True)
        dFs_Y2double_both_pass = True
    else:
        Fs_Y2double_both_pass = False
        dFs_Y2double_both_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        kp_Y2double_both_compare.append(combine_file_kp_combined_Y2double_both)
        kp_Y2double_both_compare.append(sum_file_kp_Y2double_both_sum_list)
        kp_Y2double_both_difference = list_difference(combine_file_kp_combined_Y2double_both, sum_file_kp_Y2double_both_sum_list, percent_difference=True)
        kp_Y2double_both_pass = True
        dkp_Y2double_both_compare.append(combine_file_kp_combined_unc_Y2double_both)
        dkp_Y2double_both_compare.append(sum_file_dkp_Y2double_both_sum_list)
        dkp_Y2double_both_difference = list_difference(combine_file_kp_combined_unc_Y2double_both,sum_file_dkp_Y2double_both_sum_list,percent_difference=True)
        dkp_Y2double_both_pass = True
    else:
        kp_Y2double_both_pass = False
        dkp_Y2double_both_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        keff_Y2double_both_compare.append(combine_file_keff_combined_Y2double_both)
        keff_Y2double_both_compare.append(sum_file_keff_Y2double_both_sum_list)
        keff_Y2double_both_difference = list_difference(combine_file_keff_combined_Y2double_both, sum_file_keff_Y2double_both_sum_list, percent_difference=True)
        keff_Y2double_both_pass = True
        dkeff_Y2double_both_compare.append(combine_file_keff_combined_unc_Y2double_both)
        dkeff_Y2double_both_compare.append(sum_file_dkeff_Y2double_both_sum_list)
        dkeff_Y2double_both_difference = list_difference(combine_file_keff_combined_unc_Y2double_both,sum_file_dkeff_Y2double_both_sum_list,percent_difference=True)
        dkeff_Y2double_both_pass = True
    else:
        keff_Y2double_both_pass = False
        dkeff_Y2double_both_pass = False
    if calculation_type == 'Multiplicity' and use_user_specified_lifetime == True:
        Ml_Y2user_lifetime_compare.append(combine_file_Ml_combined_Y2user_lifetime)
        Ml_Y2user_lifetime_compare.append(sum_file_Ml_Y2user_lifetime_sum_list)
        Ml_Y2user_lifetime_difference = list_difference(combine_file_Ml_combined_Y2user_lifetime, sum_file_Ml_Y2user_lifetime_sum_list, percent_difference=True)
        Ml_Y2user_lifetime_pass = True
        dMl_Y2user_lifetime_compare.append(combine_file_Ml_combined_unc_Y2user_lifetime)
        dMl_Y2user_lifetime_compare.append(sum_file_dMl_Y2user_lifetime_sum_list)
        dMl_Y2user_lifetime_difference = list_difference(combine_file_Ml_combined_unc_Y2user_lifetime,sum_file_dMl_Y2user_lifetime_sum_list,percent_difference=True)
        dMl_Y2user_lifetime_pass = True
    else:
        Ml_Y2user_lifetime_pass = False
        dMl_Y2user_lifetime_pass = False
    if calculation_type == 'Multiplicity' and use_user_specified_lifetime == True:
        Mt_Y2user_lifetime_compare.append(combine_file_Mt_combined_Y2user_lifetime)
        Mt_Y2user_lifetime_compare.append(sum_file_Mt_Y2user_lifetime_sum_list)
        Mt_Y2user_lifetime_difference = list_difference(combine_file_Mt_combined_Y2user_lifetime, sum_file_Mt_Y2user_lifetime_sum_list, percent_difference=True)
        Mt_Y2user_lifetime_pass = True
        dMt_Y2user_lifetime_compare.append(combine_file_Mt_combined_unc_Y2user_lifetime)
        dMt_Y2user_lifetime_compare.append(sum_file_dMt_Y2user_lifetime_sum_list)
        dMt_Y2user_lifetime_difference = list_difference(combine_file_Mt_combined_unc_Y2user_lifetime,sum_file_dMt_Y2user_lifetime_sum_list,percent_difference=True)
        dMt_Y2user_lifetime_pass = True
    else:
        Mt_Y2user_lifetime_pass = False
        dMt_Y2user_lifetime_pass = False
    if calculation_type == 'Multiplicity' and use_user_specified_lifetime == True:
        Fs_Y2user_lifetime_compare.append(combine_file_Fs_combined_Y2user_lifetime)
        Fs_Y2user_lifetime_compare.append(sum_file_Fs_Y2user_lifetime_sum_list)
        Fs_Y2user_lifetime_difference = list_difference(combine_file_Fs_combined_Y2user_lifetime, sum_file_Fs_Y2user_lifetime_sum_list, percent_difference=True)
        Fs_Y2user_lifetime_pass = True
        dFs_Y2user_lifetime_compare.append(combine_file_Fs_combined_unc_Y2user_lifetime)
        dFs_Y2user_lifetime_compare.append(sum_file_dFs_Y2user_lifetime_sum_list)
        dFs_Y2user_lifetime_difference = list_difference(combine_file_Fs_combined_unc_Y2user_lifetime,sum_file_dFs_Y2user_lifetime_sum_list,percent_difference=True)
        dFs_Y2user_lifetime_pass = True
    else:
        Fs_Y2user_lifetime_pass = False
        dFs_Y2user_lifetime_pass = False
    if calculation_type == 'Multiplicity' and use_user_specified_lifetime == True:
        kp_Y2user_lifetime_compare.append(combine_file_kp_combined_Y2user_lifetime)
        kp_Y2user_lifetime_compare.append(sum_file_kp_Y2user_lifetime_sum_list)
        kp_Y2user_lifetime_difference = list_difference(combine_file_kp_combined_Y2user_lifetime, sum_file_kp_Y2user_lifetime_sum_list, percent_difference=True)
        kp_Y2user_lifetime_pass = True
        dkp_Y2user_lifetime_compare.append(combine_file_kp_combined_unc_Y2user_lifetime)
        dkp_Y2user_lifetime_compare.append(sum_file_dkp_Y2user_lifetime_sum_list)
        dkp_Y2user_lifetime_difference = list_difference(combine_file_kp_combined_unc_Y2user_lifetime,sum_file_dkp_Y2user_lifetime_sum_list,percent_difference=True)
        dkp_Y2user_lifetime_pass = True
    else:
        kp_Y2user_lifetime_pass = False
        dkp_Y2user_lifetime_pass = False
    if calculation_type == 'Multiplicity' and use_user_specified_lifetime == True:
        keff_Y2user_lifetime_compare.append(combine_file_keff_combined_Y2user_lifetime)
        keff_Y2user_lifetime_compare.append(sum_file_keff_Y2user_lifetime_sum_list)
        keff_Y2user_lifetime_difference = list_difference(combine_file_keff_combined_Y2user_lifetime, sum_file_keff_Y2user_lifetime_sum_list, percent_difference=True)
        keff_Y2user_lifetime_pass = True
        dkeff_Y2user_lifetime_compare.append(combine_file_keff_combined_unc_Y2user_lifetime)
        dkeff_Y2user_lifetime_compare.append(sum_file_dkeff_Y2user_lifetime_sum_list)
        dkeff_Y2user_lifetime_difference = list_difference(combine_file_keff_combined_unc_Y2user_lifetime,sum_file_dkeff_Y2user_lifetime_sum_list,percent_difference=True)
        dkeff_Y2user_lifetime_pass = True
    else:
        keff_Y2user_lifetime_pass = False
        dkeff_Y2user_lifetime_pass = False
    
    return gatewidth_pass, gatewidth_compare, Y1_pass, Y1_compare, Y1_difference, dY1_pass, dY1_compare, dY1_difference, R1_pass, R1_compare, R1_difference, dR1_pass, dR1_compare, dR1_difference, Y2_pass, Y2_compare, Y2_difference, dY2_pass, dY2_compare, dY2_difference, Ym_pass, Ym_compare, Ym_difference, dYm_pass, dYm_compare, dYm_difference, R2_single_Y2_pass, R2_single_Y2_compare, R2_single_Y2_difference, dR2_single_Y2_pass, dR2_single_Y2_compare, dR2_single_Y2_difference, R2_double1_Y2_pass, R2_double1_Y2_compare, R2_double1_Y2_difference, dR2_double1_Y2_pass, dR2_double1_Y2_compare, dR2_double1_Y2_difference, R2_double2_Y2_pass, R2_double2_Y2_compare, R2_double2_Y2_difference, dR2_double2_Y2_pass, dR2_double2_Y2_compare, dR2_double2_Y2_difference,R2_double_both_Y2_pass, R2_double_both_Y2_compare, R2_double_both_Y2_difference, dR2_double_both_Y2_pass, dR2_double_both_Y2_compare, dR2_double_both_Y2_difference,R2_user_lifetime_Y2_pass, R2_user_lifetime_Y2_compare, R2_user_lifetime_Y2_difference, dR2_user_lifetime_Y2_pass, dR2_user_lifetime_Y2_compare, dR2_user_lifetime_Y2_difference, calc_eff_kn_pass, calc_eff_kn_compare, calc_eff_kn_difference, calc_eff_unc_kn_pass, calc_eff_unc_kn_compare, calc_eff_unc_kn_difference, Ml_Y2single_pass, Ml_Y2single_compare, Ml_Y2single_difference, dMl_Y2single_pass, dMl_Y2single_compare, dMl_Y2single_difference, Mt_Y2single_pass, Mt_Y2single_compare, Mt_Y2single_difference, dMt_Y2single_pass, dMt_Y2single_compare, dMt_Y2single_difference, Fs_Y2single_pass, Fs_Y2single_compare, Fs_Y2single_difference, dFs_Y2single_pass, dFs_Y2single_compare, dFs_Y2single_difference, kp_Y2single_pass, kp_Y2single_compare, kp_Y2single_difference, dkp_Y2single_pass, dkp_Y2single_compare, dkp_Y2single_difference, keff_Y2single_pass, keff_Y2single_compare, keff_Y2single_difference, dkeff_Y2single_pass, dkeff_Y2single_compare, dkeff_Y2single_difference, Ml_Y2double1_pass, Ml_Y2double1_compare, Ml_Y2double1_difference, dMl_Y2double1_pass, dMl_Y2double1_compare, dMl_Y2double1_difference, Mt_Y2double1_pass, Mt_Y2double1_compare, Mt_Y2double1_difference, dMt_Y2double1_pass, dMt_Y2double1_compare, dMt_Y2double1_difference, Fs_Y2double1_pass, Fs_Y2double1_compare, Fs_Y2double1_difference, dFs_Y2double1_pass, dFs_Y2double1_compare, dFs_Y2double1_difference, kp_Y2double1_pass, kp_Y2double1_compare, kp_Y2double1_difference, dkp_Y2double1_pass, dkp_Y2double1_compare, dkp_Y2double1_difference, keff_Y2double1_pass, keff_Y2double1_compare, keff_Y2double1_difference, dkeff_Y2double1_pass, dkeff_Y2double1_compare, dkeff_Y2double1_difference, Ml_Y2double2_pass, Ml_Y2double2_compare, Ml_Y2double2_difference, dMl_Y2double2_pass, dMl_Y2double2_compare, dMl_Y2double2_difference, Mt_Y2double2_pass, Mt_Y2double2_compare, Mt_Y2double2_difference, dMt_Y2double2_pass, dMt_Y2double2_compare, dMt_Y2double2_difference, Fs_Y2double2_pass, Fs_Y2double2_compare, Fs_Y2double2_difference, dFs_Y2double2_pass, dFs_Y2double2_compare, dFs_Y2double2_difference, kp_Y2double2_pass, kp_Y2double2_compare, kp_Y2double2_difference, dkp_Y2double2_pass, dkp_Y2double2_compare, dkp_Y2double2_difference, keff_Y2double2_pass, keff_Y2double2_compare, keff_Y2double2_difference, dkeff_Y2double2_pass, dkeff_Y2double2_compare, dkeff_Y2double2_difference, Ml_Y2double_both_pass, Ml_Y2double_both_compare, Ml_Y2double_both_difference, dMl_Y2double_both_pass, dMl_Y2double_both_compare, dMl_Y2double_both_difference, Mt_Y2double_both_pass, Mt_Y2double_both_compare, Mt_Y2double_both_difference, dMt_Y2double_both_pass, dMt_Y2double_both_compare, dMt_Y2double_both_difference, Fs_Y2double_both_pass, Fs_Y2double_both_compare, Fs_Y2double_both_difference, dFs_Y2double_both_pass, dFs_Y2double_both_compare, dFs_Y2double_both_difference, kp_Y2double_both_pass, kp_Y2double_both_compare, kp_Y2double_both_difference, dkp_Y2double_both_pass, dkp_Y2double_both_compare, dkp_Y2double_both_difference, keff_Y2double_both_pass, keff_Y2double_both_compare, keff_Y2double_both_difference, dkeff_Y2double_both_pass, dkeff_Y2double_both_compare, dkeff_Y2double_both_difference, Ml_Y2user_lifetime_pass, Ml_Y2user_lifetime_compare, Ml_Y2user_lifetime_difference, dMl_Y2user_lifetime_pass, dMl_Y2user_lifetime_compare, dMl_Y2user_lifetime_difference, Mt_Y2user_lifetime_pass, Mt_Y2user_lifetime_compare, Mt_Y2user_lifetime_difference, dMt_Y2user_lifetime_pass, dMt_Y2user_lifetime_compare, dMt_Y2user_lifetime_difference, Fs_Y2user_lifetime_pass, Fs_Y2user_lifetime_compare, Fs_Y2user_lifetime_difference, dFs_Y2user_lifetime_pass, dFs_Y2user_lifetime_compare, dFs_Y2user_lifetime_difference, kp_Y2user_lifetime_pass, kp_Y2user_lifetime_compare, kp_Y2user_lifetime_difference, dkp_Y2user_lifetime_pass, dkp_Y2user_lifetime_compare, dkp_Y2user_lifetime_difference, keff_Y2user_lifetime_pass, keff_Y2user_lifetime_compare, keff_Y2user_lifetime_difference, dkeff_Y2user_lifetime_pass, dkeff_Y2user_lifetime_compare, dkeff_Y2user_lifetime_difference
    

def compare_individual_combine_sum(combine_Y2_rate_results_filepath, sum_histogram_filepath,current_save_path, calculation_type, perform_Y2_single_fit, perform_Y2_double_fit, use_user_specified_lifetime, individual_filepath_and_filename):
   
    combine_file_gatewidth_list, combine_file_Y1_combined, combine_file_Y1_combined_unc, combine_file_Y1_combined_sd, combine_file_Y1_individual_unc_avg, combine_file_Y2_combined, combine_file_Y2_combined_unc, combine_file_Y2_combined_sd, combine_file_Y2_individual_unc_avg, combine_file_R1_combined, combine_file_R1_combined_unc, combine_file_R1_combined_sd, combine_file_R1_individual_unc_avg, combine_file_R2_single_Y2_decay_combined, combine_file_R2_single_Y2_decay_combined_unc, combine_file_R2_single_Y2_decay_combined_sd, combine_file_R2_single_Y2_decay_individual_unc_avg, combine_file_R2_double1_Y2_decay_combined, combine_file_R2_double1_Y2_decay_combined_unc, combine_file_R2_double1_Y2_decay_combined_sd, combine_file_R2_double1_Y2_decay_individual_unc_avg, combine_file_R2_double2_Y2_decay_combined, combine_file_R2_double2_Y2_decay_combined_unc, combine_file_R2_double2_Y2_decay_combined_sd, combine_file_R2_double2_Y2_decay_individual_unc_avg, combine_file_R2_double_both_Y2_decay_combined, combine_file_R2_double_both_Y2_decay_combined_unc, combine_file_R2_double_both_Y2_decay_combined_sd, combine_file_R2_double_both_Y2_decay_individual_unc_avg, combine_file_R2_user_lifetime_combined, combine_file_R2_user_lifetime_combined_unc, combine_file_R2_user_lifetime_combined_sd, combine_file_R2_user_lifetime_individual_unc_avg, combine_file_Ym_combined, combine_file_Ym_combined_unc, combine_file_Ym_combined_sd, combine_file_Ym_individual_unc_avg, combine_file_calc_eff_kn_combined, combine_file_calc_eff_kn_combined_unc, combine_file_calc_eff_kn_combined_sd, combine_file_calc_eff_kn_individual_unc_avg, combine_file_Ml_combined_Y2single, combine_file_Ml_combined_unc_Y2single, combine_file_Ml_combined_sd_Y2single, combine_file_Ml_individual_unc_avg_Y2single, combine_file_Mt_combined_Y2single, combine_file_Mt_combined_unc_Y2single, combine_file_Mt_combined_sd_Y2single, combine_file_Mt_individual_unc_avg_Y2single, combine_file_Fs_combined_Y2single, combine_file_Fs_combined_unc_Y2single, combine_file_Fs_combined_sd_Y2single, combine_file_Fs_individual_unc_avg_Y2single, combine_file_kp_combined_Y2single, combine_file_kp_combined_unc_Y2single, combine_file_kp_combined_sd_Y2single, combine_file_kp_individual_unc_avg_Y2single, combine_file_keff_combined_Y2single, combine_file_keff_combined_unc_Y2single, combine_file_keff_combined_sd_Y2single, combine_file_keff_individual_unc_avg_Y2single, combine_file_Ml_combined_Y2double1, combine_file_Ml_combined_unc_Y2double1, combine_file_Ml_combined_sd_Y2double1, combine_file_Ml_individual_unc_avg_Y2double1, combine_file_Mt_combined_Y2double1, combine_file_Mt_combined_unc_Y2double1, combine_file_Mt_combined_sd_Y2double1, combine_file_Mt_individual_unc_avg_Y2double1, combine_file_Fs_combined_Y2double1, combine_file_Fs_combined_unc_Y2double1, combine_file_Fs_combined_sd_Y2double1, combine_file_Fs_individual_unc_avg_Y2double1, combine_file_kp_combined_Y2double1, combine_file_kp_combined_unc_Y2double1, combine_file_kp_combined_sd_Y2double1, combine_file_kp_individual_unc_avg_Y2double1, combine_file_keff_combined_Y2double1, combine_file_keff_combined_unc_Y2double1, combine_file_keff_combined_sd_Y2double1, combine_file_keff_individual_unc_avg_Y2double1, combine_file_Ml_combined_Y2double2, combine_file_Ml_combined_unc_Y2double2, combine_file_Ml_combined_sd_Y2double2, combine_file_Ml_individual_unc_avg_Y2double2, combine_file_Mt_combined_Y2double2, combine_file_Mt_combined_unc_Y2double2, combine_file_Mt_combined_sd_Y2double2, combine_file_Mt_individual_unc_avg_Y2double2, combine_file_Fs_combined_Y2double2, combine_file_Fs_combined_unc_Y2double2, combine_file_Fs_combined_sd_Y2double2, combine_file_Fs_individual_unc_avg_Y2double2, combine_file_kp_combined_Y2double2, combine_file_kp_combined_unc_Y2double2, combine_file_kp_combined_sd_Y2double2, combine_file_kp_individual_unc_avg_Y2double2, combine_file_keff_combined_Y2double2, combine_file_keff_combined_unc_Y2double2, combine_file_keff_combined_sd_Y2double2, combine_file_keff_individual_unc_avg_Y2double2, combine_file_Ml_combined_Y2double_both, combine_file_Ml_combined_unc_Y2double_both, combine_file_Ml_combined_sd_Y2double_both, combine_file_Ml_individual_unc_avg_Y2double_both, combine_file_Mt_combined_Y2double_both, combine_file_Mt_combined_unc_Y2double_both, combine_file_Mt_combined_sd_Y2double_both, combine_file_Mt_individual_unc_avg_Y2double_both, combine_file_Fs_combined_Y2double_both, combine_file_Fs_combined_unc_Y2double_both, combine_file_Fs_combined_sd_Y2double_both, combine_file_Fs_individual_unc_avg_Y2double_both, combine_file_kp_combined_Y2double_both, combine_file_kp_combined_unc_Y2double_both, combine_file_kp_combined_sd_Y2double_both, combine_file_kp_individual_unc_avg_Y2double_both, combine_file_keff_combined_Y2double_both, combine_file_keff_combined_unc_Y2double_both, combine_file_keff_combined_sd_Y2double_both, combine_file_keff_individual_unc_avg_Y2double_both, combine_file_Ml_combined_Y2user_lifetime, combine_file_Ml_combined_unc_Y2user_lifetime, combine_file_Ml_combined_sd_Y2user_lifetime, combine_file_Ml_individual_unc_avg_Y2user_lifetime, combine_file_Mt_combined_Y2user_lifetime, combine_file_Mt_combined_unc_Y2user_lifetime, combine_file_Mt_combined_sd_Y2user_lifetime, combine_file_Mt_individual_unc_avg_Y2user_lifetime, combine_file_Fs_combined_Y2user_lifetime, combine_file_Fs_combined_unc_Y2user_lifetime, combine_file_Fs_combined_sd_Y2user_lifetime, combine_file_Fs_individual_unc_avg_Y2user_lifetime, combine_file_kp_combined_Y2user_lifetime, combine_file_kp_combined_unc_Y2user_lifetime, combine_file_kp_combined_sd_Y2user_lifetime, combine_file_kp_individual_unc_avg_Y2user_lifetime, combine_file_keff_combined_Y2user_lifetime, combine_file_keff_combined_unc_Y2user_lifetime, combine_file_keff_combined_sd_Y2user_lifetime, combine_file_keff_individual_unc_avg_Y2user_lifetime = combine_prepare(combine_Y2_rate_results_filepath, current_save_path, calculation_type, perform_Y2_single_fit, perform_Y2_double_fit, use_user_specified_lifetime)    
    
    sum_file_gatewidth_list, sum_file_first_reduced_factorial_moment_sum_list, sum_file_second_reduced_factorial_moment_sum_list, sum_file_third_reduced_factorial_moment_sum_list, sum_file_fourth_reduced_factorial_moment_sum_list, sum_file_first_factorial_moment_sum_list, sum_file_second_factorial_moment_sum_list, sum_file_third_factorial_moment_sum_list, sum_file_fourth_factorial_moment_sum_list, sum_file_Y1_sum_list, sum_file_dY1_sum_list, sum_file_Y2_sum_list, sum_file_dY2_sum_list, sum_file_R1_sum_list, sum_file_dR1_sum_list, sum_file_fit1log_A, sum_file_fit1log_A_unc, sum_file_fit1log_B, sum_file_fit1log_B_unc, sum_file_fit1log_det_lifetime, sum_file_fit1log_det_lifetime_unc, sum_file_omega2_single_results, sum_file_R2_single_Y2_decay, sum_file_R2_unc_single_Y2_decay, sum_file_fit2log_A, sum_file_fit2log_A_unc, sum_file_fit2log_B, sum_file_fit2log_B_unc, sum_file_fit2log_C, sum_file_fit2log_C_unc, sum_file_fit2log_D, sum_file_fit2log_D_unc, sum_file_fit2log_det_lifetime1, sum_file_fit2log_det_lifetime1_unc, sum_file_fit2log_det_lifetime2, sum_file_fit2log_det_lifetime2_unc, sum_file_omega2_double1_results, sum_file_R2_double1_Y2_decay, sum_file_R2_unc_double1_Y2_decay, sum_file_omega2_double2_results, sum_file_R2_double2_Y2_decay, sum_file_R2_unc_double2_Y2_decay, sum_file_R2_double_both_Y2_decay, sum_file_R2_unc_double_both_Y2_decay, sum_file_omega2_lifetime_user_results, sum_file_R2_user_lifetime, sum_file_R2_unc_user_lifetime, sum_file_Ym_list, sum_file_dYm_list, sum_file_calc_eff_kn_sum_list, sum_file_calc_eff_unc_kn_sum_list, sum_file_Ml_Y2single_sum_list, sum_file_dMl_Y2single_sum_list, sum_file_Mt_Y2single_sum_list, sum_file_dMt_Y2single_sum_list, sum_file_Fs_Y2single_sum_list, sum_file_dFs_Y2single_sum_list, sum_file_kp_Y2single_sum_list, sum_file_dkp_Y2single_sum_list, sum_file_keff_Y2single_sum_list, sum_file_dkeff_Y2single_sum_list, sum_file_Ml_Y2double1_sum_list, sum_file_dMl_Y2double1_sum_list, sum_file_Mt_Y2double1_sum_list, sum_file_dMt_Y2double1_sum_list, sum_file_Fs_Y2double1_sum_list, sum_file_dFs_Y2double1_sum_list, sum_file_kp_Y2double1_sum_list, sum_file_dkp_Y2double1_sum_list, sum_file_keff_Y2double1_sum_list, sum_file_dkeff_Y2double1_sum_list, sum_file_Ml_Y2double2_sum_list, sum_file_dMl_Y2double2_sum_list, sum_file_Mt_Y2double2_sum_list, sum_file_dMt_Y2double2_sum_list, sum_file_Fs_Y2double2_sum_list, sum_file_dFs_Y2double2_sum_list, sum_file_kp_Y2double2_sum_list, sum_file_dkp_Y2double2_sum_list, sum_file_keff_Y2double2_sum_list, sum_file_dkeff_Y2double2_sum_list, sum_file_Ml_Y2double_both_sum_list, sum_file_dMl_Y2double_both_sum_list, sum_file_Mt_Y2double_both_sum_list, sum_file_dMt_Y2double_both_sum_list, sum_file_Fs_Y2double_both_sum_list, sum_file_dFs_Y2double_both_sum_list, sum_file_kp_Y2double_both_sum_list, sum_file_dkp_Y2double_both_sum_list, sum_file_keff_Y2double_both_sum_list, sum_file_dkeff_Y2double_both_sum_list, sum_file_Ml_Y2user_lifetime_sum_list, sum_file_dMl_Y2user_lifetime_sum_list, sum_file_Mt_Y2user_lifetime_sum_list, sum_file_dMt_Y2user_lifetime_sum_list, sum_file_Fs_Y2user_lifetime_sum_list, sum_file_dFs_Y2user_lifetime_sum_list, sum_file_kp_Y2user_lifetime_sum_list, sum_file_dkp_Y2user_lifetime_sum_list, sum_file_keff_Y2user_lifetime_sum_list, sum_file_dkeff_Y2user_lifetime_sum_list = sum_prepare(sum_histogram_filepath, current_save_path, calculation_type, perform_Y2_single_fit, perform_Y2_double_fit, use_user_specified_lifetime, sumfile=True)
    
    indiv_file_gatewidth_list, indiv_file_first_reduced_factorial_moment, indiv_file_second_reduced_factorial_moment, indiv_file_third_reduced_factorial_moment, indiv_file_fourth_reduced_factorial_moment, indiv_file_first_factorial_moment, indiv_file_second_factorial_moment, indiv_file_third_factorial_moment, indiv_file_fourth_factorial_moment, indiv_file_Y1, indiv_file_dY1, indiv_file_Y2, indiv_file_dY2, indiv_file_R1, indiv_file_dR1, indiv_file_fit1log_A, indiv_file_fit1log_A_unc, indiv_file_fit1log_B, indiv_file_fit1log_B_unc, indiv_file_fit1log_det_lifetime, indiv_file_fit1log_det_lifetime_unc, indiv_file_omega2_single_results, indiv_file_R2_single_Y2_decay, indiv_file_R2_unc_single_Y2_decay, indiv_file_fit2log_A, indiv_file_fit2log_A_unc, indiv_file_fit2log_B, indiv_file_fit2log_B_unc, indiv_file_fit2log_C, indiv_file_fit2log_C_unc, indiv_file_fit2log_D, indiv_file_fit2log_D_unc, indiv_file_fit2log_det_lifetime1, indiv_file_fit2log_det_lifetime1_unc, indiv_file_fit2log_det_lifetime2, indiv_file_fit2log_det_lifetime2_unc, indiv_file_omega2_double1_results, indiv_file_R2_double1_Y2_decay, indiv_file_R2_unc_double1_Y2_decay, indiv_file_omega2_double2_results, indiv_file_R2_double2_Y2_decay, indiv_file_R2_unc_double2_Y2_decay, indiv_file_R2_double_both_Y2_decay, indiv_file_R2_unc_double_both_Y2_decay, indiv_file_omega2_lifetime_user_results, indiv_file_R2_user_lifetime, indiv_file_R2_unc_user_lifetime, indiv_file_Ym_list, indiv_file_dYm_list, indiv_file_calc_eff_kn, indiv_file_calc_eff_unc_kn, indiv_file_Ml_Y2single, indiv_file_dMl_Y2single, indiv_file_Mt_Y2single, indiv_file_dMt_Y2single, indiv_file_Fs_Y2single, indiv_file_dFs_Y2single, indiv_file_kp_Y2single, indiv_file_dkp_Y2single, indiv_file_keff_Y2single, indiv_file_dkeff_Y2single, indiv_file_Ml_Y2double1, indiv_file_dMl_Y2double1, indiv_file_Mt_Y2double1, indiv_file_dMt_Y2double1, indiv_file_Fs_Y2double1, indiv_file_dFs_Y2double1, indiv_file_kp_Y2double1, indiv_file_dkp_Y2double1, indiv_file_keff_Y2double1, indiv_file_dkeff_Y2double1, indiv_file_Ml_Y2double2, indiv_file_dMl_Y2double2, indiv_file_Mt_Y2double2, indiv_file_dMt_Y2double2, indiv_file_Fs_Y2double2, indiv_file_dFs_Y2double2, indiv_file_kp_Y2double2, indiv_file_dkp_Y2double2, indiv_file_keff_Y2double2, indiv_file_dkeff_Y2double2, indiv_file_Ml_Y2double_both, indiv_file_dMl_Y2double_both, indiv_file_Mt_Y2double_both, indiv_file_dMt_Y2double_both, indiv_file_Fs_Y2double_both, indiv_file_dFs_Y2double_both, indiv_file_kp_Y2double_both, indiv_file_dkp_Y2double_both, indiv_file_keff_Y2double_both, indiv_file_dkeff_Y2double_both, indiv_file_Ml_Y2user_lifetime, indiv_file_dMl_Y2user_lifetime, indiv_file_Mt_Y2user_lifetime, indiv_file_dMt_Y2user_lifetime, indiv_file_Fs_Y2user_lifetime, indiv_file_dFs_Y2user_lifetime, indiv_file_kp_Y2user_lifetime, indiv_file_dkp_Y2user_lifetime, indiv_file_keff_Y2user_lifetime, indiv_file_dkeff_Y2user_lifetime = sum_prepare(individual_filepath_and_filename, current_save_path, calculation_type, perform_Y2_single_fit, perform_Y2_double_fit, use_user_specified_lifetime, sumfile=False)
    
    # generate plots
    gatewidth_compare = []
    Y1_compare = []
    dY1_compare = []
    R1_compare = []
    dR1_compare = []
    Y2_compare = []
    dY2_compare = []
    Ym_compare = []
    dYm_compare = []
    R2_single_Y2_compare = []
    dR2_single_Y2_compare = []
    R2_double1_Y2_compare = []
    dR2_double1_Y2_compare = []
    R2_double2_Y2_compare = []
    dR2_double2_Y2_compare = []
    R2_double_both_Y2_compare = []
    dR2_double_both_Y2_compare = []
    R2_user_lifetime_Y2_compare = []
    dR2_user_lifetime_Y2_compare = []
    calc_eff_kn_compare = []
    calc_eff_unc_kn_compare = []
    Ml_Y2single_compare = []
    dMl_Y2single_compare = []
    Mt_Y2single_compare = []
    dMt_Y2single_compare = []
    Fs_Y2single_compare = []
    dFs_Y2single_compare = []
    kp_Y2single_compare = []
    dkp_Y2single_compare = []
    keff_Y2single_compare = []
    dkeff_Y2single_compare = []
    Ml_Y2double1_compare = []
    dMl_Y2double1_compare = []
    Mt_Y2double1_compare = []
    dMt_Y2double1_compare = []
    Fs_Y2double1_compare = []
    dFs_Y2double1_compare = []
    kp_Y2double1_compare = []
    dkp_Y2double1_compare = []
    keff_Y2double1_compare = []
    dkeff_Y2double1_compare = []
    Ml_Y2double2_compare = []
    dMl_Y2double2_compare = []
    Mt_Y2double2_compare = []
    dMt_Y2double2_compare = []
    Fs_Y2double2_compare = []
    dFs_Y2double2_compare = []
    kp_Y2double2_compare = []
    dkp_Y2double2_compare = []
    keff_Y2double2_compare = []
    dkeff_Y2double2_compare = []
    Ml_Y2double_both_compare = []
    dMl_Y2double_both_compare = []
    Mt_Y2double_both_compare = []
    dMt_Y2double_both_compare = []
    Fs_Y2double_both_compare = []
    dFs_Y2double_both_compare = []
    kp_Y2double_both_compare = []
    dkp_Y2double_both_compare = []
    keff_Y2double_both_compare = []
    dkeff_Y2double_both_compare = []
    Ml_Y2user_lifetime_compare = []
    dMl_Y2user_lifetime_compare = []
    Mt_Y2user_lifetime_compare = []
    dMt_Y2user_lifetime_compare = []
    Fs_Y2user_lifetime_compare = []
    dFs_Y2user_lifetime_compare = []
    kp_Y2user_lifetime_compare = []
    dkp_Y2user_lifetime_compare = []
    keff_Y2user_lifetime_compare = []
    dkeff_Y2user_lifetime_compare = []
    
    Y1_difference = []
    dY1_difference = []
    R1_difference = []
    dR1_difference = []
    Y2_difference = []
    dY2_difference = []
    Ym_difference = []
    dYm_difference = []
    R2_single_Y2_difference = []
    dR2_single_Y2_difference = []
    R2_double1_Y2_difference = []
    dR2_double1_Y2_difference = []
    R2_double2_Y2_difference = []
    dR2_double2_Y2_difference = []
    R2_double_both_Y2_difference = []
    dR2_double_both_Y2_difference = []
    R2_user_lifetime_Y2_difference = []
    dR2_user_lifetime_Y2_difference = []
    calc_eff_kn_difference = []
    calc_eff_unc_kn_difference = []
    Ml_Y2single_difference = []
    dMl_Y2single_difference = []
    Mt_Y2single_difference = []
    dMt_Y2single_difference = []
    Fs_Y2single_difference = []
    dFs_Y2single_difference = []
    kp_Y2single_difference = []
    dkp_Y2single_difference = []
    keff_Y2single_difference = []
    dkeff_Y2single_difference = []
    Ml_Y2double1_difference = []
    dMl_Y2double1_difference = []
    Mt_Y2double1_difference = []
    dMt_Y2double1_difference = []
    Fs_Y2double1_difference = []
    dFs_Y2double1_difference = []
    kp_Y2double1_difference = []
    dkp_Y2double1_difference = []
    keff_Y2double1_difference = []
    dkeff_Y2double1_difference = []
    Ml_Y2double2_difference = []
    dMl_Y2double2_difference = []
    Mt_Y2double2_difference = []
    dMt_Y2double2_difference = []
    Fs_Y2double2_difference = []
    dFs_Y2double2_difference = []
    kp_Y2double2_difference = []
    dkp_Y2double2_difference = []
    keff_Y2double2_difference = []
    dkeff_Y2double2_difference = []
    Ml_Y2double_both_difference = []
    dMl_Y2double_both_difference = []
    Mt_Y2double_both_difference = []
    dMt_Y2double_both_difference = []
    Fs_Y2double_both_difference = []
    dFs_Y2double_both_difference = []
    kp_Y2double_both_difference = []
    dkp_Y2double_both_difference = []
    keff_Y2double_both_difference = []
    dkeff_Y2double_both_difference = []
    Ml_Y2user_lifetime_difference = []
    dMl_Y2user_lifetime_difference = []
    Mt_Y2user_lifetime_difference = []
    dMt_Y2user_lifetime_difference = []
    Fs_Y2user_lifetime_difference = []
    dFs_Y2user_lifetime_difference = []
    kp_Y2user_lifetime_difference = []
    dkp_Y2user_lifetime_difference = []
    keff_Y2user_lifetime_difference = []
    dkeff_Y2user_lifetime_difference = []
    
    if type(combine_file_gatewidth_list[0]) == int and type(sum_file_gatewidth_list[0]) == int and type(indiv_file_gatewidth_list[0]) == int:
        gatewidth_compare.append(indiv_file_gatewidth_list)
        gatewidth_compare.append(combine_file_gatewidth_list)
        gatewidth_compare.append(sum_file_gatewidth_list)
        gatewidth_pass = True
    else:
        gatewidth_pass = False
    if type(combine_file_Y1_combined[0]) == float and type(sum_file_Y1_sum_list[0]) == float and type(indiv_file_Y1[0]) == float:
        Y1_compare.append(indiv_file_Y1)
        Y1_compare.append(combine_file_Y1_combined)
        Y1_compare.append(sum_file_Y1_sum_list)
        Y1_difference.append(list_difference(indiv_file_Y1, combine_file_Y1_combined, percent_difference=True))
        Y1_difference.append(list_difference(indiv_file_Y1, sum_file_Y1_sum_list,percent_difference=True))
        Y1_pass = True
        dY1_compare.append(indiv_file_dY1)
        dY1_compare.append(combine_file_Y1_combined_unc)
        dY1_compare.append(sum_file_dY1_sum_list)
        dY1_difference.append(list_difference(indiv_file_dY1, combine_file_Y1_combined_unc,percent_difference=True))
        dY1_difference.append(list_difference(indiv_file_dY1, sum_file_dY1_sum_list,percent_difference=True))
        dY1_pass = True
    else:
        Y1_pass = False
        dY1_pass = False
    if type(combine_file_R1_combined[0]) == float and type(sum_file_R1_sum_list[0]) == float and type(indiv_file_R1[0]) == float:
        R1_compare.append(indiv_file_R1)
        R1_compare.append(combine_file_R1_combined)
        R1_compare.append(sum_file_R1_sum_list)
        R1_difference.append(list_difference(indiv_file_R1, combine_file_R1_combined,percent_difference=True))
        R1_difference.append(list_difference(indiv_file_R1, sum_file_R1_sum_list,percent_difference=True))
        R1_pass = True
        dR1_compare.append(indiv_file_dR1)
        dR1_compare.append(combine_file_R1_combined_unc)
        dR1_compare.append(sum_file_dR1_sum_list)
        dR1_difference.append(list_difference(indiv_file_dR1,combine_file_R1_combined_unc,percent_difference=True))
        dR1_difference.append(list_difference(indiv_file_dR1, sum_file_dR1_sum_list,percent_difference=True))
        dR1_pass = True
    else:
        R1_pass = False
        dR1_pass = False
    if type(combine_file_Y2_combined[0]) == float and type(sum_file_Y2_sum_list[0]) == float and type(indiv_file_Y2[0]) == float:
        Y2_compare.append(indiv_file_Y2)
        Y2_compare.append(combine_file_Y2_combined)
        Y2_compare.append(sum_file_Y2_sum_list)
        Y2_difference.append(list_difference(indiv_file_Y2, combine_file_Y2_combined,percent_difference=True))
        Y2_difference.append(list_difference(indiv_file_Y2, sum_file_Y2_sum_list,percent_difference=True))
        Y2_pass = True
        dY2_compare.append(indiv_file_dY2)
        dY2_compare.append(combine_file_Y2_combined_unc)
        dY2_compare.append(sum_file_dY2_sum_list)
        dY2_difference.append(list_difference(indiv_file_dY2, combine_file_Y2_combined_unc,percent_difference=True))
        dY2_difference.append(list_difference(indiv_file_dY2, sum_file_dY2_sum_list,percent_difference=True))
        dY2_pass = True
    else:
        Y2_pass = False
        dY2_pass = False
    if type(combine_file_Ym_combined[0]) == float and type(sum_file_Ym_list[0]) == float and type(indiv_file_Ym_list[0]) == float:
        Ym_compare.append(indiv_file_Ym_list)
        Ym_compare.append(combine_file_Ym_combined)
        Ym_compare.append(sum_file_Ym_list)
        Ym_difference.append(list_difference(indiv_file_Ym_list, combine_file_Ym_combined,percent_difference=True))
        Ym_difference.append(list_difference(indiv_file_Ym_list, sum_file_Ym_list,percent_difference=True))
        Ym_pass = True
        dYm_compare.append(indiv_file_dYm_list)
        dYm_compare.append(combine_file_Ym_combined_unc)
        dYm_compare.append(sum_file_dYm_list)
        dYm_difference.append(list_difference(indiv_file_dYm_list, combine_file_Ym_combined_unc,percent_difference=True))
        dYm_difference.append(list_difference(indiv_file_dYm_list, sum_file_dYm_list,percent_difference=True))
        dYm_pass = True
    else:
        Ym_pass = False
        dYm_pass = False
    if type(combine_file_R2_single_Y2_decay_combined[0]) == float and type(sum_file_R2_single_Y2_decay[0]) == float and type(indiv_file_R2_single_Y2_decay[0]) == float:
        R2_single_Y2_compare.append(indiv_file_R2_single_Y2_decay)
        R2_single_Y2_compare.append(combine_file_R2_single_Y2_decay_combined)
        R2_single_Y2_compare.append(sum_file_R2_single_Y2_decay)
        R2_single_Y2_difference.append(list_difference(indiv_file_R2_single_Y2_decay, combine_file_R2_single_Y2_decay_combined,percent_difference=True))
        R2_single_Y2_difference.append(list_difference(indiv_file_R2_single_Y2_decay, sum_file_R2_single_Y2_decay,percent_difference=True))
        R2_single_Y2_pass = True
        dR2_single_Y2_compare.append(indiv_file_R2_unc_single_Y2_decay)
        dR2_single_Y2_compare.append(combine_file_R2_single_Y2_decay_combined_unc)
        dR2_single_Y2_compare.append(sum_file_R2_unc_single_Y2_decay)
        dR2_single_Y2_difference.append(list_difference(indiv_file_R2_unc_single_Y2_decay, combine_file_R2_single_Y2_decay_combined_unc,percent_difference=True))
        dR2_single_Y2_difference.append(list_difference(indiv_file_R2_unc_single_Y2_decay, sum_file_R2_unc_single_Y2_decay,percent_difference=True))
        dR2_single_Y2_pass = True
    else:
        R2_single_Y2_pass = False
        dR2_single_Y2_pass = False
    if type(combine_file_R2_double1_Y2_decay_combined[0]) == float and type(sum_file_R2_double1_Y2_decay[0]) == float and type(indiv_file_R2_double1_Y2_decay[0]) == float:
        R2_double1_Y2_compare.append(indiv_file_R2_double1_Y2_decay)
        R2_double1_Y2_compare.append(combine_file_R2_double1_Y2_decay_combined)
        R2_double1_Y2_compare.append(sum_file_R2_double1_Y2_decay)
        R2_double1_Y2_difference.append(list_difference(indiv_file_R2_double1_Y2_decay, combine_file_R2_double1_Y2_decay_combined,percent_difference=True))
        R2_double1_Y2_difference.append(list_difference(indiv_file_R2_double1_Y2_decay, sum_file_R2_double1_Y2_decay,percent_difference=True))
        R2_double1_Y2_pass = True
        dR2_double1_Y2_compare.append(indiv_file_R2_unc_double1_Y2_decay)
        dR2_double1_Y2_compare.append(combine_file_R2_double1_Y2_decay_combined_unc)
        dR2_double1_Y2_compare.append(sum_file_R2_unc_double1_Y2_decay)
        dR2_double1_Y2_difference.append(list_difference(indiv_file_R2_unc_double1_Y2_decay, combine_file_R2_double1_Y2_decay_combined_unc,percent_difference=True))
        dR2_double1_Y2_difference.append(list_difference(indiv_file_R2_unc_double1_Y2_decay, sum_file_R2_unc_double1_Y2_decay,percent_difference=True))
        dR2_double1_Y2_pass = True
    else:
        R2_double1_Y2_pass = False
        dR2_double1_Y2_pass = False
    if type(combine_file_R2_double2_Y2_decay_combined[0]) == float and type(sum_file_R2_double2_Y2_decay[0]) == float and type(indiv_file_R2_double2_Y2_decay[0]) == float:
        R2_double2_Y2_compare.append(indiv_file_R2_double2_Y2_decay)
        R2_double2_Y2_compare.append(combine_file_R2_double2_Y2_decay_combined)
        R2_double2_Y2_compare.append(sum_file_R2_double2_Y2_decay)
        R2_double2_Y2_difference.append(list_difference(indiv_file_R2_double2_Y2_decay, combine_file_R2_double2_Y2_decay_combined,percent_difference=True))
        R2_double2_Y2_difference.append(list_difference(indiv_file_R2_double2_Y2_decay, sum_file_R2_double2_Y2_decay,percent_difference=True))
        R2_double2_Y2_pass = True
        dR2_double2_Y2_compare.append(indiv_file_R2_unc_double2_Y2_decay)
        dR2_double2_Y2_compare.append(combine_file_R2_double2_Y2_decay_combined_unc)
        dR2_double2_Y2_compare.append(sum_file_R2_unc_double2_Y2_decay)
        dR2_double2_Y2_difference.append(list_difference(indiv_file_R2_unc_double2_Y2_decay, combine_file_R2_double2_Y2_decay_combined_unc,percent_difference=True))
        dR2_double2_Y2_difference.append(list_difference(indiv_file_R2_unc_double2_Y2_decay, sum_file_R2_unc_double2_Y2_decay,percent_difference=True))
        dR2_double2_Y2_pass = True
    else:
        R2_double2_Y2_pass = False
        dR2_double2_Y2_pass = False
    if type(combine_file_R2_double_both_Y2_decay_combined[0]) == float and type(sum_file_R2_double_both_Y2_decay[0]) == float and type(indiv_file_R2_double_both_Y2_decay[0]) == float:
        R2_double_both_Y2_compare.append(indiv_file_R2_double_both_Y2_decay)
        R2_double_both_Y2_compare.append(combine_file_R2_double_both_Y2_decay_combined)
        R2_double_both_Y2_compare.append(sum_file_R2_double_both_Y2_decay)
        R2_double_both_Y2_difference.append(list_difference(indiv_file_R2_double_both_Y2_decay, combine_file_R2_double_both_Y2_decay_combined,percent_difference=True))
        R2_double_both_Y2_difference.append(list_difference(indiv_file_R2_double_both_Y2_decay, sum_file_R2_double_both_Y2_decay,percent_difference=True))
        R2_double_both_Y2_pass = True
        dR2_double_both_Y2_compare.append(indiv_file_R2_unc_double_both_Y2_decay)
        dR2_double_both_Y2_compare.append(combine_file_R2_double_both_Y2_decay_combined_unc)
        dR2_double_both_Y2_compare.append(sum_file_R2_unc_double_both_Y2_decay)
        dR2_double_both_Y2_difference.append(list_difference(indiv_file_R2_unc_double_both_Y2_decay, combine_file_R2_double_both_Y2_decay_combined_unc,percent_difference=True))
        dR2_double_both_Y2_difference.append(list_difference(indiv_file_R2_unc_double_both_Y2_decay, sum_file_R2_unc_double_both_Y2_decay,percent_difference=True))
        dR2_double_both_Y2_pass = True
    else:
        R2_double_both_Y2_pass = False
        dR2_double_both_Y2_pass = False
    if type(combine_file_R2_user_lifetime_combined[0]) == float and type(sum_file_R2_user_lifetime[0]) == float and type(indiv_file_R2_user_lifetime[0]) == float:
        R2_user_lifetime_Y2_compare.append(indiv_file_R2_user_lifetime)
        R2_user_lifetime_Y2_compare.append(combine_file_R2_user_lifetime_combined)
        R2_user_lifetime_Y2_compare.append(sum_file_R2_user_lifetime)
        R2_user_lifetime_Y2_difference.append(list_difference(indiv_file_R2_user_lifetime, combine_file_R2_user_lifetime_combined,percent_difference=True))
        R2_user_lifetime_Y2_difference.append(list_difference(indiv_file_R2_user_lifetime, sum_file_R2_user_lifetime,percent_difference=True))
        R2_user_lifetime_Y2_pass = True
        dR2_user_lifetime_Y2_compare.append(indiv_file_R2_unc_user_lifetime)
        dR2_user_lifetime_Y2_compare.append(combine_file_R2_user_lifetime_combined_unc)
        dR2_user_lifetime_Y2_compare.append(sum_file_R2_unc_user_lifetime)
        dR2_user_lifetime_Y2_difference.append(list_difference(indiv_file_R2_unc_user_lifetime, combine_file_R2_user_lifetime_combined_unc,percent_difference=True))
        dR2_user_lifetime_Y2_difference.append(list_difference(indiv_file_R2_unc_user_lifetime, sum_file_R2_unc_user_lifetime,percent_difference=True))
        dR2_user_lifetime_Y2_pass = True
    else:
        R2_user_lifetime_Y2_pass = False
        dR2_user_lifetime_Y2_pass = False
    if calculation_type == 'Cf' and type(combine_file_calc_eff_kn_combined[0]) == float and type(sum_file_calc_eff_kn_sum_list[0]) == float and type(indiv_file_calc_eff_kn[0]) == float:
        calc_eff_kn_compare.append(indiv_file_calc_eff_kn)
        calc_eff_kn_compare.append(combine_file_calc_eff_kn_combined)
        calc_eff_kn_compare.append(sum_file_calc_eff_kn_sum_list)
        calc_eff_kn_difference.append(list_difference(indiv_file_calc_eff_kn, combine_file_calc_eff_kn_combined,percent_difference=True))
        calc_eff_kn_difference.append(list_difference(indiv_file_calc_eff_kn, sum_file_calc_eff_kn_sum_list,percent_difference=True))
        calc_eff_kn_pass = True
        calc_eff_unc_kn_compare.append(indiv_file_calc_eff_unc_kn)
        calc_eff_unc_kn_compare.append(combine_file_calc_eff_kn_combined_unc)
        calc_eff_unc_kn_compare.append(sum_file_calc_eff_unc_kn_sum_list)
        calc_eff_unc_kn_difference.append(list_difference(indiv_file_calc_eff_unc_kn,combine_file_calc_eff_kn_combined_unc,percent_difference=True))
        calc_eff_unc_kn_difference.append(list_difference(indiv_file_calc_eff_unc_kn,sum_file_calc_eff_unc_kn_sum_list,percent_difference=True))
        calc_eff_unc_kn_pass = True
    else:
        calc_eff_kn_pass = False
        calc_eff_unc_kn_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_single_fit == True:
        Ml_Y2single_compare.append(indiv_file_Ml_Y2single)
        Ml_Y2single_compare.append(combine_file_Ml_combined_Y2single)
        Ml_Y2single_compare.append(sum_file_Ml_Y2single_sum_list)
        Ml_Y2single_difference.append(list_difference(indiv_file_Ml_Y2single, combine_file_Ml_combined_Y2single, percent_difference=True))
        Ml_Y2single_difference.append(list_difference(indiv_file_Ml_Y2single, sum_file_Ml_Y2single_sum_list, percent_difference=True))
        Ml_Y2single_pass = True
        dMl_Y2single_compare.append(indiv_file_dMl_Y2single)
        dMl_Y2single_compare.append(combine_file_Ml_combined_unc_Y2single)
        dMl_Y2single_compare.append(sum_file_dMl_Y2single_sum_list)
        dMl_Y2single_difference.append(list_difference(indiv_file_dMl_Y2single, combine_file_Ml_combined_unc_Y2single,percent_difference=True))
        dMl_Y2single_difference.append(list_difference(indiv_file_dMl_Y2single, sum_file_dMl_Y2single_sum_list,percent_difference=True))
        dMl_Y2single_pass = True
    else:
        Ml_Y2single_pass = False
        dMl_Y2single_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_single_fit == True:
        Mt_Y2single_compare.append(indiv_file_Mt_Y2single)
        Mt_Y2single_compare.append(combine_file_Mt_combined_Y2single)
        Mt_Y2single_compare.append(sum_file_Mt_Y2single_sum_list)
        Mt_Y2single_difference.append(list_difference(indiv_file_Mt_Y2single, combine_file_Mt_combined_Y2single, percent_difference=True))
        Mt_Y2single_difference.append(list_difference(indiv_file_Mt_Y2single, sum_file_Mt_Y2single_sum_list, percent_difference=True))
        Mt_Y2single_pass = True
        dMt_Y2single_compare.append(indiv_file_dMt_Y2single)
        dMt_Y2single_compare.append(combine_file_Mt_combined_unc_Y2single)
        dMt_Y2single_compare.append(sum_file_dMt_Y2single_sum_list)
        dMt_Y2single_difference.append(list_difference(indiv_file_dMt_Y2single, combine_file_Mt_combined_unc_Y2single,percent_difference=True))
        dMt_Y2single_difference.append(list_difference(indiv_file_dMt_Y2single, sum_file_dMt_Y2single_sum_list,percent_difference=True))
        dMt_Y2single_pass = True
    else:
        Mt_Y2single_pass = False
        dMt_Y2single_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_single_fit == True:
        Fs_Y2single_compare.append(indiv_file_Fs_Y2single)
        Fs_Y2single_compare.append(combine_file_Fs_combined_Y2single)
        Fs_Y2single_compare.append(sum_file_Fs_Y2single_sum_list)
        Fs_Y2single_difference.append(list_difference(indiv_file_Fs_Y2single, combine_file_Fs_combined_Y2single, percent_difference=True))
        Fs_Y2single_difference.append(list_difference(indiv_file_Fs_Y2single, sum_file_Fs_Y2single_sum_list, percent_difference=True))
        Fs_Y2single_pass = True
        dFs_Y2single_compare.append(indiv_file_dFs_Y2single)
        dFs_Y2single_compare.append(combine_file_Fs_combined_unc_Y2single)
        dFs_Y2single_compare.append(sum_file_dFs_Y2single_sum_list)
        dFs_Y2single_difference.append(list_difference(indiv_file_dFs_Y2single, combine_file_Fs_combined_unc_Y2single,percent_difference=True))
        dFs_Y2single_difference.append(list_difference(indiv_file_dFs_Y2single, sum_file_dFs_Y2single_sum_list,percent_difference=True))
        dFs_Y2single_pass = True
    else:
        Fs_Y2single_pass = False
        dFs_Y2single_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_single_fit == True:
        kp_Y2single_compare.append(indiv_file_kp_Y2single)
        kp_Y2single_compare.append(combine_file_kp_combined_Y2single)
        kp_Y2single_compare.append(sum_file_kp_Y2single_sum_list)
        kp_Y2single_difference.append(list_difference(indiv_file_kp_Y2single,combine_file_kp_combined_Y2single, percent_difference=True))
        kp_Y2single_difference.append(list_difference(indiv_file_kp_Y2single,sum_file_kp_Y2single_sum_list, percent_difference=True))
        kp_Y2single_pass = True
        dkp_Y2single_compare.append(indiv_file_dkp_Y2single)
        dkp_Y2single_compare.append(combine_file_kp_combined_unc_Y2single)
        dkp_Y2single_compare.append(sum_file_dkp_Y2single_sum_list)
        dkp_Y2single_difference.append(list_difference(indiv_file_dkp_Y2single,combine_file_kp_combined_unc_Y2single,percent_difference=True))
        dkp_Y2single_difference.append(list_difference(indiv_file_dkp_Y2single,sum_file_dkp_Y2single_sum_list,percent_difference=True))
        dkp_Y2single_pass = True
    else:
        kp_Y2single_pass = False
        dkp_Y2single_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_single_fit == True:
        keff_Y2single_compare.append(indiv_file_keff_Y2single)
        keff_Y2single_compare.append(combine_file_keff_combined_Y2single)
        keff_Y2single_compare.append(sum_file_keff_Y2single_sum_list)
        keff_Y2single_difference.append(list_difference(indiv_file_keff_Y2single,combine_file_keff_combined_Y2single, percent_difference=True))
        keff_Y2single_difference.append(list_difference(indiv_file_keff_Y2single,sum_file_keff_Y2single_sum_list, percent_difference=True))
        keff_Y2single_pass = True
        dkeff_Y2single_compare.append(indiv_file_dkeff_Y2single)
        dkeff_Y2single_compare.append(combine_file_keff_combined_unc_Y2single)
        dkeff_Y2single_compare.append(sum_file_dkeff_Y2single_sum_list)
        dkeff_Y2single_difference.append(list_difference(indiv_file_dkeff_Y2single,combine_file_keff_combined_unc_Y2single,percent_difference=True))
        dkeff_Y2single_difference.append(list_difference(indiv_file_dkeff_Y2single,sum_file_dkeff_Y2single_sum_list,percent_difference=True))
        dkeff_Y2single_pass = True
    else:
        keff_Y2single_pass = False
        dkeff_Y2single_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        Ml_Y2double1_compare.append(indiv_file_Ml_Y2double1)
        Ml_Y2double1_compare.append(combine_file_Ml_combined_Y2double1)
        Ml_Y2double1_compare.append(sum_file_Ml_Y2double1_sum_list)
        Ml_Y2double1_difference.append(list_difference(indiv_file_Ml_Y2double1,combine_file_Ml_combined_Y2double1, percent_difference=True))
        Ml_Y2double1_difference.append(list_difference(indiv_file_Ml_Y2double1,sum_file_Ml_Y2double1_sum_list, percent_difference=True))
        Ml_Y2double1_pass = True
        dMl_Y2double1_compare.append(indiv_file_dMl_Y2double1)
        dMl_Y2double1_compare.append(combine_file_Ml_combined_unc_Y2double1)
        dMl_Y2double1_compare.append(sum_file_dMl_Y2double1_sum_list)
        dMl_Y2double1_difference.append(list_difference(indiv_file_dMl_Y2double1,combine_file_Ml_combined_unc_Y2double1,percent_difference=True))
        dMl_Y2double1_difference.append(list_difference(indiv_file_dMl_Y2double1,sum_file_dMl_Y2double1_sum_list,percent_difference=True))
        dMl_Y2double1_pass = True
    else:
        Ml_Y2double1_pass = False
        dMl_Y2double1_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        Mt_Y2double1_compare.append(indiv_file_Mt_Y2double1)
        Mt_Y2double1_compare.append(combine_file_Mt_combined_Y2double1)
        Mt_Y2double1_compare.append(sum_file_Mt_Y2double1_sum_list)
        Mt_Y2double1_difference.append(list_difference(indiv_file_Mt_Y2double1,combine_file_Mt_combined_Y2double1, percent_difference=True))
        Mt_Y2double1_difference.append(list_difference(indiv_file_Mt_Y2double1, sum_file_Mt_Y2double1_sum_list, percent_difference=True))
        Mt_Y2double1_pass = True
        dMt_Y2double1_compare.append(indiv_file_dMt_Y2double1)
        dMt_Y2double1_compare.append(combine_file_Mt_combined_unc_Y2double1)
        dMt_Y2double1_compare.append(sum_file_dMt_Y2double1_sum_list)
        dMt_Y2double1_difference.append(list_difference(indiv_file_dMt_Y2double1,combine_file_Mt_combined_unc_Y2double1,percent_difference=True))
        dMt_Y2double1_difference.append(list_difference(indiv_file_dMt_Y2double1,sum_file_dMt_Y2double1_sum_list,percent_difference=True))
        dMt_Y2double1_pass = True
    else:
        Mt_Y2double1_pass = False
        dMt_Y2double1_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        Fs_Y2double1_compare.append(indiv_file_Fs_Y2double1)
        Fs_Y2double1_compare.append(combine_file_Fs_combined_Y2double1)
        Fs_Y2double1_compare.append(sum_file_Fs_Y2double1_sum_list)
        Fs_Y2double1_difference.append(list_difference(indiv_file_Fs_Y2double1,combine_file_Fs_combined_Y2double1, percent_difference=True))
        Fs_Y2double1_difference.append(list_difference(indiv_file_Fs_Y2double1, sum_file_Fs_Y2double1_sum_list, percent_difference=True))
        Fs_Y2double1_pass = True
        dFs_Y2double1_compare.append(indiv_file_dFs_Y2double1)
        dFs_Y2double1_compare.append(combine_file_Fs_combined_unc_Y2double1)
        dFs_Y2double1_compare.append(sum_file_dFs_Y2double1_sum_list)
        dFs_Y2double1_difference.append(list_difference(indiv_file_dFs_Y2double1,combine_file_Fs_combined_unc_Y2double1,percent_difference=True))
        dFs_Y2double1_difference.append(list_difference(indiv_file_dFs_Y2double1,sum_file_dFs_Y2double1_sum_list,percent_difference=True))
        dFs_Y2double1_pass = True
    else:
        Fs_Y2double1_pass = False
        dFs_Y2double1_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        kp_Y2double1_compare.append(indiv_file_kp_Y2double1)
        kp_Y2double1_compare.append(combine_file_kp_combined_Y2double1)
        kp_Y2double1_compare.append(sum_file_kp_Y2double1_sum_list)
        kp_Y2double1_difference.append(list_difference(indiv_file_kp_Y2double1,combine_file_kp_combined_Y2double1, percent_difference=True))
        kp_Y2double1_difference.append(list_difference(indiv_file_kp_Y2double1, sum_file_kp_Y2double1_sum_list, percent_difference=True))
        kp_Y2double1_pass = True
        dkp_Y2double1_compare.append(indiv_file_dkp_Y2double1)
        dkp_Y2double1_compare.append(combine_file_kp_combined_unc_Y2double1)
        dkp_Y2double1_compare.append(sum_file_dkp_Y2double1_sum_list)
        dkp_Y2double1_difference.append(list_difference(indiv_file_dkp_Y2double1,combine_file_kp_combined_unc_Y2double1,percent_difference=True))
        dkp_Y2double1_difference.append(list_difference(indiv_file_dkp_Y2double1,sum_file_dkp_Y2double1_sum_list,percent_difference=True))
        dkp_Y2double1_pass = True
    else:
        kp_Y2double1_pass = False
        dkp_Y2double1_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        keff_Y2double1_compare.append(indiv_file_keff_Y2double1)
        keff_Y2double1_compare.append(combine_file_keff_combined_Y2double1)
        keff_Y2double1_compare.append(sum_file_keff_Y2double1_sum_list)
        keff_Y2double1_difference.append(list_difference(indiv_file_keff_Y2double1,combine_file_keff_combined_Y2double1, percent_difference=True))
        keff_Y2double1_difference.append(list_difference(indiv_file_keff_Y2double1,sum_file_keff_Y2double1_sum_list, percent_difference=True))
        keff_Y2double1_pass = True
        dkeff_Y2double1_compare.append(indiv_file_dkeff_Y2double1)
        dkeff_Y2double1_compare.append(combine_file_keff_combined_unc_Y2double1)
        dkeff_Y2double1_compare.append(sum_file_dkeff_Y2double1_sum_list)
        dkeff_Y2double1_difference.append(list_difference(indiv_file_dkeff_Y2double1,combine_file_keff_combined_unc_Y2double1,percent_difference=True))
        dkeff_Y2double1_difference.append(list_difference(indiv_file_dkeff_Y2double1,sum_file_dkeff_Y2double1_sum_list,percent_difference=True))
        dkeff_Y2double1_pass = True
    else:
        keff_Y2double1_pass = False
        dkeff_Y2double1_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        Ml_Y2double2_compare.append(indiv_file_Ml_Y2double2)
        Ml_Y2double2_compare.append(combine_file_Ml_combined_Y2double2)
        Ml_Y2double2_compare.append(sum_file_Ml_Y2double2_sum_list)
        Ml_Y2double2_difference.append(list_difference(indiv_file_Ml_Y2double2,combine_file_Ml_combined_Y2double2, percent_difference=True))
        Ml_Y2double2_difference.append(list_difference(indiv_file_Ml_Y2double2,sum_file_Ml_Y2double2_sum_list, percent_difference=True))
        Ml_Y2double2_pass = True
        dMl_Y2double2_compare.append(indiv_file_dMl_Y2double2)
        dMl_Y2double2_compare.append(combine_file_Ml_combined_unc_Y2double2)
        dMl_Y2double2_compare.append(sum_file_dMl_Y2double2_sum_list)
        dMl_Y2double2_difference.append(list_difference(combine_file_Ml_combined_unc_Y2double2,sum_file_dMl_Y2double2_sum_list,percent_difference=True))
        dMl_Y2double2_difference.append(list_difference(combine_file_Ml_combined_unc_Y2double2,sum_file_dMl_Y2double2_sum_list,percent_difference=True))
        dMl_Y2double2_pass = True
    else:
        Ml_Y2double2_pass = False
        dMl_Y2double2_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        Mt_Y2double2_compare.append(indiv_file_Mt_Y2double2)
        Mt_Y2double2_compare.append(combine_file_Mt_combined_Y2double2)
        Mt_Y2double2_compare.append(sum_file_Mt_Y2double2_sum_list)
        Mt_Y2double2_difference.append(list_difference(indiv_file_Mt_Y2double2,combine_file_Mt_combined_Y2double2, percent_difference=True))
        Mt_Y2double2_difference.append(list_difference(indiv_file_Mt_Y2double2,sum_file_Mt_Y2double2_sum_list, percent_difference=True))
        Mt_Y2double2_pass = True
        dMt_Y2double2_compare.append(indiv_file_dMt_Y2double2)
        dMt_Y2double2_compare.append(combine_file_Mt_combined_unc_Y2double2)
        dMt_Y2double2_compare.append(sum_file_dMt_Y2double2_sum_list)
        dMt_Y2double2_difference.append(list_difference(indiv_file_dMt_Y2double2,combine_file_Mt_combined_unc_Y2double2, percent_difference=True))
        dMt_Y2double2_difference.append(list_difference(indiv_file_dMt_Y2double2,sum_file_dMt_Y2double2_sum_list, percent_difference=True))
        dMt_Y2double2_pass = True
    else:
        Mt_Y2double2_pass = False
        dMt_Y2double2_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        Fs_Y2double2_compare.append(indiv_file_Fs_Y2double2)
        Fs_Y2double2_compare.append(combine_file_Fs_combined_Y2double2)
        Fs_Y2double2_compare.append(sum_file_Fs_Y2double2_sum_list)
        Fs_Y2double2_difference.append(list_difference(indiv_file_Fs_Y2double2,combine_file_Fs_combined_Y2double2, percent_difference=True))
        Fs_Y2double2_difference.append(list_difference(indiv_file_Fs_Y2double2,sum_file_Fs_Y2double2_sum_list, percent_difference=True))
        Fs_Y2double2_pass = True
        dFs_Y2double2_compare.append(indiv_file_dFs_Y2double2)
        dFs_Y2double2_compare.append(combine_file_Fs_combined_unc_Y2double2)
        dFs_Y2double2_compare.append(sum_file_dFs_Y2double2_sum_list)
        dFs_Y2double2_difference.append(list_difference(indiv_file_dFs_Y2double2,combine_file_Fs_combined_unc_Y2double2, percent_difference=True))
        dFs_Y2double2_difference.append(list_difference(indiv_file_dFs_Y2double2,sum_file_dFs_Y2double2_sum_list, percent_difference=True))
        dFs_Y2double2_pass = True
    else:
        Fs_Y2double2_pass = False
        dFs_Y2double2_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        kp_Y2double2_compare.append(indiv_file_kp_Y2double2)
        kp_Y2double2_compare.append(combine_file_kp_combined_Y2double2)
        kp_Y2double2_compare.append(sum_file_kp_Y2double2_sum_list)
        kp_Y2double2_difference.append(list_difference(indiv_file_kp_Y2double2,combine_file_kp_combined_Y2double2, percent_difference=True))
        kp_Y2double2_difference.append(list_difference(indiv_file_kp_Y2double2,sum_file_kp_Y2double2_sum_list, percent_difference=True))
        kp_Y2double2_pass = True
        dkp_Y2double2_compare.append(indiv_file_dkp_Y2double2)
        dkp_Y2double2_compare.append(combine_file_kp_combined_unc_Y2double2)
        dkp_Y2double2_compare.append(sum_file_dkp_Y2double2_sum_list)
        dkp_Y2double2_difference.append(list_difference(indiv_file_dkp_Y2double2,combine_file_kp_combined_unc_Y2double2, percent_difference=True))
        dkp_Y2double2_difference.append(list_difference(indiv_file_dkp_Y2double2,sum_file_dkp_Y2double2_sum_list, percent_difference=True))
        dkp_Y2double2_pass = True
    else:
        kp_Y2double2_pass = False
        dkp_Y2double2_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        keff_Y2double2_compare.append(indiv_file_keff_Y2double2)
        keff_Y2double2_compare.append(combine_file_keff_combined_Y2double2)
        keff_Y2double2_compare.append(sum_file_keff_Y2double2_sum_list)
        keff_Y2double2_difference.append(list_difference(indiv_file_keff_Y2double2,combine_file_keff_combined_Y2double2, percent_difference=True))
        keff_Y2double2_difference.append(list_difference(indiv_file_keff_Y2double2,sum_file_keff_Y2double2_sum_list, percent_difference=True))
        keff_Y2double2_pass = True
        dkeff_Y2double2_compare.append(indiv_file_dkeff_Y2double2)
        dkeff_Y2double2_compare.append(combine_file_keff_combined_unc_Y2double2)
        dkeff_Y2double2_compare.append(sum_file_dkeff_Y2double2_sum_list)
        dkeff_Y2double2_difference.append(list_difference(indiv_file_dkeff_Y2double2,combine_file_keff_combined_unc_Y2double2, percent_difference=True))
        dkeff_Y2double2_difference.append(list_difference(indiv_file_dkeff_Y2double2,sum_file_dkeff_Y2double2_sum_list, percent_difference=True))
        dkeff_Y2double2_pass = True
    else:
        keff_Y2double2_pass = False
        dkeff_Y2double2_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        Ml_Y2double_both_compare.append(indiv_file_Ml_Y2double_both)
        Ml_Y2double_both_compare.append(combine_file_Ml_combined_Y2double_both)
        Ml_Y2double_both_compare.append(sum_file_Ml_Y2double_both_sum_list)
        Ml_Y2double_both_difference.append(list_difference(indiv_file_Ml_Y2double_both,combine_file_Ml_combined_Y2double_both, percent_difference=True))
        Ml_Y2double_both_difference.append(list_difference(indiv_file_Ml_Y2double_both,sum_file_Ml_Y2double_both_sum_list, percent_difference=True))
        Ml_Y2double_both_pass = True
        dMl_Y2double_both_compare.append(indiv_file_dMl_Y2double_both)
        dMl_Y2double_both_compare.append(combine_file_Ml_combined_unc_Y2double_both)
        dMl_Y2double_both_compare.append(sum_file_dMl_Y2double_both_sum_list)
        dMl_Y2double_both_difference.append(list_difference(indiv_file_dMl_Y2double_both,combine_file_Ml_combined_unc_Y2double_both, percent_difference=True))
        dMl_Y2double_both_difference.append(list_difference(indiv_file_dMl_Y2double_both,sum_file_dMl_Y2double_both_sum_list, percent_difference=True))
        dMl_Y2double_both_pass = True
    else:
        Ml_Y2double_both_pass = False
        dMl_Y2double_both_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        Mt_Y2double_both_compare.append(indiv_file_Mt_Y2double_both)
        Mt_Y2double_both_compare.append(combine_file_Mt_combined_Y2double_both)
        Mt_Y2double_both_compare.append(sum_file_Mt_Y2double_both_sum_list)
        Mt_Y2double_both_difference.append(list_difference(indiv_file_Mt_Y2double_both,combine_file_Mt_combined_Y2double_both, percent_difference=True))
        Mt_Y2double_both_difference.append(list_difference(indiv_file_Mt_Y2double_both,sum_file_Mt_Y2double_both_sum_list, percent_difference=True))
        Mt_Y2double_both_pass = True
        dMt_Y2double_both_compare.append(indiv_file_dMt_Y2double_both)
        dMt_Y2double_both_compare.append(combine_file_Mt_combined_unc_Y2double_both)
        dMt_Y2double_both_compare.append(sum_file_dMt_Y2double_both_sum_list)
        dMt_Y2double_both_difference.append(list_difference(indiv_file_dMt_Y2double_both,combine_file_Mt_combined_unc_Y2double_both, percent_difference=True))
        dMt_Y2double_both_difference.append(list_difference(indiv_file_dMt_Y2double_both,sum_file_dMt_Y2double_both_sum_list, percent_difference=True))
        dMt_Y2double_both_pass = True
    else:
        Mt_Y2double_both_pass = False
        dMt_Y2double_both_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        Fs_Y2double_both_compare.append(indiv_file_Fs_Y2double_both)
        Fs_Y2double_both_compare.append(combine_file_Fs_combined_Y2double_both)
        Fs_Y2double_both_compare.append(sum_file_Fs_Y2double_both_sum_list)
        Fs_Y2double_both_difference.append(list_difference(indiv_file_Fs_Y2double_both,combine_file_Fs_combined_Y2double_both, percent_difference=True))
        Fs_Y2double_both_difference.append(list_difference(indiv_file_Fs_Y2double_both,sum_file_Fs_Y2double_both_sum_list, percent_difference=True))
        Fs_Y2double_both_pass = True
        dFs_Y2double_both_compare.append(indiv_file_dFs_Y2double_both)
        dFs_Y2double_both_compare.append(combine_file_Fs_combined_unc_Y2double_both)
        dFs_Y2double_both_compare.append(sum_file_dFs_Y2double_both_sum_list)
        dFs_Y2double_both_difference.append(list_difference(indiv_file_dFs_Y2double_both,combine_file_Fs_combined_unc_Y2double_both, percent_difference=True))
        dFs_Y2double_both_difference.append(list_difference(indiv_file_dFs_Y2double_both,sum_file_dFs_Y2double_both_sum_list, percent_difference=True))
        dFs_Y2double_both_pass = True
    else:
        Fs_Y2double_both_pass = False
        dFs_Y2double_both_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        kp_Y2double_both_compare.append(indiv_file_kp_Y2double_both)
        kp_Y2double_both_compare.append(combine_file_kp_combined_Y2double_both)
        kp_Y2double_both_compare.append(sum_file_kp_Y2double_both_sum_list)
        kp_Y2double_both_difference.append(list_difference(indiv_file_kp_Y2double_both,combine_file_kp_combined_Y2double_both, percent_difference=True))
        kp_Y2double_both_difference.append(list_difference(indiv_file_kp_Y2double_both,sum_file_kp_Y2double_both_sum_list, percent_difference=True))
        kp_Y2double_both_pass = True
        dkp_Y2double_both_compare.append(indiv_file_dkp_Y2double_both)
        dkp_Y2double_both_compare.append(combine_file_kp_combined_unc_Y2double_both)
        dkp_Y2double_both_compare.append(sum_file_dkp_Y2double_both_sum_list)
        dkp_Y2double_both_difference.append(list_difference(indiv_file_dkp_Y2double_both,combine_file_kp_combined_unc_Y2double_both, percent_difference=True))
        dkp_Y2double_both_difference.append(list_difference(indiv_file_dkp_Y2double_both,sum_file_dkp_Y2double_both_sum_list, percent_difference=True))
        dkp_Y2double_both_pass = True
    else:
        kp_Y2double_both_pass = False
        dkp_Y2double_both_pass = False
    if calculation_type == 'Multiplicity' and perform_Y2_double_fit == True:
        keff_Y2double_both_compare.append(indiv_file_keff_Y2double_both)
        keff_Y2double_both_compare.append(combine_file_keff_combined_Y2double_both)
        keff_Y2double_both_compare.append(sum_file_keff_Y2double_both_sum_list)
        keff_Y2double_both_difference.append(list_difference(indiv_file_keff_Y2double_both,combine_file_keff_combined_Y2double_both, percent_difference=True))
        keff_Y2double_both_difference.append(list_difference(indiv_file_keff_Y2double_both,sum_file_keff_Y2double_both_sum_list, percent_difference=True))
        keff_Y2double_both_pass = True
        dkeff_Y2double_both_compare.append(indiv_file_dkeff_Y2double_both)
        dkeff_Y2double_both_compare.append(combine_file_keff_combined_unc_Y2double_both)
        dkeff_Y2double_both_compare.append(sum_file_dkeff_Y2double_both_sum_list)
        dkeff_Y2double_both_difference.append(list_difference(indiv_file_dkeff_Y2double_both,combine_file_keff_combined_unc_Y2double_both, percent_difference=True))
        dkeff_Y2double_both_difference.append(list_difference(indiv_file_dkeff_Y2double_both,sum_file_dkeff_Y2double_both_sum_list, percent_difference=True))
        dkeff_Y2double_both_pass = True
    else:
        keff_Y2double_both_pass = False
        dkeff_Y2double_both_pass = False
    if calculation_type == 'Multiplicity' and use_user_specified_lifetime == True:
        Ml_Y2user_lifetime_compare.append(indiv_file_Ml_Y2user_lifetime)
        Ml_Y2user_lifetime_compare.append(combine_file_Ml_combined_Y2user_lifetime)
        Ml_Y2user_lifetime_compare.append(sum_file_Ml_Y2user_lifetime_sum_list)
        Ml_Y2user_lifetime_difference.append(list_difference(indiv_file_Ml_Y2user_lifetime,combine_file_Ml_combined_Y2user_lifetime, percent_difference=True))
        Ml_Y2user_lifetime_difference.append(list_difference(indiv_file_Ml_Y2user_lifetime,sum_file_Ml_Y2user_lifetime_sum_list, percent_difference=True))
        Ml_Y2user_lifetime_pass = True
        dMl_Y2user_lifetime_compare.append(indiv_file_dMl_Y2user_lifetime)
        dMl_Y2user_lifetime_compare.append(combine_file_Ml_combined_unc_Y2user_lifetime)
        dMl_Y2user_lifetime_compare.append(sum_file_dMl_Y2user_lifetime_sum_list)
        dMl_Y2user_lifetime_difference.append(list_difference(indiv_file_dMl_Y2user_lifetime,combine_file_Ml_combined_unc_Y2user_lifetime, percent_difference=True))
        dMl_Y2user_lifetime_difference.append(list_difference(indiv_file_dMl_Y2user_lifetime,sum_file_dMl_Y2user_lifetime_sum_list, percent_difference=True))
        dMl_Y2user_lifetime_pass = True
    else:
        Ml_Y2user_lifetime_pass = False
        dMl_Y2user_lifetime_pass = False
    if calculation_type == 'Multiplicity' and use_user_specified_lifetime == True:
        Mt_Y2user_lifetime_compare.append(indiv_file_Mt_Y2user_lifetime)
        Mt_Y2user_lifetime_compare.append(combine_file_Mt_combined_Y2user_lifetime)
        Mt_Y2user_lifetime_compare.append(sum_file_Mt_Y2user_lifetime_sum_list)
        Mt_Y2user_lifetime_difference.append(list_difference(indiv_file_Mt_Y2user_lifetime,combine_file_Mt_combined_Y2user_lifetime, percent_difference=True))
        Mt_Y2user_lifetime_difference.append(list_difference(indiv_file_Mt_Y2user_lifetime,sum_file_Mt_Y2user_lifetime_sum_list, percent_difference=True))
        Mt_Y2user_lifetime_pass = True
        dMt_Y2user_lifetime_compare.append(indiv_file_dMt_Y2user_lifetime)
        dMt_Y2user_lifetime_compare.append(combine_file_Mt_combined_unc_Y2user_lifetime)
        dMt_Y2user_lifetime_compare.append(sum_file_dMt_Y2user_lifetime_sum_list)
        dMt_Y2user_lifetime_difference.append(list_difference(indiv_file_dMt_Y2user_lifetime,combine_file_Mt_combined_unc_Y2user_lifetime, percent_difference=True))
        dMt_Y2user_lifetime_difference.append(list_difference(indiv_file_dMt_Y2user_lifetime,sum_file_dMt_Y2user_lifetime_sum_list, percent_difference=True))
        dMt_Y2user_lifetime_pass = True
    else:
        Mt_Y2user_lifetime_pass = False
        dMt_Y2user_lifetime_pass = False
    if calculation_type == 'Multiplicity' and use_user_specified_lifetime == True:
        Fs_Y2user_lifetime_compare.append(indiv_file_Fs_Y2user_lifetime)
        Fs_Y2user_lifetime_compare.append(combine_file_Fs_combined_Y2user_lifetime)
        Fs_Y2user_lifetime_compare.append(sum_file_Fs_Y2user_lifetime_sum_list)
        Fs_Y2user_lifetime_difference.append(list_difference(indiv_file_Fs_Y2user_lifetime,combine_file_Fs_combined_Y2user_lifetime, percent_difference=True))
        Fs_Y2user_lifetime_difference.append(list_difference(indiv_file_Fs_Y2user_lifetime,sum_file_Fs_Y2user_lifetime_sum_list, percent_difference=True))
        Fs_Y2user_lifetime_pass = True
        dFs_Y2user_lifetime_compare.append(indiv_file_dFs_Y2user_lifetime)
        dFs_Y2user_lifetime_compare.append(combine_file_Fs_combined_unc_Y2user_lifetime)
        dFs_Y2user_lifetime_compare.append(sum_file_dFs_Y2user_lifetime_sum_list)
        dFs_Y2user_lifetime_difference.append(list_difference(indiv_file_dFs_Y2user_lifetime,combine_file_Fs_combined_unc_Y2user_lifetime, percent_difference=True))
        dFs_Y2user_lifetime_difference.append(list_difference(indiv_file_dFs_Y2user_lifetime,sum_file_dFs_Y2user_lifetime_sum_list, percent_difference=True))
        dFs_Y2user_lifetime_pass = True
    else:
        Fs_Y2user_lifetime_pass = False
        dFs_Y2user_lifetime_pass = False
    if calculation_type == 'Multiplicity' and use_user_specified_lifetime == True:
        kp_Y2user_lifetime_compare.append(indiv_file_kp_Y2user_lifetime)
        kp_Y2user_lifetime_compare.append(combine_file_kp_combined_Y2user_lifetime)
        kp_Y2user_lifetime_compare.append(sum_file_kp_Y2user_lifetime_sum_list)
        kp_Y2user_lifetime_difference.append(list_difference(indiv_file_kp_Y2user_lifetime,combine_file_kp_combined_Y2user_lifetime, percent_difference=True))
        kp_Y2user_lifetime_difference.append(list_difference(indiv_file_kp_Y2user_lifetime,sum_file_kp_Y2user_lifetime_sum_list, percent_difference=True))
        kp_Y2user_lifetime_pass = True
        dkp_Y2user_lifetime_compare.append(indiv_file_dkp_Y2user_lifetime)
        dkp_Y2user_lifetime_compare.append(combine_file_kp_combined_unc_Y2user_lifetime)
        dkp_Y2user_lifetime_compare.append(sum_file_dkp_Y2user_lifetime_sum_list)
        dkp_Y2user_lifetime_difference.append(list_difference(indiv_file_dkp_Y2user_lifetime,combine_file_kp_combined_unc_Y2user_lifetime, percent_difference=True))
        dkp_Y2user_lifetime_difference.append(list_difference(indiv_file_dkp_Y2user_lifetime,sum_file_dkp_Y2user_lifetime_sum_list, percent_difference=True))
        dkp_Y2user_lifetime_pass = True
    else:
        kp_Y2user_lifetime_pass = False
        dkp_Y2user_lifetime_pass = False
    if calculation_type == 'Multiplicity' and use_user_specified_lifetime == True:
        keff_Y2user_lifetime_compare.append(indiv_file_keff_Y2user_lifetime)
        keff_Y2user_lifetime_compare.append(combine_file_keff_combined_Y2user_lifetime)
        keff_Y2user_lifetime_compare.append(sum_file_keff_Y2user_lifetime_sum_list)
        keff_Y2user_lifetime_difference.append(list_difference(indiv_file_keff_Y2user_lifetime,combine_file_keff_combined_Y2user_lifetime, percent_difference=True))
        keff_Y2user_lifetime_difference.append(list_difference(indiv_file_keff_Y2user_lifetime,sum_file_keff_Y2user_lifetime_sum_list, percent_difference=True))
        keff_Y2user_lifetime_pass = True
        dkeff_Y2user_lifetime_compare.append(indiv_file_dkeff_Y2user_lifetime)
        dkeff_Y2user_lifetime_compare.append(combine_file_keff_combined_unc_Y2user_lifetime)
        dkeff_Y2user_lifetime_compare.append(sum_file_dkeff_Y2user_lifetime_sum_list)
        dkeff_Y2user_lifetime_difference.append(list_difference(indiv_file_dkeff_Y2user_lifetime,combine_file_keff_combined_unc_Y2user_lifetime, percent_difference=True))
        dkeff_Y2user_lifetime_difference.append(list_difference(indiv_file_dkeff_Y2user_lifetime,sum_file_dkeff_Y2user_lifetime_sum_list, percent_difference=True))
        dkeff_Y2user_lifetime_pass = True
    else:
        keff_Y2user_lifetime_pass = False
        dkeff_Y2user_lifetime_pass = False
    
    return gatewidth_pass, gatewidth_compare, Y1_pass, Y1_compare, Y1_difference, dY1_pass, dY1_compare, dY1_difference, R1_pass, R1_compare, R1_difference, dR1_pass, dR1_compare, dR1_difference, Y2_pass, Y2_compare, Y2_difference, dY2_pass, dY2_compare, dY2_difference, Ym_pass, Ym_compare, Ym_difference, dYm_pass, dYm_compare, dYm_difference, R2_single_Y2_pass, R2_single_Y2_compare, R2_single_Y2_difference, dR2_single_Y2_pass, dR2_single_Y2_compare, dR2_single_Y2_difference, R2_double1_Y2_pass, R2_double1_Y2_compare, R2_double1_Y2_difference, dR2_double1_Y2_pass, dR2_double1_Y2_compare, dR2_double1_Y2_difference, R2_double2_Y2_pass, R2_double2_Y2_compare, R2_double2_Y2_difference, dR2_double2_Y2_pass, dR2_double2_Y2_compare, dR2_double2_Y2_difference,R2_double_both_Y2_pass, R2_double_both_Y2_compare, R2_double_both_Y2_difference, dR2_double_both_Y2_pass, dR2_double_both_Y2_compare, dR2_double_both_Y2_difference,R2_user_lifetime_Y2_pass, R2_user_lifetime_Y2_compare, R2_user_lifetime_Y2_difference, dR2_user_lifetime_Y2_pass, dR2_user_lifetime_Y2_compare, dR2_user_lifetime_Y2_difference, calc_eff_kn_pass, calc_eff_kn_compare, calc_eff_kn_difference, calc_eff_unc_kn_pass, calc_eff_unc_kn_compare, calc_eff_unc_kn_difference, Ml_Y2single_pass, Ml_Y2single_compare, Ml_Y2single_difference, dMl_Y2single_pass, dMl_Y2single_compare, dMl_Y2single_difference, Mt_Y2single_pass, Mt_Y2single_compare, Mt_Y2single_difference, dMt_Y2single_pass, dMt_Y2single_compare, dMt_Y2single_difference, Fs_Y2single_pass, Fs_Y2single_compare, Fs_Y2single_difference, dFs_Y2single_pass, dFs_Y2single_compare, dFs_Y2single_difference, kp_Y2single_pass, kp_Y2single_compare, kp_Y2single_difference, dkp_Y2single_pass, dkp_Y2single_compare, dkp_Y2single_difference, keff_Y2single_pass, keff_Y2single_compare, keff_Y2single_difference, dkeff_Y2single_pass, dkeff_Y2single_compare, dkeff_Y2single_difference, Ml_Y2double1_pass, Ml_Y2double1_compare, Ml_Y2double1_difference, dMl_Y2double1_pass, dMl_Y2double1_compare, dMl_Y2double1_difference, Mt_Y2double1_pass, Mt_Y2double1_compare, Mt_Y2double1_difference, dMt_Y2double1_pass, dMt_Y2double1_compare, dMt_Y2double1_difference, Fs_Y2double1_pass, Fs_Y2double1_compare, Fs_Y2double1_difference, dFs_Y2double1_pass, dFs_Y2double1_compare, dFs_Y2double1_difference, kp_Y2double1_pass, kp_Y2double1_compare, kp_Y2double1_difference, dkp_Y2double1_pass, dkp_Y2double1_compare, dkp_Y2double1_difference, keff_Y2double1_pass, keff_Y2double1_compare, keff_Y2double1_difference, dkeff_Y2double1_pass, dkeff_Y2double1_compare, dkeff_Y2double1_difference, Ml_Y2double2_pass, Ml_Y2double2_compare, Ml_Y2double2_difference, dMl_Y2double2_pass, dMl_Y2double2_compare, dMl_Y2double2_difference, Mt_Y2double2_pass, Mt_Y2double2_compare, Mt_Y2double2_difference, dMt_Y2double2_pass, dMt_Y2double2_compare, dMt_Y2double2_difference, Fs_Y2double2_pass, Fs_Y2double2_compare, Fs_Y2double2_difference, dFs_Y2double2_pass, dFs_Y2double2_compare, dFs_Y2double2_difference, kp_Y2double2_pass, kp_Y2double2_compare, kp_Y2double2_difference, dkp_Y2double2_pass, dkp_Y2double2_compare, dkp_Y2double2_difference, keff_Y2double2_pass, keff_Y2double2_compare, keff_Y2double2_difference, dkeff_Y2double2_pass, dkeff_Y2double2_compare, dkeff_Y2double2_difference, Ml_Y2double_both_pass, Ml_Y2double_both_compare, Ml_Y2double_both_difference, dMl_Y2double_both_pass, dMl_Y2double_both_compare, dMl_Y2double_both_difference, Mt_Y2double_both_pass, Mt_Y2double_both_compare, Mt_Y2double_both_difference, dMt_Y2double_both_pass, dMt_Y2double_both_compare, dMt_Y2double_both_difference, Fs_Y2double_both_pass, Fs_Y2double_both_compare, Fs_Y2double_both_difference, dFs_Y2double_both_pass, dFs_Y2double_both_compare, dFs_Y2double_both_difference, kp_Y2double_both_pass, kp_Y2double_both_compare, kp_Y2double_both_difference, dkp_Y2double_both_pass, dkp_Y2double_both_compare, dkp_Y2double_both_difference, keff_Y2double_both_pass, keff_Y2double_both_compare, keff_Y2double_both_difference, dkeff_Y2double_both_pass, dkeff_Y2double_both_compare, dkeff_Y2double_both_difference, Ml_Y2user_lifetime_pass, Ml_Y2user_lifetime_compare, Ml_Y2user_lifetime_difference, dMl_Y2user_lifetime_pass, dMl_Y2user_lifetime_compare, dMl_Y2user_lifetime_difference, Mt_Y2user_lifetime_pass, Mt_Y2user_lifetime_compare, Mt_Y2user_lifetime_difference, dMt_Y2user_lifetime_pass, dMt_Y2user_lifetime_compare, dMt_Y2user_lifetime_difference, Fs_Y2user_lifetime_pass, Fs_Y2user_lifetime_compare, Fs_Y2user_lifetime_difference, dFs_Y2user_lifetime_pass, dFs_Y2user_lifetime_compare, dFs_Y2user_lifetime_difference, kp_Y2user_lifetime_pass, kp_Y2user_lifetime_compare, kp_Y2user_lifetime_difference, dkp_Y2user_lifetime_pass, dkp_Y2user_lifetime_compare, dkp_Y2user_lifetime_difference, keff_Y2user_lifetime_pass, keff_Y2user_lifetime_compare, keff_Y2user_lifetime_difference, dkeff_Y2user_lifetime_pass, dkeff_Y2user_lifetime_compare, dkeff_Y2user_lifetime_difference
    