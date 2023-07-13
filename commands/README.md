# Automating Commands

When the user wants to run the same thing multiple times, it may become tedious to manually enter each command. For this reason command inputs can be automated in two different ways. This section will walk through the example of opening the program, importing settings from auto.json, and closing the program. Commands for this would normally be:
* i - import custom settings
* a - append settings to default
* auto - the name of the settings file
* (blank) - exit the program
* q - confirm the quit
With both options, the commands need to be preceded by ```--command``` *or* ```-c```. The lets the the program know where to start reading command line arguments as program commands.

## Formatting

Commands can be handed to the program through command line arguments when calling the program. There are two acceptable ways to pass commands:

1. Send raw commands as command line arguments. In this mode, the command line arguments can directly be the commands that would be entered during runtime. For the example, the formatting would be as follows:

```python3.10 driver.py --commands i a auto x q```

Alternatively:

```python3.10 driver.py -c i a auto x q```

Note that instead of an empty input for exiting the program, there is an x instead. This is because it is not possible to have empty command line arguments. As such, x is also a valid command for returning from submenus (Rossi Alpha, Power Spectral Density, and Settings Editor) as well as exiting the program. However, be aware that it is not acceptable to use an x command in any other circumstance. If a blank command is needed, use the following option to pass commands.

2. Send a file as a command line argument. In this mode, the file you are sending (can be given as an absolute or relative path) will contain a command on each line. As long as the file has as extension (.txt, for example), any file name is valid. In this example, the file will be called ```input.txt``` and will be formatted as follows:

```input.txt```:

i

a

auto

(blank)

q


Then, to run the program with these commands (in this case assuming input.txt is in the same folder as driver.py), the command line call would be:

```python3.10 driver.py --commands input.txt```

Alternatively:

```python3.10 driver.py -c input.txt```

Both of these examples would result in the same code execution. However, note it is possible to have a blank command in the file format (the (blank) text is just a placeholder - see the input.txt file included in this package for a literal example). For this reason, there should be no extra newlines at the end of the file unless the last desired command is a blank command.

## Flexibility and Restrictions

The automated command input is quite flexibile - it can take in any number of command line arguments, and the user can mix and match raw commands and file names as needed. Furthermore, the commands given to the program do not need to end the program. If the program runs out of given commands, it will prompt the user to enter commands as usual.

Besides the necessity of the x command with raw commands, note there is another restriction on automated commands in that they cannot control vim editing. If an automated command chooses to edit the current settings or append new ones, it will be up to the user to manually do so. However, once the vim editor is closed the automated commands will continue running as normal.

## Quiet Mode

When enabled, quiet mode will silence all program outputs to the command line excluding error messages and input prompts. This mode is intended for automated commands, when the listing of options is unnecessary and may flood the command line tab with undesired output. ***It is not recommended*** to use this mode when manually running the program. When using quiet mode, ***it is recommended*** to keep logs enabled so that any important changes/analysis can be recorded for later reference.

Quiet mode can also be passed in as a command line argument as ```--quiet``` *or* ```-q```. This is because there are some inital messages that are printed before settings are initialized and are therefore unaffected by the later imported settings. Similarly, note that default settings have quiet mode turned off, so even if the program is run with ```--quiet```, using default settings will almost immediately turn this off. 

The --quiet and --commands argument are independent and can be listed in any order. However, please ensure that they only occur once at most, and that all program commands follow -c/--commands and come before -q/--quiet (if the quiet mode option is given after).

To run an example, enter the following command:

```python3.10 driver.py -c input.txt -q```

Alternatively:

```python3.10 driver.py -q -c input.txt```