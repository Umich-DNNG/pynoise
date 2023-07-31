'''The program that should be run whenever the user wants to do analysis.'''



# Necessary imports.
import sys
import driver as drv
import gui



def main():

    '''The main function that starts the whole program.'''


    # Try to find the -g command-line 
    # argument and start the gui if found.
    try:
        sys.argv.index('-g')
        gui.startup()
    # If not found:
    except ValueError:
        # Try to find the --gui command-line 
        # argument and start the gui if found.
        try:
            sys.argv.index('--gui')
            gui.startup()
        # If not found, run the terminal driver.
        except ValueError:
            drv.main()



# Tells the program what function to run when this 
# is the program that is called on the terminal.
if __name__ == "__main__":
    main()