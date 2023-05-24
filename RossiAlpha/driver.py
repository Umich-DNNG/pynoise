from settings import *
import sys

setting = Settings()

def ioSet():
    print('What setting would you like to edit?')
    print('')
    print('')
    print('')

def genSet():
    print('What setting would you like to edit?')
    print('')
    print('')
    print('')
    print('')
    print('')
    print('')
    print('')
    print('')
    print('')
    print('')

def visSet():
    print('What setting would you like to edit?')
    print('')
    print('')
    print('')
    print('')
    print('')

def histSet():
    print('What setting would you like to edit?')
    print('')
    print('')
    print('')

def fitSet():
    print('What setting would you like to edit?')
    print('')
    print('')
    print('')
    print('')
    print('')

def resSet():
    print('There is only one residual plot setting - s.')
    print('The current value of s is',setting.get('residual_plot_settings','s'),
          'and must be a float.')
    choice = input('Enter a new value: ')
    if choice.replace(".", "").isnumeric():
        setting.set('','',float(choice))
        print('Set the value of s to ' + choice + '.')
    else:
        print('Your input must be a numeric value')

def settingsEditor():
    selection = ''
    print('What setting group would you like to edit?')
    print('i - input/output settings')
    print('g - general settings')
    print('v - histogram visual settings')
    print('h - histogram generation settings')
    print('l - line fitting settings')
    print('r - residual plot settings')
    print('e - exit to main menu')
    while selection != 'e':
        selection = input('Enter print command: ')
        match selection:
            case 'i':
                ioSet()
            case 'g':
                genSet()
            case 'v':
                visSet()
            case 'h':
                histSet()
            case 'l':
                fitSet()
            case 'r':
                resSet()
            case 'e':
                print('Returning to menu...\n')
                break
            case _:
                print('Unknown input. Use one of the aforementioned commands to select a settings group.')
                print()

def printSelector():
    selection = ''
    print('What settings would you like to view?')
    print('i - input/output settings')
    print('g - general settings')
    print('v - histogram visual settings')
    print('h - histogram generation settings')
    print('l - line fitting settings')
    print('r - residual plot settings')
    print('a - view all settings')
    print('e - exit to main menu')
    while selection != 'e':
        selection = input('Enter print command: ')
        match selection:
            case 'i':
                print()
                setting.print_io()
                print()
            case 'g':
                print()
                setting.print_gen()
                print()
            case 'v':
                setting.print_vis()
                print()
            case 'h':
                print()
                setting.print_hist()
                print()
            case 'l':
                print()
                setting.print_fit()
                print()
            case 'r':
                print()
                setting.print_res()
                print()
            case 'a':
                setting.print_all()
                print()
            case 'e':
                print('Returning to menu...\n')
                break
            case _:
                print('Unknown input. Use one of the aforementioned commands to edit, view, or approve the settings.')
                print()
    

def main():
    selection = ''
    file = ''
    answer = 'n'
    print('Welcome to the DNNG/PyNoise project! With this software we are '
          + 'taking radiation data fission reactions recorded by organic '
          + 'scintillators measuring from fission reactions and applying a '
          + 'line of best fit to the decay rate. Use this Python suite to '
          + 'analyze a single file or multiple across multiple folders.\n')
    print('To begin the program, you must specify an input file or folder.')
    while answer == 'n':
        file = input('Enter a file name or absolute path to a folder: ')
        if len(file) == 0:
            print('You must give a file or folder input to run the program.')
        elif file[0] == '/':
            answer = input('Confirm you are analyzing a folder (y/n): ')
            if answer == 'n':
                print('Make sure you are giving just the '
                      + 'file name to your file, not a path.')
            else:
                setting.set('io_file_info','type',2)
        else:
            answer = input('Confirm you are analyzing a single file (y/n): ')
            if answer == 'n':
                print('Make sure you are giving the absolute path '
                      + 'to your folder, beginning with a /.')
            else:
                setting.set('io_file_info','type',1)
    setting.set('io_file_info','input',file)
    print('Input file and type confirmed.\n')
    print('Choose what settings you would like to run the program with.')
    print("c - continue with the program's current settings")
    print('v - view the current settings')
    print('e - edit the settings')
    print('The program is initialized with default settings.')
    while (selection != 'c'):
        selection = input('Enter menu command: ')
        print()
        match selection:
            case 'c':
                print('Thanks for confirming your settings! You can change these at any time during the running of the program.')
            case 'v':
                printSelector()
                print("c - continue with the program's current settings")
                print('v - view the current settings')
                print('e - edit the settings')
            case 'e':
                settingsEditor()
                print("c - continue with the program's current settings")
                print('v - view the current settings')
                print('e - edit the settings')
            case _:
                print('Unknown input. Use one of the aforementioned commands to edit, view, or approve the settings.')

if __name__ == "__main__":
    main()