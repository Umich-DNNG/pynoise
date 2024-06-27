'''The object used for analyzing data.'''



# Necessary imports.
import os
import numpy as np
import matplotlib.pyplot as pyplot
import Event as evt
import time
import math
import lmxReader as lmx
from RossiAlpha import rossiAlpha as ra
from CohnAlpha import CohnAlpha as ca
from FeynmanY import feynman as fey
from tkinter import *
from tqdm import tqdm


def isValid(parameters: dict, object: dict):
    '''
    Checks if the current values are valid, ie if the object's 
    '''

    for setting in parameters:
        if parameters[setting] != object[setting]:
            return False
        return True
    

class Analyzer:

    '''The class that runs analysis. Can be used 
    in either terminal or gui implementation.'''


    def __init__(self):

        '''The initializer for the Analyzer object.'''


        # Initialize the variables used to determine whether 
        # or not certain elements have to be recreated.
        self.RATimeDifs = {'Time differences': [],
                           'Input file/folder': None,
                           'Number of folders': None,
                           'Sort data': None,
                           'Time difference method': [],
                           'Digital delay': None,
                           'Reset time': None}
        self.RAHist = {'Histogram': [],
                       'Bin width': None}
        self.RABestFit = {'Best fit': [],
                          'Fit minimum': [],
                          'Fit maximum': []}
        self.CohnAlpha = {'CA_Object': None,
                          'Histogram': [],
                          'Welch Result': [],
                          'PSD Fit Curve': []}
        self.FeynmanY = {}



    def isValid(self, method:str, parameters:dict):
        match method:
            case 'RABestFit':
                if (not self.isValid('RAHist',parameters)):
                    return False
            case 'RAHist':
                if (not self.isValid('RATimeDifs',parameters)):
                    return False
        for setting in parameters:
            if parameters[setting] != self.RATimeDifs[setting]:
                return False
            return True
        

def export(data: dict[str:tuple], 
            singles: list[tuple], 
            name: str, 
            output: str = './data'):

    '''Export data from analysis to a csv file. The file 
    will be stored in the data folder and will be named 
    based on the give analysis method and current time.
    
    Inputs:
    - dict: a dictionary that contains all the 
    list data to be outputted to the csv file. 
    Each key will be the name of the column, and 
    the value stored will be a tuple. The first 
    value is the list of data, and the second is 
    the row to start displaying the list at.
    - single: a list of single values to display on the top row. 
    Each list value will contain a tuple, whose first entry is 
    the name of the value and whose second entry is the value.
    - method: the name of the method of analysis.
    - output: the output directory. If not given, defaults to ./data.'''


    # Name the file appropriately with the method name and current time.
    fileName = (output + '/output_' + name + '.csv')
    # Open the new file.
    file = open(os.path.abspath(fileName),'w')
    # Initialize variables.
    labels = ''
    line = ''
    max = 0
    # For each dataset:
    for key in data:
        # If this is the longest dataset, store its length.
        if len(data[key][0]) + data[key][1] > max:
            max = len(data[key][0]) + data[key][1]
        # Add the dataset name to the labels string.
        labels += key + ','
        # If the dataset is starting at first 
        # row, add the first value to the row.
        if data[key][1] == 0:
            line += str(data[key][0][0]) + ','
        # Otherwise, leave an empty space.
        else:
            line += ','
    # For each single datapoint:
    for item in singles:
        # Add the data name to the labels string.
        labels += str(item[0]) + ','
        # Add the data value to the first row.
        line += str(item[1]) + ','
    # Write the columns row and first data row 
    # to the file (excluding tailing commas).
    file.write(labels[:-1] + '\n' + line[:-1] + '\n')
    # For each possible dataset index:
    for i in range(1,max):
        # Reset the line string.
        line = ''
        # For each dataset:
        for key in data:
            # If the desired beginning row for the dataset has 
            # been reached and there's still data left to print, 
            # add the proper data value to the current row.
            if i >= data[key][1] and i-data[key][1] < len(data[key][0]):
                line += str(data[key][0][i-data[key][1]]) + ','
            # Otherwise, leave an empty space.
            else:
                line += ','
        # Write the whole row to the file (excluding tailing comma).
        file.write(line[:-1]+'\n')
    # Flush the output to the file and close it.
    file.flush()
    file.close()

