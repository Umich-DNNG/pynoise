import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

#--------------------------------------------------------------------------------

def exp_decay_3_param(x, a, b, c):
    return a * np.exp(b * x) + c

def exp_decay_2_param(x, a, b):
    return a * np.exp(b * x)

#--------------------------------------------------------------------------------

def fit_RA_hist(RA_hist, Rossi_alpha_settings):
    
    num_bins = np.size(RA_hist[0])
    time_diff_centers = RA_hist[1][1:] - np.diff(RA_hist[1][:2])/2
    
    # Choose region to fit
    fit_index = ((time_diff_centers > Rossi_alpha_settings['minimum cutoff']) & 
                 (time_diff_centers >= Rossi_alpha_settings['fit range'][0]) & 
                 (time_diff_centers <= Rossi_alpha_settings['fit range'][1]))
    
    xfit = time_diff_centers[fit_index]
    
    # Fit distribution
    # Fit the data using curve_fit
    # exp_decay_fit_bounds = ([0,-np.inf,0],[np.inf,0,np.inf])
    exp_decay_fit_bounds = ([0,-np.inf],[np.inf,0])
    a0 = np.max(RA_hist[0])
    c0 = np.mean(RA_hist[0][-int(num_bins*0.05):])
    b0 = ((np.log(c0) - np.log(RA_hist[0][0] + 1e-9)) /
      (time_diff_centers[-1] - time_diff_centers[0]))
    # b0 = ((np.log(c0)-np.log(RA_hist[0][0]))/
          # (time_diff_centers[-1]-time_diff_centers[0]))
    yfit = RA_hist[0][fit_index] - c0
    # exp_decay_p0 = [a0, b0, c0]
    exp_decay_p0 = a0, a0

    popt, pcov = curve_fit(exp_decay_2_param, xfit, yfit,
                           bounds=exp_decay_fit_bounds, maxfev=1e6)
    
    yfit = exp_decay_3_param(xfit, *popt, c0)
    
    popt = np.hstack((popt, c0))
    
    return [time_diff_centers, popt, pcov, xfit, yfit]

#--------------------------------------------------------------------------------

def fit_RA_hist_weighting(RA_hist,Rossi_alpha_settings):
    
    num_bins = np.size(RA_hist[0])
    time_diff_centers = RA_hist[1]
    
    # Calculate weighting with relative variance
    uncertainties = RA_hist[2]
    
    # Choose region to fit
    fit_index = ((time_diff_centers > Rossi_alpha_settings['minimum cutoff']) & 
                 (time_diff_centers >= Rossi_alpha_settings['fit range'][0]) & 
                 (time_diff_centers <= Rossi_alpha_settings['fit range'][1]))
    
    xfit = time_diff_centers[fit_index]
    
    # Fit distribution
    # Fit the data using curve_fit
    # exp_decay_fit_bounds = ([0,-np.inf,0],[np.inf,0,np.inf])
    exp_decay_fit_bounds = ([0,-np.inf],[np.inf,0])

    a0 = np.max(RA_hist[0])
    c0 = np.mean(RA_hist[0][-int(num_bins*0.05):])
    b0 = ((np.log(c0)-np.log(RA_hist[0][0]))/
          (time_diff_centers[-1]-time_diff_centers[0]))
    
    yfit = RA_hist[0][fit_index] - c0
    # exp_decay_p0 = [a0, b0, c0]
    exp_decay_p0 = [a0, b0]
    popt, pcov = curve_fit(exp_decay_2_param, xfit, yfit, bounds=exp_decay_fit_bounds, p0=exp_decay_p0,
                           maxfev=1e6, sigma=uncertainties[fit_index], absolute_sigma=True)
    
    yfit = exp_decay_3_param(xfit, *popt, c0)
    
    popt = np.hstack((popt, c0))
    
    cerr = np.std(RA_hist[0][-int(num_bins*0.05):], axis=0, ddof=1)
    
    perr = np.sqrt(np.diag(pcov))
    
    perr = np.hstack((perr, cerr))
    
    return [time_diff_centers, popt, pcov, perr, xfit, yfit]

#--------------------------------------------------------------------------------

def make_RA_hist_and_fit(time_diffs, Rossi_alpha_settings):
    
    num_bins = int(Rossi_alpha_settings['reset time'] / Rossi_alpha_settings['bin width'])
    
    RA_hist = np.histogram(time_diffs,bins=num_bins, range=[0,Rossi_alpha_settings['reset time']])
    
    [time_diff_centers, popt, pcov, xfit, yfit] = \
        fit_RA_hist(RA_hist,Rossi_alpha_settings)
    
    return [RA_hist, popt, pcov, xfit, yfit]

