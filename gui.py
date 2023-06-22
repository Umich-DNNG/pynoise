from tkinter import *
from tkinter import ttk
import tkinter as tk
import settings as set
import os
import numpy as np
from PowerSpectralDensity import PSD
from RossiAlpha import analyzeAll as mn
from RossiAlpha import fitting as fit
from RossiAlpha import plots as plt
from RossiAlpha import timeDifs as dif
from RossiAlpha import analyzingFolders as fol

window = None
parameters = None
response = None

# Where the time differences are stored.
time_difs = None
time_difs_file = None
time_difs_method = None
# Where the histogram plot is stored.
histogram = None
hist_file = None
hist_method = None
# Where the best fit curve is stored.
best_fit = None

def prompt(message, title, function, prev):
    global window, response
    response = tk.StringVar()
    for item in window.winfo_children():
        item.destroy()
    window.title(title)
    ttk.Label(window,
              name='prompt',
              text=message
              ).grid(column=0,row=0)
    ttk.Entry(window,
              name='response',
              textvariable=response,
              ).grid(column=0,row=1)
    ttk.Button(window,
              name='continue',
              text='Continue',
              command=function
              ).grid(column=0,row=2)
    ttk.Button(window,
              name='cancel',
              text='Cancel',
              command=prev
              ).grid(column=0,row=3)
    
def error(message):
    window=Tk()
    window.title('ERROR!')
    ttk.Label(window,
            name='message',
            text=message
            ).grid(column=0,row=0)
    ttk.Button(window,
               name='return',
               text='OK',
               command=window.destroy
               ).grid(column=0,row=1)
    window.mainloop()

def warningFunction(to, window):
    window.destroy()
    to()


def warning(message, to):
    window=Tk()
    window.title('WARNING!')
    ttk.Label(window,
            name='message',
            text=message
            ).grid(column=0,row=0)
    ttk.Button(window,
               name='yes',
               text='Yes',
               command=lambda: warningFunction(to, window)
               ).grid(column=0,row=1)
    ttk.Button(window,
               name='no',
               text='No',
               command=window.destroy
               ).grid(column=0,row=2)
    window.mainloop()

def createTimeDifs():
    global time_difs, time_difs_file, time_difs_method, parameters
    name = parameters.settings['Input/Output Settings']['Input file/folder']
    name = name[name.rfind('/')+1:]
    if name.count('.') > 0:
        if parameters.settings['Input/Output Settings'].get('Data Column') is not None:
            data = np.loadtxt(parameters.settings['Input/Output Settings']['Input file/folder'],delimiter=" ", usecols=(parameters.settings['Input/Output Settings']['Data Column']))
        else:
            data = np.loadtxt(parameters.settings['Input/Output Settings']['Input file/folder'])

        if parameters.settings['General Settings']['Sort data']:
            data = np.sort(data)
        time_difs = dif.timeDifCalcs(data, 
            parameters.settings['RossiAlpha Settings']['Reset time'], 
            parameters.settings['RossiAlpha Settings']['Time difference method'])
        time_difs = time_difs.calculate_time_differences()
        time_difs_file = parameters.settings['Input/Output Settings']['Input file/folder']
        time_difs_method = parameters.settings['RossiAlpha Settings']['Time difference method']

def createPlot():

    '''Creates a histogram based on the time difference data.
    
    Will overwrite the current histogram, if one exists.

    Assumes that the time difference data is valid.'''

    global time_difs, histogram, hist_file, hist_method, parameters
    histogram = plt.RossiHistogram(parameters.settings['RossiAlpha Settings']['Reset time'],
                              parameters.settings['RossiAlpha Settings']['Bin width'],
                              parameters.settings['Histogram Visual Settings'],
                              parameters.settings['Input/Output Settings']['Save directory'])
    histogram.plot(time_difs,
              save_fig=parameters.settings['General Settings']['Save figures'],
              show_plot=parameters.settings['General Settings']['Show plots'])
    hist_file = parameters.settings['Input/Output Settings']['Input file/folder']
    hist_method = parameters.settings['RossiAlpha Settings']['Time difference method']

