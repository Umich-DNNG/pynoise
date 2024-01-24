# Automating Commands

When the user is ready to run analysis, it may become tedious to manually enter each command. For this reason command inputs can be automated by providing the `[-c|--command]` argument when running the PyNoise Suite. 

*Note that `[-c|--command]` can only be run in terminal mode; if combined with `[-g|--gui]`, GUI mode will take precedence over commands.*  

This section will walk through the example of opening the program, importing settings from auto.json, and closing the program. Commands for this would normally be:
* i - import custom settings
* a - append settings to default
* auto - the name of the settings file
* (blank) - exit the program
* q - confirm the quit

## Formatting

Commands will be given to the program upon running `main.py` following the `[-c|--command]` argument. *If you are also providing the `[-q|--quiet]` argument, ensure it is not provided in the middle of these command arguments.* There are two acceptable ways to pass commands:

1. Pass raw commands as arguments. The command line arguments will directly be the commands that would be entered during runtime. For the given example, the formatting would be as follows:

```python3.10 main.py [-c|--commands] i a auto x q```

Note that there is an x for exiting the program, as it is not possible to have empty command line arguments. As such, x is a valid command wherever an empty argument would be valid.

2. Send a file as a command line argument. In this mode, the file you are sending (can be given as an absolute or relative path) will contain a command on each line. As long as the file has as extension (.txt, for example), any file name is valid. The example used here can be viewed in the `input.txt` file.

To run the program with these commands, the call would be:

```python3.10 driver.py [-c|--commands] ./commands/input.txt```

Both of these examples would result in the same code execution. However, note it is possible to have a blank command in the file format. *For this reason, there should be no extra newlines at the end of the file unless the last desired command is a blank command.*

## Flexibility and Restrictions

The automated command input is quite flexibile - it can take in any number of command line arguments, and the user can mix and match raw commands and file names as needed. Furthermore, the commands given to the program do not need to end the program. If the program runs out of given commands, it will prompt the user to enter commands as usual.

Besides the necessity of the x command with raw commands, note there is another restriction on automated commands in that they cannot control vim editing. If an automated command chooses to edit the current settings or append new ones, it will be up to the user to manually do so. However, once the vim editor is closed the automated commands will continue running as normal.