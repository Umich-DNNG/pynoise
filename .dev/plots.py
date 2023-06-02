import numpy as np
import matplotlib.pyplot as plt
import os

plt.ioff()

class RossiHistogram:
    def __init__(self, reset_time, bin_width, plot_opts, save_dir= None):

        '''
        Description:
            - Creating a Plot() object and its variables.

        Inputs:
            - plotSettings (setting for the plotting)
            - plotOptions (style setting for different plotting options)
            - show_plot (boolean to show or not to show plots)

        Outputs: 
            - Plot() object
        '''

        self.options = plot_opts
        self.save_dir = save_dir

        self.reset_time = reset_time
        self.bin_width = bin_width
        self.x_axis = "Time Differences"
        self.y_axis = "Count"
        self.title = "Histogram"
        
        self.counts, self.bin_edges, self.bin_centers = None, None, None

    def plot(self, time_diffs, save_fig, show_plot):
        '''
        Creating histogram from an array of time differences and plotting it.
        Saving and showing the plot can be turned on or off.

        Inputs:
            - self (all the private variables in Plot() object)
            - time_diffs (array of time differences)

        Outputs: 
            - counts (The set of values of the histogram as a list)
            - bin_centers (adjusted bin centers for visual plotting)
            - bin_edges (The edges of the bins are mentioned as a parameter)
        '''
  
        num_bins = int(self.reset_time / self.bin_width)

        counts, bin_edges = np.histogram(time_diffs, bins=num_bins, range=[0, self.reset_time])

        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])

        if save_fig == True:

            plt.figure()
            plt.bar(bin_centers, counts, width=0.8 * (bin_centers[1] - bin_centers[0]), alpha=0.6, fill=True, **self.options)

            plt.xlabel(self.x_axis)
            plt.ylabel(self.y_axis)
            plt.title(self.title)

            plt.tight_layout()
            save_filename = os.path.join(self.save_dir, 'histogram.png')
            plt.savefig(save_filename, dpi=300, bbox_inches='tight')
        
        if show_plot == True:

            if not save_fig:
                plt.figure()
            plt.bar(bin_centers, counts, width=0.8 * (bin_centers[1] - bin_centers[0]), alpha=0.6, fill=True, **self.options)

            plt.xlabel(self.x_axis)
            plt.ylabel(self.y_axis)
            plt.title(self.title)
            
            plt.show()

        self.counts = counts
        self.bin_centers = bin_centers
        self.bin_edges = bin_edges

        return counts, bin_centers, bin_edges