'''The file that creates and runs all program GUI elements.'''

from tkinter import *
from tkinter import ttk
import tkinter as tk
import settings as set
import os
import run

# The main window that is used for the program.
window = None
# The settings used during runtime
parameters = None

def prompt(prev, to, message='Enter your choice:', title='User Prompt'):

    '''Create a prompt window to get a text input from the user.
    
    Requires:
    - prev: the function to return to if the user cancels the input.
    - to: the function that is called when the user confirms their input.
    
    Optional:
    - message: the message that the user sees above the entry box.
    - title: the title of the window'''

    global window
    response = tk.StringVar()
    # Clear the window of all previous entries, labels, and buttons.
    for item in window.winfo_children():
        item.destroy()
    # Properly name the window.
    window.title(title)
    # The label with the appropriate prompt message.
    ttk.Label(window,
              name='prompt',
              text=message
              ).grid(column=0,row=0)
    # The text box where the user can type their response.
    ttk.Entry(window,
              name='response',
              textvariable=response,
              ).grid(column=0,row=1)
    # The confirmation button.
    ttk.Button(window,
              name='continue',
              text='Continue',
              command=lambda: to(response.get())
              ).grid(column=0,row=2)
    # The cancel button.
    ttk.Button(window,
              name='cancel',
              text='Cancel',
              command=prev
              ).grid(column=0,row=3)
    
def error(message='Something went wrong. Please contact the developers.',
          title='ERROR!'):
    '''Create an error popup for when the user encounters an error.
    
    Parameters:
    - message: the error message that the user will see.
    - title: the title of the window.
    
    If no parameters are given, a default error popup is shown. '''

    # Create a new popup and title it accordingly.
    popup=Tk()
    popup.title(title)
    # The label with the appropriate error message.
    ttk.Label(popup,
            name='message',
            text=message
            ).grid(column=0,row=0)
    # The button to confirm the user has seen the error.
    ttk.Button(popup,
               name='return',
               text='OK',
               command=popup.destroy
               ).grid(column=0,row=1)
    # Open the popup.
    popup.mainloop()

def warning(to,
            message='This action will delete data. Are you sure you want to do this?',
            title='WARNING!'):

    '''Display a warning popup when the user is at risk of deleting/overwriting data.
    
    Requires:
    - to: the function to be called should the user choose to ignore the warning.
    
    Optional:
    - message: the warning the user will receive.
    - title: the title of the popup.'''

    # Create a new popup and title it accordingly.
    popup=Tk()
    popup.title(title)
    # The label with the appropriate warning message.
    ttk.Label(popup,
            name='message',
            text=message
            ).grid(column=0,row=0)
    # The yes button.
    ttk.Button(popup,
               name='yes',
               text='Yes',
               command=lambda: run.warningFunction(popup, to)
               ).grid(column=0,row=1)
    # The no button.
    ttk.Button(popup,
               name='no',
               text='No',
               command=popup.destroy
               ).grid(column=0,row=2)
    # Open the popup.
    popup.mainloop()

