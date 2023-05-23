from settings import *
import sys

setting = Settings()

def settingsEditor():
    print('TODO')

def printSelector():
    selection = input('What settings would you like to view? Enter i for input/output '
                    + 'settings, g for general settings, v for histogram visual '
                    + 'settings, h for histogram generation settings, l for line '
                    + 'fitting settings, r for residual plot settings, and a to '
                    + 'view all settings.')

def main():
    selection = ''
    print('Welcome to the DNNG/PyNoise project! With this software we are '
          + 'taking radiation data fission reactions recorded by organic '
          + 'scintillators measuring from fission reactions and applying a '
          + 'line of best fit to the decay rate. Use this Python suite to '
          + 'analyze a single file or multiple across multiple folders.\n')
    while (selection != 'c'):
        selection = input("Type c to continue with the program's default settings, v to "
                        + "view the current settings, and e to edit the settings.")
        if selection == 'c':
            print('Thanks for confirming your settings! You can change these at any time during the running of the program.')
        elif selection == 'v':
            printSelector()
        elif selection == 'e':
            settingsEditor()
        else:
            print('Unknown input. Use one of the aforementioned commands to edit, view, or approve the settings.')

if __name__ == "__main__":
    main()