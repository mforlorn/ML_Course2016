import numpy as np
import scipy as sc

from KernelMatrix import KernelMatrix, SquareDist
from learn_error import learn_error
from tsvd import tsvd
from rls import rls
from cutoff import cutoff
from land import land
from nu import nu

def learn(knl, kpar, filt, t_range, X, y, task='Classification'):
    #LEARN Learns an estimator. 
    #   ALPHA = LEARN(KNL, KPAR, FILT, T_RANGE, X, Y) calculates a set of 
    #   estimators given a kernel type 'KNL' and (if needed) a kernel parameter 
    #   'KPAR', a filter type 'FILT', a range of regularization parameters 
    #   'T_RANGE' and a training set composed by the input matrix 'X[n,d]' and
    #   the output vector 'Y[n,1]'.
    #
    #   The allowed values for 'KNL' and 'KPAR' are described in the
    #   documentation given with the 'KERNEL' function.
    #
    #   The allowed values for 'FILT' are:
    #       'Reg. Least Squared'   - regularized least squares
    #       'Landweber'  - iterative Landweber
    #       'Truncated SVD'  - truncated SVD
    #       'NU-method'    - nu-method
    #       'Spectral Cut-Off'- spectral cut-off
    #
    #   The parameter 'T_RANGE' may be a range of values or a single value.
    #   In case of 'FILT' equal 'land' or 'nu', 'T_RANGE' *MUST BE* a single
    #   integer value, because its value is interpreted as 'T_MAX' (see also 
    #   LAND and NU documentation). Note that in case of 'land' the algorithm
    #   step size 'tau' will be automatically calculated (and printed).
    #
    #   ALPHA, ERR = LEARN(KNL, FILT, T_RANGE, X, Y, TASK) also returns
    #   either classification or regression errors (on the training data)
    #   according to the parameter 'TASK':
    #       'Classification' - classification
    #       'Regression'  - regression
    #
    #   Example:
    #       alpha = learn('Linear', [], 'Reg. Least Squared', np.linspace(1, 10, 20), X, y)
    #       alpha = learn('Gaussian', 2.0, 'Landweber', 100, X, y)
    #       alpha, err = learn('Linear', [] , 'Truncated SVD', np.linspace(1, 10, 20), X, y, 'Regression')
    #
    #   See also KCV, KERNEL, LEARN_ERROR
    
    # Check inputs
    if (filt=='NU-method' and len(t_range) != 1) or (filt=='Landweber' and len(t_range) != 1):
        print 'The dimension of the t_range array MUST be 1'           
    
    if (task=='Classification' or task=='Regression')==False:
        print 'Unknown learning task!'
    
    # Compute kernel K
    if knl=='cust':
        n = np.size(X, axis=0)
        if (np.size(kpar, axis=0)==n or np.size(kpar, axis=1)==n)==False:
            print 'Not valid custom kernel'
    else:
        K = KernelMatrix(X, X, knl, kpar)
        
    # Algorithm execution
    if filt=='Landweber':
        if knl=='Gaussian':
            tau = 2.0
        else:
            s = sc.sparse.linalg.eigsh(K, 1, which='LM' )
            tau = 2.0/float(s[0][0])
        print 'Calculated step size tau:', tau        
        alpha = land(K, t_range, y, tau, True)

    elif filt=='NU-method':
        alpha = nu(K, t_range, y, True)
        
    elif filt=='Reg. Least Squared':
        alpha = rls(K, t_range, y)
        
    elif filt=='Truncated SVD':
        alpha = tsvd(K, t_range, y)
        
    elif filt=='Spectral Cut-Off':
        alpha = cutoff(K, t_range, y)
        
    else:
        print 'Unknown filter. Please specify one in: nu, rls, tsvd, land, cutoff' 
    
    #Training Error requested
    err = np.zeros((1,np.size(alpha, axis=1)))
    for i in range(0, np.size(alpha, axis=1)):
        alphai=np.reshape(alpha[:,i], (np.size(K, axis=1),1))
        y_lrnt = np.dot(K, alphai)
        err[0, i]=learn_error( y_lrnt, y, task)  
    
    return alpha, err