def calculateTimeDifsAndPlot():

    global histogram, time_difs, hist_file, hist_method, parameters
    time_difs = None
    if parameters.settings['Input/Output Settings'].get('Data Column') is not None:
        data = np.loadtxt(parameters.settings['Input/Output Settings']['Input file/folder'],delimiter=" ", usecols=(parameters.settings['Input/Output Settings']['Data Column']))
    else:
        data = np.loadtxt(parameters.settings['Input/Output Settings']['Input file/folder'])

    if parameters.settings['General Settings']['Sort data']:
        data = np.sort(data)

    thisTimeDifCalc = dif.timeDifCalcs(data, parameters.settings['RossiAlpha Settings']['Reset time'], parameters.settings['RossiAlpha Settings']['Time difference method'])

    histogram, counts, bin_centers, bin_edges = thisTimeDifCalc.calculateTimeDifsAndBin(parameters.settings['RossiAlpha Settings']['Bin width'], parameters.settings['General Settings']['Save figures'], parameters.settings['General Settings']['Show plots'], parameters.settings['Input/Output Settings']['Save directory'], parameters.settings['Histogram Visual Settings'])
    hist_file = parameters.settings['Input/Output Settings']['Input file/folder']
    hist_method = parameters.settings['RossiAlpha Settings']['Time difference method']

def plotSplit():
    global parameters
    if time_difs is None or (not (time_difs_method == parameters.settings['RossiAlpha Settings']['Time difference method'] and time_difs_file == parameters.settings['Input/Output Settings']['Input file/folder'])):
        if (parameters.settings['RossiAlpha Settings']['Combine Calc and Binning']):
            calculateTimeDifsAndPlot()
        else:
            createTimeDifs()
            if not parameters.settings['RossiAlpha Settings']['Combine Calc and Binning'] :
                createPlot()
    else:
        createPlot()

def createBestFit():

    global time_difs, histogram, best_fit, parameters
    counts = histogram.counts
    bin_centers = histogram.bin_centers

    best_fit = fit.RossiHistogramFit(counts, bin_centers, parameters.settings)
        
    best_fit.fit_and_residual(save_every_fig=parameters.settings['General Settings']['Save figures'], 
                              show_plot=parameters.settings['General Settings']['Show plots'])

def raAll(single):
    global time_difs, histogram, best_fit
    if single:
        time_difs, histogram, best_fit = mn.analyzeAllType1(parameters.settings)
    else:
        mn.analyzeAllType2(parameters.settings)

def raSplit(mode):
    if parameters.settings['Input/Output Settings']['Input file/folder'] == 'none':
        error('You currently have no input file or folder defined.\n\n'
            + 'Please make sure to specify one before running any analysis.\n')
    else:
        name = parameters.settings['Input/Output Settings']['Input file/folder']
        name = name[name.rfind('/')+1:]
        if name.count('.') > 0:
            if parameters.settings['RossiAlpha Settings']['Time difference method'] != 'any_and_all':
                error('To analyze a single file, you must use '
                    + 'the any_and_all time difference method only.\n')
            else:
                match mode:
                    case 'raAll':
                        raAll(True)
                    case 'createTimeDifs':
                        warning('There are already stored time differences '
                            + 'in this runtime. Do you want to overwrite them?',
                            createTimeDifs)
                    case 'plotSplit':
                        warning('There is an already stored histogram '
                            + 'in this runtime. Do you want to overwrite it?',
                            plotSplit)
                    case 'createBestFit':
                        warning('There is an already stored best fit line '
                            + 'in this runtime. Do you want to overwrite it?',
                            createBestFit)

        else:
            if mode != 'raAll':
                error('You can only run full folder analysis.\n\n'
                      + 'These modular options are for single files.')
            else:
                raAll(False)

def conduct_PSD():
    global parameters

    file_path = parameters.settings['Input/Output Settings']['Input file/folder']

    values = np.loadtxt(file_path, usecols=(0,3), max_rows=2000000, dtype=float)

    PSD_Object = PSD.PowerSpectralDensity(list_data_array=values, 
                                        leg_label="TEST", 
                                        clean_pulses_switch=parameters.settings['PSD Settings']['Clean pulses switch'], 
                                        dwell_time=parameters.settings['PSD Settings']['Dwell time'], 
                                        meas_time_range=parameters.settings['PSD Settings']['Meas time range'])
    
    PSD_Object.conduct_APSD(show_plot=parameters.settings['General Settings']['Show plots'], 
                            save_fig=parameters.settings['General Settings']['Save figures'],
                            save_dir=parameters.settings['Input/Output Settings']['Save directory'])

