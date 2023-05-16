import os  # For scanning directories
import numpy as np
from timeDifs import timeDifCalcs
from plots import Plot
import fitting
import matplotlib.pyplot as plt  # For plotting data summaries

# --------------------------------------------------------------------------------


def compile_sample_stdev_RA_dist(settings):
    data_folder = settings.io_file_info["input folder"]
    num_folders = 10
    i = 0
    for fol_num in range(1, num_folders + 1):
        for filename in os.listdir(data_folder + "/" + str(fol_num)):
            if filename.endswith("n_allch.txt"):
                path_to_data = data_folder + "/" + str(fol_num) + "/" + filename
                list_data_n = np.loadtxt(path_to_data, delimiter=" ")
                # list_data_n = np.genfromtxt(path_to_data, delimiter=' ')
                list_data = list_data_n[:, 1]
                if settings.general_program_settings["sort data?"] == "yes":
                    list_data = np.sort(list_data)
                from timeDifs import timeDifCalcs

                thisData = timeDifCalcs(list_data, settings.general_program_settings,settings.generating_histogram_settings)
                

                if i == 0:
                    time_diffs = thisData.calculate_time_differences()
                    # [RA_hist, popt, pcov, x_fit, y_fit] = make_RA_hist_and_fit(time_diffs, general_settings)
                    # RA_hist_array = RA_hist[0]
                    # popt_array = popt

                    thisPlot = Plot(
                        settings.generating_histogram_settings,
                        settings.histogram_visual_settings,
                        False,
                    )
                    counts, bin_centers, bin_edges = thisPlot.plot(time_diffs)
                    RA_hist_array = counts
                    #popt = fitting.fit_and_residual(counts,bin_centers,settings.general_program_settings["minimum cutoff"],settings.general_program_settings["fit range"],"Time Differences (ns)","Coincidence rate (s^-1)","Any-and-all",settings.line_fitting_settings,settings.residual_plot_settings,False,)
                    from fitting import Fit
                    thisFit = Fit(counts,bin_centers,settings.generating_histogram_settings,settings.line_fitting_settings, settings.general_program_settings,settings.residual_plot_settings,False)
                    popt = thisFit.fit_and_residual
                    popt_array = popt

                else:
                    time_diffs = thisData.calculate_time_differences()
                    # [RA_hist, popt, pcov, x_fit, y_fit] = make_RA_hist_and_fit(time_diffs, Rossi_alpha_settings)
                    # RA_hist_array = np.vstack((RA_hist_array, RA_hist[0]))
                    # popt_array = np.vstack((popt_array, popt))

                    thisPlot = Plot(
                        settings.generating_histogram_settings,
                        settings.histogram_visual_settings,
                        False,
                    )
                    counts, bin_centers, bin_edges = thisPlot.plot(time_diffs)

                    thisFit = Fit(counts,bin_centers,settings.generating_histogram_settings,settings.line_fitting_settings, settings.general_program_settings,settings.residual_plot_settings,False)
                    popt = thisFit.fit_and_residual
                    RA_hist_array = np.vstack((RA_hist_array, counts))
                    popt_array = np.vstack((popt_array, popt))

                i = i + 1
                break


    RA_std_dev = np.std(RA_hist_array, axis=0, ddof=1)
    RA_hist_total = np.sum(RA_hist_array, axis=0)

    time_diff_centers = bin_edges[1:] - np.diff(bin_edges[:2]) / 2
    RA_hist_total = np.vstack((RA_hist_total, time_diff_centers, RA_std_dev * num_folders))

    return RA_hist_total
