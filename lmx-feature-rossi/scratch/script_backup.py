### script for copying/backing up files


# standard imports
import sys
import shutil


def script_backup(path, fname, copy_postscript, extension):
    
    src = fname
    if extension in fname:
        dst = path+fname[:fname.find(extension)]+copy_postscript+extension
    else:
        sys.exit('Exit: the specified extension is not in the specified filename.')
    
    shutil.copyfile(src, dst)
    

#fname = 'test.txt'
#extension = '.txt'
#copy_postscript = '_backup'
#script_backup(fname, copy_postscript, extension)