def printType(value):
    if isinstance(value, list):
        response ='['
        for entry in value:
            response += printType(entry) + ', '
        response = response[0:len(response)-2] + ']'
        return response
    if isinstance(value, bool):
        if value:
            return 'True'
        else:
            return 'False'
    elif isinstance(value, float) and (value > 1000 or value < -1000 or (value < 0.01 and value > -0.01 and value != 0)):
        return "{:e}".format(value)
    else:
        return str(value)

def saveType(value: str):
    if value[0] == '[':
        value = value[1:len(value)-1]
        response = []
        while value.find(', ') != -1:
            response.append(saveType(value[0:value.find(', ')]))
            value=value[value.find(', ')+2:]
        response.append(saveType(value))
        return response
    elif value == 'True':
        return True
    elif value == 'False':
        return False
    elif value.isnumeric():
        return int(value)
    try:
        response = float(value)
        return response
    except ValueError:
        return value

def setMenu(prev):
    global window
    for item in window.winfo_children():
        item.destroy()
    window.title('Settings Editor & Viewer')
    ttk.Label(window,
              name='prompt',
              text='What settings do you want to edit/view?',
              ).grid(column=0,row=0)
    ttk.Button(window,
              name='current',
              text='Current Settings',
              command=lambda: editor_menu(prev)
              ).grid(column=0,row=1)
    ttk.Button(window,
              name='import',
              text='Import settings file',
              command=lambda: download_menu(lambda: setMenu(prev), setMenu, prev)
              ).grid(column=0,row=2)
    ttk.Button(window,
              name='return',
              text='Return to previous menu',
              command=prev
              ).grid(column=0,row=3)

def edit(inputs, prev):
    global parameters
    for group in inputs:
        for setting in inputs[group]:
            parameters.settings[group][setting] = saveType(inputs[group][setting].get())
    setMenu(prev)

def editor_menu(prev):
    global window, parameters
    groupNum=0
    curTop=0
    curMax = 0
    inputs={}
    for item in window.winfo_children():
        item.destroy()
    window.title('View/Edit Current Settings')
    for group in parameters.settings:
        if (groupNum*3) % 9 == 0:
            curTop += curMax
            curMax = 0
        ttk.Label(window,
                  name=group[0:group.find(' Settings')].lower(),
                  text=group[0:group.find(' Settings')] + ':'
                  ).grid(column=(groupNum*3) % 9,row=curTop)
        setNum=1
        for setting in parameters.settings[group]:
            if inputs.get(group) == None:
                inputs[group] = {}
            inputs[group][setting]=tk.StringVar()
            ttk.Label(window,
                  name=(group + ' ' + setting).lower(),
                  text=setting + ':'
                  ).grid(column=(groupNum*3+1) % 9,row=curTop+setNum)
            tk.Entry(window,
                  name=(group + ' ' + setting + ' value').lower(),
                  textvariable=inputs[group][setting]
                  ).grid(column=(groupNum*3+2) % 9,row=curTop+setNum)
            window.children[(group + ' ' + setting + ' value').lower()].insert(0,printType(parameters.settings[group][setting]))
            setNum += 1
        if setNum > curMax:
            curMax = setNum
        groupNum += 1
    curTop += curMax
    ttk.Button(window,
                name='save',
                text='Save changes',
                command=lambda: edit(inputs, prev)
                ).grid(column=0 % 9,row=curTop)
    ttk.Button(window,
                  name='cancel',
                  text='Cancel changes',
                  command=lambda: setMenu(prev)
                  ).grid(column=0 % 9,row=curTop+1)

def raMenu():
    global window
    for item in window.winfo_children():
        item.destroy()
    window.title('Rossi Alpha Analysis')
    ttk.Label(window,
              name='prompt',
              text='What would you like to do?'
              ).grid(column=0,row=0)
    ttk.Button(window,
              name='all',
              text='Run entire analysis',
              command=lambda: raSplit('raAll')
              ).grid(column=0,row=1)
    ttk.Button(window,
              name='time_dif',
              text='Calculate time differences',
              command=lambda: raSplit('createTimeDifs')
              ).grid(column=0,row=2)
    ttk.Button(window,
              name='histogram',
              text='Create histogram',
              command=lambda: raSplit('plotSplit')
              ).grid(column=0,row=3)
    ttk.Button(window,
              name='fit',
              text='Fit data',
              command=lambda: raSplit('createBestFit')
              ).grid(column=0,row=4)
    ttk.Button(window,
              name='settings',
              text='Program settings',
              command=lambda: setMenu(raMenu)
              ).grid(column=0,row=5)
    ttk.Button(window,
              name='return',
              text='Return to main menu',
              command=main
              ).grid(column=0,row=6)

