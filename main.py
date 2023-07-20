import sys
import driver as drv
import gui

def main():
    try:
        sys.argv.index('-g')
        gui.startup()
    except ValueError:
        try:
            sys.argv.index('--gui')
            gui.startup()
        except ValueError:
            drv.main()

if __name__ == "__main__":
    main()