#--------------------------------------------------------------------------------

def plot_RA_and_fit(RA_hist, xfit, yfit, Rossi_alpha_settings, x_label='Time difference (ns)', y_label='Counts'):
    
    time_diff_centers = RA_hist[1][1:] - np.diff(RA_hist[1][:2])/2
    
    fig2, ax2 = plt.subplots()
    
    # Create a scatter plot with the data
    ax2.scatter(time_diff_centers, RA_hist[0])
    
    # Add the fit to the data
    ax2.plot(xfit, yfit, 'r-', label='Fit')
    
    # Set the axis labels
    ax2.set_xlabel(x_label)
    ax2.set_ylabel(y_label)
    ax2.set_yscale(Rossi_alpha_settings['plot scale'])
    
    # Display the plot
    plt.show()
    
    return

#--------------------------------------------------------------------------------

def plot_RA_and_fit_errorbar(RA_hist, xfit, yfit, Rossi_alpha_settings, xlabel1='Time difference (ns)', ylabel1='Count rate (s$^{-1}$)',
                             xlabel2='Time difference (ns)', ylabel2='Residual count rate (s$^{-1}$)'):
    
    time_diff_centers = RA_hist[1]
    
    meas_time = Rossi_alpha_settings['meas time']
    
    fig1, ax1 = plt.subplots()
    
    # Create a errorbar plot with the data
    ax1.errorbar(
        time_diff_centers, RA_hist[0]/meas_time, yerr=RA_hist[2]/meas_time, 
        fmt='o', markersize=5, capsize=3)
    
    # Add the fit to the data
    ax1.plot(xfit, yfit/meas_time, 
             'r--', label='Fit')
    
    # Set the axis labels
    ax1.set_xlabel(xlabel1)
    ax1.set_ylabel(ylabel1)
    ax1.set_yscale(Rossi_alpha_settings['plot scale'])
    
    # Display the plot
    plt.show()
    
    fig2, ax2 = plt.subplots()
    
    # Create a residuals plot with the data and fit
    index = (time_diff_centers >= xfit[0]) & (time_diff_centers <= xfit[-1])
    residuals = RA_hist[0][index]-yfit
    ax2.errorbar(time_diff_centers[index], residuals/meas_time, 
                 yerr=RA_hist[2][index]/meas_time, fmt='o', markersize=5, capsize=3)
    ax2.axhline(y=0, linestyle='--', color='gray')
    
    # Set the axis labels
    ax2.set_xlabel(xlabel2)
    ax2.set_ylabel(ylabel2)
    ax2.set_yscale('linear')
    
    # Display the plot
    plt.show()
    
    return

#--------------------------------------------------------------------------------
# OWN CODE BELOW
#--------------------------------------------------------------------------------

def exp_func(t, A, alpha, B):
    return A * np.exp(-alpha * t) + B

#--------------------------------------------------------------------------------

def fit(counts, bin_centers, x_axis, y_axis, title, options):

    # fitting line function to plot
    popt, pcov = curve_fit(exp_func, bin_centers, counts)

    # displaying fitting parameters
    print('Fit parameters: A =', popt[0], ', alpha =', popt[1], ', B =', popt[2])

    # deriving line x and line y
    line_x = np.linspace(bin_centers[0], bin_centers[-1], len(bin_centers))
    line_y = exp_func(line_x, *popt)

    # plotting the best fit curve to the plot
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(bin_centers, counts, width=0.8*(bin_centers[1]-bin_centers[0]), alpha=0.6, color='g')
    ax.plot(line_x, line_y, 'r--', label='Fit: A=%5.3f, alpha=%5.3f, B=%5.3f' % tuple(popt), **options)
    ax.legend()
    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)
    ax.set_title(title)

    plt.show()

    return line_y

#--------------------------------------------------------------------------------

def residual_plot(counts, bin_centers, line_y, x_axis, y_axis, title, options):
    # compute residuals
    residuals = counts - line_y

    # create scatter plot of residuals
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(bin_centers, residuals, **options)
    ax.axhline(y=0, color='r', linestyle='--')
    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)
    ax.set_title(title)
    fig.tight_layout()

    plt.show()