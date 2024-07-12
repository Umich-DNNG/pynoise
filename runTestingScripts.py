from pathlib import Path
import subprocess

def runCohnAlphaUnitTests():

    # use subprocess to run Python
    # runs this line in the bash shell:
    # python3 main.py -c i a test_stilbene_2in_CROCUS_20cm_offset_east c f x x q
    # link to documentation: https://docs.python.org/3/library/subprocess.html
    
    # 'i , 'a', 'settings file name.json 'loads in the settings file with corresponding name
    # 'c', 'f' means to run the Cohn Alpha method, and to fit the plot
    # 'x', 'x', 'q' means to exit the program

    subprocess.run([
        'python', 'main.py', '-c', 'i', 'a',
        'test_stilbene_2in_CROCUS_20cm_offset_east',
        'c', 'f', 'x', 'x', 'q'
    ])

    # loads in auto.json as the settings
    # add commands such as 'r', 'c', to run Rossi/Cohn Alpha analysis methods
    # for example,
    subprocess.run([
        'python', 'main.py', '-c', 'i', 'a', 'auto', 'x', 'q'
    ])

    # use h5diff to determine differences between the two files
    # use return code to determine if equal or not
    # documentation link: https://manpages.ubuntu.com/manpages/lunar/man1/h5diff.1.html
    
    result = subprocess.run([
        'h5diff',
        'OUTPUT FILE HERE',
        'TEST FILE HERE'
        ],
        capture_output=True,
        text=True)

    # if failed, print error message
    # print differences with stdout
    # print error output if h5diff failed to run with stderr
    if result.returncode != 0:
        print('RESULTS ARE DIFFERENT')
        print('stdout output:')
        print(result.stdout)
        print('stderror output:')
        print(result.stderr)


def main(): 
    print('Testing Cohn-Alpha Method')
    runCohnAlphaUnitTests()


if __name__=="__main__": 
    main()
