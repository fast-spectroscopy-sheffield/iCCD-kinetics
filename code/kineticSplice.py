import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import UnivariateSpline

class KineticSplice(object):
    
    def __init__(self, overlappedPairs):
        self._overlappedPairs = overlappedPairs
            
    def _calculateInitialGuess(self):
        initialGuess = []
        for pair in self._overlappedPairs:
            scalingFactorGuess = pair[0].max()/pair[1].max()
            initialGuess.append(scalingFactorGuess)
        initialGuess = np.array(initialGuess).mean()
        return initialGuess
    
    def _constructDataAndFittingVector(self):
        for index, pair in enumerate(self._overlappedPairs):
            if index == 0:
                data = pair[0]
                vector = pair[1]
            else:
                data = np.append(data, pair[0])
                vector = np.append(vector, pair[1])
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
        del(pcov)
        scalingFactor = popt[0]
        return scalingFactor