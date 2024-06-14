import os
from tqdm import tqdm


def importAnalysis(data: dict[str:[]],
                   name: str,
                   singles:list = None,
                   output: str = './data'):
    '''Importing analysis data from a csv file. The imported data
    will be stored in the data dict. The name of the columns
    in the csv file should match the name of the keys in the dict.
    Singles should be an empty list to be populated with tuples.
    The tuple's first value will be the single's column header,
    the second value will be the value of the single.
    Note: if singles == None, assuming no singles value to be imported
    
    Inputs:
    - dict: a dictionary that contains all the 
    list data to be outputted to the csv file. 
    Each key will be the name of the column, and 
    the value stored will be a tuple. The first 
    value is the list of data, and the second is 
    the row to start displaying the list at.
    - single: a list of single values to display on the top row. 
    Each list value will contain a tuple, whose first entry is 
    the name of the value and whose second entry is the value.
    - method: the name of the method of analysis.
    - output: the output directory. If not given, defaults to ./data.'''

    # construct import file name
    fileName = (output + '/output_' + name + '.csv')
    # open file
    # if file does not exist, print message then return
    try:
        with open(fileName, 'r') as file:
            print("reading in analysis data...")
            # grab header as well as 1st line of data
            headerLine = next(file)
            singleLine = next(file)

            # split string into list separating by comma via split()
            # removing newlines via strip()
            # calculate number of data columns
            headerLine = headerLine.strip().split(',')
            singleLine = singleLine.strip().split(',')

            numDataColumns = len(data.keys())

            # if singles is None, then skip
            # otherwise if singles is a list, populate list
            if singles is not None:
                # start at singles column
                # grab header information in addition to value
                # append to return list
                for tuple in zip(headerLine[numDataColumns:], singleLine[numDataColumns:]):
                    singles.append(tuple)

            # add information from 1st line to each of the lists in the dict
            # exclude singles information
            for i in range(numDataColumns):
                # use headerLine as key

                data[headerLine[i]].append(singleLine[i])

            # iterate through the rest of the file
            # use headerLine as key and append values
            for i, line in enumerate(tqdm(file)):
                line = line.strip().split(',')
                for i in range(numDataColumns):
                    data[headerLine[i]].append(line[i])

        print("Finished reading in analysis data")
    except FileNotFoundError:
        print("Analysis data could not be found")
        print("Generating analysis data from input file")

def exportAnalysis(data: dict[str:tuple], 
            singles: list[tuple], 
            name: str, 
            output: str = './data'):

    '''Export data from analysis to a csv file. The file 
    will be stored in the data folder and will be named 
    based on the give analysis method and current time.
    
    Inputs:
    - dict: a dictionary that contains all the 
    list data to be outputted to the csv file. 
    Each key will be the name of the column, and 
    the value stored will be a tuple. The first 
    value is the list of data, and the second is 
    the row to start displaying the list at.
    - single: a list of single values to display on the top row. 
    Each list value will contain a tuple, whose first entry is 
    the name of the value and whose second entry is the value.
    - method: the name of the method of analysis.
    - output: the output directory. If not given, defaults to ./data.'''


    # Name the file appropriately with the method name and current time.
    fileName = (output + '/output_' + name + '.csv')
    # Open the new file.
    file = open(os.path.abspath(fileName),'w')
    # Initialize variables.
    labels = ''
    line = ''
    max = 0
    # For each dataset:
    for key in data:
        # If this is the longest dataset, store its length.
        if len(data[key][0]) + data[key][1] > max:
            max = len(data[key][0]) + data[key][1]
        # Add the dataset name to the labels string.
        labels += key + ','
        # If the dataset is starting at first 
        # row, add the first value to the row.
        if data[key][1] == 0:
            line += str(data[key][0][0]) + ','
        # Otherwise, leave an empty space.
        else:
            line += ','
    # For each single datapoint:
    for item in singles:
        # Add the data name to the labels string.
        labels += str(item[0]) + ','
        # Add the data value to the first row.
        line += str(item[1]) + ','
    # Write the columns row and first data row 
    # to the file (excluding tailing commas).
    file.write(labels[:-1] + '\n' + line[:-1] + '\n')
    # For each possible dataset index:
    for i in range(1,max):
        # Reset the line string.
        line = ''
        # For each dataset:
        for key in data:
            # If the desired beginning row for the dataset has 
            # been reached and there's still data left to print, 
            # add the proper data value to the current row.
            if i >= data[key][1] and i-data[key][1] < len(data[key][0]):
                line += str(data[key][0][i-data[key][1]]) + ','
            # Otherwise, leave an empty space.
            else:
                line += ','
        # Write the whole row to the file (excluding tailing comma).
        file.write(line[:-1]+'\n')
    # Flush the output to the file and close it.
    file.flush()
    file.close()