def psdMenu():
    global window
    for item in window.winfo_children():
        item.destroy()
    window.title('Power Spectral Density Analysis')
    ttk.Label(window,
              name='prompt',
              text='What would you like to do?'
              ).grid(column=0,row=0)
    ttk.Button(window,
              name='run',
              text='Run analysis',
              command=conduct_PSD
              ).grid(column=0,row=1)
    ttk.Button(window,
              name='settings',
              text='Program settings',
              command=lambda: setMenu(psdMenu)
              ).grid(column=0,row=2)
    ttk.Button(window,
              name='return',
              text='Return to main menu',
              command=main
              ).grid(column=0,row=3)

def default():
    global parameters
    path = os.path.abspath('default.json')
    parameters.read(path)
    main()

def download_menu(prev, to, param):
    global window
    for item in window.winfo_children():
        item.destroy()
    window.title('Download Settings')
    ttk.Label(window,
              name='choice',
              text='You have two import options:'
              ).grid(column=0,row=0)
    ttk.Button(window,
               name='overwrite',
               text='Overwrite entire settings',
               command=lambda: prompt('Enter a settings file (no .json extension):','Overwrite Settings',lambda: download(False, to, param),lambda: download_menu(prev, to, param))
               ).grid(column=0,row=1)
    ttk.Button(window,
               name='append',
               text='Append settings to default',
               command=lambda: prompt('Enter a settings file (no .json extension):','Append Settings to Default',lambda: download(True, to, param),lambda: download_menu(prev, to, param))
               ).grid(column=0,row=2)
    ttk.Button(window,
               name='cancel',
               text='Cancel',
               command=prev
               ).grid(column=0,row=3)

def download(append, prev, param):
    global window, response, parameters
    file = response.get() + '.json'
    if os.path.isfile(os.path.abspath(file)):
        if append:
            parameters.read(os.path.abspath('default.json'))
            parameters.append(os.path.abspath(file))
        else:
            parameters.read(os.path.abspath(file))
        if param != None:
            prev(param)
        else:
            prev()
    else:
        error(file + ' does not exist in the given directory.\n\n'
            + 'Make sure that your settings file is named correctly, '
            + 'the correct absolute/relative path to it is given, and '
            + 'you did not include the .json extenstion in your input.')

def main():
    global window
    for item in window.winfo_children():
        item.destroy()
    window.title('Main Menu')
    ttk.Label(window,
              name='choice',
              text='You can utilize any of the following functions:'
              ).grid(column=0,row=0)
    ttk.Button(window,
               name='rossi_alpha',
               text='Run Rossi Alpha analysis',
               command=raMenu
               ).grid(column=0,row=1)
    ttk.Button(window,
               name='power_spectral_density',
               text='Run Power Spectral Density analysis',
               command=psdMenu
               ).grid(column=0,row=2)
    ttk.Button(window,
               name='settings',
               text='Edit the program settings',
               command=lambda: setMenu(main)
               ).grid(column=0,row=3)
    ttk.Button(window,
               name='quit',
               text='Quit the program',
               command=lambda: warning('Are you sure you want to quit the program?',window.destroy)
               ).grid(column=0,row=4)

def startup():
    global window, parameters
    if window == None:
        window = Tk()
        window.title('Welcome!')
    else:
        for item in window.winfo_children():
            item.destroy()
    if parameters == None:
        parameters = set.Settings()
    window.grid()
    ttk.Label(window,
            name='welcome',
            text='Welcome to the DNNG/PyNoise project.\n\nWith '
            + 'this software we are taking radiation data from '
            + 'fission reactions \n(recorded by organic scintillators) '
            + 'and analyzing it using various methods and tools.\n\n'
            + 'Use this Python suite to analyze a single file or '
            + 'multiple across numerous folders.\n'
            ).grid(column=0, row=0)
    ttk.Label(window,
            name='choice',
            text='Would you like to use the default settings or import another .json file?'
            ).grid(column=0, row=1)
    ttk.Button(window, name='default', text="Default", command=default).grid(column=0, row=2)
    ttk.Button(window, name='import', text="Import Settings", command=lambda:download_menu(startup, main, None)).grid(column=0, row=3)
    window.mainloop()