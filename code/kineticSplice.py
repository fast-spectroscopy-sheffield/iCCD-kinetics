import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import UnivariateSpline

class KineticSplice(object):
    
    def __init__(self, overlappedPair):
        self._overlappedPair = overlappedPair
            
    def _calculateInitialGuess(self):
        initialGuess = self._overlappedPair[0].max()/self._overlappedPair[1].max()
        return initialGuess
    
    def _constructDataAndFittingVector(self):
        data = self._overlappedPair[0]
        vector = self._overlappedPair[1]
        return data, vector
    
    @staticmethod
    def _splineFittingFunction(x, vector, scalingFactor):
        xvector = range(len(vector))
        spl = UnivariateSpline(xvector, vector, s=0)
        value = spl(x)*scalingFactor
        return value
        
    def calculateScalingFactor(self):
        data, vector = self._constructDataAndFittingVector()
        x = range(len(data))
        initialGuess = self._calculateInitialGuess()
        popt, pcov = curve_fit(lambda x, scalingFactor: self._splineFittingFunction(x, vector, scalingFactor), x, data, p0=[initialGuess], bounds=(0, np.inf))
        scalingFactor = popt[0]
        error = np.sqrt(pcov[0, 0])
        return scalingFactor, error