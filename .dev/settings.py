import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

class Settings:

    def __init__(self,
                 
                ioSettings={
                                'Input type':0,
                                'Input file/folder':'',
                                'Save directory':''
                            },

                genSettings={  
                                'Fit range':[0,0],
                                'Plot scale':'',
                                'Time difference method':'',
                                'Digital delay':0,
                                'Number of folders':0,
                                'Meas time per folder':0,
                                'Sort data?':False,
                                'Save figures?':False,
                                'Show plots?':False,
                            },

                visSettings={},

                histSettings={
                                'Reset time':0,
                                'Bin width':0,
                                'Minimum cutoff':0
                            },

                fitSettings={},

                resSettings={}
                ):
        
        self.settings = {'Input/Output Settings': ioSettings,
                         'General Settings': genSettings,
                         'Histogram Visual Settings': visSettings,
                         'Histogram Generation Settings': histSettings,
                         'Line Fitting Settings': fitSettings,
                         'Residual Plot Settings': resSettings
        }
        self.changed = False

    def isFloat(self, input):

        try:
            float(input)
            return True
        except ValueError:
            return False

    def updated(self):

        return self.changed

    def update(self):

        self.changed = True

    def set(self, group, setting, value):

        self.settings[group][setting] = value
    
    def get(self, group, setting):

        return self.settings[group].get(setting)
    
    def remove(self, group, setting):

        self.settings[group].pop(setting)

    def readPlot(self, group, f):

        self.settings[group] = {}
        line = f.readline().replace('\n','')
        while line[0] != '#':
            split = line.find(':')
            setting = line[:split]
            value = line[split+2:]
            if value == 'True':
                self.set(group,setting,True)
            elif value == 'False':
                self.set(group,setting,False)
            elif value.isnumeric():
                self.set(group,setting,int(value))
            elif self.isFloat(value):
                self.set(group,setting,float(value))
            else:
                self.set(group,setting,value)
            line = f.readline().replace('\n','')

    def read(self, path):

        f = open(path, "r")
        line = ''
        while line != 'Input/Output Settings':
            line = f.readline().replace('\n','')
        f.readline()
        line = f.readline().replace('\n','')
        self.set('Input/Output Settings','Input type',int(line[12]))
        if line[12] == '0':
            print('WARNING: with the current imported settings, the input file'
                      + '/folder is not specified. You must add it manually.')
            f.readline()
        else:
            line = f.readline().replace('\n','')
            file = line[19:]
            self.set('Input/Output Settings','Input file/folder',os.path.abspath(file))
        line = f.readline().replace('\n','')
        file = line[16:]
        self.set('Input/Output Settings','Save directory',os.path.abspath(file))
        f.readline()
        f.readline()
        f.readline()
        line = f.readline().replace('\n','')
        line = line[12:len(line)-1]
        begin = float(line[:line.find(',')])
        end = float(line[line.find(',')+1:])
        self.set('General Settings','Fit range',[begin,end])
        line = f.readline().replace('\n','')
        self.set('General Settings','Plot scale',line[12:])
        line = f.readline().replace('\n','')
        self.set('General Settings','Time difference method',line[24:])
        line = f.readline().replace('\n','')
        self.set('General Settings','Digital delay',int(line[15:]))
        line = f.readline().replace('\n','')
        self.set('General Settings','Number of folders',int(line[19:]))
        line = f.readline().replace('\n','')
        self.set('General Settings','Meas time per folder',int(line[22:]))
        line = f.readline().replace('\n','')
        if line[12] == 'T':
            self.set('General Settings','Sort data?',True)
        else:
            self.set('General Settings','Sort data?',False)
        line = f.readline().replace('\n','')
        if line[15] == 'T':
            self.set('General Settings','Save figures?',True)
        else:
            self.set('General Settings','Save figures?',False)
        line = f.readline().replace('\n','')
        if line[13] == 'T':
            self.set('General Settings','Show plots?',True)
        else:
            self.set('General Settings','Show plots?',False)
        f.readline()
        f.readline()
        f.readline()
        self.readPlot('Histogram Visual Settings',f)
        f.readline()
        f.readline()
        line = f.readline().replace('\n','')
        self.set('Histogram Generation Settings','Reset time',float(line[12:]))
        line = f.readline().replace('\n','')
        self.set('Histogram Generation Settings','Bin width',int(line[11:]))
        line = f.readline().replace('\n','')
        self.set('Histogram Generation Settings','Minimum cutoff',int(line[16:]))
        f.readline()
        f.readline()
        f.readline()
        self.readPlot('Line Fitting Settings',f)
        f.readline()
        f.readline()
        self.readPlot('Residual Plot Settings',f)
        self.changed = False

    def write(self, path, default):

        f = open(path,'w')
        if default:
            f.write('# The default settings for running the PyNoise project.\n')
        else:
            f.write('# Custom user generated settings.\n')
        f.write('#----------------------------------------------'
                + '------------------------------------------\n')
        for group in self.settings:
            f.write(group + '\n')
            f.write('#----------------------------------------------'
                    + '------------------------------------------\n')
            for setting in self.settings[group]:
                f.write(setting + ': ')
                f.write(str(self.get(group, setting)))
                f.write('\n')
            f.write('#----------------------------------------------'
                    + '------------------------------------------\n')

    def print_section(self, group):

        print(group)
        if len(self.settings[group]) == 0:
            print ('No specified settings.')
        else:
            for setting in self.settings[group]:
                print(setting,'-',self.get(group,setting))

    def print_all(self):

        print('\nHere are the current settings for the program:')
        print()
        self.print_section('Input/Output Settings')
        print()
        self.print_section('General Settings')
        print()
        self.print_section('Histogram Visual Settings')
        print()
        self.print_section('Histogram Generation Settings')
        print()
        self.print_section('Line Fitting Settings')
        print()
        self.print_section('Residual Plot Settings')