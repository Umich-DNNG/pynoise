'''The class for constructing and calculating time 
difference objects for RossiAlpha analysis. Supports 
separated and combined histogram/time difference operations.'''



# Necessary imports.
import numpy as np
from . import plots as plt
import Event as evt
import lmxReader as lmx
import os
import json



class timeDifCalcs:
    
    '''The time differences object that stores 
    events and calculates time differences.'''

    def __init__(self, io: dict, reset_time: float = None, method: str = 'aa', digital_delay: int = None, folderNum = 0, sort_data: bool = False):
        
        '''Initializes a time difference object. Autogenerates variables where necessary.
    
        Inputs:
        - events: the list of measurement times for each data point.
        - digital_delay: the amount of digital delay, if 
        applicable. Only required when using the dd method.
        - reset_time: the maximum time difference allowed. If 
        not given, will autogenerate the best reset time.
        - method: the method of calculating time 
        differences (assumes aa).'''
        

        # If a reset time is given, use it.
        if reset_time != None:
            self.reset_time = float(reset_time)
        # TODO: Otherwise, generate one.
        else:
            self.reset_time = 0
        # Store the method of analysis.
        self.method = method
        # When considering digital delay, store given digital delay.
        if self.method == 'dd':
            self.digital_delay = digital_delay
        # Initialize the blank time differences.
        self.timeDifs = None
        self.export = io['Save time differences']
        self.overwrite = io['Overwrite lower reset times']
        self.outputFolder = io['Save directory']
        name = io['Input file/folder']
        # if is a folder analysis, retrieve the name of the folder. 
        # When this function is called on a folder, the input file/folder was changed to the user inputted folder name + "/" + the current folder number
        # TODO: change calling logic to not have to do this?
        if folderNum is not 0:
            temp = name[:name.rfind('/')]
            name = temp[temp.rfind('/')+1:]
        # if is a file, retrieve the name of just the file
        else:
            name = name[name.rfind('/')+1:]
        self.outputName = 'output_rossi_time_difs_' + name
        # self.outputName = io['Output name']
        self.folderNum = folderNum
        self.file_name = os.path.abspath(self.outputFolder) + '/' + self.outputName + '/' + (str(self.folderNum) + '/' if self.folderNum != 0 else '') + self.method + '/'
        self.pregenerated = ''
        if os.path.exists(self.file_name):
            for time_dif_data in os.listdir(self.file_name):
                if len(time_dif_data) > 3 and time_dif_data[-3:] == '.td' and time_dif_data[:-3].isnumeric() and int(time_dif_data[:-3]) >= self.reset_time:
                    self.pregenerated = self.file_name + time_dif_data
                    break
        if self.pregenerated == '':
            # Create empty data and time difference lists.
            self.events = []
            # Load the data according to its file type.
            if io['Input file/folder'].endswith(".txt"):
                self.events = evt.createEventsListFromTxtFile(io['Input file/folder'],
                                                    io['Time column'],
                                                    io['Channels column'],
                                                    True,
                                                    io['Quiet mode'],
                                                    self.folderNum != 0)
            elif io['Input file/folder'].endswith(".lmx"):
                self.events =  lmx.readLMXFile(io['Input file/folder'])
            # If folder analysis:
            else:
                # For each file in the specified folder:
                for filename in os.listdir(io['Input file/folder']):
                    if len(filename) >= 14:
                        board = filename[0:8]
                        ntxt = filename[len(filename)-6:]
                        channel = filename[8:len(filename)-6]
                        if board == 'board0ch' and ntxt == '_n.txt' and channel.isnumeric() and int(channel) >= 0:
                            # Change the input file to this file.
                            # Add the data from this file to the events list.
                            self.events.extend(evt.createEventsListFromTxtFile(io['Input file/folder'] + "/" + filename,
                                                                        io['Time column'],
                                                                        int(channel),
                                                                        False,
                                                                        io['Quiet mode'],
                                                                        True))
            # Sort the data if applicable.
            if sort_data:
                self.events.sort(key=lambda Event: Event.time)

    def exportTimeDifs(self):
        if self.pregenerated == '':
            file_check = os.path.abspath(self.outputFolder) + '/'
            if not os.path.exists(file_check):
                os.mkdir(file_check)
            file_check += self.outputName + '/'
            if not os.path.exists(file_check):
                os.mkdir(file_check)
            if self.folderNum != 0:
                file_check += str(self.folderNum) + '/'
                if not os.path.exists(file_check):
                    os.mkdir(file_check)
            file_check += self.method + '/'
            if not os.path.exists(file_check):
                os.mkdir(file_check)
            if self.overwrite:
                for time_dif_data in os.listdir(self.file_name):
                    if len(time_dif_data) > 3 and time_dif_data[-3:] == '.td' and time_dif_data[:-3].isnumeric() and int(time_dif_data[:-3]) <= self.reset_time:
                        os.remove(self.file_name + time_dif_data)
            with open(self.file_name + str(int(self.reset_time)) + '.td','w') as file:
                json.dump({"Time differences":self.timeDifs.tolist()},file,indent=2)

    def calculateTimeDifsFromEvents(self):

        '''Returns and stores the array of time differences used 
        for constructing a histogram based on the stored method.

        Outputs:
        - the calculated time differences.'''
        
        # Construct the empty time differences array, store the total 
        # number of data points, and initialize the indexing variable.
        
        if self.pregenerated != '':
            with open(self.pregenerated,'r') as file:
                self.timeDifs = np.array([item for item in json.load(file)['Time differences'] if item <= self.reset_time])
            return self.timeDifs
        time_diffs = np.array([])
        n = len(self.events)
        i = 0
        prevent = False
        # Iterate through the whole time vector.
        while i < len(self.events):
            # Create an empty channel bank.
            ch_bank = set()
            # Iterate through the rest of the vector
            # starting 1 after the current data point.
            for j in range(i + 1, n):
                # If the current time difference exceeds the 
                # reset time range, break to the next data point.
                if self.events[j].time - self.events[i].time > self.reset_time:
                    break
                # If the method is any and all, continue. Otherwise, assure 
                # that the channels are different between the two data points.
                if((self.method == 'aa') or self.events[j].channel != self.events[i].channel):
                    # If the method is any and all or cross_correlation, continue. Otherwise, 
                    # check that the current data point's channel is not in the bank.
                    if(self.method == 'aa' or 
                       self.method == 'cc' or 
                       self.events[j].channel not in ch_bank):
                        # Add the current time difference to the list.
                        time_diffs = np.append(time_diffs,(self.events[j].time - self.events[i].time))
                    # If digital delay is on:
                    elif(self.method == 'dd'):
                        # Skip to the nearest data point after the
                        # current one with the digital delay added.
                        stamped_time = self.events[i].time
                        while self.events[i].time < stamped_time + self.digital_delay:
                           i += 1
                        prevent = True
                    # Add the current channel to the channel bank if considering channels.
                    if(self.method != "aa"):
                        ch_bank.add(self.events[j].channel)
            # Iterate to the next data point without double counting for digital delay.
            if not prevent:
                i += 1
            else:
                prevent = False
        # Store the time differences array.
        self.timeDifs = time_diffs
        if self.export:
            self.exportTimeDifs()
        # Return the time differences array.
        return self.timeDifs
    


    def calculateTimeDifsAndBin(self, 
                                input:str,
                                bin_width:int = None, 
                                save_fig:bool = False, 
                                show_plot:bool = True, 
                                save_dir:str= './', 
                                plot_opts:dict = None, 
                                folder:bool = False, 
                                verbose:bool = False):
        
        '''Simultaneously calculates the time differences for 
        the timeDifs object and adds them to a new histogram.
        
        Inputs:
        - bin width: the width of each histogram bin. If 
        not given, will autogenerate a reasonable width.
        TODO: Actually do this.
        - save_fig: whether or not the figures should be saved 
        to the given directory after creation (assumes False).
        - show_plot: whether or not the figures should be 
        shown to the user upon creation (assumes True).
        - save_dir: if save_fig is True, what directory the figures 
        will be saved in (assumes the current working directory).
        - plot_opts: all the matplotlib plot parameters.
        - folder: whether or not this plot is for folder analysis.
        - verbose: whether or not folder analysis should output file results.
        
        Outputs:
        - RossiHistogram object
        - histogram: the list of counts for each histogram bin.
        - bin_centers: the time at the center of each bin.
        - bin_edges: the time on the edge of each bin.
        '''
        
        
        # Store the number of data points, the number of bins, 
        # and initialize the data point index and histogram array.
        n = len(self.events)
        i = 0
        num_bins = int(self.reset_time / bin_width)
        histogram = np.zeros(num_bins)
        prevent = False
        # Iterate through the whole time vector.
        while i < len(self.events):
            # Create an empty channel bank.
            ch_bank = set()
            # Iterate through the rest of the vector
            # starting 1 after the current data point.
            for j in range(i + 1, n):
                # If the current time difference exceeds the 
                # reset time range, break to the next data point.
                if self.events[j].time - self.events[i].time > self.reset_time:
                    break
                # If the method is any and all, continue. Otherwise, assure 
                # that the channels are different between the two data points.
                if((self.method == 'aa') or self.events[j].channel != self.events[i].channel):
                    # If the method is any and all or cross_correlation, continue. Otherwise, 
                    # check that the current data point's channel is not in the bank.
                    if(self.method == 'aa' or self.method == 'cc' or self.events[j].channel not in ch_bank):
                        # Store the current time difference.
                        thisDif = self.events[j].time - self.events[i].time
                        # Calculate the bin index for the current time difference.
                        binIndex = int((thisDif) / bin_width)
                        # If the calculated index is exactly at the end 
                        # of the time range, put it into the last bin.
                        if(binIndex == num_bins):
                            binIndex -= 1
                        # Increase the histogram count in the appropriate bin.
                        histogram[binIndex] += 1    
                    # If digital delay is on:
                    elif(self.method == 'dd'):
                        # Skip to the nearest data point after the
                        # current one with the digital delay added.
                        stamped_time = self.events[i]
                        while self.events[i].time < stamped_time + self.digital_delay:
                           i += 1
                        prevent = True
                    # Add the current channel to the channel bank if considering channels.
                    if(self.method != "aa"):
                        ch_bank.add(self.events[j].channel)
            # Iterate to the next data point.
            if not prevent:
                i += 1
            else:
                prevent = False
        # Normalize the histogram.
        bin_edges = np.linspace(0, self.reset_time, num_bins + 1)
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])
        # Constuct the rossiHistogram object and plot accordingly.
        rossiHistogram = plt.RossiHistogram(bin_width= bin_width, reset_time=self.reset_time)
        rossiHistogram.initFromHist(histogram,bin_centers,bin_edges)
        rossiHistogram.plotFromHist(input,self.method,plot_opts,save_fig,show_plot,save_dir,folder,verbose)
        # Return the rossiHistogram object and related NP arrays.
        return rossiHistogram, histogram, bin_centers, bin_edges