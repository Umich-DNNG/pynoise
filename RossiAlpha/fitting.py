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
    def __init__(self, counts, bin_centers,timeDifMethod = 'aa', begin = None, end = None):
        
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
        if begin == None:
            begin = min(bin_centers)
        if end == None:
            end = max(bin_centers)
        self.fit_range = [begin, end]
        self.timeDifMethod = timeDifMethod
        self.save_fig = False
        self.save_dir = "./data"
        self.show_plot = True
        self.fitting_options = None
        self.residual_options = None
        self.hist_visual_options = None
        self.a = None
        self.b = None
        self.alpha = None
        self.pred = None
        self.residuals = None




    def fit(self, save_fig: bool = True, save_dir = './data', show_plot: bool = True, fitting_opts = None,hist_visual_opts = None):
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

        # Choosing region to fit
        self.fit_index = np.where((self.bin_centers >= self.fit_range[0]) & 
                             (self.bin_centers <= self.fit_range[1]))

        xfit = self.bin_centers[self.fit_index]

        # Fitting distribution
        # Fitting the data using curve_fit
        exp_decay_fit_bounds = ([0,-np.inf],[np.inf,0])
        a0 = np.max(self.counts)
        c0 = np.mean(self.counts[-int(num_bins*0.05):])
        b0 = ((np.log(c0)-np.log(self.counts[0]))/
            (self.bin_centers[-1]-self.bin_centers[0]))
        
        yfit = self.counts[self.fit_index] - c0
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
        self.fitting_options['label'] = ((prev_label if prev_label != None else 'Fitted Curve') 
                                         + f' (A={self.a:.3g}, alpha={self.alpha:.3g}, B={self.b:.3g})')

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
            save_filename = os.path.join(self.save_dir, 'fitted')
            fig.savefig(save_filename, dpi=300, bbox_inches='tight')

        # Showing plot (optional)
        if show_plot:
            plt.show()
        plt.close()
        return popt

