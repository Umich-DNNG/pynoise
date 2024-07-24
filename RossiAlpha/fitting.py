import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os

from . import rossiAlpha as ra
import hdf5
plt.ioff()

def createBestFit(fit:dict, hist:dict, settings: dict, settingsPath: str):
    '''Create a Rossi Histogram line of best fit and residual plot for file analysis.

    Inputs:
    - fit: dictionary from the calling class to add fit data to
    - hist: dictionary from the calling class containing histogram data
    - settings: dictionary holding the runtime settings
    - settingsPath: string path to the settings file'''

    setupFit(fit, settings)

    # for each histogram data set to be fitted
    for i in range(0, ra.getNumSets(settings)):
        # figure out the time difference method used
        if isinstance(settings['RossiAlpha Settings']['Time difference method'], list):
            method = settings['RossiAlpha Settings']['Time difference method'][i]
        else:
            method = settings['RossiAlpha Settings']['Time difference method']
        # create a fit graph for each fit min/max pair
        for j in range(0, len(fit['Fit minimum'])):
            fit['Best fit'].append(RossiHistogramFit(hist['Histogram'][i].counts,
                                                hist['Histogram'][i].bin_centers,
                                                method,
                                                fit['Fit minimum'][j],
                                                fit['Fit maximum'][j]))
            # craft the output name
            output = settings['Input/Output Settings']['Input file/folder']
            output = output[output.rfind('/')+1:]
            output = output + '_' + method + '_' + str(settings['RossiAlpha Settings']['Bin width']) + '_' + str(settings['RossiAlpha Settings']['Reset time'])
            # plot the fit graph using the current settings
            fit['Best fit'][i].fit_and_residual(settings['Input/Output Settings']['Save figures'],
                                                settings['Input/Output Settings']['Save directory'],
                                                settings['General Settings']['Show plots'],
                                                settings['Line Fitting Settings'],
                                                settings['Scatter Plot Settings'],
                                                settings['Histogram Visual Settings'],
                                                output,
                                                method,
                                                False,
                                                settings['General Settings']['Verbose iterations'])
            plt.close()
            if settings['Input/Output Settings']['Save outputs']:
                array = np.array([hist['Histogram'][i].bin_centers, hist['Histogram'][i].counts]).T
                array = [array, fit['Best fit'][-1].pred, fit['Best fit'][-1].residuals]
                hdf5.writeHDF5Data(array,
                                   ['plot values', 'fit count', 'perr'],
                                   ['RossiAlpha', 'fit', 'total', f"{fit['Fit minimum'][i]}-{fit['Fit maximum'][i]}", 'plot'],
                                   settings,
                                   'pynoise',
                                   settingsPath)
                array2 = [fit['Best fit'][-1].a, fit['Best fit'][-1].perr[0], fit['Best fit'][-1].alpha, fit['Best fit'][-1].perr[1], fit['Best fit'][-1].b]
                hdf5.writeHDF5Data(array2,
                                   ['A', 'A uncertainty', 'alpha', 'alpha uncertainty', 'B'],
                                   ['RossiAlpha', 'fit', 'total', f"{fit['Fit minimum'][i]}-{fit['Fit maximum'][i]}", 'function'],
                                   settings,
                                   'pynoise',
                                   settingsPath)


