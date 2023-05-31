import numpy as np
import matplotlib.pyplot as plt
import os

class RossiHistogram:
    def __init__(self, reset_time, bin_width, plot_opts, save_dir= None):

        self.options = plot_opts
        self.save_dir = save_dir

        self.reset_time = reset_time
        self.bin_width = bin_width
        self.x_axis = "Time Differences"
        self.y_axis = "Count"
        self.title = "Histogram"
        
        self.counts, self.bin_edges, self.bin_centers = None, None, None

    def plot(self, time_diffs, save_fig, show_plot):

        num_bins = int(self.reset_time / self.bin_width)

        counts, bin_edges = np.histogram(time_diffs, bins=num_bins, range=[0, self.reset_time])

        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])

        plt.bar(bin_centers, counts, width=0.8 * (bin_centers[1] - bin_centers[0]), alpha=0.6, fill=True, **self.options)

        plt.xlabel(self.x_axis)
        plt.ylabel(self.y_axis)
        plt.title(self.title)

        if save_fig:
            plt.tight_layout()
            save_filename = os.path.join(self.save_dir, 'histogram.png')
            plt.savefig(save_filename, dpi=300, bbox_inches='tight')

        if show_plot:
            plt.show()

        self.counts = counts
        self.bin_centers = bin_centers
        self.bin_edges = bin_edges

        return counts, bin_centers, bin_edges