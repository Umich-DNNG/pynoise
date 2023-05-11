import numpy as np                    # For processing data
import matplotlib.pyplot as plt       # For plotting data summaries
from matplotlib.colors import LogNorm # For adjusting colorbar scale
import copy

#--------------------------------------------------------------------------------

def plot_PSD(list_data, nbins=1000, x_label='Light yield (keVee)', y_label='Tail over Total'):

    # generate grey colormap 
    cmap = plt.cm.get_cmap('Greys')
    
    plt.subplots(dpi=400)
    
    energy = (list_data[:,1]*478/1.6)
    x, y = [0, 2000], [0, 0.6]

    psd = list_data[:,2]/list_data[:,1]
        
    plt.hist2d(energy, psd, bins=nbins, 
               range=[x,y], 
               norm=LogNorm(),
               cmap=cmap)
    
    # create a 2D histogram
    h, xedges, yedges = np.histogram2d(energy, psd, bins=nbins, range=[x,y])
    
    # get the maximum value of the histogram
    dim_3_max = np.amax(h)
                
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    
    cbar = plt.colorbar()
    cbar.ax.set_title(r'Counts')
    plt.show()
    
    return dim_3_max

#--------------------------------------------------------------------------------

def plot_n_g_colors_PSD(list_data_n,list_data_g,dim_3_max, x_label='Light yield (keVee)', y_label='Tail over Total'):
    
    ToTs_n = list_data_n[:,2]/list_data_n[:,1]
    ToTs_g = list_data_g[:,2]/list_data_g[:,1]
    
    LOs_calib_n = list_data_n[:,1]*478*1.6
    LOs_calib_g = list_data_g[:,1]*478*1.6
    
    xbins = np.linspace(0,1600,801)
    ybins = np.linspace(0,0.6,1001)
    
    my_cmap = copy.copy(plt.cm.get_cmap('Blues'))
    # my_cmap.set_bad(color='black')
    my_cmap_2 = copy.copy(plt.cm.get_cmap('Reds'))
    # my_cmap_2.set_bad(color='black')
    plt.subplots(dpi= 400)

    hist_n = plt.hist2d(LOs_calib_n, ToTs_n, bins=(xbins,ybins), 
                        range=[[0, 1600],[0.0, 0.6]], 
                        norm=LogNorm(vmax=dim_3_max), 
                        cmap =my_cmap, label='n')
    
    hist_g = plt.hist2d(LOs_calib_g, ToTs_g, bins=(xbins,ybins), 
                        range=[[0, 1600],[0.0, 0.6]], 
                        norm=LogNorm(vmax=dim_3_max), 
                        cmap =my_cmap_2, label=r'$\gamma$')
    
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    cbar_n = plt.colorbar(hist_n[3])
    cbar_g = plt.colorbar(hist_g[3])
    cbar_n.ax.set_title(r'n')
    cbar_g.ax.set_title(r'$\gamma$')
    plt.show()
    
    return

#--------------------------------------------------------------------------------

def plot_n_g_colors_PSD_discrim(list_data, ToT, x_label='Light yield (keVee)', y_label='Tail over Total'):
    
    ToTs = list_data[:,2]/list_data[:,1]
    
    ind_n, ind_g = ToTs > ToT, ToTs <= ToT
    
    list_data_n, list_data_g = list_data[ind_n], list_data[ind_g]
    
    ToTs_n = list_data_n[:,2]/list_data_n[:,1]
    ToTs_g = list_data_g[:,2]/list_data_g[:,1]
    
    LOs_calib_n = list_data_n[:,1]*478*1.6
    LOs_calib_g = list_data_g[:,1]*478*1.6
    
    my_cmap = copy.copy(plt.cm.get_cmap('Blues'))
    my_cmap.set_bad(color='white')
    my_cmap_2 = copy.copy(plt.cm.get_cmap('Reds'))
    # my_cmap_2.set_bad(color='black')
    fig, ax = plt.subplots(dpi= 400)
    hist_n = plt.hist2d(LOs_calib_n, ToTs_n, bins=200, 
                        range=[[0, 2000],[0.0, 0.6]], norm=LogNorm(), 
                        cmap =my_cmap, label='n')
    hist_g = plt.hist2d(LOs_calib_g, ToTs_g, bins=200, 
                        range=[[0, 2000],[0.0, 0.6]], norm=LogNorm(), 
                        cmap =my_cmap_2, label=r'$\gamma$')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    cbar_n = plt.colorbar(hist_n[3])
    cbar_g = plt.colorbar(hist_g[3])
    cbar_n.ax.set_title(r'n')
    cbar_g.ax.set_title(r'$\gamma$')

    plt.show()
    
    return

#--------------------------------------------------------------------------------
# OWN CODE BELOW
#--------------------------------------------------------------------------------
class Plot:
    def __init__(self,plotSettings,plotOptions):
        self.reset_time = plotSettings['reset time']
        self.bin_width = plotSettings['bin width']
        self.options = plotOptions
        self.x_axis = "Time Differences"
        self.y_axis = "Count"
        self.title = "Histogram"
    def plot(self, time_diffs):

        # calculating number of bins for histogram plot
        num_bins = int(self.reset_time/self.bin_width)

        # generating histogram
        counts, bin_edges = np.histogram(time_diffs, bins=num_bins, range=[0, self.reset_time])

        # adjusting the bin centers
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])

        # plotting
        # plt.plot(bin_centers, counts, drawstyle='steps-post', **self.options)
        plt.bar(bin_centers, counts, width=0.8*(bin_centers[1]-bin_centers[0]), alpha=0.6, color='b', align='center', edgecolor='k', linewidth=0.5, fill=True)
        plt.xlabel(self.x_axis)
        plt.ylabel(self.y_axis)
        plt.title(self.title)

        # saving plot
        # plt.savefig('test2', dpi=300, bbox_inches='tight')

        return counts, bin_centers