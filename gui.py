from tkinter import *
from tkinter import ttk
import tkinter as tk
import settings as set
import os

root = None
frame = None
parameters = None
response = None

def prompt(message, title, function, prev):
    global root, frame, response
    response = tk.StringVar()
    for item in frame.winfo_children():
        item.destroy()
    root.title(title)
    ttk.Label(frame,
              name='prompt',
              text=message
              ).grid(column=0,row=0)
    ttk.Entry(frame,
              name='response',
              textvariable=response,
              ).grid(column=0,row=1)
    ttk.Button(frame,
              name='continue',
              text='Continue',
              command=function
              ).grid(column=0,row=2)
    ttk.Button(frame,
              name='cancel',
              text='Cancel',
              command=prev
              ).grid(column=0,row=3)
    
def error(message):
    root=Tk()
    root.title('Uh oh!')
    frame = ttk.Frame(root, name='error_menu', padding=10)
    frame.grid()
    ttk.Label(frame,
            name='message',
            text=message
            ).grid(column=0,row=0)
    ttk.Button(frame,
               name='return',
               text='OK',
               command=root.destroy
               ).grid(column=0,row=1)
    root.mainloop()

def editor_menu(append):
    global root, frame, parameters
    groupNum=0
    inputs=[]
    for item in frame.winfo_children():
        item.destroy()
    if append:
        root.title('Append Settings')
    else:
        root.title('View/Edit Current Settings')
    for group in parameters.settings:
        ttk.Label(frame,
                  name=group.lower(),
                  text=group + ':'
                  ).grid(column=(groupNum*3) % 6,row=groupNum)
        setNum=0
        for setting in parameters.settings[group]:
            inputs.append(tk.StringVar(value=parameters.settings[group][setting]))
            ttk.Label(frame,
                  name=(group + ' ' + setting).lower(),
                  text=setting + ':'
                  ).grid(column=(groupNum*3+1) % 6,row=groupNum+setNum)
            ttk.Entry(frame,
                  name=(group + ' ' + setting + ' value').lower(),
                  textvariable=inputs[len(inputs)-1]
                  ).grid(column=(groupNum*3+2) % 6,row=groupNum+setNum)
            setNum += 1
        groupNum += 1


def setMenu():
    global root, frame
    for item in frame.winfo_children():
        item.destroy()
    root.title('Settings Editor & Viewer')
    ttk.Label(frame,
              name='prompt',
              text='What settings do you want to edit/view?',
              ).grid(column=0,row=0)
    ttk.Button(frame,
              name='current',
              text='Current Settings',
              command=lambda: editor_menu(False)
              ).grid(column=0,row=1)
    ttk.Button(frame,
              name='import',
              text='Import settings file'
              ).grid(column=0,row=2)
    ttk.Button(frame,
              name='append',
              text='Append settings',
              command=lambda: editor_menu(True)
              ).grid(column=0,row=3)
    ttk.Button(frame,
              name='return',
              text='Return to main menu',
              command=main
              ).grid(column=0,row=4)

def raMenu():
    global root, frame
    for item in frame.winfo_children():
        item.destroy()
    root.title('Rossi Alpha Analysis')
    ttk.Label(frame,
              name='prompt',
              text='What analysis would you like to perform?'
              ).grid(column=0,row=0)
    ttk.Button(frame,
              name='all',
              text='Run entire analysis'
              ).grid(column=0,row=1)
    ttk.Button(frame,
              name='time_dif',
              text='Calculate time differences'
              ).grid(column=0,row=2)
    ttk.Button(frame,
              name='histogram',
              text='Create histogram'
              ).grid(column=0,row=3)
    ttk.Button(frame,
              name='fit',
              text='Fit data'
              ).grid(column=0,row=4)
    ttk.Button(frame,
              name='settings',
              text='Program settings',
              command=setMenu
              ).grid(column=0,row=5)
    ttk.Button(frame,
              name='return',
              text='Return to main menu',
              command=main
              ).grid(column=0,row=6)

