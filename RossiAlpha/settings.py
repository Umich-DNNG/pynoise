class IOSettings:
    def __init__(self, typeIn, inputIn, outputIn):
        self.type = typeIn
        self.input = inputIn
        self.output = outputIn

class GenSettings:
    def __init__(self, fitIn, scaleIn, methodIn, delayIn, numIn, measIn, sortIn, saveIn, showIn, dirIn):
        self.fit = fitIn
        self.scale = scaleIn
        self.method = methodIn
        self.delay = delayIn
        self.num = numIn
        self.meas = measIn
        self.sort = sortIn
        self.save = saveIn
        self.show = showIn
        self.dir = dirIn

class VisSettings:
    def __init__(self, colorIn, edgeIn, faceIn, styleIn, widthIn):
        self.color = colorIn
        self.edge = edgeIn
        self.face = faceIn
        self.style = styleIn
        self.width = widthIn

class HistSettings:
    def __init__(self, timeIn=2e3, widthIn=2, cutoffIn=30):
        self.time = timeIn
        self.width = widthIn
        self.cutoff = cutoffIn

class FitSettings:
    def __init__(self, colorIn='red', edgeIn='blue', faceIn='black', styleIn='-', widthIn=1):
        self.color = colorIn
        self.edge = edgeIn
        self.face = faceIn
        self.style = styleIn
        self.width = widthIn

class ResSettings:
    def __init__(self, sIn=8):
        self.s = sIn