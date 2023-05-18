import os  # For scanning directories
import numpy as np

# --------------------------------------------------------------------------------


# settings class stores the separate dictionaries of settings created from the input file
class Settings:
    def __init__(
        self,
        io_file_info,
        general_program_settings,
        histogram_visual_settings,
        line_fitting_settings,
        residual_plot_settings,
        generating_histogram_settings,
    ):
        self.io_file_info = io_file_info
        self.general_program_settings = general_program_settings
        self.histogram_visual_settings = histogram_visual_settings
        self.generating_histogram_settings = generating_histogram_settings
        self.line_fitting_settings = line_fitting_settings
        self.residual_plot_settings = residual_plot_settings


# reads in the input from settings.txt and stores it in dictionaries
def readInput(filePath = None):

    ''' Reads the settings file and stores the appropriate data
    
    Arguments: (optional) filePath a path to the settings txt file that the user wants to read from, if none specified, program will look for "settings.txt" in the current directory
    
    Returns: a Settings object that contains io_file_info, general_program settings, histogram_visual settings, line_fittings settings, residual_plot_settings, generating_histogram_settings dictionaries'''

    current_path = os.path.realpath(__file__)
    file_path = os.path.join(os.path.dirname(current_path), "settings.txt")
    io_file_info = {}
    general_program_settings = {}
    histogram_visual_settings = {}
    generating_histogram_settings = {}
    line_fitting_settings = {}
    residual_plot_settings = {}

    with open(file_path, "r") as f:
        current_section = None
        for line in f:
            if line.startswith("#"):
                continue
            if "I/O FILE INFO" in line:
                current_section = io_file_info
            elif "GENERAL PROGRAM SETTINGS" in line:
                current_section = general_program_settings
            elif "HISTOGRAM VISUAL SETTINGS" in line:
                current_section = histogram_visual_settings
            elif "LINE FITTING SETTINGS" in line:
                current_section = line_fitting_settings
            elif "RESIDUAL PLOT SETTINGS" in line:
                current_section = residual_plot_settings
            elif "GENERATING HISTOGRAM SETTINGS" in line:
                current_section = generating_histogram_settings
            else:
                settingName, setting = line.strip().split(":")
                setting = setting.strip()
                settingName = settingName.strip()
                if settingName == "fit range":
                    setting_array = np.array([float(d) for d in setting.strip("[]").split(",")])
                    current_section[settingName.strip()] = setting_array
                elif setting.isdigit():
                    setting = float(setting)
                    current_section[settingName.strip()] = setting
                else:
                    current_section[settingName.strip()] = setting
        generating_histogram_settings["reset time"] = float(
            generating_histogram_settings["reset time"]
        )
        generating_histogram_settings["bin width"] = int(
            generating_histogram_settings["bin width"]
        )
        theseSettings = Settings(
            io_file_info,
            general_program_settings,
            histogram_visual_settings,
            line_fitting_settings,
            residual_plot_settings,
            generating_histogram_settings,
        )
    return theseSettings