def psdMenu():
    global root, frame
    for item in frame.winfo_children():
        item.destroy()
    root.title('Power Spectral Density Analysis')
    ttk.Label(frame,
              name='prompt',
              text='What analysis would you like to perform?'
              ).grid(column=0,row=0)
    ttk.Button(frame,
              name='settings',
              text='Program settings'
              ).grid(column=0,row=5)
    ttk.Button(frame,
              name='return',
              text='Return to main menu',
              command=main
              ).grid(column=0,row=6)

def shutdown():
    global root
    for item in frame.winfo_children():
        item.destroy()
    root.title('Confirm shutdown')
    ttk.Label(frame,
              name='message',
              text='Are you sure you want to quit the program?'
              ).grid(column=0,row=0)
    ttk.Button(frame,
              name='yes',
              text='Yes',
              command=root.destroy
              ).grid(column=0,row=1)
    ttk.Button(frame,
              name='no',
              text='No',
              command=main
              ).grid(column=0,row=2)

def default():
    global parameters
    path = os.path.abspath('default.json')
    parameters.read(path)
    main()

def download_menu(prev):
    global root, frame
    for item in frame.winfo_children():
        item.destroy()
    root.title('Download Settings')
    ttk.Label(frame,
              name='choice',
              text='You have two import options:'
              ).grid(column=0,row=0)
    ttk.Button(frame,
               name='overwrite',
               text='Overwrite entire settings',
               command=lambda: prompt('Enter a settings file (no .json extension):','Overwrite Settings',lambda: download(False),lambda: download_menu(prev))
               ).grid(column=0,row=1)
    ttk.Button(frame,
               name='append',
               text='Append settings to default',
               command=lambda: prompt('Enter a settings file (no .json extension):','Append Settings to Default',lambda: download(True),lambda: download_menu(prev))
               ).grid(column=0,row=2)
    ttk.Button(frame,
               name='cancel',
               text='Cancel',
               command=prev
               ).grid(column=0,row=3)

def download(append):
    global root, response, parameters
    file = response.get() + '.json'
    if os.path.isfile(os.path.abspath(file)):
        if append:
            parameters.read(os.path.abspath('default.json'))
            parameters.append(os.path.abspath(file))
        else:
            parameters.read(os.path.abspath(file))
        main()
    else:
        error('ERROR: ' + file + ' does not exist in the given directory.\n\n'
            + 'Make sure that your settings file is named correctly, '
            + 'the correct absolute/relative path to it is given, and '
            + 'you did not include the .json extenstion in your input.')

def main():
    global root, frame
    for item in frame.winfo_children():
        item.destroy()
    root.title('Main Menu')
    ttk.Label(frame,
              name='choice',
              text='You can utilize any of the following functions:'
              ).grid(column=0,row=0)
    ttk.Button(frame,
               name='rossi_alpha',
               text='Run Rossi Alpha analysis',
               command=raMenu
               ).grid(column=0,row=1)
    ttk.Button(frame,
               name='power_spectral_density',
               text='Run Power Spectral Density analysis'
               ).grid(column=0,row=2)
    ttk.Button(frame,
               name='settings',
               text='Edit the program settings',
               command=setMenu
               ).grid(column=0,row=3)
    ttk.Button(frame,
               name='quit',
               text='Quit the program',
               command=shutdown
               ).grid(column=0,row=4)

def startup():
    global root, frame, parameters
    if root == None:
        root = Tk()
        root.title('Welcome!')
    if frame == None:
        frame = ttk.Frame(root, name='startup_menu', padding=10)
    else:
        for item in frame.winfo_children():
            item.destroy()
    if parameters == None:
        parameters = set.Settings()
    frame.grid()
    ttk.Label(frame,
            name='welcome',
            text='Welcome to the DNNG/PyNoise project.\n\nWith '
            + 'this software we are taking radiation data from '
            + 'fission reactions \n(recorded by organic scintillators) '
            + 'and analyzing it using various methods and tools.\n\n'
            + 'Use this Python suite to analyze a single file or '
            + 'multiple across numerous folders.\n'
            ).grid(column=0, row=0)
    ttk.Label(frame,
            name='choice',
            text='Would you like to use the default settings or import another .json file?'
            ).grid(column=0, row=1)
    ttk.Button(frame, name='default', text="Default", command=default).grid(column=0, row=2)
    ttk.Button(frame, name='import', text="Import Settings", command=lambda:download_menu(startup)).grid(column=0, row=3)
    root.mainloop()