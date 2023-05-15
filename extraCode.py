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

def exp_decay_3_param(x, a, b, c):
    return a * np.exp(b * x) + c

def exp_decay_2_param(x, a, b):
    return a * np.exp(b * x)

#--------------------------------------------------------------------------------

def fit_RA_hist(RA_hist, Rossi_alpha_settings):
    
    num_bins = np.size(RA_hist[0])
    time_diff_centers = RA_hist[1][1:] - np.diff(RA_hist[1][:2])/2
    
    # Choose region to fit
    fit_index = ((time_diff_centers > Rossi_alpha_settings['minimum cutoff']) & 
                 (time_diff_centers >= Rossi_alpha_settings['fit range'][0]) & 
                 (time_diff_centers <= Rossi_alpha_settings['fit range'][1]))
    
    xfit = time_diff_centers[fit_index]
    
    # Fit distribution
    # Fit the data using curve_fit
    # exp_decay_fit_bounds = ([0,-np.inf,0],[np.inf,0,np.inf])
    exp_decay_fit_bounds = ([0,-np.inf],[np.inf,0])
    a0 = np.max(RA_hist[0])
    c0 = np.mean(RA_hist[0][-int(num_bins*0.05):])
    b0 = ((np.log(c0) - np.log(RA_hist[0][0] + 1e-9)) /
      (time_diff_centers[-1] - time_diff_centers[0]))
    # b0 = ((np.log(c0)-np.log(RA_hist[0][0]))/
          # (time_diff_centers[-1]-time_diff_centers[0]))
    yfit = RA_hist[0][fit_index] - c0
    # exp_decay_p0 = [a0, b0, c0]
    exp_decay_p0 = a0, a0

    popt, pcov = curve_fit(exp_decay_2_param, xfit, yfit,
                           bounds=exp_decay_fit_bounds, maxfev=1e6)
    
    yfit = exp_decay_3_param(xfit, *popt, c0)
    
    popt = np.hstack((popt, c0))
    
    return [time_diff_centers, popt, pcov, xfit, yfit]

#--------------------------------------------------------------------------------

def fit_RA_hist_weighting(RA_hist,Rossi_alpha_settings):
    
    num_bins = np.size(RA_hist[0])
    time_diff_centers = RA_hist[1]
    
    # Calculate weighting with relative variance
    uncertainties = RA_hist[2]
    
    # Choose region to fit
    fit_index = ((time_diff_centers > Rossi_alpha_settings['minimum cutoff']) & 
                 (time_diff_centers >= Rossi_alpha_settings['fit range'][0]) & 
                 (time_diff_centers <= Rossi_alpha_settings['fit range'][1]))
    
    xfit = time_diff_centers[fit_index]
    
    # Fit distribution
    # Fit the data using curve_fit
    # exp_decay_fit_bounds = ([0,-np.inf,0],[np.inf,0,np.inf])
    exp_decay_fit_bounds = ([0,-np.inf],[np.inf,0])

    a0 = np.max(RA_hist[0])
    c0 = np.mean(RA_hist[0][-int(num_bins*0.05):])
    b0 = ((np.log(c0)-np.log(RA_hist[0][0]))/
          (time_diff_centers[-1]-time_diff_centers[0]))
    
    yfit = RA_hist[0][fit_index] - c0
    # exp_decay_p0 = [a0, b0, c0]
    exp_decay_p0 = [a0, b0]
    popt, pcov = curve_fit(exp_decay_2_param, xfit, yfit, bounds=exp_decay_fit_bounds, p0=exp_decay_p0,
                           maxfev=1e6, sigma=uncertainties[fit_index], absolute_sigma=True)
    
    yfit = exp_decay_3_param(xfit, *popt, c0)
    
    popt = np.hstack((popt, c0))
    
    cerr = np.std(RA_hist[0][-int(num_bins*0.05):], axis=0, ddof=1)
    
    perr = np.sqrt(np.diag(pcov))
    
    perr = np.hstack((perr, cerr))
    
    return [time_diff_centers, popt, pcov, perr, xfit, yfit]

#--------------------------------------------------------------------------------

def make_RA_hist_and_fit(time_diffs, Rossi_alpha_settings):
    
    num_bins = int(Rossi_alpha_settings['reset time'] / Rossi_alpha_settings['bin width'])
    
    RA_hist = np.histogram(time_diffs,bins=num_bins, range=[0,Rossi_alpha_settings['reset time']])
    
    [time_diff_centers, popt, pcov, xfit, yfit] = \
        fit_RA_hist(RA_hist,Rossi_alpha_settings)
    
    return [RA_hist, popt, pcov, xfit, yfit]

#--------------------------------------------------------------------------------

def plot_RA_and_fit(RA_hist, xfit, yfit, Rossi_alpha_settings, x_label='Time difference (ns)', y_label='Counts'):
    
    time_diff_centers = RA_hist[1][1:] - np.diff(RA_hist[1][:2])/2
    
    fig2, ax2 = plt.subplots()
    
    # Create a scatter plot with the data
    ax2.scatter(time_diff_centers, RA_hist[0])
    
    # Add the fit to the data
    ax2.plot(xfit, yfit, 'r-', label='Fit')
    
    # Set the axis labels
    ax2.set_xlabel(x_label)
    ax2.set_ylabel(y_label)
    ax2.set_yscale(Rossi_alpha_settings['plot scale'])
    
    # Display the plot
    plt.show()
    
    return

#--------------------------------------------------------------------------------

def plot_RA_and_fit_errorbar(RA_hist, xfit, yfit, Rossi_alpha_settings, xlabel1='Time difference (ns)', ylabel1='Count rate (s$^{-1}$)',
                             xlabel2='Time difference (ns)', ylabel2='Residual count rate (s$^{-1}$)'):
    
    time_diff_centers = RA_hist[1]
    
    meas_time = Rossi_alpha_settings['meas time']
    
    fig1, ax1 = plt.subplots()
    
    # Create a errorbar plot with the data
    ax1.errorbar(
        time_diff_centers, RA_hist[0]/meas_time, yerr=RA_hist[2]/meas_time, 
        fmt='o', markersize=5, capsize=3)
    
    # Add the fit to the data
    ax1.plot(xfit, yfit/meas_time, 
             'r--', label='Fit')
    
    # Set the axis labels
    ax1.set_xlabel(xlabel1)
    ax1.set_ylabel(ylabel1)
    ax1.set_yscale(Rossi_alpha_settings['plot scale'])
    
    # Display the plot
    plt.show()
    
    fig2, ax2 = plt.subplots()
    
    # Create a residuals plot with the data and fit
    index = (time_diff_centers >= xfit[0]) & (time_diff_centers <= xfit[-1])
    residuals = RA_hist[0][index]-yfit
    ax2.errorbar(time_diff_centers[index], residuals/meas_time, 
                 yerr=RA_hist[2][index]/meas_time, fmt='o', markersize=5, capsize=3)
    ax2.axhline(y=0, linestyle='--', color='gray')
    
    # Set the axis labels
    ax2.set_xlabel(xlabel2)
    ax2.set_ylabel(ylabel2)
    ax2.set_yscale('linear')
    
    # Display the plot
    plt.show()
    
    return
