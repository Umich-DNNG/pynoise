'''Old code within the Cohn Alpha method
Didn't want to delete the code, so placed into here for now
Michael Yang'''

def conduct_CPSD(self,
                show_plot: bool = True,
                save_fig: bool = True,
                save_dir: str = './',
                caSet: dict = {},
                sps: dict = {},
                lfs: dict = {},
                scatter_opt: dict = {}):
    
    # Annotation Parameters
    self.annotate_font_weight = caSet['Annotation Font Weight']
    self.annotate_color = caSet['Annotation Color']
    self.annotate_background_color = caSet['Annotation Background Color']

    # Making count of bins over time histogram
    count_bins = np.diff(self.meas_time_range) / self.dwell_time

    counts_time_hist = np.zeros([2,int(count_bins)])

    index = self.list_data_array[:,0]!=0

    times = self.list_data_array[index, 0]

    N, _ = np.histogram(
                times,
                bins=int(count_bins),
                range=self.meas_time_range
                )
    counts_time_hist[0,:] = N

    list_data_array = np.loadtxt(caSet['Second Input file'])
    index = list_data_array[:,0]!=0

    N, _ = np.histogram(list_data_array,
                        bins=int(count_bins),
                        range=self.meas_time_range)
    
    counts_time_hist[1,:] = N
    
    # counts_time_hist = np.zeros([2,int(count_bins)])
    ''' if np.size(channels) == 2:
        i=0
        for ch in channels:
            
            if self.clean_pulses_switch == 1:
                indices = (self.list_data_array[:,-1]==1)

            times = self.list_data_array[indices, 0]

            N, _ = np.histogram(
                times,
                bins=int(count_bins),
                range=self.meas_time_range
                )
            counts_time_hist[i,:] = N
            i+=1
    else:
        print("Must specify two and only two channels to cross-correlate.")
    '''

    timeline = np.linspace(start=self.meas_time_range[0], 
                        stop=self.meas_time_range[1],
                        num=int(count_bins))/1e9

    '''fig1, ax1 = pyplot.subplots()
    ax1.plot(timeline, counts_time_hist, '.', label="TBD")
    ax1.plot(timeline, counts_time_hist2, '.', label="TBD")

    ax1.set_ylabel('Counts')
    ax1.set_xlabel('Time(s)')
    ax1.legend()'''
    
    # Plot counts over time histogram (ensure constant or near constant)
    i=0
    for ch in [0,1]:
        fig1, ax1 = pyplot.subplots()
        ax1.plot(timeline, counts_time_hist[i,:], '.', label="TBD")

        ax1.set_ylabel('Counts')
        ax1.set_xlabel('Time(s)')
        ax1.legend()
        i+=1

    fs = 1/(timeline[3]-timeline[2]) # Get frequency of counts samples

    f, Pxy = signal.csd(
        counts_time_hist[0,:], 
        counts_time_hist[1,:], 
        fs, 
        nperseg=2**10, 
        window='boxcar')
    Pxy = np.abs(Pxy)

    '''f1, Pxx1 = signal.welch(x=counts_time_hist[0,:], 
                        fs=fs, 
                        nperseg=2**12, 
                        window='boxcar')
    
    f2, Pxx2 = signal.welch(x=counts_time_hist[1,:], 
                        fs=fs, 
                        nperseg=2**12, 
                        window='boxcar')'''

    # Apply welch windows and FFT to tapered windows, summation is smoothed FFT

    # f, Pxx = lpsd(counts_time_hist, fs, window='boxcar')
    # # Apply logarithmically spaced power spectral density

    popt, pcov = curve_fit(CAFit, f[1:-2], Pxy[1:-2],
                                    p0=[Pxy[2], 25, 0],
                                    bounds=(0, np.inf),
                                    maxfev=100000
                                    )

    '''popt1, pcov1 = curve_fit(CAFit, f1[1:-2], 
                                    Pxx1[1:-2],
                                    p0=[Pxx1[2], 25, 0.001],
                                    bounds=(0, np.inf),
                                    maxfev=100000
                                    )
    
    popt2, pcov2 = curve_fit(CAFit, f2[1:-2], 
                                    Pxx2[1:-2],
                                    p0=[Pxx2[2], 25, 0.001],
                                    bounds=(0, np.inf),
                                    maxfev=100000
                                    )'''
    
    fig2, ax2 = pyplot.subplots()
    ax2.semilogx(f[1:-2], Pxy[1:-2], '.', **sps)
    ax2.semilogx(f[1:-2], CAFit(f[1:-2], *popt), **lfs)
    ymin, ymax = ax2.get_ylim()
    dy = ymax-ymin
    ax2.set_xlim([1, 200])
    ax2.set_xlabel('Frequency(Hz)')
    ax2.set_ylabel('PSD (V$^2$/Hz)')
    # ax2.set_yscale('log')
    alph_str = (r'$\alpha$ = (' +
            str(np.around(popt[1]*2*np.pi, decimals=2))+
            '$\pm$ '+
            str(np.around(np.sqrt(pcov[1,1])*2*np.pi, decimals=2))
            +') 1/s')
    ax2.annotate(alph_str, xy=(1.5, ymin+0.1*dy), xytext=(1.5, ymin+0.1*dy),
                fontsize=16, fontweight='bold',
                color='black', backgroundcolor='white')
    # ax2.text(1.5, ymin+0.1*dy, alph_str)

    # ax2.set_title(pyplot_title)
    ax2.legend(loc='upper right')

    ax2.grid()

    '''
    # Plotting the auto-power-spectral-density distribution and fit
    figauto1, (axauto1, axauto2) = pyplot.subplots(nrows=2, sharex=True, figsize=(8, 6), gridspec_kw={'height_ratios': [2, 1]})
    figauto2, (axauto3, axauto4) = pyplot.subplots(nrows=2, sharex=True, figsize=(8, 6), gridspec_kw={'height_ratios': [2, 1]})

    # Creating a plot with semilogarithmic (log-scale) x-axis 
    axauto1.semilogx(f1[1:-2], Pxx1[1:-2], '.', **sps)
    axauto1.semilogx(f1[1:-2], CAFit(f[1:-2], *popt1), **lfs)

    axauto3.semilogx(f2[1:-2], Pxx2[1:-2], '.', **sps)
    axauto3.semilogx(f2[1:-2], CAFit(f[1:-2], *popt2), **lfs)

    # Setting minimum and maximum for y
    ymin, ymax = ax1.get_ylim()
    dy = ymax-ymin

    # Constructing alpha string
    alph_str1 = (r'$\alpha$ = (' +
                str(np.around(popt1[1]*2*np.pi, decimals=2)) + '$\pm$ '+ 
                str(np.around(pcov1[1,1]*2*np.pi, decimals=2)) + ') 1/s')
    alph_str2 = (r'$\alpha$ = (' +
                str(np.around(popt2[1]*2*np.pi, decimals=2)) + '$\pm$ '+ 
                str(np.around(pcov2[1,1]*2*np.pi, decimals=2)) + ') 1/s')
    
        # Annotating the plots
    axauto1.annotate(alph_str1, 
                xy=(1.5, ymin+0.1*dy), 
                xytext=(1.5, ymin+0.1*dy),
                fontsize=16, 
                fontweight=self.annotate_font_weight,
                color=self.annotate_color, 
                backgroundcolor=self.annotate_background_color)
    axauto3.annotate(alph_str2, 
                xy=(1.5, ymin+0.1*dy), 
                xytext=(1.5, ymin+0.1*dy),
                fontsize=16, 
                fontweight=self.annotate_font_weight,
                color=self.annotate_color, 
                backgroundcolor=self.annotate_background_color)
    
    # Creating title and legend
    axauto1.set_title('Cohn Alpha Graph')
    axauto1.legend(loc='upper right')

    axauto3.set_title('Cohn Alpha Graph')
    axauto3.legend(loc='upper right')

    # Creating axis titles
    axauto1.set_xlim([1, 200])
    axauto1.set_xlabel('Frequency(Hz)')
    axauto1.set_ylabel('Intensity (V$^2$/Hz)')

    axauto3.set_xlim([1, 200])
    axauto3.set_xlabel('Frequency(Hz)')
    axauto3.set_ylabel('Intensity (V$^2$/Hz)')

    # Compute residuals
    residuals1 = ((CAFit(f1[1:-2], *popt1) - Pxx1[1:-2]) / Pxx1[1:-2]) * 100
    residuals2 = ((CAFit(f2[1:-2], *popt2) - Pxx2[1:-2]) / Pxx2[1:-2]) * 100

    # Computing residuals and plot in bottom subplot
    axauto2.scatter(f[1:-2], residuals1, **scatter_opt)  # Use f for residuals
    axauto2.axhline(y=0, color='#162F65', linestyle='--')
    axauto2.set_xlabel('Frequency(Hz)')
    axauto2.set_ylabel('Percent difference (%)')

    axauto4.scatter(f[1:-2], residuals2, **scatter_opt)  # Use f for residuals
    axauto4.axhline(y=0, color='#162F65', linestyle='--')
    axauto4.set_xlabel('Frequency(Hz)')
    axauto4.set_ylabel('Percent difference (%)')
    
    # Saving figures (optional)
    if save_fig:
        fig1.tight_layout()
        save_filename = os.path.join(save_dir, 'CohnAlpha')
        fig1.savefig(save_filename, dpi=300, bbox_inches='tight')

        fig2.tight_layout()
        save_filename = os.path.join(save_dir, 'CohnAlpha')
        fig2.savefig(save_filename, dpi=300, bbox_inches='tight')

        figauto1.tight_layout()
        save_filename = os.path.join(save_dir, 'CohnAlpha')
        figauto1.savefig(save_filename, dpi=300, bbox_inches='tight')

        figauto2.tight_layout()
        save_filename = os.path.join(save_dir, 'CohnAlpha')
        figauto2.savefig(save_filename, dpi=300, bbox_inches='tight')

    # Showing plots (optional)
    if show_plot:
        pyplot.show()
    '''
    pyplot.show()

    return f, Pxy, popt, pcov