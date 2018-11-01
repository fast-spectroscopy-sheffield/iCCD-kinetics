import numpy as np
import pandas as pd

'''
Thanks to Francesco Rossetto for the algorithm.
'''

class CosmicRayRemoval(object):
    
    def __init__(self):
        pass

    @staticmethod
    def _movavg1d(a, *arg):
        '''
        Moving average for 1-d numpy arrays, called by movavg().
        '''
        if len(arg) == 0: raise TypeError('movavg expected 1 argument, got 0')
        elif len(arg) == 1: l = r = arg[0]
        elif len(arg) == 2: l, r = arg
        else: raise TypeError('movavg expected at most 2 arguments, got {}'.format(len(arg)))
        N = len(a)
        b = np.array([None]*N)
        for i in range(N):
            n_i = i - l if i-l > 0 else 0
            n_f = i + r if i+r < N else N
            b[i] = np.mean(a[n_i:n_f+1])
        return b
    
    def _crremove1d(self, a, **kwarg):
        '''
        Cosmic rays removal for 1-d numpy arrays, called by crremove()
        '''
        n = kwarg.pop('n', 10)
        thr = kwarg.pop('threshold', 10.)
        if kwarg: raise TypeError('crremove() got an unexpected keyword argument \'{}\''.format(kwarg.popitem()[0]))
        smooth = self._movavg(a, n)
        res = (a - smooth)**2
        res /= np.mean(res)
        ind = np.where(res > thr)
        b = np.empty_like(a)
        for i in range(len(a)):
            b[i] = smooth[i] if i in tuple(map(tuple, ind))[0] else a[i]
        return b
    
    def _movavg(self, inarr, *arg, **kwarg):
        '''
        Moving average for numpy arrays.
        
        Parameters
        ----------
        inarr : ndarray
            Input array to compute the moving average.
        arg : int
            If only one integer argument is provided, it's going to be taken as the
            value for the left and right window size, if two values are provided
            it's going to be the size of the left and right span respectively.
        axis : int, optional
            Axis on which the function is applied.
        
        Returns
        -------
        out : ndarray
            Moving average of the input array.
            
        Examples
        --------
        >>> import numpy as np
        >>> rnd = np.random.rand(50)
        >>> rnd
        array([ 0.32998439,  0.67953025,  0.48393839, ...,  0.14899097,
            0.69393512,  0.49948959])
        >>> movavg(rnd,10)
        array([0.61760506276997718, 0.62464670813790357, 0.62971175629157217, ...,
           0.45550012798103856, 0.4483887547214726, 0.40823090604608248], dtype=object)
        '''
        ax = kwarg.pop('axis', 0)
        if kwarg: raise TypeError('movavg() got an unexpected keyword argument \'{}\''.format(kwarg.popitem()[0]))
        b = np.apply_along_axis(self._movavg1d, ax,inarr, *arg, **kwarg)
        return b
    
    def _crremove(self, inarr, **kwarg):
        '''
        Simple cosmic rays removal algorithm.
        
        Parameters
        ----------
        inarr : ndarray
            Input array of the spectrum.
        axis : int, optional
            Axis on which the function is applied. Default is 0.
        n : int, optional
            Size of the window where the moving average is computed. Default is 10.
        threshold : float, optional
            Threshold at which the average quadratic deviation is high enough to
            be considered a cosmic ray. Default is 10.0.
        
        Returns
        -------
        out : ndarray
            Cleaned spectra.
        '''
        ax = kwarg.pop('axis', 0)
        b = np.apply_along_axis(self._crremove1d, ax, inarr, **kwarg)
        return b
    
    def removeCosmicRaysPandasDataFrame(self, df, iterations=2):
        '''
        Wraps the numpy methods from Francesco around a Pandas DataFrame
        Allows for direct integration with Kinetic Joining app
        
        Parameters
        ----------
        df : pandas dataframe with index as wavelength, columns as times
        
        Returns
        -------
        out : the same dataframe but with cosmic rays removed
        '''
        numpyArray = df.values
        correctedArray = self._crremove(numpyArray)
        if iterations > 1:
            for i in range(iterations-1):
                correctedArray = self._crremove(correctedArray)
        correctedDF = pd.DataFrame(index=df.index, columns=df.columns, data=correctedArray)
        return correctedDF
        