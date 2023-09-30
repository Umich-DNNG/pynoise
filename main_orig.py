# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 17:13:04 2023

@author: 357375

Main processing script for MUSIC data solely in Python.
"""

import sys

# # Define location of Git synchoronized Python functions
# python_scripts_path = (r'/Users/fdarby/Documents/Git' + 
#                        '/flynn-darby-mixed-pulse-processing' + 
#                        '/python/pythonScripts')

# # Add python functions folder to path
# sys.path.extend([python_scripts_path])

# from Data_structure import DataLoader # For building data file load structure

import numpy as np                    # For processing data
import os                             # For scanning directories
import matplotlib.pyplot as plt       # For plotting data summaries
from matplotlib.colors import LogNorm # For adjusting colorbar scale
# from scipy.signal import find_peaks
from scipy.optimize import curve_fit
import copy
import seaborn as sns
sns.set(rc={"figure.dpi": 350, 'savefig.dpi': 350})
sns.set_style("ticks")
sns.set_context("talk", font_scale=0.8)

def plot_PSD(list_data):
    
    cmap = plt.cm.get_cmap('Greys')
    reversed_cmap = cmap
    
    fig, ax = plt.subplots(dpi=400)
    
    energy = (list_data[:,1]*478/1.6)
    x = [0, 2000]
    y =[0, 0.6]
    nbins = 1000
    xlabstr = 'Light yield (keVee)'
        
    psd = list_data[:,2]/list_data[:,1]
        
    plt.hist2d(energy, psd, bins=nbins, 
               range=[x,
                      y], 
               norm=LogNorm(),
               cmap=reversed_cmap)
    
    # create a 2D histogram
    h, xedges, yedges = np.histogram2d(energy, psd, bins=nbins, 
                                       range=[x,y])
    
    # get the maximum value of the histogram
    dim_3_max = np.amax(h)
                
    plt.xlabel(xlabstr)
    plt.ylabel('Tail over Total')
    
    
    cbar = plt.colorbar()
    cbar.ax.set_title(r'Counts')
    plt.show()
    
    return dim_3_max


def plot_n_g_colors_PSD(list_data_n,list_data_g,dim_3_max):
    
    ToTs_n = list_data_n[:,2]/list_data_n[:,1]
    ToTs_g = list_data_g[:,2]/list_data_g[:,1]
    
    LOs_calib_n = list_data_n[:,1]*478*1.6
    LOs_calib_g = list_data_g[:,1]*478*1.6
    
    xbins = np.linspace(0,1600,801)
    ybins = np.linspace(0,0.6,1001)
    
    my_cmap = copy.copy(plt.cm.get_cmap('Blues'))
    # my_cmap.set_bad(color='black')
    my_cmap_2 = copy.copy(plt.cm.get_cmap('Reds'))
    # my_cmap_2.set_bad(color='black')
    fig, ax = plt.subplots(dpi= 400)
    hist_n = plt.hist2d(LOs_calib_n, ToTs_n, bins=(xbins,ybins), 
                        range=[[0, 1600],[0.0, 0.6]], 
                        norm=LogNorm(vmax=dim_3_max), 
                        cmap =my_cmap, label='n')
    hist_g = plt.hist2d(LOs_calib_g, ToTs_g, bins=(xbins,ybins), 
                        range=[[0, 1600],[0.0, 0.6]], 
                        norm=LogNorm(vmax=dim_3_max), 
                        cmap =my_cmap_2, label=r'$\gamma$')
    plt.xlabel('Light yield (keVee)')
    plt.ylabel('Tail over Total')
    cbar_n = plt.colorbar(hist_n[3])
    cbar_g = plt.colorbar(hist_g[3])
    cbar_n.ax.set_title(r'n')
    cbar_g.ax.set_title(r'$\gamma$')
    # plt.legend()
    # plt.title(labels[i])
    plt.show()
    
    return

def plot_n_g_colors_PSD_discrim(list_data,ToT):
    
    ToTs = list_data[:,2]/list_data[:,1]
    
    ind_n = ToTs > ToT
    ind_g = ToTs <= ToT
    
    list_data_n = list_data[ind_n]
    list_data_g = list_data[ind_g]
    
    ToTs_n = list_data_n[:,2]/list_data_n[:,1]
    ToTs_g = list_data_g[:,2]/list_data_g[:,1]
    
    LOs_calib_n = list_data_n[:,1]*478*1.6
    LOs_calib_g = list_data_g[:,1]*478*1.6
    
    my_cmap = copy.copy(plt.cm.get_cmap('Blues'))
    my_cmap.set_bad(color='white')
    my_cmap_2 = copy.copy(plt.cm.get_cmap('Reds'))
    # my_cmap_2.set_bad(color='black')
    fig, ax = plt.subplots(dpi= 400)
    hist_n = plt.hist2d(LOs_calib_n, ToTs_n, bins=200, 
                        range=[[0, 2000],[0.0, 0.6]], norm=LogNorm(), 
                        cmap =my_cmap, label='n')
    hist_g = plt.hist2d(LOs_calib_g, ToTs_g, bins=200, 
                        range=[[0, 2000],[0.0, 0.6]], norm=LogNorm(), 
                        cmap =my_cmap_2, label=r'$\gamma$')
    plt.xlabel('Light yield (keVee)')
    plt.ylabel('Tail over Total')
    cbar_n = plt.colorbar(hist_n[3])
    cbar_g = plt.colorbar(hist_g[3])
    cbar_n.ax.set_title(r'n')
    cbar_g.ax.set_title(r'$\gamma$')
    # plt.legend()
    # plt.title(labels[i])
    plt.show()
    
    return

def sortrows(array,column):
    
    column_to_sort_by = column
    indices = np.argsort(array[:, column_to_sort_by])
    sorted_array = np.take(array, indices, axis=0)
    
    return sorted_array

def calculate_time_differences(list_data, Rossi_alpha_settings):
    
    time_vector = list_data[:,1]
    
    reset_time = Rossi_alpha_settings['reset time']
    
    if Rossi_alpha_settings['time difference method'] == 'any-and-all':
        time_diffs = any_and_all_time_differences(time_vector,reset_time)
    elif (Rossi_alpha_settings['time difference method'] == 
          'any-and-all cross-correlations'):
        channels = list_data[:,0]
        time_diffs = any_and_all_cross_correlation_time_differences(
                        time_vector,channels,reset_time
                        )
    elif (Rossi_alpha_settings['time difference method'] == 
          'any-and-all cross-correlations no-repeat'):
        channels = list_data[:,0]
        time_diffs = any_and_all_cross_correlation_no_repeat_time_differences(
                        time_vector,channels,reset_time
                        )
    elif (Rossi_alpha_settings['time difference method'] == 
          'any-and-all cross-correlations no-repeat digital-delay'):
        channels = list_data[:,0]
        time_diffs = \
            any_and_all_cross_correlation_no_repeat_digital_delay_time_differences(
                        time_vector,channels,reset_time
                        )
    else:
        print()
        print(Rossi_alpha_settings['time difference method'])
        print('This time difference method requested is either mistyped or')
        print('has not been programmed. The current available options are:')
        print()
        print('any-and-all')
        print('any-and-all cross-correlations')
        print('any-and-all cross-correlations no-repeat')
        print('any-and-all cross-correlations no-repeat digital-delay')
        print()
    
    return time_diffs

def any_and_all_time_differences(time_vector,reset_time):
    
    time_diffs = []
    for i in range(len(time_vector)):
        for j in range(i+1, len(time_vector)):
            if time_vector[j] - time_vector[i] > reset_time:
                break
            time_diffs.append(time_vector[j] - time_vector[i])
            
    return time_diffs

def any_and_all_cross_correlation_time_differences(
        time_vector,channels,reset_time
        ):
    
    time_diffs = []
    for i in range(len(time_vector)):
        for j in range(i+1, len(time_vector)):
            if channels[j] - channels[i] != 0:
                if time_vector[j] - time_vector[i] > reset_time:
                    break
                time_diffs.append(time_vector[j] - time_vector[i])
            
    return time_diffs

def any_and_all_cross_correlation_no_repeat_time_differences(
        time_vector,channels,reset_time
        ):
    
    time_diffs = []
    for i in range(len(time_vector)):
        ch_bank = []
        for j in range(i+1, len(time_vector)):
            if channels[j] - channels[i] != 0:
                if time_vector[j] - time_vector[i] > reset_time:
                    break
                elif sum(ch_bank - channels[j] == 0) == 0:
                    time_diffs.append(time_vector[j] - time_vector[i])
                ch_bank.append(channels[j])
            
    return time_diffs

def any_and_all_cross_correlation_no_repeat_digital_delay_time_differences(
        time_vector,channels,reset_time
        ):
    
    digital_delay = Rossi_alpha_settings['digital delay']
    
    time_diffs = []
    i = 0
    while i < len(time_vector):
        ch_bank = []
        for j in range(i+1, len(time_vector)):
            if channels[j] - channels[i] != 0:
                if time_vector[j] - time_vector[i] > reset_time:
                    break
                elif sum(ch_bank - channels[j] == 0) == 0:
                    time_diffs.append(time_vector[j] - time_vector[i])
                else:
                    stamped_time = time_vector[i]
                    while time_vector[i] < stamped_time + digital_delay:
                        i = i + 1
                ch_bank.append(channels[j])
        i = i + 1
            
    return time_diffs

# Define the function to fit
def exp_decay_3_param(x, a, b, c):
    return a * np.exp(b * x) + c

# Define the function to fit
def exp_decay_2_param(x, a, b):
    return a * np.exp(b * x)

def fit_RA_hist(RA_hist,Rossi_alpha_settings):
    
    num_bins = np.size(RA_hist[0])
    time_diff_centers = RA_hist[1][1:] - np.diff(RA_hist[1][:2])/2
    
    # Choose region to fit
    fit_index = (
        (time_diff_centers > Rossi_alpha_settings['minimum cutoff']) & 
        (time_diff_centers >= Rossi_alpha_settings['fit range'][0]) & 
        (time_diff_centers <= Rossi_alpha_settings['fit range'][1])
        )
    xfit = time_diff_centers[fit_index]
    
    # Fit distribution
    # Fit the data using curve_fit
    # exp_decay_fit_bounds = ([0,-np.inf,0],[np.inf,0,np.inf])
    exp_decay_fit_bounds = ([0,-np.inf],[np.inf,0])
    a0 = np.max(RA_hist[0])
    c0 = np.mean(RA_hist[0][-int(num_bins*0.05):])
    b0 = (
        (np.log(c0)-np.log(RA_hist[0][0]))/
          (time_diff_centers[-1]-time_diff_centers[0])
          )
    yfit = RA_hist[0][fit_index] - c0
    # exp_decay_p0 = [a0, b0, c0]
    exp_decay_p0 = [a0, b0]
    popt, pcov = curve_fit(
        exp_decay_2_param, 
        xfit, 
        yfit,
        bounds=exp_decay_fit_bounds,
        p0=exp_decay_p0,
        maxfev=1e6)
    
    yfit = exp_decay_3_param(xfit, *popt, c0)
    
    popt = np.hstack((popt, c0))
    
    return [time_diff_centers, popt, pcov, xfit, yfit]

def fit_RA_hist_weighting(RA_hist,Rossi_alpha_settings):
    
    num_bins = np.size(RA_hist[0])
    time_diff_centers = RA_hist[1]
    
    # Calculate weighting with relative variance
    uncertainties = RA_hist[2]
    
    # Choose region to fit
    fit_index = (
        (time_diff_centers > Rossi_alpha_settings['minimum cutoff']) & 
        (time_diff_centers >= Rossi_alpha_settings['fit range'][0]) & 
        (time_diff_centers <= Rossi_alpha_settings['fit range'][1])
                 )
    xfit = time_diff_centers[fit_index]
    
    # Fit distribution
    # Fit the data using curve_fit
    # exp_decay_fit_bounds = ([0,-np.inf,0],[np.inf,0,np.inf])
    exp_decay_fit_bounds = ([0,-np.inf],[np.inf,0])
    a0 = np.max(RA_hist[0])
    c0 = np.mean(RA_hist[0][-int(num_bins*0.05):])
    b0 = (
        (np.log(c0)-np.log(RA_hist[0][0]))/
          (time_diff_centers[-1]-time_diff_centers[0])
          )
    yfit = RA_hist[0][fit_index] - c0
    # exp_decay_p0 = [a0, b0, c0]
    exp_decay_p0 = [a0, b0]
    popt, pcov = curve_fit(
        exp_decay_2_param, 
        xfit, 
        yfit,
        bounds=exp_decay_fit_bounds,
        p0=exp_decay_p0,
        maxfev=1e6,
        sigma=uncertainties[fit_index], 
        absolute_sigma=True
        )
    
    yfit = exp_decay_3_param(xfit, *popt, c0)
    
    popt = np.hstack((popt, c0))
    
    cerr = np.std(RA_hist[0][-int(num_bins*0.05):], axis=0, ddof=1)
    
    perr = np.sqrt(np.diag(pcov)) 
    
    perr = np.hstack((perr, cerr))
    
    return [time_diff_centers, popt, pcov, perr, xfit, yfit]

def make_RA_hist_and_fit(time_diffs, Rossi_alpha_settings):
    
    bin_width = Rossi_alpha_settings['bin width']
    reset_time = Rossi_alpha_settings['reset time']
    
    num_bins = int(reset_time/bin_width)
    
    RA_hist = np.histogram(time_diffs,bins=num_bins,range=[0,reset_time])
    
    [time_diff_centers, popt, pcov, xfit, yfit] = \
        fit_RA_hist(RA_hist,Rossi_alpha_settings)
    
    return [RA_hist, popt, pcov, xfit, yfit]

def plot_RA_and_fit(RA_hist, xfit, yfit, Rossi_alpha_settings):
    
    time_diff_centers = RA_hist[1][1:] - np.diff(RA_hist[1][:2])/2
    
    fig2, ax2 = plt.subplots()
    
    # Create a scatter plot with the data
    ax2.scatter(time_diff_centers, RA_hist[0])
    
    # Add the fit to the data
    ax2.plot(xfit, yfit, 'r-', label='Fit')
    
    # Set the axis labels
    ax2.set_xlabel('Time difference (ns)')
    ax2.set_ylabel('Counts')
    ax2.set_yscale(Rossi_alpha_settings['plot scale'])
    
    # Display the plot
    plt.show()
    
    return

def plot_RA_and_fit_errorbar(RA_hist, xfit, yfit, Rossi_alpha_settings):
    
    time_diff_centers = RA_hist[1]
    
    meas_time = Rossi_alpha_settings['meas time']
    
    fig1, ax1 = plt.subplots()
    
    # Create a errorbar plot with the data
    ax1.errorbar(
        time_diff_centers, RA_hist[0]/meas_time, yerr=RA_hist[2]/meas_time, 
        fmt='o', markersize=5, capsize=3
        )
    
    # Add the fit to the data
    ax1.plot(xfit, yfit/meas_time, 
             'r--', label='Fit')
    
    # Set the axis labels
    ax1.set_xlabel('Time difference (ns)')
    ax1.set_ylabel('Count rate (s$^{-1}$)')
    ax1.set_yscale(Rossi_alpha_settings['plot scale'])
    
    # Display the plot
    plt.show()
    
    fig2, ax2 = plt.subplots()
    
    # Create a residuals plot with the data and fit
    index = (time_diff_centers >= xfit[0]) & (time_diff_centers <= xfit[-1])
    residuals = RA_hist[0][index]-yfit
    ax2.errorbar(
        time_diff_centers[index], 
        residuals/meas_time, yerr=RA_hist[2][index]/meas_time, 
        fmt='o', markersize=5, capsize=3
        )
    ax2.axhline(y=0, linestyle='--', color='gray')
    
    # Set the axis labels
    ax2.set_xlabel('Time difference (ns)')
    ax2.set_ylabel('Residual count rate (s$^{-1}$)')
    ax2.set_yscale('linear')
    
    # Display the plot
    plt.show()
    
    return

def plot_RA_and_fits_errorbar(
        RA_hist, xfit1, xfit2, xfit3, 
        popt_array, perr_array, Rossi_alpha_settings
        ):
    
    time_diff_centers = RA_hist[1]
    
    meas_time = Rossi_alpha_settings['meas time']
    
    # Plot distribution fits
    fig1, ax1 = plt.subplots()
    
    # Create a errorbar plot with the data
    ax1.errorbar(
        time_diff_centers, RA_hist[0]/meas_time, yerr=RA_hist[2]/meas_time, 
        fmt='.', markersize=10, capsize=2, color='k', 
        markerfacecolor=(0, 0, 0, 0),
        markeredgecolor='k',
        label='Time-difference histogram data'
        )
    
    # Create a scatter plot with the data
    # ax1.scatter(
    #     time_diff_centers, RA_hist[0]/meas_time, 
    #     marker='.',
    #     s=10, 
    #     # capsize=3, 
    #     color='k', 
    #     label='Time-difference histogram data'
    #     )
    
    # pp = -popt_array[:,1]**(-1)
    # pp_err = -pp*perr_array[:,1]/popt_array[:,1]
    
    ylim = plt.gca().get_ylim()
    # xlim = plt.gca().get_xlim()
    
    # Add the fits to the data
    yfit = exp_decay_3_param(xfit1, *popt_array[0])
    ax1.plot(xfit1, yfit/meas_time, 
             'k--', 
             label=('Full fit'),
             # label=(
             #     r'-$\alpha^{-1}$' + ' = {:.2f} +/- {:.2f} ns, '.format(pp[0],
             #                                                      pp_err[0]
             #                                                      ) + 
             #        'Full fit')
             # alpha=0.8
             )
    yfit = exp_decay_3_param(xfit2, *popt_array[1])
    yshade = ylim[1]*np.ones(np.size(yfit))
    ax1.stackplot(xfit2,yshade,alpha=0.2,color='b',labels=['Early region'])
    ax1.plot(xfit2, yfit/meas_time, 
             'b-.', 
             label=('Early region fit'),
             # label=(
             #     r'-$\alpha^{-1}$' + ' = {:.2f} +/- {:.2f} ns, '.format(pp[1],
             #                                                      pp_err[1]
             #                                                      ) + 
             #        'Early region fit'),
             # alpha=0.7
             )
    yfit = exp_decay_3_param(xfit3, *popt_array[1])
    yshade = ylim[1]*np.ones(np.size(yfit))
    ax1.stackplot(xfit3,yshade,alpha=0.2,color='r',
                  labels=['Late region'], linestyle='-.')
    ax1.plot(xfit3, yfit/meas_time, 
             'r-.', 
             label=('Late region fit'),
            # label=(
            #     r'-$\alpha^{-1}$' + ' = {:.2f} +/- {:.2f} ns, '.format(pp[2],
            #                                                      pp_err[2]
            #                                                      ) + 
            #        'Late region fit'),
             # alpha=0.7
             )
    
    # Set the axis labels
    ax1.set_xlabel('Time difference (ns)')
    ax1.set_ylabel('Coincidence rate (s$^{-1}$)')
    ax1.set_yscale(Rossi_alpha_settings['plot scale'])
    
    # plt.xlim([300,600])
    
    # Add equation to plot
    # plt.text(xlim[1]*0.6, ylim[1]*0.35, 
    #          r'$p(\Delta t)=A*e^{\alpha \Delta t} + C$', 
    #          fontsize=16, color='k', ha='center', va='center')
    
    plt.legend(loc='best',framealpha=1)
    plt.show()
    
    return

def compile_sample_stdev_RA_dist(data_folder, Rossi_alpha_settings):
    
    num_folders = Rossi_alpha_settings['number of folders']
    
    # Combine all channel data in each sub folder

    # Neutron data

    i = 0;   
    for fol_num in range(1, num_folders + 1):
        
        for filename in os.listdir(data_folder + '/' + str(fol_num)):              
            
            if filename.endswith('n_allch.txt'):
                
                path_to_data = data_folder + '/' + str(fol_num) + '/' + filename
                list_data_n = np.loadtxt(path_to_data)
                
                if i == 0:
                    time_diffs = \
                        calculate_time_differences(
                            list_data_n, 
                            Rossi_alpha_settings
                            )
                    [RA_hist, popt, pcov, x_fit, y_fit] = \
                        make_RA_hist_and_fit(
                            time_diffs, 
                            Rossi_alpha_settings
                            )
                    RA_hist_array = RA_hist[0]
                    popt_array = popt
                else:
                    time_diffs = \
                        calculate_time_differences(
                            list_data_n, 
                            Rossi_alpha_settings
                            )
                    [RA_hist, popt, pcov, x_fit, y_fit] = \
                        make_RA_hist_and_fit(
                            time_diffs, 
                            Rossi_alpha_settings
                            )
                    RA_hist_array = np.vstack((RA_hist_array, RA_hist[0]))
                    popt_array = np.vstack((popt_array, popt))
                    
                i = i + 1
                
    RA_std_dev = np.std(RA_hist_array, axis=0, ddof=1)            
    RA_hist_total = np.sum(RA_hist_array, axis=0)
    time_diff_centers = RA_hist[1][1:] - np.diff(RA_hist[1][:2])/2
    RA_hist_total = np.vstack((RA_hist_total, time_diff_centers, RA_std_dev*num_folders))
    
    return RA_hist_total

# Choose Data Directory
# Off external hard drive
# data_folder = ('D:/Research_Assistant/2021_DAF_MUSiC/Data/OSCAR' + 
#                '/20210322_Wk4/20210322_06_RF3-42_CF_OS_run1_60min_0947')
# data_folder = (r'/Users/fdarby/Dropbox (University of Michigan)' + 
#                 r'/ENGIN-Well-counter/MUSIC/Data/OSCAR/20210322_Wk4' + 
#                 r'/20210322_06_RF3-42_CF_OS_run1_60min_0947')
# data_folder = (r'/Users/fdarby/Dropbox (University of Michigan)' + 
#                r'/ENGIN-Well-counter/MUSIC/Data/OSCAR/20210322_Wk4' + 
#                r'/20210322_06_RF3-42_CF_OS_run2_25min_1055')
# data_folder = (r'/Users/fdarby/Dropbox (University of Michigan)' + 
#                 r'/ENGIN-Well-counter/MUSIC/Data/OSCAR/20210322_Wk4' + 
#                 r'/20210322_07_RF3-44_CF_OS_58min')
data_folder = (r'/Users/fdarby/Dropbox (University of Michigan)' + 
                r'/ENGIN-Well-counter/MUSIC/Data/OSCAR/20210329_Wk5' + 
                r'/20210329_10_RF9-46_CF_OS_61min_1minfiles')

# Rossi-alpha settings
Rossi_alpha_settings = dict([('reset time', 2e3), ('bin width', 2),
                             ('minimum cutoff', 25), ('fit range', [0, 2e3]),
                             ('plot scale', 'linear'), 
                             ('time difference method', 
                              'any-and-all'), ('digital delay', 750),
                             ('number of folders', 61),
                             ('meas time per folder', 60)])

num_folders = Rossi_alpha_settings['number of folders']
meas_time_per_folder = Rossi_alpha_settings['meas time per folder']
Rossi_alpha_settings['meas time'] = num_folders*meas_time_per_folder

# Combine all channel data in each sub folder and plot PSD
list_data = []
i = 0
for fol_num in range(1,num_folders+1):
    for ch in range(0,12):
        if i > 0:
            list_data = np.vstack((list_data, \
                np.loadtxt((data_folder + '/' + str(fol_num) +
                                         '/board0ch' + str(ch) + '.txt'))))
        else:
            list_data = np.loadtxt((data_folder + '/' + str(fol_num) +
                                     '/board0ch' + str(ch) + '.txt'))
        i += 1

plot_PSD(list_data)

# Combine all channel data in each sub folder and plot PSD
list_data = []
i = 0
for fol_num in range(1,num_folders+1):
    for ch in range(0,12):
        if i > 0:
            list_data = np.vstack((list_data, \
                np.loadtxt((data_folder + '/' + str(fol_num) +
                                         '/board0ch' + str(ch) + '.txt'))))
        else:
            list_data = np.loadtxt((data_folder + '/' + str(fol_num) +
                                     '/board0ch' + str(ch) + '.txt'))
        i += 1

plot_PSD(list_data)

# Combine all channel data in each sub folder and plot PSD
list_data_n = []
list_data_g = []
i = 0
for fol_num in range(1,num_folders+1):
    for ch in range(0,12):
        if i > 0:
            list_data_n = np.vstack((list_data_n, \
                np.loadtxt((data_folder + '/' + str(fol_num) +
                                         '/board0ch' + str(ch) + '_n.txt'))))
            list_data_g = np.vstack((list_data_g, \
                np.loadtxt((data_folder + '/' + str(fol_num) +
                                         '/board0ch' + str(ch) + '_g.txt'))))
        else:
            list_data_n = np.loadtxt((data_folder + '/' + str(fol_num) +
                                     '/board0ch' + str(ch) + '_n.txt'))
            list_data_g = np.loadtxt((data_folder + '/' + str(fol_num) +
                                     '/board0ch' + str(ch) + '_g.txt'))
        i += 1

plot_n_g_colors_PSD(list_data_n,list_data_g)

# Neutron data
# for fol_num in range(1, num_folders + 1):
    
#     i = 0;   
    
#     for filename in os.listdir(data_folder + '/' + str(fol_num)):              
        
#         if filename.endswith('_n.txt'):
            
#             path_to_data = data_folder + '/' + str(fol_num) + '/' + filename
            
#             if i == 0:
#                 list_add = np.loadtxt(path_to_data)
#                 ch = int((filename.replace('board0ch','')).replace('_n.txt',''))
#                 list_data_n = np.hstack((ch*np.ones([np.size(list_add,0),1]), list_add))
#             else:
#                 list_add = np.loadtxt(path_to_data)
#                 ch = int((filename.replace('board0ch','')).replace('_n.txt',''))
#                 list_add = np.hstack((ch*np.ones([np.size(list_add,0),1]), list_add))
#                 list_data_n = np.vstack((list_data_n, list_add))
                
#             i = i + 1
        
#     list_data_n = sortrows(list_data_n,1)
    
#     np.savetxt((data_folder + '/' + str(fol_num) + '/' + 'board0_n_allch.txt'),
#                 list_data_n, fmt=['%.0f', '%.2f', '%.4f', '%.4f'])
    
# Combine all channel data from each sub folder

# Neutron data
    
# i = 0;   
# for fol_num in range(1, num_folders + 1):
    
#     for filename in os.listdir(data_folder + '/' + str(fol_num)):              
        
#         if filename.endswith('n_allch.txt'):
            
#             path_to_data = data_folder + '/' + str(fol_num) + '/' + filename
            
#             if i == 0:
#                 list_data_n = np.loadtxt(path_to_data)
#             else:
#                 list_add = np.loadtxt(path_to_data)
#                 list_data_n = np.vstack((list_data_n, list_add))
                
#             i = i + 1
        
# list_data_n = sortrows(list_data_n,1)

# np.savetxt((data_folder + '/' + 'board0_n_allch.txt'),
#             list_data_n, fmt=['%.0f', '%.2f', '%.4f', '%.4f'])

# Compile RA histograms and get fits

# alpha_array = [];
# alpha_unc_array = [];

# # Any-and-all
# Rossi_alpha_settings['time difference method'] = \
#     'any-and-all'
# RA_hist_total = compile_sample_stdev_RA_dist(data_folder, Rossi_alpha_settings)


# alpha_vector = []
# alpha_unc_vector = []

# Rossi_alpha_settings['fit range'] = [0, 2e3]
# [time_diff_centers, popt, pcov, perr, xfit1, yfit] = \
#     fit_RA_hist_weighting(RA_hist_total,Rossi_alpha_settings)
# popt_array = popt
# perr_array = perr
# alpha_vector.append(popt[1])
# alpha_unc_vector.append(perr[1])

# Rossi_alpha_settings['fit range'] = [0, 400]
# [time_diff_centers, popt, pcov, perr, xfit2, yfit] = \
#     fit_RA_hist_weighting(RA_hist_total,Rossi_alpha_settings)
# popt_array = np.vstack((popt_array, popt))
# perr_array = np.vstack((perr_array, perr))
# alpha_vector.append(popt[1])
# alpha_unc_vector.append(perr[1])

# Rossi_alpha_settings['fit range'] = [500, Rossi_alpha_settings['reset time']]
# [time_diff_centers, popt, pcov, perr, xfit3, yfit] = \
#     fit_RA_hist_weighting(RA_hist_total,Rossi_alpha_settings)
# popt_array = np.vstack((popt_array, popt))
# perr_array = np.vstack((perr_array, perr))
# alpha_vector.append(popt[1])
# alpha_unc_vector.append(perr[1])

# plot_RA_and_fits_errorbar(
#         RA_hist_total, xfit1, xfit2, xfit3, 
#         popt_array, perr_array, Rossi_alpha_settings
#         )

# alpha_array = alpha_vector
# alpha_unc_array = alpha_unc_vector

# print(popt_array)

# # Add basic cross-correlation
# Rossi_alpha_settings['time difference method'] = \
#     'any-and-all cross-correlations'
    
# RA_hist_total = \
#     compile_sample_stdev_RA_dist(data_folder, Rossi_alpha_settings)

# alpha_vector = []
# alpha_unc_vector = []

# Rossi_alpha_settings['fit range'] = [0, 2e3]
# [time_diff_centers, popt, pcov, perr, xfit1, yfit] = \
#     fit_RA_hist_weighting(RA_hist_total,Rossi_alpha_settings)
# popt_array = popt
# perr_array = perr
# alpha_vector.append(popt[1])
# alpha_unc_vector.append(perr[1])

# Rossi_alpha_settings['fit range'] = [0, 400]
# [time_diff_centers, popt, pcov, perr, xfit2, yfit] = \
#     fit_RA_hist_weighting(RA_hist_total,Rossi_alpha_settings)
# popt_array = np.vstack((popt_array, popt))
# perr_array = np.vstack((perr_array, perr))
# alpha_vector.append(popt[1])
# alpha_unc_vector.append(perr[1])

# Rossi_alpha_settings['fit range'] = [500, Rossi_alpha_settings['reset time']]
# [time_diff_centers, popt, pcov, perr, xfit3, yfit] = \
#     fit_RA_hist_weighting(RA_hist_total,Rossi_alpha_settings)
# popt_array = np.vstack((popt_array, popt))
# perr_array = np.vstack((perr_array, perr))
# alpha_vector.append(popt[1])
# alpha_unc_vector.append(perr[1])

# plot_RA_and_fits_errorbar(
#         RA_hist_total, xfit1, xfit2, xfit3, 
#         popt_array, perr_array, Rossi_alpha_settings
#         )

# alpha_array = np.vstack((alpha_array,alpha_vector))
# alpha_unc_array = np.vstack((alpha_unc_array,alpha_unc_vector))

# print(popt_array)
    
# # Add multi-level cross-correlation
# Rossi_alpha_settings['time difference method'] = \
#     'any-and-all cross-correlations no-repeat'
    
# RA_hist_total = compile_sample_stdev_RA_dist(data_folder, Rossi_alpha_settings)

# alpha_vector = []
# alpha_unc_vector = []

# Rossi_alpha_settings['fit range'] = [0, 2e3]
# [time_diff_centers, popt, pcov, perr, xfit1, yfit] = \
#     fit_RA_hist_weighting(RA_hist_total,Rossi_alpha_settings)
# popt_array = popt
# perr_array = perr
# alpha_vector.append(popt[1])
# alpha_unc_vector.append(perr[1])

# Rossi_alpha_settings['fit range'] = [0, 400]
# [time_diff_centers, popt, pcov, perr, xfit2, yfit] = \
#     fit_RA_hist_weighting(RA_hist_total,Rossi_alpha_settings)
# popt_array = np.vstack((popt_array, popt))
# perr_array = np.vstack((perr_array, perr))
# alpha_vector.append(popt[1])
# alpha_unc_vector.append(perr[1])

# Rossi_alpha_settings['fit range'] = [500, Rossi_alpha_settings['reset time']]
# [time_diff_centers, popt, pcov, perr, xfit3, yfit] = \
#     fit_RA_hist_weighting(RA_hist_total,Rossi_alpha_settings)
# popt_array = np.vstack((popt_array, popt))
# perr_array = np.vstack((perr_array, perr))
# alpha_vector.append(popt[1])
# alpha_unc_vector.append(perr[1])

# plot_RA_and_fits_errorbar(
#         RA_hist_total, xfit1, xfit2, xfit3, 
#         popt_array, perr_array, Rossi_alpha_settings
#         )

# alpha_array = np.vstack((alpha_array,alpha_vector))
# alpha_unc_array = np.vstack((alpha_unc_array,alpha_unc_vector))

# print(popt_array)

# # Add multi-level cross-correlation with digital delay
# Rossi_alpha_settings['time difference method'] = \
#     'any-and-all cross-correlations no-repeat digital-delay'
    
# RA_hist_total = compile_sample_stdev_RA_dist(data_folder, Rossi_alpha_settings)

# alpha_vector = []
# alpha_unc_vector = []

# Rossi_alpha_settings['fit range'] = [0, 2e3]
# [time_diff_centers, popt, pcov, perr, xfit1, yfit] = \
#     fit_RA_hist_weighting(RA_hist_total,Rossi_alpha_settings)
# popt_array = popt
# perr_array = perr
# alpha_vector.append(popt[1])
# alpha_unc_vector.append(perr[1])

# Rossi_alpha_settings['fit range'] = [0, 400]
# [time_diff_centers, popt, pcov, perr, xfit2, yfit] = \
#     fit_RA_hist_weighting(RA_hist_total,Rossi_alpha_settings)
# popt_array = np.vstack((popt_array, popt))
# perr_array = np.vstack((perr_array, perr))
# alpha_vector.append(popt[1])
# alpha_unc_vector.append(perr[1])

# Rossi_alpha_settings['fit range'] = [500, Rossi_alpha_settings['reset time']]
# [time_diff_centers, popt, pcov, perr, xfit3, yfit] = \
#     fit_RA_hist_weighting(RA_hist_total,Rossi_alpha_settings)
# popt_array = np.vstack((popt_array, popt))
# perr_array = np.vstack((perr_array, perr))
# alpha_vector.append(popt[1])
# alpha_unc_vector.append(perr[1])

# plot_RA_and_fits_errorbar(
#         RA_hist_total, xfit1, xfit2, xfit3, 
#         popt_array, perr_array, Rossi_alpha_settings
#         )

# alpha_array = np.vstack((alpha_array,alpha_vector))
# alpha_unc_array = np.vstack((alpha_unc_array,alpha_unc_vector))

# print(popt_array)

# Work from already built histograms

alpha_array = [];
alpha_unc_array = [];

# Load RA histograms and get fits
# Any-and-all
RA_hist = np.loadtxt('RA_hist_total_aaa_config_10.txt')

alpha_vector = []
alpha_unc_vector = []

Rossi_alpha_settings['fit range'] = [0, 2e3]
[time_diff_centers, popt, pcov, perr, xfit1, yfit] = \
    fit_RA_hist_weighting(RA_hist,Rossi_alpha_settings)
# xfit_array = xfit
popt_array = popt
perr_array = perr
alpha_vector.append(popt[1])
alpha_unc_vector.append(perr[1])

Rossi_alpha_settings['fit range'] = [0, 400]
[time_diff_centers, popt, pcov, perr, xfit2, yfit] = \
    fit_RA_hist_weighting(RA_hist,Rossi_alpha_settings)
# xfit_array = np.vstack((xfit_array, xfit))
popt_array = np.vstack((popt_array, popt))
perr_array = np.vstack((perr_array, perr))
alpha_vector.append(popt[1])
alpha_unc_vector.append(perr[1])

Rossi_alpha_settings['fit range'] = [500, Rossi_alpha_settings['reset time']]
[time_diff_centers, popt, pcov, perr, xfit3, yfit] = \
    fit_RA_hist_weighting(RA_hist,Rossi_alpha_settings)
# xfit_array = np.vstack((xfit_array, xfit))
popt_array = np.vstack((popt_array, popt))
perr_array = np.vstack((perr_array, perr))
alpha_vector.append(popt[1])
alpha_unc_vector.append(perr[1])

plot_RA_and_fits_errorbar(
        RA_hist, xfit1, xfit2, xfit3, 
        popt_array, perr_array, Rossi_alpha_settings
        )

alpha_array.append(alpha_vector)
alpha_unc_array.append(alpha_unc_vector)

print(popt_array)

# Add basic cross-correlation
RA_hist = np.loadtxt('RA_hist_total_aaa_cc_config_10.txt')

alpha_vector = []
alpha_unc_vector = []

Rossi_alpha_settings['fit range'] = [0, 2e3]
[time_diff_centers, popt, pcov, perr, xfit1, yfit] = \
    fit_RA_hist_weighting(RA_hist,Rossi_alpha_settings)
# xfit_array = xfit
popt_array = popt
perr_array = perr
alpha_vector.append(popt[1])
alpha_unc_vector.append(perr[1])

Rossi_alpha_settings['fit range'] = [0, 400]
[time_diff_centers, popt, pcov, perr, xfit2, yfit] = \
    fit_RA_hist_weighting(RA_hist,Rossi_alpha_settings)
# xfit_array = np.vstack((xfit_array, xfit))
popt_array = np.vstack((popt_array, popt))
perr_array = np.vstack((perr_array, perr))
alpha_vector.append(popt[1])
alpha_unc_vector.append(perr[1])

Rossi_alpha_settings['fit range'] = [500, Rossi_alpha_settings['reset time']]
[time_diff_centers, popt, pcov, perr, xfit3, yfit] = \
    fit_RA_hist_weighting(RA_hist,Rossi_alpha_settings)
# xfit_array = np.vstack((xfit_array, xfit))
popt_array = np.vstack((popt_array, popt))
perr_array = np.vstack((perr_array, perr))
alpha_vector.append(popt[1])
alpha_unc_vector.append(perr[1])

plot_RA_and_fits_errorbar(
        RA_hist, xfit1, xfit2, xfit3, 
        popt_array, perr_array, Rossi_alpha_settings
        )


print(popt_array)

# Add multi-level cross-correlation
RA_hist = np.loadtxt('RA_hist_total_aaa_cc_nr_config_10.txt')

alpha_vector = []
alpha_unc_vector = []

Rossi_alpha_settings['fit range'] = [0, 2e3]
[time_diff_centers, popt, pcov, perr, xfit1, yfit] = \
    fit_RA_hist_weighting(RA_hist,Rossi_alpha_settings)
# xfit_array = xfit
popt_array = popt
perr_array = perr
alpha_vector.append(popt[1])
alpha_unc_vector.append(perr[1])

Rossi_alpha_settings['fit range'] = [0, 400]
[time_diff_centers, popt, pcov, perr, xfit2, yfit] = \
    fit_RA_hist_weighting(RA_hist,Rossi_alpha_settings)
# xfit_array = np.vstack((xfit_array, xfit))
popt_array = np.vstack((popt_array, popt))
perr_array = np.vstack((perr_array, perr))
alpha_vector.append(popt[1])
alpha_unc_vector.append(perr[1])

Rossi_alpha_settings['fit range'] = [500, Rossi_alpha_settings['reset time']]
[time_diff_centers, popt, pcov, perr, xfit3, yfit] = \
    fit_RA_hist_weighting(RA_hist,Rossi_alpha_settings)
# xfit_array = np.vstack((xfit_array, xfit))
popt_array = np.vstack((popt_array, popt))
perr_array = np.vstack((perr_array, perr))
alpha_vector.append(popt[1])
alpha_unc_vector.append(perr[1])

plot_RA_and_fits_errorbar(
        RA_hist, xfit1, xfit2, xfit3, 
        popt_array, perr_array, Rossi_alpha_settings
        )


print(popt_array)

# Add multi-level cross-correlation with digital delay
RA_hist = np.loadtxt('RA_hist_total_aaa_cc_nr_dd_config_10.txt')

alpha_vector = []
alpha_unc_vector = []

Rossi_alpha_settings['fit range'] = [0, 2e3]
[time_diff_centers, popt, pcov, perr, xfit1, yfit] = \
    fit_RA_hist_weighting(RA_hist,Rossi_alpha_settings)
# xfit_array = xfit
popt_array = popt
perr_array = perr
alpha_vector.append(popt[1])
alpha_unc_vector.append(perr[1])

Rossi_alpha_settings['fit range'] = [0, 400]
[time_diff_centers, popt, pcov, perr, xfit2, yfit] = \
    fit_RA_hist_weighting(RA_hist,Rossi_alpha_settings)
# xfit_array = np.vstack((xfit_array, xfit))
popt_array = np.vstack((popt_array, popt))
perr_array = np.vstack((perr_array, perr))
alpha_vector.append(popt[1])
alpha_unc_vector.append(perr[1])

Rossi_alpha_settings['fit range'] = [500, Rossi_alpha_settings['reset time']]
[time_diff_centers, popt, pcov, perr, xfit3, yfit] = \
    fit_RA_hist_weighting(RA_hist,Rossi_alpha_settings)
# xfit_array = np.vstack((xfit_array, xfit))
popt_array = np.vstack((popt_array, popt))
perr_array = np.vstack((perr_array, perr))
alpha_vector.append(popt[1])
alpha_unc_vector.append(perr[1])

plot_RA_and_fits_errorbar(
        RA_hist, xfit1, xfit2, xfit3, 
        popt_array, perr_array, Rossi_alpha_settings
        )

alpha_array = np.vstack((alpha_array,alpha_vector))
alpha_unc_array = np.vstack((alpha_unc_array,alpha_unc_vector))

pp_array = -alpha_array**(-1)
pp_unc_array = -pp_array*alpha_unc_array/alpha_array

# print(popt_array)


# Make alpha estimate plot

fig3, ax3 = plt.subplots()

i = 0
ax3.errorbar(
    [1,2], pp_array[:,i], pp_unc_array[:,i], 
    fmt='d', markersize=10, capsize=3, color='k', 
    label='Full fit'
    )

i = 1
ax3.errorbar(
    [1,2], pp_array[:,i], pp_unc_array[:,i], 
    fmt='<', markersize=10, capsize=3, color='b', 
    label='Early region fit',
    alpha=0.5
    )

i = 2
ax3.errorbar(
    [1,2], pp_array[:,i], pp_unc_array[:,i], 
    fmt='>', markersize=10, capsize=3, color='r', 
    label='Late region fit',
    alpha=0.5
    )

ax3.set_xlim([0.75,2.25])

# Set the axis labels
# ax3.set_xlabel('Time difference (ns)')
ax3.set_ylabel(r'-$\alpha^{-1}$ (ns)')
# ax3.set_yscale(Rossi_alpha_settings['plot scale'])
plt.xticks([1,2],
           labels=['Any-and-all','Digital delay'])

# Add equation to plot
# plt.text(xlim[1]*0.6, ylim[1]*0.35, 
#          r'$p(\Delta t)=A*e^{\alpha \Delta t} + C$', 
#          fontsize=16, color='k', ha='center', va='center')

plt.legend(loc='center')
plt.show()

# # Import all neutron detections from array with tags
# list_data_n = np.loadtxt(data_folder + '/' + 'board0_n_allch.txt')

# # Do a Rossi-alpha fit

# time_diffs = calculate_time_differences(list_data_n, Rossi_alpha_settings)

# [RA_hist, popt, pcov, x_fit, y_fit] = \
#     make_and_plot_RA_hist_and_fit(time_diffs, Rossi_alpha_settings)
        
# # Gamma-ray data
# i = 0;   

# for filename in os.listdir(data_folder + '/1'):              
    
#     if filename.endswith('_g.txt'):
        
#         path_to_data = data_folder + '/1/' + filename
        
#         if i == 0:
#             list_data_g = np.loadtxt(path_to_data)
#         else:
#             list_data_g = np.vstack([list_data_g, np.loadtxt(path_to_data)])
            
#         i = i + 1
        
# # Total data
# i = 0;           
    
# for i in range(0, 11):
    
#     path_to_data = data_folder + '/1/board0ch' + str(i) + '.txt'
    
#     if i == 0:
#         list_data = np.loadtxt(path_to_data)
#     else:
#         list_data = np.vstack([list_data, np.loadtxt(path_to_data)])
        
#     i = i + 1
        


# for i in range(2, num_folders):
    
#     for filename in os.listdir(data_folder + '/' + str(i)):
        
#         if filename.endswith('board0ch*_n.txt'):
            
#             path_to_data = data_folder + filename
            
#             Data = Load_Waveforms(path_to_data,num_samples,num_waveforms)