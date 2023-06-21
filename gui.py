from tkinter import *
from tkinter import ttk
import tkinter as tk
import editor as edit
import os

root = None
frame = None
editor = None
response = None

def shutdown():
    global root, frame
    for item in frame.winfo_children():
        item.destroy()
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
    global editor
    path = os.path.abspath('default.json')
    editor.parameters.read(path)
    editor.changeLog()
    editor.log('Settings from default.json succesfully imported.')
    main()

def prompt(message, function):
    global root, frame, response
    response = tk.StringVar()
    for item in frame.winfo_children():
        item.destroy()
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

def download_menu(prev):
    global root, frame
    for item in frame.winfo_children():
        item.destroy()
    ttk.Label(frame,
              name='choice',
              text='You have two import options:'
              ).grid(column=0,row=0)
    ttk.Button(frame,
               name='overwrite',
               text='Overwrite entire settings',
               command=lambda: prompt('Enter a settings file (no .json extension):',lambda: download(False))
               ).grid(column=0,row=1)
    ttk.Button(frame,
               name='append',
               text='Append settings to default',
               command=lambda: prompt('Enter a settings file (no .json extension):',lambda: download(True))
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

def download(append):
    global root, response, editor
    file = response.get() + '.json'
    if os.path.isfile(os.path.abspath(file)):
        if append:
            editor.parameters.read(os.path.abspath('default.json'))
            editor.parameters.append(os.path.abspath(file))
            editor.changeLog()
            editor.log('Settings from ' + file + ' succesfully'
                        + ' appended to the default.')
        else:
            editor.parameters.read(os.path.abspath(file))
            editor.changeLog()
            editor.log('Settings from ' + file + ' succesfully imported.')
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
    ttk.Label(frame,
              name='choice',
              text='You can utilize any of the following functions:'
              ).grid(column=0,row=0)
    ttk.Button(frame,
               name='rossi_alpha',
               text='Run Rossi Alpha analysis'
               ).grid(column=0,row=1)
    ttk.Button(frame,
               name='power_spectral_density',
               text='Run Power Spectral Density analysis'
               ).grid(column=0,row=2)
    ttk.Button(frame,
               name='settings',
               text='Edit the program settings'
               ).grid(column=0,row=3)
    ttk.Button(frame,
               name='quit',
               text='Quit the program',
               command=shutdown
               ).grid(column=0,row=4)

def startup():
    global root, frame, editor
    if root == None:
        root = Tk()
        root.title('PyNoise')
    if frame == None:
        frame = ttk.Frame(root, name='startup_menu', padding=10)
    else:
        for item in frame.winfo_children():
            item.destroy()
    if editor == None:
        editor = edit.Editor()
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