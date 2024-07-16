from CohnAlpha import CohnAlpha as ca

# global Cohn Alpha Object
caObj: ca.CohnAlpha = None

def initCohnAlphaObject(settings: dict = {}):
    '''Initializes global Cohn Alpha Object
    
    Inputs:
    - settings: the current user's runtime settings'''

    # NOTE: must declare variable as global before reference otherwise Python complains
    global caObj
    
    # if uninitialized then set variable
    if caObj is None:
        caObj = ca.CohnAlpha(settings=settings)
    
    


def plotCohnAlphaHist(settings:dict = {}, settingsPath:str = './settings/default.json'):
    
    '''
    Creates a Cohn Alpha Counts Histogram
    Created Histogram is saved in the Analyzer class
    
    Inputs:
    - settings: the current user's runtime settings
    - overwrite: if overwriting the current information in memory
    '''

    initCohnAlphaObject(settings)
    caObj.plotCountsHistogram(settings=settings, settingsPath=settingsPath)
    return True


def applyWelchApprox(settings:dict = {}, settingsPath:str = './settings/default.json'):
    
    '''
    Applies the Welch Approximation transformation
    Frequencies as well as Power Spectral Density is saved in Analyzer class
    Will generate any required missing information
    
    Inputs:
    - settings: the current user's runtime settings
    - overwrite: if overwriting the current information in memory
    '''
    
    initCohnAlphaObject(settings)
    caObj.welchApproxFourierTrans(settings=settings, settingsPath=settingsPath)
    return True


def fitCohnAlpha(settings:dict = {}, settingsPath:str = './settings/default.json', showSubPlots:bool = False):
    
    '''
    Fits a Power Spectral Density Curve onto a 
    Transformed graph is saved into the Analyzer class
    
    Will run entire method if required information is missing
    
    Inputs:
    - settings: the current user's runtime settings
    '''
    
    initCohnAlphaObject(settings)
    caObj.fitCohnAlpha(settings=settings, settingsPath=settingsPath, showSubPlots=showSubPlots)
    return True