def calcNumFolders(original):
    '''Computes the number of folders on the given path.

    Inputs:
    - original: string, the original name of the input file.

    Outputs:
    - bool: true if number of folders is valid, false otherwise.
    - numFolders: int, the number of folders computed
    '''
    numFolders = 0
    while (os.path.exists(original + '/' + str(numFolders + 1))):
        numFolders += 1
    if (numFolders <= 1):
        print('ERROR: Running RossiAlpha method on a folder with \"null\" number of folders requires more than 1 folder in the path.\n')
        return False, 0
    return True, numFolders

def replace_zeroes(self, lst: list):

    '''Replace all zeroes in a list with 
    the average of the non-zero elements.
    
    Inputs:
    - lst: the list to be edited.
    
    Outputs:
    - the edited list.'''
    

    # Create a list of all the non-zero elements and compute their average.
    non_zero_elements = [x for x in lst if x != 0]
    if len(non_zero_elements) != 0:
        average = sum(non_zero_elements) / len(non_zero_elements)
        # For each zero in the list, replace it with the average.
        for i in range(len(lst)):
            if lst[i] == 0:
                lst[i] = average
        # Return the edited list.
    return lst



class Analyzer:

    '''The class that runs analysis. Can be used 
    in either terminal or gui implementation.'''


    def __init__(self):

        '''The initializer for the Analyzer object.'''


        # Initialize the variables used to determine whether 
        # or not certain elements have to be recreated.
        self.RossiAlpha = None
        self.CohnAlpha = {}
        self.FeynmanY = {}


    def runFeynmanY(self, 
                    io: dict, 
                    fy: dict, 
                    show: bool, 
                    save: bool, 
                    quiet: bool, 
                    verbose: bool = False, 
                    hvs: dict = {}, 
                    lfs: dict = {},
                    sps: dict = {}, 
                    window: Tk = None):
        
        '''Run FeynmanY analysis for varying tau values.
        Plots each tau value and estimates alpha.
        
        Inputs:
        - io: the Input/Output Settings dictionary.
        - fy: the FeynmanY Settings dictionary.
        - show: whether or not to show plots.
        - save: whether or not to save plots.
        - quiet: whether or not to silence print statements.
        - verbose: whether or not the analysis should 
        consider each tau value for exporting.
        - hvs: the Histogram Visual Settings.
        - lfs: the Line Fitting Settings.
        - sps: the Scatter Plot Settings.
        - window: the window object, if being run in GUI mode.'''
        

        # Initialize variables.
        yValues = []
        y2Values = []
        tValues = []
        # Fill the tau list with the desired tau values.
        tValues.extend(range(fy['Tau range'][0], fy['Tau range'][1]+1, fy['Increment amount']))
        # Create a FeynmanY object.
        FeynmanYObject = fey.FeynmanY(fy['Tau range'], fy['Increment amount'], fy['Plot scale'])
        # Load in the data and sort it.
        data = evt.createEventsListFromTxtFile(io['Input file/folder'],
                                               io['Time column'],
                                               io['Channels column'],
                                               True,
                                               quiet,
                                               False)
        data.sort(key=lambda Event: Event.time)
        # Initialize variables for counting
        # the total real measurement time.
        meas_time = 0
        begin = data[0].time
        end = data[0].time
        # Iterate through the data.
        for entry in data:
            # If we have reached a jump:
            if entry.time - end > 1e13:
                # Add the previous measurement 
                # time range to the total.
                meas_time += end - begin
                # Reset the beginning time
                begin = entry.time
            # Move the ending time up.
            end = entry.time
        # Add the remaining time range.
        meas_time += end - begin
        # For GUI mode.
        if window is not None:
            # Increment the progress bar.
            window.children['progress']['value'] += 1
            wait = BooleanVar()
            # After 1 ms, set the dummy variable to True.
            window.after(1, wait.set, True)
            # Wait for the dummy variable to be set, then continue.
            window.wait_variable(wait)
        # If not in quiet mode, display progress.
        if not quiet:
            print('Running each tau value...')
        # For each tau value:
        for tau in tqdm(tValues):
            # Convert the data into bin frequency counts.
            counts = FeynmanYObject.randomCounts(data, tau, meas_time)
            # Compute the variance to mean for this 
            # tau value and add it to the list.
            FeynmanYObject.computeMoments(counts, tau)
            y, y2 = FeynmanYObject.computeYY2(tau)
            yValues.append(y)
            y2Values.append(y2)
            # If in verbose mode:
            if verbose:
                # Save the raw data if desired..
                if io['Save outputs']:
                    self.export({'Count': (range(0,len(counts)), 0),
                                 'Frequency': (counts,0)},
                                 [('Tau',tau)],
                                 'FY' + str(tau),
                                 io['Save directory'])
                # Call the histogram plotter if desired.
                if show or save:
                    FeynmanYObject.FeynmanY_histogram(counts,
                                                    fy['Plot scale'],
                                                    show,
                                                    save,
                                                    io['Save directory'],
                                                    hvs)
            # For GUI mode.
            if window is not None:
                # Increment the progress bar.
                window.children['progress']['value'] += 1
                wait = BooleanVar()
                # After 1 ms, set the dummy variable to True.
                window.after(1, wait.set, True)
                # Wait for the dummy variable to be set, then continue.
                window.wait_variable(wait)
        # Plot and fit both Y and Y2 values against tau.
        FeynmanYObject.plot(tValues, yValues, save, show, io['Save directory'])
        FeynmanYObject.plot(tValues, y2Values, save, show, io['Save directory'])
        FeynmanYObject.fitting(tValues, 
                               yValues, 
                               gamma_guess=yValues[-1], 
                               alpha_guess=-0.01, 
                               save_fig=save, 
                               show_plot=show, 
                               save_dir=io['Save directory'],
                               fit_opt=lfs,
                               scatter_opt=sps,
                               type='Y')
        FeynmanYObject.fitting(tValues, 
                               y2Values, 
                               gamma_guess=yValues[-1], 
                               alpha_guess=-0.01, 
                               save_fig=save, 
                               show_plot=show, 
                               save_dir=io['Save directory'],
                               fit_opt=lfs,
                               scatter_opt=sps,
                               type='Y2')
        # If saving raw dta:
        if io['Save outputs']:
            # Create a proper file name.
            if verbose:
                filename = 'FYFull'
            else:
                filename = 'FY'
            # Export the data.
            self.export({'Tau':(tValues,0),
                         'Experimental Y':(yValues,0),
                         'Experimental Y2':(y2Values,0),
                         'Predicted Y2': (FeynmanYObject.pred,0)},
                        [('Gamma',FeynmanYObject.gamma),
                         ('Alpha',FeynmanYObject.alpha),
                         ('Input file', io['Input file/folder'])],
                        filename,
                        io['Save directory'])

    def genCohnAlphaObject(self, settings: dict = {}):
        '''Creates a Cohn Alpha object
        
        Inputs:
        - settings: the current user's runtime settings'''

        # Load the values from the specified file into an NP array.
        values = np.loadtxt(settings['Input/Output Settings']['Input file/folder'], usecols=0, dtype=float)

        return ca.CohnAlpha(values,
                            settings['CohnAlpha Settings']['Dwell time'],
                            settings['CohnAlpha Settings']['Meas time range'],
                            settings['Input/Output Settings']['Quiet mode'])


    def plotCohnAlphaHist(self, settings:dict = {}, overwrite:bool = True):
        
        '''
        Creates a Cohn Alpha Counts Histogram
        Created Histogram is saved in the Analyzer class
        
        Inputs:
        - settings: the current user's runtime settings
        - overwrite: if overwriting the current information in memory
        '''

        if self.CohnAlpha['CA_Object'] is None:
            self.CohnAlpha['CA_Object'] = self.genCohnAlphaObject(settings)

        if not overwrite:
            return False

        self.CohnAlpha['CA_Object'].plotCountsHistogram(settings)
        return True


        # OLD CODE
        # LEAVING HERE FOR NOW
        # WOULD SAVE DATA IN MEMORY, preferably grab data from disk when needed is better

        # # if overwriting or no histogram in memory, then clear and generate new histogram
        # # if not overwriting and histogram in memory exists, then do not generate
        # if not overwrite and self.CohnAlpha['Histogram'] != []:
        #     return False
            
        #     # TODO: currently displaying an image is not working. Shows image inside of a plot. Need to fix
        #     # If show plots enabled, then show the plot before returning
        #     # if settings['General Settings']['Show plots']:
        #         # imgFilePath = os.path.join(settings['Input/Output Settings']['Save directory'], 'CACountsHist' + str(self.CohnAlpha['CA_Object'].dwell_time) + '.png')
        #         # img = pyplot.imread(imgFilePath)
        #         # pyplot.imshow(img)
        #         # pyplot.show()
        #         # pyplot.close()


        # # clear dependent data
        # self.CohnAlpha['Histogram'].clear()
        # self.CohnAlpha['Welch Result'].clear()
        # self.CohnAlpha['PSD Fit Curve'].clear()

        # print('\nPlotting the Cohn Alpha Histogram...')
        # self.CohnAlpha['Histogram'].append(self.CohnAlpha['CA_Object'].plotCountsHistogram(settings))
        # return True



    def applyWelchApprox(self, settings:dict = {}, overwrite:bool = True):
        
        '''
        Applies the Welch Approximation transformation
        Frequencies as well as Power Spectral Density is saved in Analyzer class
        Will generate any required missing information
        
        Inputs:
        - settings: the current user's runtime settings
        - overwrite: if overwriting the current information in memory
        '''

        # Ensure that histogram exists
        self.plotCohnAlphaHist(settings=settings, overwrite=overwrite)

        if not overwrite:
            return False
        self.CohnAlpha['CA_Object'].welchApproxFourierTrans(settings)
        return True

        # OLD CODE


        # # If overwriting or no data exists, then clear and generate
        # # If not overwriting and data exists, then don't clear and return early
        # if not overwrite and self.CohnAlpha['Welch Result'] != []:
        #     return False

        # self.CohnAlpha['Welch Result'].clear()
        # self.CohnAlpha['PSD Fit Curve'].clear()

        # # Generate a graph for each histogram
        # # TODO: double check with Flynn the behavior for folder analysis
        # for hist in self.CohnAlpha['Histogram']:
        #     welchResultDict = self.CohnAlpha['CA_Object'].welchApproxFourierTrans(hist, settings)
        #     self.CohnAlpha['Welch Result'].append(welchResultDict)



    def fitPSDCurve(self, settings:dict = {}, overwrite:bool = True):        
        
        '''
        Fits a Power Spectral Density Curve onto a 
        Transformed graph is saved into the Analyzer class
        
        Will run entire method if required information is missing
        
        Inputs:
        - settings: the current user's runtime settings
        '''
        
        # ensure necessary data exists
        self.applyWelchApprox(settings=settings, overwrite=overwrite)

        if not overwrite:
            return False
    
        self.CohnAlpha['CA_Object'].fitPSDCurve(settings=settings)
        return True

        # OLD CODE

        # # if overwriting or no data exists, then generate best fit
        # # if not overwriting and data exists, then do not generate
        # if not overwrite and self.CohnAlpha['PSD Fit Curve'] != []:
        #     return False
        
        # self.CohnAlpha['PSD Fit Curve'].clear()
        
        # dict_list = self.CohnAlpha['Welch Result']
        # for dict in dict_list:
        #     PSDFitCurveDict = self.CohnAlpha['CA_Object'].fitPSDCurve(settings=settings, welchResultDict=dict)
        #     self.CohnAlpha['PSD Fit Curve'].append(PSDFitCurveDict)
        
        # return True