def folderFit(fit: dict, hist: dict, settings: dict, settingsPath: str, numFolders: int):
    '''Create a Rossi Histogram line of best fit and residual plot for folder analysis.

    Inputs:
    - fit: dictionary from the calling class to add fit data to
    - hist: dictionary from the calling class containing histogram data
    - settings: dictionary holding the runtime settings
    - settingsPath: string path to the settings file
    - numFolder: number of subfolders'''
    total = []
    setupFit(fit, settings)
    # for verbose iterations only, create a fit graph for each subfolder
    if settings['General Settings']['Verbose iterations']:
        subfolderFit(fit, hist, settings, settingsPath, numFolders)

    name = settings['Input/Output Settings']['Input file/folder']
    name = name[name.rfind('/')+1:]

    # for each histogram data set to be fitted
    for i in range(0, len(hist['Histogram'])):
        # figure out the time difference method used
        if isinstance(settings['RossiAlpha Settings']['Time difference method'], list):
            method = settings['RossiAlpha Settings']['Time difference method'][i]
        else:
            method = settings['RossiAlpha Settings']['Time difference method']

        # Create a fit object for the total histogram(s) for the ranges.
        total.append(np.vstack((hist['Histogram'][i].counts, hist['Histogram'][i].bin_centers, hist['Uncertainty'][i])))
        for j in range(len(fit['Fit minimum'])):
            fit['Best fit'].append(Fit_With_Weighting(total[i],
                                                    fit['Fit minimum'][j],
                                                    fit['Fit maximum'][j],
                                                    settings['Input/Output Settings']['Save directory'],
                                                    settings['Line Fitting Settings'], 
                                                    settings['Scatter Plot Settings']))
            # Fit the total histogram with weighting.
            fit['Best fit'][-1].fit_RA_hist_weighting()
            # Plot the total histogram fit.
            suffix = name + '_' + method + '_' + str(settings['RossiAlpha Settings']['Bin width']) + '_' + str(settings['RossiAlpha Settings']['Reset time'])
            fit['Best fit'][-1].plot_RA_and_fit(settings['Input/Output Settings']['Save figures'], 
                                            settings['General Settings']['Show plots'],
                                            settings['RossiAlpha Settings']['Error Bar/Band'],
                                            suffix,
                                            method)
            plt.close()
            # save data to hdf5 if desired
            if settings['Input/Output Settings']['Save outputs']:
                array = np.array([hist['Histogram'][i].bin_centers, hist['Histogram'][i].counts, hist['Uncertainty'][i]]).T
                array = [array, fit['Best fit'][-1].pred, fit['Best fit'][-1].residuals]
                hdf5.writeHDF5Data(array,
                                   ['plot values', 'fit count', 'perr'],
                                   ['RossiAlpha', 'fit', 'total', f"{fit['Fit minimum'][i]}-{fit['Fit maximum'][i]}", 'plot'],
                                   settings,
                                   'pynoise',
                                   settingsPath)
                array2 = [fit['Best fit'][-1].a, fit['Best fit'][-1].perr[0], fit['Best fit'][-1].alpha, fit['Best fit'][-1].perr[1], fit['Best fit'][-1].b]
                hdf5.writeHDF5Data(array2,
                                   ['A', 'A uncertainty', 'alpha', 'alpha uncertainty', 'B'],
                                   ['RossiAlpha', 'fit', 'total', f"{fit['Fit minimum'][i]}-{fit['Fit maximum'][i]}", 'function'],
                                   settings,
                                   'pynoise',
                                   settingsPath)


# ---------- helper functions for the main fit functions -------------------


def subfolderFit(fit:dict, hist: dict, settings: dict, settingsPath: str, numFolders: int):
    '''
    Create fit plots for subfolders in a folder analysis

    Inputs:
    - fit: dictionary from the calling class to add fit data to
    - hist: dictionary from the calling class containing histogram data
    - settings: dictionary holding the runtime settings
    - settingsPath: string path to the settings file
    - numFolder: number of subfolders    
    '''
    if isinstance(settings['RossiAlpha Settings']['Time difference method'], list):
        method = settings['RossiAlpha Settings']['Time difference method'][0]
    else:
        method = settings['RossiAlpha Settings']['Time difference method']
    for folder in range(numFolders):
        for i in range(len(fit['Fit minimum'])):
            subfolder = RossiHistogramFit(hist['Subplots'][folder].counts,
                                          hist['Subplots'][folder].bin_centers,
                                          method,
                                          fit['Fit minimum'][i],
                                          fit['Fit maximum'][i])
            # craft the output name
            output =  settings['Input/Output Settings']['Input file/folder']
            output = output + f'/{folder + 1}'
            output = output[output[:output.rfind('/')].rfind('/')+1:].replace('/','-')
            output = output + '_' + method + '_' + str(settings['RossiAlpha Settings']['Bin width']) + '_' + str(settings['RossiAlpha Settings']['Reset time'])
            subfolder.fit_and_residual(settings['Input/Output Settings']['Save figures'],
                                                settings['Input/Output Settings']['Save directory'],
                                                settings['General Settings']['Show plots'],
                                                settings['Line Fitting Settings'],
                                                settings['Scatter Plot Settings'],
                                                settings['Histogram Visual Settings'],
                                                output,
                                                method,
                                                True,
                                                settings['General Settings']['Verbose iterations'])
            if settings['Input/Output Settings']['Save outputs']:
                array = np.array([hist['Subplots'][folder].bin_centers, hist['Subplots'][folder].counts]).T
                array = [array, subfolder.pred, subfolder.residuals]
                hdf5.writeHDF5Data(array,
                                   ['plot values', 'fit count', 'perr'],
                                   ['RossiAlpha', 'fit', str(folder + 1), f"{fit['Fit minimum'][i]}-{fit['Fit maximum'][i]}", 'plot'],
                                   settings,
                                   'pynoise',
                                   settingsPath)

                array2 = [subfolder.a, subfolder.perr[0], subfolder.alpha, subfolder.perr[1], subfolder.b]
                hdf5.writeHDF5Data(array2,
                                   ['A', 'A uncertainty', 'alpha', 'alpha uncertainty', 'B'],
                                   ['RossiAlpha', 'fit', str(folder + 1), f"{fit['Fit minimum'][i]}-{fit['Fit maximum'][i]}", 'function'],
                                   settings,
                                   'pynoise',
                                   settingsPath)
            plt.close()


