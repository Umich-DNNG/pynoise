import sys

# # Define location of Git synchoronized Python functions
# # Add python functions folder to path
# sys.path.extend([python_scripts_path])

# from Data_structure import DataLoader # For building data file load structure

import numpy as np                    # For processing data
import os                             # For scanning directories
import matplotlib.pyplot as plt       # For plotting data summaries
from matplotlib.colors import LogNorm # For adjusting colorbar scale
# from scipy.signal import find_peaks
from scipy.optimize import curve_fit
import copy
import seaborn as sns
sns.set(rc={"figure.dpi": 350, 'savefig.dpi': 350})
sns.set_style("ticks")
sns.set_context("talk", font_scale=0.8)

#get the settings for the user to use
def getSettings():
    current_path = os.path.realpath(__file__)
    file_path = os.path.join(os.path.dirname(current_path), "Rossi_alpha_settings.txt")
    Rossi_alpha_settings = {}
    with open(file_path, 'r') as file:
        for line in file:
            settingName = line.split(':')[0].strip()
            setting = line.split(':')[1].strip()
            if(settingName == 'fit range'):
                setting = [float(s) for s in setting[1:-1].split(",")]
            Rossi_alpha_settings[settingName] = setting
            
    Rossi_alpha_settings['reset time'] = float(Rossi_alpha_settings['reset time'])
    Rossi_alpha_settings['bin width'] = int(Rossi_alpha_settings['bin width'])
    Rossi_alpha_settings['minimum cutoff'] = int(Rossi_alpha_settings['minimum cutoff'])
    Rossi_alpha_settings['digital delay'] = int(Rossi_alpha_settings['digital delay'])
    Rossi_alpha_settings['meas time per folder'] = int(Rossi_alpha_settings['meas time per folder'])
    return Rossi_alpha_settings

def main():
    settings = getSettings()
    current_path = os.path.realpath(__file__)
    file_path = os.path.join(os.path.dirname(current_path), "RF3-40_59min.txt")
    list_data_n = np.loadtxt(file_path)
    
    import timeDifs
    time_diffs = timeDifs.calculate_time_differences(list_data_n, settings)

    import fitting
    [RA_hist, popt, pcov, x_fit, y_fit] = fitting.make_RA_hist_and_fit(time_diffs, settings)

    RA_hist_array = RA_hist[0]
    popt_array = popt

    RA_std_dev = np.std(RA_hist_array, axis=0, ddof=1)            
    RA_hist_total = np.sum(RA_hist_array, axis=0)
    time_diff_centers = RA_hist[1][1:] - np.diff(RA_hist[1][:2])/2

    [time_diff_centers, popt, pcov, perr, xfit1, yfit] = fitting.fit_RA_hist_weighting(RA_hist_total, settings)

    popt_array = np.vstack((popt_array, popt))
    perr_array = np.vstack((perr_array, perr))

    fitting.plot_RA_and_fit_errorbar(RA_hist, x_fit, y_fit, settings, xlabel1='Time difference (ns)', ylabel1='Count rate (s$^{-1}$)',
                             xlabel2='Time difference (ns)', ylabel2='Residual count rate (s$^{-1}$)')
    
if __name__ == '__main__':
    main()

