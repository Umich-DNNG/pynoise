import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import sys


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

class Fit:
    def __init__(self, counts,bin_centers, generating_hist_settings,fitting_opts, general_settings, residual_opts,showPlot = True):
        self.counts = counts
        self.bin_centers = bin_centers
        self.fit_range = general_settings['fit range']
        self.min_cutoff = generating_hist_settings['minimum cutoff']
        self.fitting_options = fitting_opts
        self.residual_options = residual_opts
        self.show_plot = showPlot
        self.timeDifMethod = general_settings['time difference method']


    def fit(self):

        num_bins = np.size(self.counts)
        time_diff_centers = self.bin_centers[1:] - np.diff(self.bin_centers[:2])/2

        # Choosing region to fit
        fit_index = np.where(
        (time_diff_centers > self.min_cutoff) & 
        (time_diff_centers >= self.fit_range[0]) & 
        (time_diff_centers <= self.fit_range[1]))

        xfit = time_diff_centers[fit_index]

        # Fitting distribution
        # Fitting the data using curve_fit
        exp_decay_fit_bounds = ([0,-np.inf],[np.inf,0])
        a0 = np.max(self.counts)
        c0 = np.mean(self.counts[-int(num_bins*0.05):])
        b0 = ((np.log(c0)-np.log(self.counts[0]))/
            (time_diff_centers[-1]-time_diff_centers[0]))
        
        yfit = self.counts[fit_index] - c0
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
        fig, ax1 = plt.subplots(nrows=2, sharex=True, figsize=(8, 6), gridspec_kw={'height_ratios': [2, 1]})

        # plotting histogram and fitting curve in top subplot
        ax1.bar(self.bin_centers, self.counts, width=0.8*(self.bin_centers[1]-self.bin_centers[0]), alpha=0.6,
                color="b",
                align="center",
                edgecolor="k",
                linewidth=0.5,
                fill=True)
        ax1.plot(line_x, line_y, 'r--', label='Fit: A=%5.3f, alpha=%5.3f, B=%5.3f' % tuple(popt), **self.fitting_options)
        ax1.legend()
        ax1.set_ylabel(self.y_axis)

        if self.show_plot == True:
            plt.show()

        fig.savefig('fitted_only', dpi=300, bbox_inches='tight')

        return popt

#--------------------------------------------------------------------------------

    def fit_and_residual(self):

        num_bins = np.size(self.counts)
        time_diff_centers = self.bin_centers[1:] - np.diff(self.bin_centers[:2])/2

        # Choosing region to fit
        fit_index = np.where(
        (time_diff_centers > self.min_cutoff) & 
        (time_diff_centers >= self.fit_range[0]) & 
        (time_diff_centers <= self.fit_range[1]))

        xfit = time_diff_centers[fit_index]

        # Fitting distribution
        # Fitting the data using curve_fit
        exp_decay_fit_bounds = ([0,-np.inf],[np.inf,0])
        a0 = np.max(self.counts)
        c0 = np.mean(self.counts[-int(num_bins*0.05):])
        b0 = ((np.log(c0)-np.log(self.counts[0]))/
            (time_diff_centers[-1]-time_diff_centers[0]))
        
        yfit = self.counts[fit_index] - c0
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

        if self.show_plot == True:
            # create figure and axes
            fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True, figsize=(8, 6), gridspec_kw={'height_ratios': [2, 1]})

            # plotting histogram and fitting curve in top subplot
            ax1.bar(self.bin_centers, self.counts, width=0.8*(self.bin_centers[1]-self.bin_centers[0]), alpha=0.6,
                    color="b",
                    align="center",
                    edgecolor="k",
                    linewidth=0.5,
                    fill=True)
            ax1.plot(line_x, line_y, 'r--', label='Fit: A=%5.3f, alpha=%5.3f, B=%5.3f' % tuple(popt), **self.fitting_options)
            ax1.legend()
            ax1.set_ylabel("Coincidence rate (s^-1)")

            # computing residuals and plot in bottom subplot
            residuals = self.counts[fit_index] - line_y
            residuals_norm = residuals / np.max(np.abs(residuals))

            index = (time_diff_centers >= xfit[0]) & (time_diff_centers <= xfit[-1])

            ax2.scatter(time_diff_centers[index], residuals_norm, **self.residual_options)
            ax2.axhline(y=0, color='r', linestyle='--')
            ax2.set_ylim([-1, 1])
            ax2.set_xlabel("Time Differences(ns)")
            ax2.set_ylabel('Relative residuals')

            # setting title for entire figure
            fig.suptitle(self.timeDifMethod, fontsize=14)

            # adjusting layout and display plot
            fig.tight_layout()

            
            # displaying plot
            plt.show()

            # saving plot to file
            fig.savefig('fitted_and_residual', dpi=300, bbox_inches='tight')

        return popt

