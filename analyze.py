'''The object used for analyzing data.'''



# Necessary imports.
import os
import Event as evt
from FeynmanY import feynman as fey
from tkinter import *
from tqdm import tqdm


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


def replace_zeroes(lst: list):

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


# ---------- unorganized feymanY code -----------

class Analyzer:

    '''The class that runs analysis. Can be used 
    in either terminal or gui implementation.'''


    def __init__(self):

        '''The initializer for the Analyzer object.'''
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
        
