class Settings:

    def __init__(self,
                 
                 ioSettings={   'Input file/folder':'',
                                'Output file':'',
                                'Input type':2},

                 genSettings={  'Fit range':[0,2e3],
                                'Plot scale':'linear',
                                'Time difference method':'any_and_all',
                                'Digital Delay':750,
                                'Number of folders':10,
                                'Meas time per folder':60,
                                'Sort data?':'yes',
                                'Save figures?':'yes',
                                'Show plots?':'no',
                                'Save directory':'./'},

                visSettings={   'color':'black',
                                'markeredgecolor':'blue',
                                'markerfacecolor':'black',
                                'linestyle':'-',
                                'linewidth':3},

                histSettings={  'Reset time':2e3,
                                'Bin width':2,
                                'Minimum cutoff':30},

                fitSettings={   'color':'red',
                                'markeredgecolor':'blue',
                                'markerfacecolor':'black',
                                'linestyle':'-',
                                'linewidth':1},

                resSettings={'s':8.0}
                ):
        
        self.settings = {'Input/Output Settings': ioSettings,
                         'General Settings': genSettings,
                         'Histogram Visual Settings': visSettings,
                         'Histogram Generation Settings': histSettings,
                         'Line Fitting Settings': fitSettings,
                         'Residual Plot Settings': resSettings
        }

    def set(self, type, setting, value):
        self.settings[type][setting] = value
    
    def get(self, type, setting):
        return self.settings[type].get(setting)
    
    def remove(self, type, setting):
        self.settings[type].pop(setting)

    def print_section(self, type):
        print(type)
        if len(self.settings[type]) == 0:
            print ('No settings')
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