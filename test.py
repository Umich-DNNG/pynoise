import sys
from pathlib import Path
import subprocess


# the two hdf5 files to be compared
# if using different files, replace './data/pynoise.h5' and/or './data/pynoise_master.h5' with the path to your hdf5 files
file1 = Path('./data/pynoise_master.h5').resolve()
file2 = Path('./data/pynoise_wrong.h5').resolve()

# subprocess.run() takes in a string value, not a float value
precision:str = '0.05'

# all data1/data2 lines commented out due to no longer keeping processing_data_master.h5 on branch
# data1 = Path('./data/processing_data_master.h5').resolve()
# data2 = Path('./data/processing_data.h5').resolve()


def ignoreLines(i, line1:str = "", line2:str = ""):
    # output[i] == hdf5 data path, output[i + 1] == # differences found
    # ignore datasets that have 0 differences found
    if line2 == '0 differences found':
        i += 2
        return i, False

    # Temporary: avoid printing dataset differences
    elif line1.find('[') != -1 and line1.find(']') != -1:
        i += 1
        return i, False

    # Temporary: avoid printing column headers
    elif line1.find('position') != -1 and line1.find('difference') != -1:
        i += 1
        return i, False

    # Avoid printing divider
    elif line1.find('---------------------') != -1:
        i += 1
        return i, False

    # Avoid printing size of datasets
    elif line1.find('size:') != -1:
        i += 1
        return i, False

    return i, True


def parseOutput(output:str = ""):

    output_list = output.split('\n')

    tree_difference_index = 0

    # only print tree similarities and differences
    # since always running h5diff with verbose option, will not crash
    # if running without verbose option, index() will raise an exception
    tree_difference_index = output_list.index('group  : </> and </>')
    for i in range(tree_difference_index):
        print(output_list[i])


    input_val = input('To see the dataset differences, enter "Y" or "y". Enter anything else to cancel: ')
    if not (input_val == 'Y' or input_val == 'y'):
        return

    # start at data differences
    i = tree_difference_index

    # iterate through data differences
    # use while loop instead of for loop to increment i by differing amounts
    # fine to use len(output_list) - 1, last item in list is a empty string
    while i < len(output_list) - 1:
        # should remove all output other than dataset differences statements
        # as well as number of differences (if differences > 0)     
        i, return_val = ignoreLines(i=i, line1=output_list[i], line2=output_list[i + 1])
        if not return_val:
            continue

        line = output_list[i]

        if line.find('difference') != -1:
            print(line)

        else:
            # slice settings file name out; only need to slice 1 of the 2 settings name, should be the same
            # e.g. settings_file_1 == 'test_stilbene_2in_CROCUS_20cm_offset_north.json'
            settings_name_start = line.find('/') + 1
            settings_name_end = line.find('.json') + len('.json')
            settings_file = line[settings_name_start:settings_name_end]

            # find iteration number
            iteration_num_start = line.find('iteration')
            iteration_num_end = line.find('/', iteration_num_start)

            # find data path
            # e.g. CohnAlpha/Scatter/Fit
            data_path_start = line.find('/', iteration_num_end)
            data_path_end = line.find('>')
            data_path = line[data_path_start + 1:data_path_end]
            print('Group ' + settings_file + ' at ' + data_path + ' has:')


        i += 1


def compareResults(result):

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
    # print differences
    elif result.returncode == 1:
        print('TESTS FAILED')
        print('H5DIFF FOUND DIFFERENCES BETWEEN THE TWO FILES')
        print('tree difference output:')
        parseOutput(output=result.stdout)
        print('\n')
    
        # ask users if they would like to see the verbose output
        print('\nA more detailed report, with all differences listed, can be saved into a separate text file.')
        print('WARNING: IF THERE ARE A LARGE NUMBER OF DIFFERENCES THERE WILL BE A LOT OF OUTPUT')
        print('EVERY DIFFERENCE WILL BE PRINTED. IF THERE ARE 40000 DIFFERENCES, THERE WILL BE 40000 LINES OF OUTPUT')
        print('WARNING: LARGE NUMBER OF DIFFERENCES MEANS THERE WILL BE A LOT OF OUTPUT. EACH DIFFERENCE IS A LINE.')
        input_val = input('If a more detailed report is desired, enter "Y" or "y". Enter anything else to cancel: ')
        if input_val == 'Y' or input_val == 'y':
            runh5Diff(save=True)
    
                    
    # h5diff ran into an error and failed to run
    else:
        print('ERROR')
        print('h5diff failed to run')
        print('h5diff error output:')
        print(result.stdout)



def runh5Diff(save:bool = False):

    # print('\nComparing processing data (e.g. Rossi Alpha time differences, Cohn Alpha counts histogram)')
    # if verbose:
    #     result = subprocess.run(['h5diff', '-v', data1, data2],
    #                            capture_output=True,
    #                            text=True)
    # else:
    #     result = subprocess.run(['h5diff', data1, data2],
    #                             capture_output=True,
    #                             text=True)

    # # set verbose to true to let users see verbose output only once
    # # when runh5Diff() calls compareResults() the second time
    # compareResults(result=result,verbose=True)


    # compares the files, only prints differences greater than 0.001
    # if verbose prints tree differences as well
    print('\nComparing graph data')
    result = subprocess.run(['h5diff', '-v', '-p', precision, file1, file2],
                            capture_output=True,
                            text=True)
    
    if save:
        filename = './testingDirectory/' + file1.stem + '+' + file2.stem + '_diff.txt'
        with open(filename, 'w') as file:
            file.write(result.stdout)
        filename_abspath = Path(filename).resolve()
        print('output saved at: ' + str(filename_abspath))
    else:
        compareResults(result=result)



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
    runh5Diff()



def runFeynmanYUnitTests(verbose:bool=False):
    
    print('FEYNMAN Y UNIT TESTING NOT IMPLEMENTED')
    return

    # TODO: add test cases
    # Example code to run unit tests
    # use subprocess.run() to run Python
    # link to documentation: https://docs.python.org/3/library/subprocess.html
    
    # 'i' + 'a' + '<settings file name>' loads in the settings file with corresponding name
    # 'f' + 'm' means to run the Feynman Y method, and to run the entire method
    # 'x' + 'x' + 'q' means to exit the program
    # For more information, read the commands documentation

    # the below line of code runs this line in the bash shell:
    # python3 main.py -c i a <settings file> f m x x q

    subprocess.run([
        'python', 'main.py', '-c', 'i', 'a',
        'FEYNMAN Y SETTINGS FILE HERE',
        'f', 'm', 'x', 'x', 'q'
    ])
    runh5Diff(verbose)


def main():

    # global data1
    # global data2
    global file1
    global file2
    global precision

    if len(sys.argv) > 2:
        print('The testing script only takes in at most 1 command line argument: the relative error')
        print('Please re-run the testing script and remove any extra command line arguments')
        exit(1)

    if len(sys.argv) == 1:
        print('No relative error provided, defaulting to relative error of 0.05')
    else:
        precision = sys.argv[1]
        print('Relative error set to: ' + precision)

    print('This testing script uses a command-line tool, h5diff')
    print('For more information about this tool, a link to the documentation can be found here:')
    print('https://manpages.ubuntu.com/manpages/lunar/man1/h5diff.1.html')


    print('Testing Rossi-Alpha Method')
    runRossiAlphaUnitTests()
    print('Testing Cohn-Alpha Method')
    runCohnAlphaUnitTests()
    print('Testing Feynman-Y Method')
    runFeynmanYUnitTests()


if __name__=="__main__": 
    main()