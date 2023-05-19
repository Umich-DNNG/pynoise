# Reads in a csv file

import csv


def delete_header(list_name):
    
    if len(list_name) > 0:
        del list_name[0]
        
    return list_name


def change_type(main_list):
    
    """ Attempts to convert to int. 
    If that fails it attempts to convert to float."""
    
    final_list = []
    
    for sublist in main_list:
        current_b = []
        for element in sublist:
            try:
                current_b.append(int(element))
            except:
                ValueError
                try:
                    current_b.append(float(element))
                except:
                    ValueError
                    current_b.append(element)
                
        final_list.append(current_b)
        
    return final_list


def read_csv(filename):

    [gatewidth_list, first_reduced_factorial_moment_list, second_reduced_factorial_moment_list, third_reduced_factorial_moment_list, fourth_reduced_factorial_moment_list, first_factorial_moment_list, second_factorial_moment_list, third_factorial_moment_list, fourth_factorial_moment_list, Y1_list, dY1_list, Y2_list, dY2_list, R1_list, dR1_list, R2_single_Y2_decay, R2_unc_single_Y2_decay, R2_double1_Y2_decay, R2_unc_double1_Y2_decay, R2_double2_Y2_decay, R2_unc_double2_Y2_decay, R2_double_both_Y2_decay, R2_unc_double_both_Y2_decay, R2_user_lifetime, R2_unc_user_lifetime, Ym_list, dYm_list, Ml_list_Y2_single, dMl_list_Y2_single, Fs_list_Y2_single, dFs_list_Y2_single, Mt_list_Y2_single, dMt_list_Y2_single, kp_list_Y2_single, dkp_list_Y2_single, keff_list_Y2_single, dkeff_list_Y2_single, Ml_double1_list, dMl_double1_list, Fs_double1_list, dFs_double1_list, Mt_double1_list, dMt_double1_list, kp_double1_list, dkp_double1_list, keff_double1_list, dkeff_double1_list, Ml_double2_list, dMl_double2_list, Fs_double2_list, dFs_double2_list, Mt_double2_list, dMt_double2_list, kp_double2_list, dkp_double2_list, keff_double2_list, dkeff_double2_list, Ml_double_both_list, dMl_double_both_list, Fs_double_both_list, dFs_double_both_list, Mt_double_both_list, dMt_double_both_list, kp_double_both_list, dkp_double_both_list, keff_double_both_list, dkeff_double_both_list, Ml_user_lifetime_list, dMl_user_lifetime_list, Fs_user_lifetime_list, dFs_user_lifetime_list, Mt_user_lifetime_list, dMt_user_lifetime_list, kp_user_lifetime_list, dkp_user_lifetime_list, keff_user_lifetime_list, dkeff_user_lifetime_list, calc_eff_kn_list, calc_eff_unc_kn_list] =  ([] for i in range(79))
    
    search_list = ['Gate-width', 'm1', 'm2', 'm3', 'm4', 'C1', 'C2', 'C3', 'C4', 'Y1', 'dY1', 'Y2', 'dY2', 'R1', 'dR1', 'R2_single_Y2_decay', 'R2_unc_single_Y2_decay', 'R2_double1_Y2_decay', 'R2_unc_double1_Y2_decay', 'R2_double2_Y2_decay', 'R2_unc_double2_Y2_decay', 'R2_double_both_Y2_decay', 'R2_unc_double_both_Y2_decay', 'R2_user_lifetime', 'R2_unc_user_lifetime', 'Ym', 'dYm', 'Ml (Y2 single)', 'dMl (Y2 single)', 'Fs (Y2 single)', 'dFs (Y2 single)', 'Mt (Y2 single)', 'dMt (Y2 single)', 'kp (Y2 single)', 'dkp (Y2 single)', 'keff (Y2 single)', 'dkeff (Y2 single)', 'Ml (Y2_double1)', 'dMl (Y2 double1)', 'Fs (Y2 double1)', 'dFs (Y2 double1)', 'Mt (Y2 double1)', 'dMt (Y2 double1)', 'kp (Y2 double1)', 'dkp (Y2 double1)', 'keff (Y2 double1)', 'dkeff (Y2 double1)', 'Ml (Y2_double2)', 'dMl (Y2 double2)', 'Fs (Y2 double2)', 'dFs (Y2 double2)', 'Mt (Y2 double2)', 'dMt (Y2 double2)', 'kp (Y2 double2)', 'dkp (Y2 double2)', 'keff (Y2 double2)', 'dkeff (Y2 double2)', 'Ml (Y2_double_both)', 'dMl (Y2 double_both)', 'Fs (Y2 double_both)', 'dFs (Y2 double_both)', 'Mt (Y2 double_both)', 'dMt (Y2 double_both)', 'kp (Y2 double_both)', 'dkp (Y2 double_both)', 'keff (Y2 double_both)', 'dkeff (Y2 double_both)', 'Ml (Y2_user_lifetime)', 'dMl (Y2 user_lifetime)', 'Fs (Y2 user_lifetime)', 'dFs (Y2 user_lifetime)', 'Mt (Y2 user_lifetime)', 'dMt (Y2 user_lifetime)', 'kp (Y2 user_lifetime)', 'dkp (Y2 user_lifetime)', 'keff (Y2 user_lifetime)', 'dkeff (Y2 user_lifetime)', 'eff from Cf', 'deff from Cf']
    update_lists = [gatewidth_list, first_reduced_factorial_moment_list, second_reduced_factorial_moment_list, third_reduced_factorial_moment_list, fourth_reduced_factorial_moment_list, first_factorial_moment_list, second_factorial_moment_list, third_factorial_moment_list, fourth_factorial_moment_list, Y1_list, dY1_list, Y2_list, dY2_list, R1_list, dR1_list, R2_single_Y2_decay, R2_unc_single_Y2_decay, R2_double1_Y2_decay, R2_unc_double1_Y2_decay, R2_double2_Y2_decay, R2_unc_double2_Y2_decay, R2_double_both_Y2_decay, R2_unc_double_both_Y2_decay, R2_user_lifetime, R2_unc_user_lifetime, Ym_list, dYm_list, Ml_list_Y2_single, dMl_list_Y2_single, Fs_list_Y2_single, dFs_list_Y2_single, Mt_list_Y2_single, dMt_list_Y2_single, kp_list_Y2_single, dkp_list_Y2_single, keff_list_Y2_single, dkeff_list_Y2_single, Ml_double1_list, dMl_double1_list, Fs_double1_list, dFs_double1_list, Mt_double1_list, dMt_double1_list, kp_double1_list, dkp_double1_list, keff_double1_list, dkeff_double1_list, Ml_double2_list, dMl_double2_list, Fs_double2_list, dFs_double2_list, Mt_double2_list, dMt_double2_list, kp_double2_list, dkp_double2_list, keff_double2_list, dkeff_double2_list, Ml_double_both_list, dMl_double_both_list, Fs_double_both_list, dFs_double_both_list, Mt_double_both_list, dMt_double_both_list, kp_double_both_list, dkp_double_both_list, keff_double_both_list, dkeff_double_both_list, Ml_user_lifetime_list, dMl_user_lifetime_list, Fs_user_lifetime_list, dFs_user_lifetime_list, Mt_user_lifetime_list, dMt_user_lifetime_list, kp_user_lifetime_list, dkp_user_lifetime_list, keff_user_lifetime_list, dkeff_user_lifetime_list, calc_eff_kn_list, calc_eff_unc_kn_list]
          
    f = open(filename, "r")
    data = list(csv.reader(f, delimiter=','))
    f.close()
        
    header = data[0]
    
    for i in range(0,len(update_lists)):
        
        current_search = search_list[i]
        current_update = update_lists[i]
        
        if current_search in header:
            location = header.index(current_search)
            for row in data:
                current_update.append(row[location])
    
    for sublist in update_lists:
        delete_header(sublist)
    
    update_lists = change_type(update_lists)
    
    gatewidth_list = update_lists[0]
    first_reduced_factorial_moment_list = update_lists[1]
    second_reduced_factorial_moment_list = update_lists[2]
    third_reduced_factorial_moment_list = update_lists[3]
    fourth_reduced_factorial_moment_list = update_lists[4]
    first_factorial_moment_list = update_lists[5]
    second_factorial_moment_list = update_lists[6]
    third_factorial_moment_list = update_lists[7]
    fourth_factorial_moment_list = update_lists[8]
    Y1_list = update_lists[9]
    dY1_list = update_lists[10]
    Y2_list = update_lists[11]
    dY2_list = update_lists[12]
    R1_list = update_lists[13]
    dR1_list = update_lists[14]
    R2_single_Y2_decay = update_lists[15]
    R2_unc_single_Y2_decay = update_lists[16]
    R2_double1_Y2_decay = update_lists[17]
    R2_unc_double1_Y2_decay = update_lists[18]
    R2_double2_Y2_decay = update_lists[19]
    R2_unc_double2_Y2_decay = update_lists[20]
    R2_double_both_Y2_decay = update_lists[21]
    R2_unc_double_both_Y2_decay = update_lists[22]
    R2_user_lifetime = update_lists[23]
    R2_unc_user_lifetime = update_lists[24]
    Ym_list = update_lists[25]
    dYm_list = update_lists[26]
    Ml_list_Y2_single = update_lists[27]
    dMl_list_Y2_single = update_lists[28]
    Fs_list_Y2_single = update_lists[29]
    dFs_list_Y2_single = update_lists[30]
    Mt_list_Y2_single = update_lists[31]
    dMt_list_Y2_single = update_lists[32]
    kp_list_Y2_single = update_lists[33]
    dkp_list_Y2_single = update_lists[34]
    keff_list_Y2_single = update_lists[35]
    dkeff_list_Y2_single = update_lists[36]
    Ml_double1_list = update_lists[37]
    dMl_double1_list = update_lists[38]
    Fs_double1_list = update_lists[39]
    dFs_double1_list = update_lists[40]
    Mt_double1_list = update_lists[41]
    dMt_double1_list = update_lists[42]
    kp_double1_list = update_lists[43]
    dkp_double1_list = update_lists[44]
    keff_double1_list = update_lists[45]
    dkeff_double1_list = update_lists[46]
    Ml_double2_list = update_lists[47]
    dMl_double2_list = update_lists[48]
    Fs_double2_list = update_lists[49]
    dFs_double2_list = update_lists[50]
    Mt_double2_list = update_lists[51]
    dMt_double2_list = update_lists[52]
    kp_double2_list = update_lists[53]
    dkp_double2_list = update_lists[54]
    keff_double2_list = update_lists[55]
    dkeff_double2_list = update_lists[56]
    Ml_double_both_list = update_lists[57]
    dMl_double_both_list = update_lists[58]
    Fs_double_both_list = update_lists[59]
    dFs_double_both_list = update_lists[60]
    Mt_double_both_list = update_lists[61]
    dMt_double_both_list = update_lists[62]
    kp_double_both_list = update_lists[63]
    dkp_double_both_list = update_lists[64]
    keff_double_both_list = update_lists[65]
    dkeff_double_both_list = update_lists[66]
    Ml_user_lifetime_list = update_lists[67]
    dMl_user_lifetime_list = update_lists[68]
    Fs_user_lifetime_list = update_lists[69]
    dFs_user_lifetime_list = update_lists[70]
    Mt_user_lifetime_list = update_lists[71]
    dMt_user_lifetime_list = update_lists[72]
    kp_user_lifetime_list = update_lists[73]
    dkp_user_lifetime_list = update_lists[74]
    keff_user_lifetime_list = update_lists[75]
    dkeff_user_lifetime_list = update_lists[76]
    calc_eff_kn_list = update_lists[77]
    calc_eff_unc_kn_list = update_lists[78]
    
    return gatewidth_list, first_reduced_factorial_moment_list, second_reduced_factorial_moment_list, third_reduced_factorial_moment_list, fourth_reduced_factorial_moment_list, first_factorial_moment_list, second_factorial_moment_list, third_factorial_moment_list, fourth_factorial_moment_list, Y1_list, dY1_list, Y2_list, dY2_list, R1_list, dR1_list, R2_single_Y2_decay, R2_unc_single_Y2_decay, R2_double1_Y2_decay, R2_unc_double1_Y2_decay, R2_double2_Y2_decay, R2_unc_double2_Y2_decay, R2_double_both_Y2_decay, R2_unc_double_both_Y2_decay, R2_user_lifetime, R2_unc_user_lifetime, Ym_list, dYm_list, Ml_list_Y2_single, dMl_list_Y2_single, Fs_list_Y2_single, dFs_list_Y2_single, Mt_list_Y2_single, dMt_list_Y2_single, kp_list_Y2_single, dkp_list_Y2_single, keff_list_Y2_single, dkeff_list_Y2_single, Ml_double1_list, dMl_double1_list, Fs_double1_list, dFs_double1_list, Mt_double1_list, dMt_double1_list, kp_double1_list, dkp_double1_list, keff_double1_list, dkeff_double1_list, Ml_double2_list, dMl_double2_list, Fs_double2_list, dFs_double2_list, Mt_double2_list, dMt_double2_list, kp_double2_list, dkp_double2_list, keff_double2_list, dkeff_double2_list, Ml_double_both_list, dMl_double_both_list, Fs_double_both_list, dFs_double_both_list, Mt_double_both_list, dMt_double_both_list, kp_double_both_list, dkp_double_both_list, keff_double_both_list, dkeff_double_both_list, Ml_user_lifetime_list, dMl_user_lifetime_list, Fs_user_lifetime_list, dFs_user_lifetime_list, Mt_user_lifetime_list, dMt_user_lifetime_list, kp_user_lifetime_list, dkp_user_lifetime_list, keff_user_lifetime_list, dkeff_user_lifetime_list, calc_eff_kn_list, calc_eff_unc_kn_list
    
    