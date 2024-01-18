# PyNoise Project

Welcome to the PyNoise Project! The goal of this Python suite is to process and analyze radiation data recorded from fission chain reactions. Our supported methods of analysis currently include Rossi Alpha, Cohn Alpha, and Feynman-Y. For more information about these methods, please see the README files in their respective subdirectories.

## How to Use



### Requirements

To run the PyNoise project, please ensure you have the entire repo downloaded, even if you plan to use only one analysis method. Additionally, the PyNoise suite requires Python 3.10 version to run. Make sure to update your Python version accordingly before using this program.


### Installing Required Python Packages

Pip is the preferred package manager for this project, and this README will explain how to install project dependencies with it. If you are using another manager, please consult its documentation on how to install project dependencies from the requirements.txt file. 

Ensure that Python and ```pip``` are installed on your system. You can check this by running the following commands in the terminal:
```python
python --version
pip --version
```

Create a virtual environment (optional): If you want to install your project in a virtual environment, please do so now.

With the virtual environment activated (or without one), navigate to the PyNoise directory and run the following command to install the 
project dependencies:
```python
pip install -r requirements.txt
```

NOTE: tkinter should be a package included in your Python installation — however, it can be problematic and cannot be installed with pip. Please consult https://stackoverflow.com/questions/76105218/why-does-tkinter-or-turtle-seem-to-be-missing-or-broken-shouldnt-it-be-part for assistance.

### Settings Configurations

To allow for a wide range of graphing/analysis options, there is a settings system that can be changed before or during runtime. Please consult the documentation in the settings folder, or use the default settings provided.

### Running PyNoise

To run the PyNoise program, open a terminal in the pynoise folder and enter the following command:

```python3.10 main.py [-g|--gui]```

Including the -g or --gui will run the program in GUI mode; otherwise, the program will be run on the command line. After starting the program, instructions will be given on how to proceed.