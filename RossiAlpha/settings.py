class Settings:

    def __init__(self,
                 
                 ioSettings={
                                'Input type':0,
                                'Input file/folder':'',
                                'Output file':''
                            },

                 genSettings={  
                                'Fit range':[0,0],
                                'Plot scale':'',
                                'Time difference method':'',
                                'Digital delay':0,
                                'Number of folders':0,
                                'Meas time per folder':0,
                                'Sort data?':'',
                                'Save figures?':'',
                                'Show plots?':'',
                                'Save directory':''
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
        if input.replace(".", "").isnumeric() and input.count('.') <= 1:
            return True
        else:
            return False

    def updated(self):
        return self.changed

    def update(self):
        self.changed = True

    def read(self, path):
        f = open(path, "r")
        line = ''
        while line != 'Input/Output Settings':
            line = f.readline().replace('\n','')
        f.readline()
        line = f.readline().replace('\n','')
        if line[12] == '0':
            print('WARNING: with  defualt settings, the input file'
                      + '/folder is not specified. You must add it manually.')
        self.set('Input/Output Settings','Input type',int(line[12]))
        line = f.readline().replace('\n','')
        self.set('Input/Output Settings','Input file/folder',line[19:])
        line = f.readline().replace('\n','')
        self.set('Input/Output Settings','Output file',line[13:])
        f.readline()
        f.readline()
        f.readline()
        line = f.readline().replace('\n','')
        line = line[12:len(line)-1]
        begin = int(line[:line.find(',')])
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
        self.set('General Settings','Sort data?',line[12:])
        line = f.readline().replace('\n','')
        self.set('General Settings','Save figures?',line[15:])
        line = f.readline().replace('\n','')
        self.set('General Settings','Show plots?',line[13:])
        line = f.readline().replace('\n','')
        self.set('General Settings','Save directory',line[16:])
        f.readline()
        f.readline()
        f.readline()
        line = f.readline().replace('\n','')
        while line[0] != '#':
            split = line.find(':')
            type = line[:split]
            setting = line[split+2:]
            if setting.isnumeric():
                self.set('Histogram Visual Settings',type,int(setting))
            elif self.isFloat(setting):
                self.set('Histogram Visual Settings',type,float(setting))
            else:
                self.set('Histogram Visual Settings',type,setting)
            line = f.readline().replace('\n','')
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
        line = f.readline().replace('\n','')
        while line[0] != '#':
            split = line.find(':')
            type = line[:split]
            setting = line[split+2:]
            if setting.isnumeric():
                self.set('Line Fitting Settings',type,int(setting))
            elif self.isFloat(setting):
                self.set('Line Fitting Settings',type,float(setting))
            else:
                self.set('Line Fitting Settings',type,setting)
            line = f.readline().replace('\n','')
        f.readline()
        f.readline()
        line = f.readline().replace('\n','')
        while line[0] != '#':
            split = line.find(':')
            type = line[:split]
            setting = line[split+2:]
            if setting.isnumeric():
                self.set('Residual Plot Settings',type,int(setting))
            elif self.isFloat(setting):
                self.set('Residual Plot Settings',type,float(setting))
            else:
                self.set('Residual Plot Settings',type,setting)
            line = f.readline().replace('\n','')
        self.changed = False

    def write(self, path):
        f = open(path,'w')
        f.write('# Custom user generated settings.\n')
        f.write('#----------------------------------------------------------------------------------------\n')
        for type in self.settings:
            f.write(type + '\n')
            f.write('#----------------------------------------------------------------------------------------\n')
            for setting in self.settings[type]:
                f.write(setting + ': ')
                f.write(str(self.get(type, setting)))
                f.write('\n')
            f.write('#----------------------------------------------------------------------------------------\n')

    def set(self, type, setting, value):
        self.settings[type][setting] = value
    
    def get(self, type, setting):
        return self.settings[type].get(setting)
    
    def remove(self, type, setting):
        self.settings[type].pop(setting)

    def print_section(self, type):
        print(type)
        if len(self.settings[type]) == 0:
            print ('No specified settings.')
        else:
            for setting in self.settings[type]:
                print(setting,'-',self.get(type,setting))

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