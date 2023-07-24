import numpy as np
import matplotlib.pyplot as plt
import os

plt.ioff()

class RossiHistogram:
    def __init__(self,  time_diffs = None, bin_width: int = None, reset_time: int = None):

        '''
        Description:
            - Creating a Plot() object and its variables.

        Inputs:
            - time_diffs: If Histogram is being constructed from time_differences that still need to be binned, this arg should be provided
            - bin_width: If time_diffs still need to be binned, this arg should be provided
            - reset_time: If time_diffs still need to be binned, this arg should be provided

        Outputs: 
            - Plot() object
        '''
        #Data Variables
        self.time_diffs = time_diffs
        self.reset_time = reset_time
        self.bin_width = bin_width
        # Plotting options
        self.options = None
        self.save_dir = None
        
        # Required parameters
        self.reset_time = reset_time
        self.bin_width = bin_width
        self.x_axis = "Time Differences"
        self.y_axis = "Count"
        self.title = "Histogram"
        
        # Parameters set once plot(time_diffs) is called
        self.counts, self.bin_edges, self.bin_centers = None, None, None

    def plot(self , save_fig: bool = False, show_plot: bool = True, save_dir:str= './',plot_opts: dict = None, folder: bool = False, verbose: bool = False, **kwargs ):
        

        '''
        Creating histogram from an array of time differences and plotting it.
        Saving and showing the plot can be turned on or off.

        Inputs:
            - self (all the private variables in Plot() object)
            - save_fig : True/False to save figure
            - show_plot : True/False to show plot in plot editor
            - save_dir : If save_fig = True, the save_dir must be provided. Default saves in current working directory
            - plot_opts: dictionary of histogram visual settings. 
            -**kwargs: If plot_opts is not inputed, you can input individual plot settings that you want to be applied to the plot 

        Outputs: 
            - counts (The set of values of the histogram as a list)
            - bin_centers (adjusted bin centers for visual plotting)
            - bin_edges (The edges of the bins are mentioned as a parameter)
        '''

        if plot_opts is None:
            plot_opts = {}
        plot_opts.update(kwargs)

        #TODO: Set defaults for the plot_opts if this dict is empty here.
        self.options = plot_opts
        self.save_dir = save_dir

        if (self.reset_time == None) :
            self.reset_time = np.max(self.time_diffs)

        # Calculating the number of bins
        num_bins = int(self.reset_time / self.bin_width)

        # Generating histogram
        counts, bin_edges = np.histogram(self.time_diffs, bins=num_bins, range=[0, self.reset_time])

        # Adjusting the bin centers
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])

        # Saving plot (optional)
        if save_fig and (not folder or verbose):

            # Plotting
            plt.figure()
            plt.bar(bin_centers, counts, width=0.8 * (bin_centers[1] - bin_centers[0]), **self.options)

            plt.xlabel(self.x_axis)
            plt.ylabel(self.y_axis)
            plt.title(self.title)

            plt.tight_layout()
            save_filename = os.path.join(self.save_dir, 'histogram.png')
            plt.savefig(save_filename, dpi=300, bbox_inches='tight')
        
        # Showing plot (optional)
        if show_plot and (not folder or verbose):

            # Plotting
            if not save_fig:
                plt.figure()
            plt.bar(bin_centers, counts, width=0.8 * (bin_centers[1] - bin_centers[0]), **self.options)

            plt.xlabel(self.x_axis)
            plt.ylabel(self.y_axis)
            plt.title(self.title)
            
            plt.show()

        #Set the counts, bin_centers, and bin_edges of the object
        self.counts = counts
        self.bin_centers = bin_centers
        self.bin_edges = bin_edges

        return counts, bin_centers, bin_edges
    
    #This function is to initialize the RossiHistogram if we used the combined time_diffs and hist function
    def initFromHist(self, counts, bin_centers, bin_edges):
        '''Description: Used to initialize the plot object if the data has already been processed/binned.
        
        Inputs: 
            - counts: array of histogram counts
            - bin_centers: bin centers of histogram
            - bin_edges: bin_edges of histogram
            
        Outputs:
        Nothing, but plotFromHist can now be called.'''

        self.counts = counts
        self.bin_centers = bin_centers
        self.bin_edges = bin_edges

    def plotFromHist(self, plot_opts: dict = None, save_fig: bool = False, show_plot: bool = True, save_dir:str= None, folder: bool = False, verbose: bool = False):
        '''Description: Used to plot the histogram when the time differences were calculated simulatenously while being binned. 
        
        Inputs: 
            - plot_opts: dictionary of visual settings to be applied
            - save_fig: True/False to save the figure
            - show_plot: True/False to show figure in plot editor
            - save_dir: Must be provided if save_fig is on.
            
        Outputs:
        Shows a plot/saves a figure if turned on.'''
        
        self.options = plot_opts
        self.save_dir = save_dir
        self.show_plot = show_plot

        
        if save_fig and (not folder or verbose):

            # Plotting
            plt.figure()
            plt.bar(self.bin_centers, self.counts, width=0.8 * (self.bin_centers[1] - self.bin_centers[0]), **self.options)

            plt.xlabel(self.x_axis)
            plt.ylabel(self.y_axis)
            plt.title(self.title)

            plt.tight_layout()
            save_filename = os.path.join(self.save_dir, 'histogram.png')
            plt.savefig(save_filename, dpi=300, bbox_inches='tight')
        
        # Showing plot (optional)
        if show_plot and (not folder or verbose):

            # Plotting
            if not save_fig:
                plt.figure()
            plt.bar(self.bin_centers, self.counts, width=0.8 * (self.bin_centers[1] - self.bin_centers[0]), **self.options)

            plt.xlabel(self.x_axis)
            plt.ylabel(self.y_axis)
            plt.title(self.title)
            
            plt.show()

        
