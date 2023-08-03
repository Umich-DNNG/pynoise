import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os
plt.ioff()
def exp_decay_3_param(x, a, b, c):

    '''
    Description:
        - Exponential decay function with 3 parameters including offset

    Inputs:
        - x (time differences: x-axis)
        - a (coefficient constant)
        - b (alpha value)
        - c (offset constant)

    Outputs:
        - Exponential decay function
    '''

    # exponential decay function with 3 parameters
    return a * np.exp(b * x) + c

def exp_decay_2_param(x, a, b):

    '''
    Description:
        - Exponential decay function with 2 parameters including offset

    Inputs:
        - x (time differences: x-axis)
        - a (coefficient constant)
        - b (alpha value)
    
    Outputs:
        - Exponential decay function
    '''
    
    # exponential decay function with 2 parameters
    return a * np.exp(b * x)

#--------------------------------------------------------------------------------    

class RossiHistogramFit:
    def __init__(self, counts, bin_centers,timeDifMethod = 'any_and_all', fit_range = None  ):
        
        '''
        Description:
            - Creating the a Fit() object and its variables.

        Inputs:
            - counts (The set of values of the histogram as a list)
            - bin_centers (adjusted bin centers for visual plotting)
            - timeDifMethod: method used to calculate time differences
            - fit_range: range of values to fit the curve to
            

        Outputs: 
            - Fit() object
        '''
        # Required parameters
        self.counts = counts
        self.bin_centers = bin_centers
        self.fit_range = fit_range
        self.timeDifMethod = timeDifMethod

        self.save_fig = False
        self.save_dir = "./"
        self.show_plot = True
        self.fitting_options = None
        self.residual_options = None
        self.hist_visual_options = None
        self.a = None
        self.b = None
        self.alpha = None
        self.pred = None
        self.residuals = None

        if fit_range is None:
            self.fit_range = [min(bin_centers), max(bin_centers)] 


    def fit(self, save_fig: bool = True, save_dir = './', show_plot: bool = True, fitting_opts = None,hist_visual_opts = None):
        self.fitting_options = fitting_opts
        self.hist_visual_options = hist_visual_opts
        self.save_dir = save_dir
        '''
        Description:
            - Fitting an exponential curve onto the histogram.
            - Saving and showing the plot can be turned on or off.

        Inputs:
            - save_fig: True/False to save the figure or not
            - save_dir: String with path to where figure should be saved
            - show_plot: True/False to show the plot
            - fitting_opts (setting for fitting)
            - hist_visual_opts (setting for styling histogram plot)

        Outputs: 
            - popt (Optimal values for the parameters)
        '''

        #Default Settings for Histogram Visuals
        if hist_visual_opts is None:
            hist_visual_opts = {
                "alpha": 1,
                "fill": True,
                "color": "#B2CBDE",
                "edgecolor": "#162F65",
                "linewidth": 0.4
            }
        #Default Settings for Fitting_Opts
        if fitting_opts is None:
            fitting_opts = {
                "color": "#162F65",
                "markeredgecolor": "blue",
                "markerfacecolor": "black",
                "linestyle": "-",
                "linewidth": 1
            }
        num_bins = np.size(self.counts)
        time_diff_centers = self.bin_centers[1:] - np.diff(self.bin_centers[:2])/2

        # Choosing region to fit
        fit_index = np.where((time_diff_centers >= self.fit_range[0]) & 
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

        # Deriving line x and line y
        line_x = xfit
        self.pred = exp_decay_3_param(xfit, *popt, c0)

        # Displaying fitting parameters
        popt = np.hstack((popt, c0))
        self.a = popt[0]
        self.alpha = popt[1]
        self.b = popt[2]
        print('Fit parameters: A =', popt[0], ', alpha =', popt[1], ', B =', popt[2])

        # Create figure and axes
        fig, ax1 = plt.subplots(nrows=2, sharex=True, figsize=(8, 6), gridspec_kw={'height_ratios': [2, 1]})

        # Plotting histogram and fitting curve in top subplot
        ax1.bar(self.bin_centers, self.counts, width=0.8*(self.bin_centers[1]-self.bin_centers[0]), 
                alpha=0.6, color="b", align="center", edgecolor="k", linewidth=0.5, fill=True)
        
        prev_label = self.fitting_options.get('label')
        self.fitting_options['label'] = (prev_label if prev_label != None else 'Fitted Curve') + (' (A=%5.3f, alpha=%5.3f, B=%5.3f)' % tuple(popt))

        ax1.plot(line_x, self.pred, 'r--', **self.fitting_options)
        ax1.legend()
        ax1.set_ylabel(self.y_axis)

        if prev_label == None:
            self.fitting_options.pop('label')
        else:
            self.fitting_options['label'] = prev_label

        # Saving figure (optional)
        if save_fig:
            fig.tight_layout()
            fig.savefig('fitted_only', dpi=300, bbox_inches='tight')

        # Showing plot (optional)
        if show_plot:
            plt.show()
        return popt

#--------------------------------------------------------------------------------

    def fit_and_residual(self, save_fig: bool, save_dir, show_plot: bool, fitting_opts,residual_opts,hist_visual_opts, folder_index = None, verbose: bool = False):

        '''
        Description:
            - Fitting an exponential curve onto the histogram and creating a residual plot to measure the accuracy.
            - Saving and showing the plot can be turned on or off.

        Inputs:
            Inputs:
            - save_fig: True/False to save the figure or not
            - save_dir: String with path to where figure should be saved
            - show_plot: True/False to show the plot
            - fitting_opts (setting for fitting)
            - residual_opts (setting for residuals)
            - hist_visual_opts (setting for styling histogram plot)
            - folder_index: 

        Outputs: 
            - popt (Optimal values for the parameters)
        '''

        self.fitting_options = fitting_opts
        #self.residual_options = settings['Scatter Plot Settings']
        self.residual_options = residual_opts
        #self.hist_visual_options = settings['Histogram Visual Settings']
        self.hist_visual_options = hist_visual_opts
        self.save_dir = save_dir
        self.save_fig = save_fig
        num_bins = np.size(self.counts)
        time_diff_centers = self.bin_centers[1:] - np.diff(self.bin_centers[:2])/2

        # Choosing region to fit
        fit_index = np.where((time_diff_centers >= self.fit_range[0]) & 
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

        # Deriving line x and line y
        line_x = xfit
        self.pred = exp_decay_3_param(xfit, *popt, c0)

        # Displaying fitting parameters
        popt = np.hstack((popt, c0))
        self.a = popt[0]
        self.alpha = popt[1]
        self.b = popt[2]
        if folder_index is None:
            print('Fit parameters: A =', popt[0], ', alpha =', popt[1], ', B =', popt[2])

        # Create figure and axes
        fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True, figsize=(8, 6), gridspec_kw={'height_ratios': [2, 1]})

        prev_label = self.fitting_options.get('label')
        self.fitting_options['label'] = (prev_label if prev_label != None else 'Fitted Curve') + (' (A=%5.3f, alpha=%5.3f, B=%5.3f)' % tuple(popt))

        # Plotting histogram and fitting curve in top subplot
        ax1.bar(self.bin_centers, self.counts, width=0.8*(self.bin_centers[1]-self.bin_centers[0]), **self.hist_visual_options)
        ax1.plot(line_x, self.pred, **self.fitting_options)
        ax1.legend()
        ax1.set_ylabel("Coincidence rate (s^-1)")

        if prev_label == None:
            self.fitting_options.pop('label')
        else:
            self.fitting_options['label'] = prev_label

        # Computing residuals and plot in bottom subplot
        self.residuals = self.counts[fit_index] - self.pred
        residuals_norm = self.residuals / np.max(np.abs(self.residuals))

        index = (time_diff_centers >= xfit[0]) & (time_diff_centers <= xfit[-1])

        ax2.scatter(time_diff_centers[index], residuals_norm, **self.residual_options)
        ax2.axhline(y=0, color='#162F65', linestyle='--')
        ax2.set_ylim([-1, 1])
        ax2.set_xlabel("Time Differences(ns)")
        ax2.set_ylabel('Relative Residuals (%)')

        # Setting title for entire figure
        fig.suptitle(self.timeDifMethod, fontsize=14)

        # Adjusting layout and saving figure (optional)
        if self.save_fig and (folder_index is None or verbose):
            fig.tight_layout()
            if folder_index is not None:
                save_filename = os.path.join(self.save_dir, 'fitted_and_residual_folder' + str(folder_index)) 
                fig.savefig(save_filename, dpi=300, bbox_inches='tight')
            else:
                save_filename = os.path.join(self.save_dir, 'fitted_and_residual')
                fig.savefig(save_filename, dpi=300, bbox_inches='tight')

        # Showing plot (optional)
        if show_plot and (folder_index is None or verbose):
            plt.show()
        return popt

#--------------------------------------------------------------------------------

class Fit_With_Weighting:
    def __init__(self,RA_hist_totals, fit_range: dict, saveDir: str, fitting_opts: dict, residual_opts: dict):

        '''
        Description:
            - Creating the a Fit_with_Weighting() object and its variables.

        Inputs:
            - RA_hist_totals (array of counts and uncertainties)
            - generating_hist_settings (setting for histogram plotting)
            - general_settings (general setting)
            - fitting_opts (setting for fitting)
            - residual_opts (setting for residuals)

        Outputs: 
            - Fit_with_Weighting() object
        '''

        # Plotting options
        self.fitting_options = fitting_opts
        self.residual_options = residual_opts

        # Required parameters
        self.hist = RA_hist_totals[0]
        self.num_bins = np.size(RA_hist_totals[0])
        self.time_diff_centers = RA_hist_totals[1]
        self.uncertainties = RA_hist_totals[2]
        self.fit_range = fit_range
        self.save_dir = saveDir
        self.a = None
        self.b = None
        self.alpha = None
        self.pred = None

        # Line fitting variables
        self.xfit = None


    def fit_RA_hist_weighting(self):

        '''
        Description:
            - Fitting an exponential curve onto the histogram with weighting.
            - Saving and showing the plot can be turned on or off.

        Inputs:
            - self (encompasses all private variables)

        Outputs: 
            - None
        '''

        # Choosing region to fit
        fit_index = np.where((self.time_diff_centers >= self.fit_range[0]) &
                             (self.time_diff_centers <= self.fit_range[1]))

        xfit = self.time_diff_centers[fit_index]
        
        # Fitting distribution
        # Fitting the data using curve_fit
        exp_decay_fit_bounds = ([0,-np.inf],[np.inf,0])
        a0 = np.max(self.hist)
        c0 = np.mean(self.hist[-int(self.num_bins*0.05):])
        b0 = ((np.log(c0)-np.log(self.hist[0]))/
            (self.time_diff_centers[-1]-self.time_diff_centers[0]))
        yfit = self.hist[fit_index] - c0
        exp_decay_p0 = [a0, b0]
        popt, pcov = curve_fit(exp_decay_2_param, xfit, yfit, bounds=exp_decay_fit_bounds, 
                               p0=exp_decay_p0,maxfev=1e6,sigma=self.uncertainties[fit_index], 
                               absolute_sigma=True)
        

        # Printing out optimization parameters
        self.a = popt[0]
        self.alpha = popt[1]
        self.b = c0
        print('Fit parameters: A =', popt[0], ', alpha =', popt[1], ', B =', c0)

        self.pred = exp_decay_3_param(xfit, *popt, c0)
        
        cerr = np.std(self.hist[-int(self.num_bins*0.05):], axis=0, ddof=1)
        
        perr = np.sqrt(np.diag(pcov)) 
        perr = np.hstack((perr, cerr))
        
        self.xfit = xfit

       
    def plot_RA_and_fit(self, save_fig: bool, show_plot: bool, errorBars: str):

        '''
        Description:
            - Plotting the sum of histograms generated.
            - Saving and showing the plot can be turned on or off.

        Inputs:
            - self (encompasses all private variables)

        Outputs: 
            - None
        '''

        fit_index = np.where((self.time_diff_centers >= self.fit_range[0]) &
                             (self.time_diff_centers <= self.fit_range[1]))

        time_diff_centers1 = self.time_diff_centers[1:] - np.diff(self.time_diff_centers[:2])/2
        
        fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True, figsize=(8, 6), gridspec_kw={'height_ratios': [2, 1]})
        
        # Creating a scatter plot with the data
        ax1.scatter(time_diff_centers1, self.hist[:-1], **self.residual_options)
        
        if errorBars == "bar":
            ax1.errorbar(time_diff_centers1, self.hist[:-1], yerr=self.uncertainties[:-1], fmt='o', ecolor='black',capsize=5)
        #ax.fill_between(time_diff_centers, self.hist[:-1] - self.uncertainties[:-1], self.hist[:-1] + self.uncertainties[:-1], alpha=0.3, color='gray')
        elif errorBars == "band":
            lower_bound = self.hist[:-1] - self.uncertainties[:-1]
            upper_bound = self.hist[:-1] + self.uncertainties[:-1]
            ax1.fill_between(time_diff_centers1, lower_bound, upper_bound, alpha=0.3, color='gray')

        prev_label = self.fitting_options.get('label')
        self.fitting_options['label'] = ((prev_label if prev_label != None else 'Fitted Curve')
                                         + ' (A=' + f'{self.a:.3g}' + ', alpha=' 
                                         + f'{self.alpha:.3g}' + ', B=' 
                                         + f'{self.b:.3g}' + ')')

        # Adding the fit to the data
        ax1.plot(self.xfit, self.pred, **self.fitting_options)
        
        # Setting the axis labels
        ax1.set_xlabel('Time difference (ns)')
        ax1.set_ylabel('Counts')
        ax1.legend()

        # Computing residuals and plot in bottom subplot
        residuals = self.hist[fit_index] - self.pred
        residuals_norm = residuals / np.max(np.abs(residuals))

        ax2.scatter(self.time_diff_centers[fit_index], residuals_norm, **self.residual_options)
        ax2.axhline(y=0, color='#162F65', linestyle='--')
        ax2.set_ylim([-1, 1])
        ax2.set_xlabel('Time difference (ns)')
        ax2.set_ylabel('Relative residuals (%)')

        if prev_label == None:
            self.fitting_options.pop('label')
        else:
            self.fitting_options['label'] = prev_label

        # Adjusting layout and saving figure (optional)
        if save_fig:
            fig.tight_layout()
            save_filename = os.path.join(self.save_dir, 'histogram_weighting_total.png') 
            fig.savefig(save_filename, dpi=300, bbox_inches='tight')
        
        # Displaying the plot (optional)
        if show_plot:
            plt.show()