#--------------------------------------------------------------------------------

class Fit_With_Weighting:
    def __init__(self,RA_hist_totals, generating_hist_settings, general_settings):
        self.hist = RA_hist_totals[0]
        self.num_bins = np.size(RA_hist_totals[0])
        self.time_diff_centers = RA_hist_totals[1]
        self.uncertainties = RA_hist_totals[2]
        self.fit_range = general_settings['fit range']
        self.min_cutoff = generating_hist_settings['minimum cutoff']
        self.plot_scale = general_settings['plot scale']
        self.xfit = None
        self.yfit = None
    def fit_RA_hist_weighting(self):

        
        # Choose region to fit
        fit_index = np.where(((self.time_diff_centers > self.min_cutoff) & 
            (self.time_diff_centers >= self.fit_range[0]) & 
            (self.time_diff_centers <= self.fit_range[1])))
        xfit = self.time_diff_centers[fit_index]
        
        # Fit distribution
        # Fit the data using curve_fit
        # exp_decay_fit_bounds = ([0,-np.inf,0],[np.inf,0,np.inf])
        exp_decay_fit_bounds = ([0,-np.inf],[np.inf,0])
        a0 = np.max(self.hist)
        c0 = np.mean(self.hist[-int(self.num_bins*0.05):])
        b0 = ((np.log(c0)-np.log(self.hist[0]))/
            (self.time_diff_centers[-1]-self.time_diff_centers[0]))
        yfit = self.hist[fit_index] - c0
        #exp_decay_p0 = [a0, b0, c0]
        exp_decay_p0 = [a0, b0]
        popt, pcov = curve_fit(exp_decay_2_param, xfit, yfit,bounds=exp_decay_fit_bounds, p0=exp_decay_p0,maxfev=1e6,sigma=self.uncertainties[fit_index], absolute_sigma=True)
        

        #popt, pcov = curve_fit(exp_decay_2_param, xfit, yfit, bounds=exp_decay_fit_bounds, p0=exp_decay_p0, maxfev=1e6)


        yfit = exp_decay_3_param(xfit, *popt, c0)
        
        popt = np.hstack((popt, c0))
        
        cerr = np.std(self.hist[-int(self.num_bins*0.05):], axis=0, ddof=1)
        
        perr = np.sqrt(np.diag(pcov)) 
        
        perr = np.hstack((perr, cerr))
        
        self.xfit = xfit
        self.yfit = yfit

       
    def plot_RA_and_fit(self):
        
        #time_diff_centers = RA_hist[1][1:] - np.diff(RA_hist[1][:2])/2
        
        fig2, ax2 = plt.subplots()
        
        # Create a scatter plot with the data
        ax2.scatter(self.time_diff_centers, self.hist[:-1])
        
        # Add the fit to the data
        ax2.plot(self.xfit, self.yfit, 'r-', label='Fit')
        
        # Set the axis labels
        ax2.set_xlabel('Time difference (ns)')
        ax2.set_ylabel('Counts')
        ax2.set_yscale(self.plot_scale)
        
        # Display the plot
        plt.show()
        
        return