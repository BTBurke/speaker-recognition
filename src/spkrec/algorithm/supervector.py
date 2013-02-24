#supervector.py

import numpy as np

def create_supervector(w, m, v):
    """
    Returns Gaussian Supervector (GSV) using bounded Kullback-Leibler
    distance method
    """

    #Verify input conforms to proper shapes for matrix math
    assert np.size(w,0) == np.size(m,0) == np.size(v,0)
    assert np.size(m,1) == np.size(v,1) == np.size(v,2)

    num_mixtures = np.size(w,0)
    num_mfccs = np.size(m,1)

    for i in range(num_mixtures):
        m[i,:] = np.sqrt(w[i]) * m[i,:] * np.diag(v[i,:,:]**(-.5))
    
    return np.reshape(m,(num_mixtures*num_mfccs,1))