def shutdown_menu():

    '''Load the shutdown menu GUI if need be.'''

    global window, parameters
    # Compare the current settings to the most recently 
    # imported + appended and store the changes.
    list = parameters.compare()
    # If there were changes from the baseline.
    if len(list) != 0:
        # Clear the window of all previous entries, labels, and buttons.
        for item in window.winfo_children():
            item.destroy()
        # Properly name the window.
        window.title('Unsaved Changes')
        # Notify the user of unsaved changes and note their
        # most recently imported and appended settings.
        ttk.Label(window,
                name='message',
                text='You have made unsaved changes to the settings:\n\n'
                + 'Base settings: ' + parameters.origin + '\n\nMost recently '
                + 'appended settings: ' + parameters.appended + '\n'
                ).grid(column=0,row=0)
        # Keep track of the total listed changes.
        total = 0
        # For up to 5 entries in the list.
        while total != 5 and total < len(list):
            # List the entry.
            ttk.Label(window,
                name='entry' + str(total),
                text=list[total]
                ).grid(column=0,row=total+1)
            # Increase the count.
            total += 1
        # If there were more than 5 entries,
        # note how many more there are.
        if len(list) > 5:
            ttk.Label(window,
                name='extra',
                text='\n...plus ' + str(len(list)-5) + ' more change(s).'
                ).grid(column=0,row=6)
            total += 1
        # Ask the user what they want to do.
        ttk.Label(window,
                name='prompt',
                text='\nWhat would you like to do with your changes?'
                ).grid(column=0,row=total+1)
        # Button for saving current settings to the default.
        ttk.Button(window,
                name='default',
                text='Save as default',
                command=lambda: warning(lambda: run.shutdown(window, parameters, os.path.abspath('default.json')))
                ).grid(column=0,row=total+2)
        # Button for saving current settings to another file.
        ttk.Button(window,
                name='new',
                text='Save to other file',
                command=lambda: prompt(shutdown_menu,
                                       lambda file: run.shutdown(window, parameters, os.path.abspath(file+'.json')),
                                       'Enter a name for the new settings '
                                        + '(not including the .json file extension).',
                                        'Export Settings',)
                ).grid(column=0,row=total+3)
        # Button for discarding the current settings.
        ttk.Button(window,
                name='discard',
                text='Discard changes',
                command=lambda: warning(window.destroy,
                                        'All your current changes will be lost. '
                                        + 'Are you sure you want to do this?')
                ).grid(column=0,row=total+4)
    # If no changes, program can just end here.
    else:
        window.destroy()

def setMenu(prev):

    '''The GUI for the settings menu.
    
    Requires:
    - prev: the GUI function for the previous menu.'''

    global window
    # Clear the window of all previous entries, labels, and buttons.
    for item in window.winfo_children():
        item.destroy()
    # Properly name the window.
    window.title('Settings Editor & Viewer')
    # Lable to prompt the user.
    ttk.Label(window,
              name='prompt',
              text='What settings do you want to edit/view?',
              ).grid(column=0,row=0)
    # Button to edit/view current settings.
    ttk.Button(window,
              name='current',
              text='Current Settings',
              command=lambda: editor_menu(prev)
              ).grid(column=0,row=1)
    # Button to import settings files.
    ttk.Button(window,
              name='import',
              text='Import settings file',
              command=lambda: download_menu(lambda: setMenu(prev), lambda: setMenu(prev))
              ).grid(column=0,row=2)
    # Button to return to the previous menu.
    ttk.Button(window,
              name='return',
              text='Return to previous menu',
              command=prev
              ).grid(column=0,row=3)

def editor_menu(prev):

    '''The GUI for the editor menu.
    
    Requires:
    - prev: the GUI function for the menu 
    to return to after the settings menu.'''

    global window, parameters
    groupNum=0
    curTop=0
    curMax = 0
    # Initialize inputs dictionary (assume settings groups are constant).
    inputs={'Input/Output Settings': {},
            'General Settings': {},
            'RossiAlpha Settings': {},
            'PSD Settings': {},
            'Histogram Visual Settings': {},
            'Line Fitting Settings': {},
            'Residual Plot Settings': {},}
    # Clear the window of all previous entries, labels, and buttons.
    for item in window.winfo_children():
        item.destroy()
    # Properly name the window.
    window.title('View/Edit Current Settings')
    # For each group in the settings.
    for group in parameters.settings:
        # If the start of a new row, add the previous current maximum 
        # to the current top and reset the current maximum variable. 
        if (groupNum*3) % 9 == 0:
            curTop += curMax
            curMax = 0
        # The label for the settings group.
        ttk.Label(window,
                  name=group[0:group.find(' Settings')].lower(),
                  text=group[0:group.find(' Settings')] + ':'
                  ).grid(column=(groupNum*3) % 9,row=curTop)
        # Reset the settings number (1-indexed)
        setNum=1
        # For each setting in the group.
        for setting in parameters.settings[group]:
            # Create a string variable linked to 
            # this setting in the inputs dictionary.
            inputs[group][setting]=tk.StringVar()
            # The label for the setting name.
            ttk.Label(window,
                  name=(group + ' ' + setting).lower(),
                  text=setting + ':'
                  ).grid(column=(groupNum*3+1) % 9,row=curTop+setNum)
            # The entry box for inputting/viewing the setting value.
            tk.Entry(window,
                  name=(group + ' ' + setting + ' value').lower(),
                  textvariable=inputs[group][setting]
                  ).grid(column=(groupNum*3+2) % 9,row=curTop+setNum)
            # Insert into the entry box the current value of the setting.
            window.children[(group + ' ' + setting + ' value').lower()].insert(0,run.format(parameters.settings[group][setting]))
            # Increase the setting number.
            setNum += 1
        # If the total settings in this group were the max 
        # in this row, set the current max to this value.
        if setNum > curMax:
            curMax = setNum
        # Increase the group number.
        groupNum += 1
    # Add the previous current maximum to 
    # the current top for button formatting.
    curTop += curMax
    # Button for saving changes.
    ttk.Button(window,
                name='save',
                text='Save changes',
                command=lambda: run.edit(inputs, parameters, prev)
                ).grid(column=0 % 9,row=curTop)
    # Button for canceling changes.
    ttk.Button(window,
                  name='cancel',
                  text='Cancel changes',
                  command=lambda: setMenu(prev)
                  ).grid(column=0 % 9,row=curTop+1)

