import os
from tqdm import tqdm


def importAnalysis(data: dict[str:tuple],
                   name: str,
                   singles:list = None,
                   input: str = './data'):

    '''
    Importing analysis data from a csv file. The imported data
    will be stored in the data dict. 
    
    
    The name of the columns in the csv file should match the keys in the dict.
    The value of the dict should be a tuple, in the format (list, starting int, stopping int)
    Information from rows [starting int, stopping int) will be read into the list.
    If both the first and the second int are set to a value <= 0,
    then the function will read until end of file.
    Singles should be an empty list to be populated with tuples.
    The tuple's first value will be the single's column header,
    the second value will be the value of the single.
    If singles == None, assuming no singles value to be imported.
    
    
    The function assumes that all columns of data will be read.
    Function will crash if len(data.keys()) != # of header columns

    
    Inputs:
    - dict: a dictionary. Each key will be the name of the column.
    The value stored should be a tuple, in the form of (list, starting int, stopping int)
    The list is used to store input data.
    Information from rows [starting int, stopping int) will be read into the lists.
    If starting int == stopping int <= 0, then the entire column will be read.
    - single: a list of single values to display on the top row. 
    Each list value will contain a tuple, whose first entry is 
    the name of the value and whose second entry is the value.
    - method: the name of the method of analysis.
    - input: the input directory. If not given, defaults to ./data.'''

    # construct import file name
    # attempt to open file
    fileName = (input + '/output_' + name + '.csv')
    try:
        with open(fileName, 'r') as file:
            print("reading in analysis data...")
            # grab header as well as 1st line of data
            # used to populate singles
            headerLine = next(file)
            singleLine = next(file)

            # split string into list
            # removing newlines via strip()
            # separating by comma via split()
            # calculate number of data columns
            headerLine = headerLine.strip().split(',')
            singleLine = singleLine.strip().split(',')
            numDataColumns = len(data.keys())

            # if singles is a list, populate list, otherwise ignore singles
            if singles is not None:

                # start at singles column
                # grab column in addition to value
                # append to singles list
                for header, value in zip(headerLine[numDataColumns:], singleLine[numDataColumns:]):
                    singles.append((header, value))

            # add information from 1st line to each of the lists in the dict
            # exclude singles information
            # use headerLine's values as keys
            for colNum in range(numDataColumns):
                startRow = data[headerLine[colNum]][1]
                stopRow = data[headerLine[colNum]][2]

                # if startRow and stopRow <= 0, append entire column
                # otherwise ensure in correct range [startRow, stopRow)
                if startRow <= 0 and stopRow <= 0:
                    data[headerLine[colNum]][0].append(singleLine[colNum])
                
                elif rowNum >= startRow and rowNum < stopRow:
                    data[headerLine[colNum]][0].append(line[colNum])

            # iterate through the rest of the file
            # use headerLine's values as keys
            for rowNum, line in enumerate(tqdm(file)):
                line = line.strip().split(',')
                for colNum in range(numDataColumns):
                    list = data[headerLine[colNum]][0]
                    startRow = data[headerLine[colNum]][1]
                    stopRow  = data[headerLine[colNum]][2]

                    # if starting row and stopping row are <= 0, then append without question
                    # otherwise check if in range of [starting row, stopping row)
                    if startRow <= 0 and stopRow <= 0:
                        list.append(line[colNum])

                    elif rowNum >= startRow and rowNum < stopRow:
                        list.append(line[colNum])

        print("Finished reading in analysis data")
        return True
    
    # file does not exist error
    # return false and inform users something went wrong
    except FileNotFoundError:
        print("Analysis data could not be found")
        print("Generating analysis data from input file")
        return False

    # out of bounds error (for lists), accessed inaccessible memory
    # return false and inform users something went wrong
    except IndexError:
        print("An error occurred while reading in analysis data")
        print("Generating analysis data from input file")
        return False
    
    # key error (for dicts), provided incorrect keys
    # return false and inform users something went wrong
    except KeyError:
        print("An error occurred while reading in analysis data")
        print("Generating analysis data from input file")
        return False

    

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