#--------------------------------------------------------------------------------

    def fit_and_residual(self, 
                         save_fig: bool, 
                         save_dir: str, 
                         show_plot: bool, 
                         fitting_opts: dict, 
                         residual_opts: dict, 
                         hist_visual_opts: dict, 
                         input: str, 
                         method: str = 'aa', 
                         folder: bool = False, 
                         verbose: bool = False):

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

        # Choosing region to fit
        self.fit_index = np.where((self.bin_centers >= self.fit_range[0]) & 
                             (self.bin_centers <= self.fit_range[1]))

        xfit = self.bin_centers[self.fit_index]

        # Fitting distribution
        # Fitting the data using curve_fit
        exp_decay_fit_bounds = ([0,-np.inf],[np.inf,0])
        a0 = np.max(self.counts)
        c0 = np.mean(self.counts[-int(num_bins*0.05):])
        b0 = ((np.log(c0)-np.log(self.counts[0]))/
            (self.bin_centers[-1]-self.bin_centers[0]))
        
        yfit = self.counts[self.fit_index] - c0
        exp_decay_p0 = [a0, b0]

        # Fitting line function to truncated data
        popt, pcov = curve_fit(exp_decay_2_param, xfit, yfit, bounds=exp_decay_fit_bounds, p0=exp_decay_p0, maxfev=1e6)
        self.perr = np.sqrt(np.diag(pcov))
        # Deriving line x and line y
        line_x = xfit
        self.pred = exp_decay_3_param(xfit, *popt, c0)

        # Displaying fitting parameters
        popt = np.hstack((popt, c0))
        self.a = popt[0]
        self.alpha = popt[1]
        self.b = popt[2]
        #if not folder:
            #print('Fit parameters: A =', popt[0], ', alpha =', popt[1], ', B =', popt[2])

        # Create figure and axes
        fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True, figsize=(8, 6), gridspec_kw={'height_ratios': [2, 1]})

        # Plotting histogram and fitting curve in top subplot
        ax1.bar(self.bin_centers, self.counts, width=0.8*(self.bin_centers[1]-self.bin_centers[0]), **self.hist_visual_options)
        ax1.plot(line_x, self.pred, **self.fitting_options)
        equation = r'$Ae^{\alpha}+B$:'
        alph_str = (r'$\alpha$ = (' + f'{self.alpha / 1e9:.3g}' + '$\pm$ ' + f'{self.perr[1] / 1e9:.3g}' + ') 1/s')
        a_str = (r'$A$ = (' + f'{self.a:.3g}' + '$\pm$ ' + f'{self.perr[0]:.3g}' + ') counts')
        b_str = r'$B$ = ' + f'{self.b:.3g} counts'
        ymin, ymax = ax1.get_ylim()
        xmin, xmax = ax1.get_xlim()
        xloc = (xmin+xmax)/3
        dy = ymax-ymin
        ax1.annotate(equation, 
                    xy=(xloc*3/3.5, ymax-0.2*dy), 
                    xytext=(xloc*3/3.5, ymax-0.2*dy),
                    fontsize=16)
        ax1.annotate(a_str, 
                    xy=(xloc, ymax-0.3*dy), 
                    xytext=(xloc, ymax-0.3*dy),
                    fontsize=16)
        ax1.annotate(alph_str, 
                    xy=(xloc, ymax-0.4*dy), 
                    xytext=(xloc, ymax-0.4*dy),
                    fontsize=16)
        ax1.annotate(b_str, 
                    xy=(xloc, ymax-0.5*dy), 
                    xytext=(xloc, ymax-0.5*dy),
                    fontsize=16)
        ax1.set_ylabel("Coincidence rate (s^-1)")

        # Computing residuals and plot in bottom subplot
        # self.residuals = self.counts[self.fit_index] - self.pred
        self.residuals = ((self.pred - self.counts[self.fit_index]) / self.counts[self.fit_index]) * 100
        # residuals_norm = self.residuals / np.max(np.abs(self.residuals))

        index = (self.bin_centers >= xfit[0]) & (self.bin_centers <= xfit[-1])

        ax2.scatter(self.bin_centers[index], self.residuals, **self.residual_options)
        ax2.axhline(y=0, color='#162F65', linestyle='--')
        ax2.set_xlabel("Time Differences(ns)")
        ax2.set_ylabel('Percent difference (%)')

        # Setting title for entire figure
        fig.suptitle('Fit Using ' + self.timeDifMethod, fontsize=14)

        # Adjusting layout and saving figure (optional)
        if self.save_fig and (not folder or verbose):
            fig.tight_layout()
            save_filename = os.path.join(self.save_dir, 'fit_and_res_' + input + '_' + method.replace(' ','_') + '_' + str(self.fit_range[0]) + '-' + str(self.fit_range[1]) + '.png')
            fig.savefig(save_filename, dpi=300, bbox_inches='tight')

        # Showing plot (optional)
        if show_plot and (not folder or verbose):
            plt.show()
        plt.close()
        return popt

#--------------------------------------------------------------------------------

