
import os  # For scanning directories
import numpy as np
from timeDifs import timeDifCalcs
from plots import Plot
import fitting
#--------------------------------------------------------------------------------

def compile_sample_stdev_RA_dist(data_folder, general_settings):
    
    num_folders = 10
    i = 0;   
    for fol_num in range(1, num_folders + 1):
        
        for filename in os.listdir(data_folder + '/' + str(fol_num)):              
            
            if filename.endswith('n_allch.txt'):
                
                path_to_data = data_folder + '/' + str(fol_num) + '/' + filename
                list_data_n = np.loadtxt(path_to_data)
                list_data_n = list_data_n[:,1]
                from timeDifs import timeDifCalcs
                thisData = timeDifCalcs(list_data_n, general_settings)
                # hist_settings = ________  TODO
                # line_settings = ________ TODO
                # residual settings = _________ TODO
                
                if i == 0:
                    time_diffs = thisData.calculate_time_differences()
                    [RA_hist, popt, pcov, x_fit, y_fit] = make_RA_hist_and_fit(time_diffs, general_settings)
                    RA_hist_array = RA_hist[0]
                    popt_array = popt

                    # thisPlot = Plot(theseSettings.general_program_settings, theseSettings.histogram_settings) TODO
                    # counts, bin_centers = thisPlot.plot(time_diffs)

                    # fitting.fit_and_residual(counts, bin_centers, theseSettings.general_program_settings['minimum cutoff'], "Time Differences (ns)", 
                             # "Coincidence rate (s^-1)", "Any-and-all", theseSettings.line_fitting_settings, theseSettings.residual_plot_settings)

                else:
                    time_diffs = thisData.calculate_time_differences()
                    [RA_hist, popt, pcov, x_fit, y_fit] = make_RA_hist_and_fit(time_diffs, Rossi_alpha_settings)
                    RA_hist_array = np.vstack((RA_hist_array, RA_hist[0]))
                    popt_array = np.vstack((popt_array, popt))

                    # thisPlot = Plot(theseSettings.general_program_settings, theseSettings.histogram_settings) TODO
                    # counts, bin_centers = thisPlot.plot(time_diffs)

                    # fitting.fit_and_residual(counts, bin_centers, theseSettings.general_program_settings['minimum cutoff'], "Time Differences (ns)", 
                             # "Coincidence rate (s^-1)", "Any-and-all", theseSettings.line_fitting_settings, theseSettings.residual_plot_settings)
                    
                i = i + 1
                
    RA_std_dev = np.std(RA_hist_array, axis=0, ddof=1)            
    RA_hist_total = np.sum(RA_hist_array, axis=0)
    time_diff_centers = RA_hist[1][1:] - np.diff(RA_hist[1][:2])/2
    RA_hist_total = np.vstack((RA_hist_total, time_diff_centers, RA_std_dev*num_folders))
    
    return RA_hist_total