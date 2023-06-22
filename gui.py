from tkinter import *
from tkinter import ttk
import tkinter as tk
import settings as set
import os

window = None
parameters = None
response = None

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
    window.title('Uh oh!')
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

def edit(append):
    print('TODO!!!')

def editor_menu(append):
    global window, parameters
    groupNum=0
    curTop=0
    curMax = 0
    inputs=[]
    for item in window.winfo_children():
        item.destroy()
    if append:
        window.title('Append Settings')
    else:
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
            inputs.append(tk.StringVar())
            ttk.Label(window,
                  name=(group + ' ' + setting).lower(),
                  text=setting + ':'
                  ).grid(column=(groupNum*3+1) % 9,row=curTop+setNum)
            tk.Entry(window,
                  name=(group + ' ' + setting + ' value').lower(),
                  textvariable=inputs[len(inputs)-1]
                  ).grid(column=(groupNum*3+2) % 9,row=curTop+setNum)
            if isinstance(parameters.settings[group][setting], bool):
                if parameters.settings[group][setting]:
                    window.children[(group + ' ' + setting + ' value').lower()].insert(0,'True')
                else:
                    window.children[(group + ' ' + setting + ' value').lower()].insert(0,'False')
            elif isinstance(parameters.settings[group][setting], float) and (parameters.settings[group][setting] > 1000 or parameters.settings[group][setting] < 0.01):
                window.children[(group + ' ' + setting + ' value').lower()].insert(0,"{:e}".format(parameters.settings[group][setting]))
            else:
                window.children[(group + ' ' + setting + ' value').lower()].insert(0,parameters.settings[group][setting])
            setNum += 1
        if setNum > curMax:
            curMax = setNum
        groupNum += 1
    curTop += curMax
    ttk.Button(window,
                name='save',
                text='Save changes',
                command=lambda: edit(append)
                ).grid(column=0 % 9,row=curTop)
    ttk.Button(window,
                  name='cancel',
                  text='Cancel changes',
                  command=setMenu
                  ).grid(column=0 % 9,row=curTop+1)


def setMenu():
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
              command=lambda: editor_menu(False)
              ).grid(column=0,row=1)
    ttk.Button(window,
              name='import',
              text='Import settings file',
              command=lambda: download_menu(setMenu, setMenu)
              ).grid(column=0,row=2)
    ttk.Button(window,
              name='append',
              text='Append settings',
              command=lambda: editor_menu(True)
              ).grid(column=0,row=3)
    ttk.Button(window,
              name='return',
              text='Return to main menu',
              command=main
              ).grid(column=0,row=4)

def raMenu():
    global window
    for item in window.winfo_children():
        item.destroy()
    window.title('Rossi Alpha Analysis')
    ttk.Label(window,
              name='prompt',
              text='What analysis would you like to perform?'
              ).grid(column=0,row=0)
    ttk.Button(window,
              name='all',
              text='Run entire analysis'
              ).grid(column=0,row=1)
    ttk.Button(window,
              name='time_dif',
              text='Calculate time differences'
              ).grid(column=0,row=2)
    ttk.Button(window,
              name='histogram',
              text='Create histogram'
              ).grid(column=0,row=3)
    ttk.Button(window,
              name='fit',
              text='Fit data'
              ).grid(column=0,row=4)
    ttk.Button(window,
              name='settings',
              text='Program settings',
              command=setMenu
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
              text='What analysis would you like to perform?'
              ).grid(column=0,row=0)
    ttk.Button(window,
              name='settings',
              text='Program settings'
              ).grid(column=0,row=5)
    ttk.Button(window,
              name='return',
              text='Return to main menu',
              command=main
              ).grid(column=0,row=6)

def shutdown():
    global window
    for item in window.winfo_children():
        item.destroy()
    window.title('Confirm shutdown')
    ttk.Label(window,
              name='message',
              text='Are you sure you want to quit the program?'
              ).grid(column=0,row=0)
    ttk.Button(window,
              name='yes',
              text='Yes',
              command=window.destroy
              ).grid(column=0,row=1)
    ttk.Button(window,
              name='no',
              text='No',
              command=main
              ).grid(column=0,row=2)

def default():
    global parameters
    path = os.path.abspath('default.json')
    parameters.read(path)
    main()

def download_menu(prev, to):
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
               command=lambda: prompt('Enter a settings file (no .json extension):','Overwrite Settings',lambda: download(False, to),lambda: download_menu(prev, to))
               ).grid(column=0,row=1)
    ttk.Button(window,
               name='append',
               text='Append settings to default',
               command=lambda: prompt('Enter a settings file (no .json extension):','Append Settings to Default',lambda: download(True, to),lambda: download_menu(prev, to))
               ).grid(column=0,row=2)
    ttk.Button(window,
               name='cancel',
               text='Cancel',
               command=prev
               ).grid(column=0,row=3)

def download(append, prev):
    global window, response, parameters
    file = response.get() + '.json'
    if os.path.isfile(os.path.abspath(file)):
        if append:
            parameters.read(os.path.abspath('default.json'))
            parameters.append(os.path.abspath(file))
        else:
            parameters.read(os.path.abspath(file))
        prev()
    else:
        error('ERROR: ' + file + ' does not exist in the given directory.\n\n'
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
               text='Run Power Spectral Density analysis'
               ).grid(column=0,row=2)
    ttk.Button(window,
               name='settings',
               text='Edit the program settings',
               command=setMenu
               ).grid(column=0,row=3)
    ttk.Button(window,
               name='quit',
               text='Quit the program',
               command=shutdown
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
    ttk.Button(window, name='import', text="Import Settings", command=lambda:download_menu(startup, main)).grid(column=0, row=3)
    window.mainloop()