from settings import *
import sys

setting = Settings()

def settingsEditor():
    print('TODO')
    print('Returning to menu...\n')

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
    print('Welcome to the DNNG/PyNoise project! With this software we are '
          + 'taking radiation data fission reactions recorded by organic '
          + 'scintillators measuring from fission reactions and applying a '
          + 'line of best fit to the decay rate. Use this Python suite to '
          + 'analyze a single file or multiple across multiple folders.\n')
    print('To begin the program, you must specify your settings:')
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