def raMenu():

    '''The GUI for the Rossi Alpha menu.'''

    global window, parameters
    # Clear the window of all previous entries, labels, and buttons.
    for item in window.winfo_children():
        item.destroy()
    # Properly name the window.
    window.title('Rossi Alpha Analysis')
    # Prompt the user.
    ttk.Label(window,
              name='prompt',
              text='What would you like to do?'
              ).grid(column=0,row=0)
    # Button for running all analysis.
    ttk.Button(window,
              name='all',
              text='Run entire analysis',
              command=lambda: run.raSplit('raAll', parameters)
              ).grid(column=0,row=1)
    # Button for calculating time differences.
    ttk.Button(window,
              name='time_dif',
              text='Calculate time differences',
              command=lambda: run.raSplit('createTimeDifs', parameters)
              ).grid(column=0,row=2)
    # Button for creating a histogram.
    ttk.Button(window,
              name='histogram',
              text='Create histogram',
              command=lambda: run.raSplit('plotSplit', parameters)
              ).grid(column=0,row=3)
    # Button for creating a line fit + residual.
    ttk.Button(window,
              name='fit',
              text='Fit data',
              command=lambda: run.raSplit('createBestFit', parameters)
              ).grid(column=0,row=4)
    # Button to view the program settings.
    ttk.Button(window,
              name='settings',
              text='Program settings',
              command=lambda: setMenu(raMenu)
              ).grid(column=0,row=5)
    # Button to return to the main menu.
    ttk.Button(window,
              name='return',
              text='Return to main menu',
              command=main
              ).grid(column=0,row=6)

def psdMenu():

    '''The GUI for the Power Spectral Density menu.'''

    global window, parameters
    # Clear the window of all previous entries, labels, and buttons.
    for item in window.winfo_children():
        item.destroy()
    # Properly name the window.
    window.title('Power Spectral Density Analysis')
    # Prompt the user.
    ttk.Label(window,
              name='prompt',
              text='What would you like to do?'
              ).grid(column=0,row=0)
    # Button to run analysis.
    ttk.Button(window,
              name='run',
              text='Run analysis',
              command=lambda: run.conduct_PSD(parameters)
              ).grid(column=0,row=1)
    # Button to view the program settings.
    ttk.Button(window,
              name='settings',
              text='Program settings',
              command=lambda: setMenu(psdMenu)
              ).grid(column=0,row=2)
    # Button to return to the main menu.
    ttk.Button(window,
              name='return',
              text='Return to main menu',
              command=main
              ).grid(column=0,row=3)

