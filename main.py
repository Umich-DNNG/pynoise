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

def getSettings():
    current_path = os.path.realpath(__file__)
    file_path = os.path.join(os.path.dirname(current_path), "Rossi_alpha_settings.txt")
    Rossi_alpha_settings = {}
    with open(file_path, 'r') as file:
        for line in file:
            settingName = line.split(':')[0].strip()
            setting = line.split(':')[1].strip()
            Rossi_alpha_settings[settingName] = setting
    return Rossi_alpha_settings

def main():
    settings = getSettings()
    import timeDifs
    time_Difs = timeDifs.calculate_time_differences(settings)


if __name__ == '__main__':
    main()