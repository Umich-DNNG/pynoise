from tkinter import *
from tkinter import ttk
import editor as edit

root = None
frame = None
editor = None

def default():
    #TODO: Import default settings.
    main()

def shutdown():
    global root, frame
    frame.children['choice'].destroy()
    frame.children['rossi_alpha'].destroy()
    frame.children['power_spectral_density'].destroy()
    frame.children['settings'].destroy()
    frame.children['quit'].destroy()
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

def main():
    global root, frame
    frame.destroy()
    frame = ttk.Frame(root, name='main_menu', padding=10)
    frame.grid()
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
    root = Tk()
    root.title('PyNoise')
    frame = ttk.Frame(root, name='startup_menu', padding=10)
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
    ttk.Button(frame, name='import', text="Import Settings", command=root.destroy).grid(column=0, row=3)
    root.mainloop()