def download_menu(prev, to):

    '''The GUI for the settings download menu.'''

    global window, parameters
    # Clear the window of all previous entries, labels, and buttons.
    for item in window.winfo_children():
        item.destroy()
    # Properly name the window.
    window.title('Download Settings')
    # Notify the user of the different import options.
    ttk.Label(window,
              name='choice',
              text='You have two import options:'
              ).grid(column=0,row=0)
    # Button for overwriting the entire settings.
    ttk.Button(window,
               name='overwrite',
               text='Overwrite entire settings',
               command=lambda: prompt(lambda: download_menu(prev, to),
                                      lambda file: run.download(parameters, os.path.abspath(file + '.json'), False, to),
                                      'Enter a settings file (no .json extension):',
                                      'Overwrite Settings')
               ).grid(column=0,row=1)
    # Button for appending settings to the current settings.
    ttk.Button(window,
               name='append',
               text='Append settings',
               command=lambda: prompt(lambda: download_menu(prev, to),
                                      lambda file: run.download(parameters, os.path.abspath(file + '.json'), True, to),
                                      'Enter a settings file (no .json extension):',
                                      'Append Settings to Default')
               ).grid(column=0,row=2)
    # Button for canceling settings import.
    ttk.Button(window,
               name='cancel',
               text='Cancel',
               command=prev
               ).grid(column=0,row=3)

def main():

    '''The GUI for the main menu.'''

    global window
    # Clear the window of all previous entries, labels, and buttons.
    for item in window.winfo_children():
        item.destroy()
    # Properly name the window.
    window.title('Main Menu')
    # Prompt the user.
    ttk.Label(window,
              name='choice',
              text='You can utilize any of the following functions:'
              ).grid(column=0,row=0)
    # Button to run Rossi Alpha analysis. 
    ttk.Button(window,
               name='rossi_alpha',
               text='Run Rossi Alpha analysis',
               command=raMenu
               ).grid(column=0,row=1)
    # Button to run Power Spectral Density analysis. 
    ttk.Button(window,
               name='power_spectral_density',
               text='Run Power Spectral Density analysis',
               command=psdMenu
               ).grid(column=0,row=2)
    # Button to edit the program settings.
    ttk.Button(window,
               name='settings',
               text='Edit the program settings',
               command=lambda: setMenu(main)
               ).grid(column=0,row=3)
    # Button to exit the program.
    ttk.Button(window,
               name='quit',
               text='Quit the program',
               command=lambda: warning(shutdown_menu,
                                       'Are you sure you want to quit the program?',
                                       'Shutdown Confirmation')
               ).grid(column=0,row=4)

def startup():

    '''The GUI for the startup menu.'''

    global window, parameters
    # If window is not yet defined, create it and grid it.
    if window == None:
        window = Tk()
        window.grid()
    # Otherwise, clear the window of all 
    # previous entries, labels, and buttons.
    else:
        for item in window.winfo_children():
            item.destroy()
    # Properly name the window.
    window.title('Welcome!')
    # If settings are not yet defined, construct an empty settings object.
    if parameters == None:
        parameters = set.Settings()
    # Welcome information for the user.
    ttk.Label(window,
            name='welcome',
            text='Welcome to the DNNG/PyNoise project.\n\nWith '
            + 'this software we are taking radiation data from '
            + 'fission reactions \n(recorded by organic scintillators) '
            + 'and analyzing it using various methods and tools.\n\n'
            + 'Use this Python suite to analyze a single file or '
            + 'multiple across numerous folders.\n'
            ).grid(column=0, row=0)
    # Prompt the user.
    ttk.Label(window,
            name='choice',
            text='Would you like to use the default '
            + 'settings or import another .json file?'
            ).grid(column=0, row=1)
    # Button for importing the default settings.
    ttk.Button(window,
               name='default',
               text="Default",
               command=lambda:run.download(parameters,os.path.abspath('default.json'),False,main)
               ).grid(column=0, row=2)
    # Button for importing other settings.
    ttk.Button(window,
               name='import',
               text="Import Settings",
               command=lambda:download_menu(startup, main)
               ).grid(column=0, row=3)
    # Run the window.
    window.mainloop()