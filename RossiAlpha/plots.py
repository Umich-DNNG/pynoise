import numpy as np  # For processing data
import matplotlib.pyplot as plt  # For plotting data summaries
from matplotlib.colors import LogNorm  # For adjusting colorbar scale
import copy

# --------------------------------------------------------------------------------
# OWN CODE BELOW
# --------------------------------------------------------------------------------
class RossiHistogram:
    def __init__(self, plotSettings, plotOptions, show_plot):

        '''
        Creating the a Plot() object and its variables.

        Inputs:
            - plotSettings (setting for the plotting)
            - plotOptions (style setting for different plotting options)
            - show_plot (boolean to show or not to show plots)

        Outputs: 
            - Plot() object
        '''

        # Plotting options
        self.show_plot = show_plot
        self.options = plotOptions

        # Required parameters
        self.reset_time = plotSettings["reset time"]
        self.bin_width = plotSettings["bin width"]
        self.x_axis = "Time Differences"
        self.y_axis = "Count"
        self.title = "Histogram"
        
        #Parameters set once plot(time_diffs) is called
        self.counts = None
        self.bin_edges = None
        self.bin_centers = None

    def plot(self, time_diffs, save_every_fig):

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

        # Calculating the number of bins
        num_bins = int(self.reset_time / self.bin_width)

        # Generating histogram
        counts, bin_edges = np.histogram(time_diffs, bins=num_bins, range=[0, self.reset_time])

        # Adjusting the bin centers
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])

        # Plotting
        plt.plot(bin_centers, counts, drawstyle='steps-post', **self.options)
        plt.bar(bin_centers, counts,
                width=0.8 * (bin_centers[1] - bin_centers[0]),
                alpha=0.6,
                color="b",
                align="center",
                edgecolor="k",
                linewidth=0.5,
                fill=True)
        
        plt.xlabel(self.x_axis)
        plt.ylabel(self.y_axis)
        plt.title(self.title)

        # Showing plot (optional)
        if self.show_plot == True:
            plt.show()

        # Saving plot (optional)
        if save_every_fig == True:
            plt.savefig('histogram', dpi=300, bbox_inches='tight')

        #Set the counts, bin_centers, and bin_edges of the object
        self.counts = counts
        self.bin_centers = bin_centers
        self.bin_edges = bin_edges

        return counts, bin_centers, bin_edges