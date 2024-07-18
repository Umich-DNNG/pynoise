from pathlib import Path
import subprocess


# the two hdf5 files to be compared
# if using different files, replace './data/pynoise.h5' and/or './data/pynoise_master.h5' with the path to your hdf5 files
file1 = Path('./data/pynoise_master.h5').resolve()
file2 = Path('./data/pynoise.h5').resolve()

data1 = Path('./data/processing_data_master.h5').resolve()
data2 = Path('./data/processing_data.h5').resolve()
# if adding more files, add files here, and declare the files global in the main() function below


def compareResults(result, verbose:bool=False):

    '''
    Function used to compare the two files and print differences
    input:
        result: the object returned from a subprocess.run() call
    output:
        print messages, determining if the files are different or not
    '''
    # use h5diff to determine differences between the two files
    # use return code to determine if equal or not
    # if return 0, equal
    # if return 1, differences in datasets or tree structure
    # if return 2, then h5diff failed to run
    # documentation link: https://manpages.ubuntu.com/manpages/lunar/man1/h5diff.1.html

    # h5diff ran successfully and found no differences
    if result.returncode == 0:
        print('ALL TESTS PASSED')
        print('No differences found')
        print('Tree structure and data is identical\n\n')

    # h5diff found differences
    # if differences is nothing , inform users that tree structure is different
    # Otherwise, print differences
    elif result.returncode == 1:
        print('TESTS FAILED')
        if len(result.stdout) == 0:
            print('Existing data is the same')
            print('Tree structure is different')
        else:
            print('h5diff output:')
            print(result.stdout + '\n\n')
    
        # ask users if they would like to see the verbose output
        # only ask users if comparing non-verbose output, if verbose output then do not ask and continue to next test
        if not verbose:
            print('\nWould a more detailed report be desired? All differences between the files, including tree differences, will be displayed')
            print('WARNING: if there are a large number of differences, there will be a lot of output')
            input_val = input('If a more detailed report is desired, enter "Y" or "y". Enter anything else to cancel: ')
            if input_val == 'Y' or input_val == 'y':
                runh5Diff(verbose=True)
                    
    # h5diff ran into an error and failed to run
    else:
        print('ERROR')
        print('h5diff failed to run\n\n')


def runh5Diff(verbose:bool = False):

    print('\nComparing processing data (e.g. Rossi Alpha time differences, Cohn Alpha counts histogram)')
    if verbose:
        result = subprocess.run(['h5diff', '-v', data1, data2],
                               capture_output=True,
                               text=True)
    else:
        result = subprocess.run(['h5diff', data1, data2],
                                capture_output=True,
                                text=True)

    # set verbose to true to let users see verbose output only once
    # when runh5Diff() calls compareResults() the second time
    compareResults(result=result,verbose=True)
    print('\nComparing graph data')
    if verbose:
        result = subprocess.run(['h5diff', '-v', file1, file2],
                               capture_output=True,
                               text=True)
    else:
        result = subprocess.run(['h5diff', file1, file2],
                                capture_output=True,
                                text=True)
    compareResults(result=result,verbose=verbose)



def runRossiAlphaUnitTests():
    
    print('ROSSI ALPHA UNIT TESTING NOT IMPLEMENTED')
    return

    # Example code to run unit tests
    # use subprocess.run() to run Python
    # link to documentation: https://docs.python.org/3/library/subprocess.html
    
    # 'i' + 'a' + '<settings file name>' loads in the settings file with corresponding name
    # 'r' + 'm' means to run the Rossi Alpha method, and to run the entire method
    # 'x' + 'x' + 'q' means to exit the program
    # For more information, read the commands documentation

    # the below line of code runs this line in the bash shell:
    # python3 main.py -c i a <settings file> r m x x q

    subprocess.run([
        'python', 'main.py', '-c', 'i', 'a',
        'SETTINGS FILE NAME HERE',
        'r', 'm', 'x', 'x', 'q'
    ])

    runh5Diff(verbose=False)


def runCohnAlphaUnitTests():

    # Example code to run unit tests
    # use subprocess.run() to run Python
    # link to documentation: https://docs.python.org/3/library/subprocess.html
    
    # 'i' + 'a' + '<settings file name>' loads in the settings file with corresponding name
    # 'c' + 'm' means to run the Cohn Alpha method, and to run the entire method
    # 'x' + 'x' + 'q' means to exit the program
    # For more information, read the commands documentation

    # the below line of code runs this line in the bash shell:
    # python3 main.py -c i a test_stilbene_2in_CROCUS_20cm_offset_east c m x x q

    subprocess.run([
        'python', 'main.py', '-c', 'i', 'a',
        'test_stilbene_2in_CROCUS_20cm_offset_east',
        'c', 'm', 'x', 'x', 'q'
    ])

    subprocess.run([
        'python', 'main.py', '-c', 'i', 'a',
        'test_stilbene_2in_CROCUS_20cm_offset_north',
        'c', 'm', 'x', 'x', 'q'
    ])

    # compare output
    runh5Diff(verbose=False)



def runFeynmanYUnitTests(verbose:bool=False):
    
    print('FEYNMAN Y UNIT TESTING NOT IMPLEMENTED')
    return

    # TODO: add test cases

    subprocess.run([
        'python', 'main.py', '-c', 'i', 'a',
        'FEYNMAN Y SETTINGS FILE HERE',
        'f', 'm', 'x', 'x', 'q'
    ])
    runh5Diff(verbose)


def main():
    global file1
    global file2
    global data1
    global data2
    print('Testing Rossi-Alpha Method')
    runRossiAlphaUnitTests()
    print('Testing Cohn-Alpha Method')
    runCohnAlphaUnitTests()
    print('Testing Feynman-Y Method')
    runFeynmanYUnitTests()


if __name__=="__main__": 
    main()