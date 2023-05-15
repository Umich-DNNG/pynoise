import numpy as np  # For processing data
import matplotlib.pyplot as plt  # For plotting data summaries
from matplotlib.colors import LogNorm  # For adjusting colorbar scale
import copy


# --------------------------------------------------------------------------------
# OWN CODE BELOW
# --------------------------------------------------------------------------------
class Plot:
    def __init__(self, plotSettings, plotOptions):
        self.reset_time = plotSettings["reset time"]
        self.bin_width = plotSettings["bin width"]
        self.options = plotOptions
        self.x_axis = "Time Differences"
        self.y_axis = "Count"
        self.title = "Histogram"

    def plot(self, time_diffs):
        # calculating number of bins for histogram plot
        num_bins = int(self.reset_time / self.bin_width)

        # generating histogram
        counts, bin_edges = np.histogram(
            time_diffs, bins=num_bins, range=[0, self.reset_time]
        )

        # adjusting the bin centers
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])

        # plotting
        plt.plot(bin_centers, counts, drawstyle='steps-post', **self.options)
        plt.bar(
            bin_centers,
            counts,
            width=0.8 * (bin_centers[1] - bin_centers[0]),
            alpha=0.6,
            color="b",
            align="center",
            edgecolor="k",
            linewidth=0.5,
            fill=True,
        )
        plt.xlabel(self.x_axis)
        plt.ylabel(self.y_axis)
        plt.title(self.title)

        # saving plot
        # plt.savefig('test2', dpi=300, bbox_inches='tight')

        return counts, bin_centers
