import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from scipy import signal

def CPSD(f, A, alpha, c):
    return A / (1+(f**2/alpha**2)) + c

def conduct_CPSD(PowSpecDens_settings,leg_labels,
                 plt_title,
                 clean_pulses_switch):
    
    count_bins = (
        np.diff(PowSpecDens_settings['meas time range'])/
        PowSpecDens_settings['dwell time']
                  )
    
    counts_time_hist = np.zeros([2,int(count_bins)])

    list_data_array = np.loadtxt("stilbene_2in_CROCUS_20cm_offset_east.txt")
    index = list_data_array[:,0]!=0  # Remove erroneous times
    if clean_pulses_switch == 1:
        index = index & (list_data_array[:,-1]==1)
    times = list_data_array[index,0]
    N, _ = np.histogram(
                 times,
                 bins=int(count_bins),
                 range=PowSpecDens_settings['meas time range']
                 )
    counts_time_hist[0,:] = N
    list_data_array = np.loadtxt("stilbene_2in_CROCUS_20cm_offset_north.txt")
    index = list_data_array[:,0]!=0  # Remove erroneous times
    if clean_pulses_switch == 1:
        index = index & (list_data_array[:,-1]==1)
    times = list_data_array[index,0]
    N, _ = np.histogram(
                  times,
                  bins=int(count_bins),
                  range=PowSpecDens_settings['meas time range']
                  )
    counts_time_hist[1,:] = N

    timeline = np.linspace(PowSpecDens_settings['meas time range'][0],
                PowSpecDens_settings['meas time range'][1], # Get measurement time in seconds
                int(count_bins))/1e9
    
    # Plot counts over time histogram (ensure constant or near constant)
    i=0
    for ch in [0,1]:
        fig1, ax1 = plt.subplots()
        ax1.plot(timeline, counts_time_hist[i,:], '.', label=leg_labels[i])

        ax1.set_ylabel('Counts')
        ax1.set_xlabel('Time (s)')
        ax1.legend()
        i+=1

    fs = 1/(timeline[3]-timeline[2]) # Get frequency of counts samples

    f, Pxy = signal.csd(
        counts_time_hist[0,:], counts_time_hist[1,:], fs, nperseg=2**10, window='boxcar')
    
    Pxy = np.abs(Pxy)
    # Apply welch windows and FFT to tapered windows, summation is smoothed FFT

    # f, Pxx = lpsd(counts_time_hist, fs, window='boxcar')
    # # Apply logarithmically spaced power spectral density

    popt, pcov = curve_fit(CPSD, f[1:-2], Pxy[1:-2],
                                     p0=[Pxy[2], 25, 0],
                                     bounds=(0, np.inf),
                                     maxfev=100000
                                     )
    
    fig2, ax2 = plt.subplots()
    ax2.semilogx(f[1:-2], Pxy[1:-2], '.', label=plt_title)
    ax2.semilogx(f[1:-2], CPSD(f[1:-2], *popt), '--', label='fit')
    ymin, ymax = ax2.get_ylim()
    dy = ymax-ymin
    ax2.set_xlim([1, 200])
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('PSD (Counts$^2$/Hz)')
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

    # ax2.set_title(plt_title)
    ax2.legend(loc='upper right')

    ax2.grid()

    plt_title = plt_title.replace('/','-')
    plt_title = plt_title.replace('\\','')
    plt_title = plt_title.replace('$','')

    plt.savefig((plt_title + '.pdf'))

    plt.show()

    return f, Pxy, popt, pcov

PowSpecDens_settings = {'dwell time': 1e6, 'meas time range': [0,3.75e12]}
leg_labels = ["S2E","S2N"]
plt_title = "CPSD S2E/S2N"

conduct_CPSD(PowSpecDens_settings,leg_labels,plt_title,1)