def setupFit(fit: dict, settings: dict):
    '''
    Initalize the fit dictionary for analysis

    Inputs:
    - fit: dictionary from the calling class to add fit data to
    - settings: dictionary holding the runtime settings
    '''
    fit['Best fit'].clear()
    fit['Fit minimum'].clear()
    fit['Fit maximum'].clear()
    # determine all fit maximums for the plots
    if isinstance(settings['RossiAlpha Settings']['Fit maximum'],list):
        for i in range(0,len(settings['RossiAlpha Settings']['Fit maximum'])):
            if settings['RossiAlpha Settings']['Fit maximum'][i] == None:
                fit['Fit maximum'].append(settings['RossiAlpha Settings']['Reset time'])
            else:
                fit['Fit maximum'].append(settings['RossiAlpha Settings']['Fit maximum'][i])
    else:
        if settings['RossiAlpha Settings']['Fit maximum'] == None:
            fit['Fit maximum'].append(settings['RossiAlpha Settings']['Reset time'])
        else:
            fit['Fit maximum'].append(settings['RossiAlpha Settings']['Fit maximum'])
    # determine all fit minimums for the plots
    if isinstance(settings['RossiAlpha Settings']['Fit minimum'],list):
        for i in range(0,len(settings['RossiAlpha Settings']['Fit minimum'])):
            fit['Fit minimum'].append(settings['RossiAlpha Settings']['Fit minimum'][i])
    else:
        fit['Fit minimum'].append(settings['RossiAlpha Settings']['Fit minimum'])


# --------- helper functions for the rossi alpha fit class -----------


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


#---------------------- class for rossi alpha fit -------------------------------    


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
        # exp_decay_fit_bounds = ([0,-np.inf],[np.inf,0])
        exp_decay_fit_bounds = ([np.inf,0], [0,-np.inf])
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
                         outputName: str, 
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

        # temp solution so it doesnt crash in cases of a c0 of 0 (leading to b0 of -inf, which breaks curve_fit)
        if b0 == np.inf or b0== -np.inf:
            b0 = -1

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
        alph_str = (r'$\alpha$ = (' + f'{self.alpha * 1e9:.3g}' + '$\pm$ ' + f'{self.perr[1] * 1e9:.3g}' + ') 1/s')
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
            save_filename = 'fit_and_res_' + outputName + '_' + str(self.fit_range[0]) + '-' + str(self.fit_range[1]) + '.png'
            save_filename = os.path.join(self.save_dir, save_filename)
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

        print("xfit:", xfit)
        print("yfit:", yfit)

        popt, pcov = curve_fit(exp_decay_2_param, xfit, yfit, bounds=exp_decay_fit_bounds, 
                               p0=exp_decay_p0,maxfev=1e6,sigma=self.uncertainties[self.fit_index], 
                               absolute_sigma=True)
        
        print("Optimal parameters:", popt)
        print("Covariance matrix:", pcov)
        

        # Printing out optimization parameters
        self.a = popt[0]
        self.alpha = popt[1]
        self.b = c0
        #print('Fit parameters: A =', popt[0], ', alpha =', popt[1], ', B =', c0)

        self.pred = exp_decay_3_param(xfit, *popt, c0)
        
        #cerr = np.std(self.hist[-int(self.num_bins*0.05):], axis=0, ddof=1)
        
        self.perr = np.sqrt(np.diag(pcov))
        
        self.xfit = xfit


    def plot_RA_and_fit(self, save_fig: bool, show_plot: bool, errorBars: str, pngSuffix: str, method:str = 'aa'):

        '''
        Description:
            - Plotting the sum of histograms generated.
            - Saving and showing the plot can be turned on or off.

        Inputs:
            - self (encompasses all private variables)
            - save_fig: bool indicating if the figure image should be saved or not
            - show_fig: bool indicating if the figure image should be shown or not
            - errorBars: setting for the error bars, ie "bar" or "band"
            - pngSuffix: str suffix for the png file name
            - method: time difference method used for the analysis

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
        alph_str = (r'$\alpha$ = (' + f'{self.alpha * 1e9:.3g}' + '$\pm$ ' + f'{self.perr[1] * 1e9:.3g}' + ') 1/s')
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
            save_filename = os.path.join(self.save_dir, 'weighted_fit_and_res_' + pngSuffix + '_' + str(self.fit_range[0]) + '-' + str(self.fit_range[1]) + '.png') 
            fig.savefig(save_filename, dpi=300, bbox_inches='tight')
        
        # Displaying the plot (optional)
        if show_plot:
            plt.show()
        plt.close()