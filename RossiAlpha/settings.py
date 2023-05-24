class Settings:

    def __init__(self,
                 
                 ioSettings={   'input':'',
                                'output':'',
                                'type':2},

                 genSettings={  'fit':[0,2e3],
                                'scale':'linear',
                                'method':'any_and_all',
                                'delay':750,
                                'num':10,
                                'meas':60,
                                'sort':'yes',
                                'save':'yes',
                                'show':'no',
                                'dir':'./'},

                visSettings={   'color':'black',
                                'edge':'blue',
                                'face':'black',
                                'style':'-',
                                'width':3},

                histSettings={  'time':2e3,
                                'width':2,
                                'cutoff':30},

                fitSettings={   'color':'red',
                                'edge':'blue',
                                'face':'black',
                                'style':'-',
                                'width':1},

                resSettings={'s':8.0}
                ):
        
        self.settings = {'io_file_info': ioSettings,
                         'general_program_settings': genSettings,
                         'histogram_visual_settings': visSettings,
                         'generating_histogram_settings': histSettings,
                         'line_fitting_settings': fitSettings,
                         'residual_plot_settings': resSettings
        }

    def set(self, type, setting, value):
        self.settings[type][setting] = value
    
    def get(self, type, setting):
        return self.settings[type][setting]

    def print_io(self):
        print('INPUT/OUTPUT SETTINGS')
        print('Input type:',self.get('io_file_info','type'))
        print('Input file/folder:',self.get('io_file_info','input'))
        print('Output file:',self.get('io_file_info','output'))

    def print_gen(self):
        print('GENERAL SETTINGS')
        print('Fit range:', self.settings['general_program_settings']['fit'][0],
                       'to', self.settings['general_program_settings']['fit'][1])
        print('Plot scale:',self.settings['general_program_settings']['scale'])
        print('Time difference method:',self.settings['general_program_settings']['method'])
        print('Digital Delay',self.settings['general_program_settings']['delay'])
        print('Number of folders:',self.settings['general_program_settings']['num'])
        print('Meas time per folder:',self.settings['general_program_settings']['meas'])
        print('Sort data?:',self.settings['general_program_settings']['sort'])
        print('Save figures?:',self.settings['general_program_settings']['save'])
        print('Show plots?:',self.settings['general_program_settings']['show'])
        print('Save directory:',self.settings['general_program_settings']['dir'])

    def print_vis(self):
        print('HISTOGRAM VISUAL SETTINGS')
        print('Main color:',self.settings['histogram_visual_settings']['color'])
        print('Edge color:',self.settings['histogram_visual_settings']['edge'])
        print('Face color:',self.settings['histogram_visual_settings']['face'])
        print('Line style:',self.settings['histogram_visual_settings']['style'])
        print('Line width:',self.settings['histogram_visual_settings']['width'])

    def print_hist(self):
        print('HISTOGRAM GENERATION SETTINGS')
        print('Reset time:',self.settings['generating_histogram_settings']['time'])
        print('Bin width:',self.settings['generating_histogram_settings']['width'])
        print('Minimum cutoff:',self.settings['generating_histogram_settings']['cutoff'])

    def print_fit(self):
        print('LINE FITTING SETTINGS')
        print('Main color:',self.settings['line_fitting_settings']['color'])
        print('Edge color:',self.settings['line_fitting_settings']['edge'])
        print('Face color:',self.settings['line_fitting_settings']['face'])
        print('Line style:',self.settings['line_fitting_settings']['style'])
        print('Line width:',self.settings['line_fitting_settings']['width'])

    def print_res(self):
        print('RESIDUAL PLOT SETTINGS')
        print('S:',self.settings['residual_plot_settings']['s'])

    def print_all(self):
        print('\nHere are the current settings for the program:')
        print()
        self.print_io()
        print()
        self.print_gen()
        print()
        self.print_vis()
        print()
        self.print_hist()
        print()
        self.print_fit()
        print()
        self.print_res()