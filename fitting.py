import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


#--------------------------------------------------------------------------------
# OWN CODE BELOW
#--------------------------------------------------------------------------------

# Define the function to fit
def exp_decay_3_param(x, a, b, c):
    return a * np.exp(b * x) + c

# Define the function to fit
def exp_decay_2_param(x, a, b):
    return a * np.exp(b * x)

#--------------------------------------------------------------------------------

def fit(counts, bin_centers, min_cutoff, x_axis, y_axis, title, options):

    # Fitting line function to truncated data
    popt, pcov = curve_fit(exp_func, bin_centers, counts)

    # displaying fitting parameters
    print('Fit parameters: A =', popt[0], ', alpha =', popt[1], ', B =', popt[2])

    # deriving line x and line y
    line_x = np.linspace(min_cutoff, bin_centers[-1], len(bin_centers))
    line_y = exp_func(line_x, *popt)

    # plotting the best fit curve to the plot
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(bin_centers, counts, width=0.8*(bin_centers[1]-bin_centers[0]), alpha=0.6, color='g')
    ax.plot(line_x, line_y, 'r--', label='Fit: A=%5.3f, alpha=%5.3f, B=%5.3f' % tuple(popt), **options)
    ax.legend()
    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)
    ax.set_title(title)

    # fig.savefig('test1', dpi=300, bbox_inches='tight')

    return popt, line_y

#--------------------------------------------------------------------------------

def residual_plot(counts, bin_centers, min_cutoff, line_y, x_axis, y_axis, title, options):

    # compute residuals
    residuals = counts - line_y

    # normalize residuals
    residuals_norm = residuals / np.max(np.abs(residuals))

    # create scatter plot of normalized residuals
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(bin_centers, residuals_norm, **options)
    ax.axhline(y=0, color='r', linestyle='--')
    ax.set_ylim([-1, 1])  # set y-axis limits to -1 and 1
    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)
    ax.set_title(title)
    fig.tight_layout()

    # fig.savefig('test2', dpi=300, bbox_inches='tight')

#--------------------------------------------------------------------------------



def fit_and_residual(counts, bin_centers, min_cutoff, fit_range, x_axis, y_axis, title, fitting_options, residual_options):

    num_bins = np.size(counts)
    time_diff_centers = bin_centers[1:] - np.diff(bin_centers[:2])/2

    # Choosing region to fit
    fit_index = np.where(
    (time_diff_centers > min_cutoff) & 
    (time_diff_centers >= fit_range[0]) & 
    (time_diff_centers <= fit_range[1]))

    xfit = time_diff_centers[fit_index]

    # Fitting distribution
    # Fitting the data using curve_fit
    exp_decay_fit_bounds = ([0,-np.inf],[np.inf,0])
    a0 = np.max(counts)
    c0 = np.mean(counts[-int(num_bins*0.05):])
    b0 = ((np.log(c0)-np.log(counts[0]))/
          (time_diff_centers[-1]-time_diff_centers[0]))
    
    yfit = counts[fit_index] - c0
    exp_decay_p0 = [a0, b0]

    # Fitting line function to truncated data
    popt, pcov = curve_fit(exp_decay_2_param, xfit, yfit, bounds=exp_decay_fit_bounds, p0=exp_decay_p0, maxfev=1e6)

    # deriving line x and line y
    # line_x = np.linspace(min_cutoff, bin_centers[-1], len(bin_centers))
    line_x = xfit
    line_y = exp_decay_3_param(xfit, *popt, c0)

    # displaying fitting parameters
    popt = np.hstack((popt, c0))
    print('Fit parameters: A =', popt[0], ', alpha =', popt[1], ', B =', popt[2])

    # create figure and axes
    fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True, figsize=(8, 6), gridspec_kw={'height_ratios': [2, 1]})

    # plotting histogram and fitting curve in top subplot
    ax1.bar(bin_centers, counts, width=0.8*(bin_centers[1]-bin_centers[0]), alpha=0.6,
            color="b",
            align="center",
            edgecolor="k",
            linewidth=0.5,
            fill=True)
    ax1.plot(line_x, line_y, 'r--', label='Fit: A=%5.3f, alpha=%5.3f, B=%5.3f' % tuple(popt), **fitting_options)
    ax1.legend()
    ax1.set_ylabel(y_axis)

    # computing residuals and plot in bottom subplot
    residuals = counts[fit_index] - line_y
    residuals_norm = residuals / np.max(np.abs(residuals))

    index = (time_diff_centers >= xfit[0]) & (time_diff_centers <= xfit[-1])

    ax2.scatter(time_diff_centers[index], residuals_norm, **residual_options)
    ax2.axhline(y=0, color='r', linestyle='--')
    ax2.set_ylim([-1, 1])
    ax2.set_xlabel(x_axis)
    ax2.set_ylabel('Relative residuals')

    # setting title for entire figure
    fig.suptitle(title, fontsize=14)

    # adjusting layout and display plot
    fig.tight_layout()

    # saving plot to file
    fig.savefig('test3', dpi=300, bbox_inches='tight')

    return popt