class Fit_With_Weighting:
    def __init__(self,RA_hist_totals, begin, end, saveDir: str, fitting_opts: dict, residual_opts: dict):

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
        self.bin_centers = RA_hist_totals[1]
        self.uncertainties = RA_hist_totals[2]
        self.fit_range = [begin, end]
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
        self.fit_index = np.where((self.bin_centers >= self.fit_range[0]) &
                             (self.bin_centers <= self.fit_range[1]))

        xfit = self.bin_centers[self.fit_index]
        
        # Fitting distribution
        # Fitting the data using curve_fit
        exp_decay_fit_bounds = ([0,-np.inf],[np.inf,0])
        a0 = np.max(self.hist)
        c0 = np.mean(self.hist[-int(self.num_bins*0.05):])
        b0 = ((np.log(c0 if c0 != 0 else 1e-10)-np.log(self.hist[0]))/
            (self.bin_centers[-1]-self.bin_centers[0]))
        yfit = self.hist[self.fit_index] - c0
        exp_decay_p0 = [a0, b0]
        popt, pcov = curve_fit(exp_decay_2_param, xfit, yfit, bounds=exp_decay_fit_bounds, 
                               p0=exp_decay_p0,maxfev=1e6,sigma=self.uncertainties[self.fit_index], 
                               absolute_sigma=True)
        

        # Printing out optimization parameters
        self.a = popt[0]
        self.alpha = popt[1]
        self.b = c0
        #print('Fit parameters: A =', popt[0], ', alpha =', popt[1], ', B =', c0)

        self.pred = exp_decay_3_param(xfit, *popt, c0)
        
        #cerr = np.std(self.hist[-int(self.num_bins*0.05):], axis=0, ddof=1)
        
        self.perr = np.sqrt(np.diag(pcov))
        
        self.xfit = xfit

       
    def plot_RA_and_fit(self, save_fig: bool, show_plot: bool, errorBars: str, input: str, method:str = 'aa'):

        '''
        Description:
            - Plotting the sum of histograms generated.
            - Saving and showing the plot can be turned on or off.

        Inputs:
            - self (encompasses all private variables)

        Outputs: 
            - None
        '''
        
        fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True, figsize=(8, 6), gridspec_kw={'height_ratios': [2, 1]})
        
        # Creating a scatter plot with the data
        ax1.scatter(self.bin_centers, self.hist, **self.residual_options)
        
        if errorBars == "bar":
            ax1.errorbar(self.bin_centers, self.hist, yerr=self.uncertainties, fmt='o', ecolor='black',capsize=5)
        #ax.fill_between(time_diff_centers, self.hist[:-1] - self.uncertainties[:-1], self.hist[:-1] + self.uncertainties[:-1], alpha=0.3, color='gray')
        elif errorBars == "band":
            lower_bound = self.hist - self.uncertainties
            upper_bound = self.hist + self.uncertainties
            ax1.fill_between(self.bin_centers, lower_bound, upper_bound, alpha=0.3, color='gray')

        # Adding the fit to the data
        ax1.plot(self.xfit, self.pred, **self.fitting_options)

        equation = r'$Ae^{\alpha}+B$:'
        alph_str = (r'$\alpha$ = (' + f'{self.alpha / 1e9:.3g}' + '$\pm$ ' + f'{self.perr[1] / 1e9:.3g}' + ') 1/s')
        a_str = (r'$A$ = (' + f'{self.a:.3g}' + '$\pm$ ' + f'{self.perr[0]:.3g}' + ') counts')
        b_str = r'$B$ = ' + f'{self.b:.3g} counts'
        ymin, ymax = ax1.get_ylim()
        xmin, xmax = ax1.get_xlim()
        xloc = (xmin+xmax)/3
        dy = ymax-ymin
        ax1.annotate(equation, 
                    xy=(xloc*3/3.5, ymax-0.2*dy), 
                    xytext=(xloc*3/3.5, ymax-0.2*dy),
                    fontsize=16)
        ax1.annotate(a_str, 
                    xy=(xloc, ymax-0.3*dy), 
                    xytext=(xloc, ymax-0.3*dy),
                    fontsize=16)
        ax1.annotate(alph_str, 
                    xy=(xloc, ymax-0.4*dy), 
                    xytext=(xloc, ymax-0.4*dy),
                    fontsize=16)
        ax1.annotate(b_str, 
                    xy=(xloc, ymax-0.5*dy), 
                    xytext=(xloc, ymax-0.5*dy),
                    fontsize=16)

        # Setting the axis labels
        ax1.set_xlabel('Time difference (ns)')
        ax1.set_ylabel('Counts')
        ax1.set_title('Weighted Fit Using ' + method)

        # Computing residuals and plot in bottom subplot
        # residuals = self.hist[self.fit_index] - self.pred
        self.residuals = ((self.pred - self.hist[self.fit_index]) / self.hist[self.fit_index]) * 100
        # residuals_norm = residuals / np.max(np.abs(residuals))

        ax2.scatter(self.bin_centers[self.fit_index], self.residuals, **self.residual_options)
        ax2.axhline(y=0, color='#162F65', linestyle='--')
        ax2.set_xlabel('Time difference (ns)')
        ax2.set_ylabel('Percent difference (%)')

        # Adjusting layout and saving figure (optional)
        if save_fig:
            fig.tight_layout()
            save_filename = os.path.join(self.save_dir, 'weighted_fit_and_res_' + input + '_' + method.replace(' ','_') + '_' + str(self.fit_range[0]) + '-' + str(self.fit_range[1]) + '.png') 
            fig.savefig(save_filename, dpi=300, bbox_inches='tight')
        
        # Displaying the plot (optional)
        if show_plot:
            plt.show()
        plt.close()