from CohnAlpha import CohnAlpha as ca

# global Cohn Alpha Object
caObj: ca.CohnAlpha = None

def initCohnAlphaObject(settings: dict = {}):
    '''Initializes global Cohn Alpha Object
    
    Inputs:
    - settings: the current user's runtime settings'''

    # must set variable global before using
    global caObj
    
    # if uninitialized then set variable
    # otherwise return
    if caObj is not None:
        return False
    caObj = ca.CohnAlpha(settings=settings)

    return True


def plotCohnAlphaHist(settings:dict = {}):
    
    '''
    Creates a Cohn Alpha Counts Histogram
    Created Histogram is saved in the Analyzer class
    
    Inputs:
    - settings: the current user's runtime settings
    - overwrite: if overwriting the current information in memory
    '''

    initCohnAlphaObject(settings)
    caObj.plotCountsHistogram(settings)
    return True


def applyWelchApprox(settings:dict = {}):
    
    '''
    Applies the Welch Approximation transformation
    Frequencies as well as Power Spectral Density is saved in Analyzer class
    Will generate any required missing information
    
    Inputs:
    - settings: the current user's runtime settings
    - overwrite: if overwriting the current information in memory
    '''

    plotCohnAlphaHist(settings=settings)
    
    caObj.welchApproxFourierTrans(settings)
    return True


def fitCohnAlpha(settings:dict = {}):        
    
    '''
    Fits a Power Spectral Density Curve onto a 
    Transformed graph is saved into the Analyzer class
    
    Will run entire method if required information is missing
    
    Inputs:
    - settings: the current user's runtime settings
    '''
    
    # ensure necessary data exists
    applyWelchApprox(settings=settings)

    caObj.fitCohnAlpha(settings=settings)
    return True