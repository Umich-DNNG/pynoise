class Settings:

    def __init__(self,
                 
                 ioSettings={},

                 genSettings=   {'fit':[0,2e3],
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

                resSettings={'s':8}
                ):
        
        self.settings = {'io_file_info': ioSettings,
                         'general_program_settings': genSettings,
                         'histogram_visual_settings': visSettings,
                         'generating_histogram_settings': histSettings,
                         'line_fitting_settings': fitSettings,
                         'residual_plot_settings': resSettings
        }

    def changeSetting(self, type, setting, value):
        self.settings[type][setting] = value