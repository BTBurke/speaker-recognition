#map_adapt.py
#
# Copyright 2011, Xemplar Biometrics, Inc

from scikits.learn import mixture
import numpy as np

def map_adapt_speaker(obs, world, r_m=16.0, r_w=16.0):
    
    # Catch fatal errors
    assert isinstance(world, type(mixture.GMM()))
    assert np.size(obs,1) == np.size(world.means,1)
    assert np.size(obs,0) > 1
    
    #Cast if passed in int type
    r_m = float(r_m)
    r_w = float(r_w)
    
    #Posterior probabilities
    # for X = {x_1, ..., x_T}
    # P(i|x_t) = w_i * p_i(x_t) / sum_j=1_M(w_j * P_j(x_t))
    
    posterior = world.predict_proba(obs)
    #print np.shape(posterior)

    n_i = np.sum(posterior, 0)
    #print np.shape(n_i)
    E_i = np.zeros((world.n_states,np.size(obs,1)), dtype=np.float)
    for i in range(world.n_states):
        #print np.shape(posterior[:,i]), np.shape(obs), np.shape(n_i[i])
        post_i = np.reshape(posterior[:,i],(np.size(obs,0),1))
        #print np.shape(post_i)
        E_i[i,:] = np.sum(post_i*obs, 0) / n_i[i]
    
    a_i_mean = np.reshape(n_i / (n_i + r_m), (world.n_states,1))
    a_i_weight = n_i / (n_i + r_w)
    
    T = float(np.size(obs,0))
    
    w_hat = a_i_weight * n_i / T + (1.0-a_i_weight)*world.weights
    w_hat = w_hat / np.sum(w_hat)
    
    #print np.shape(E_i), np.shape(world.means), np.shape(a_i_mean) 
    u_hat = a_i_mean * E_i + (1.0-a_i_mean)*world.means
    
    return w_hat, u_hat

def convert_type_db_gmm(u):
    """
    Given compressed numpy arrays that specify a GMM from database
    convert back to type scikits.learn.GMM
    """

    world = mixture.GMM(n_states=np.size(u.ubm_means,0))
    world.means = u.ubm_means
    vars_diag = np.zeros((np.size(u.ubm_vars,0), np.size(u.ubm_vars,1)), dtype=np.float)
    for i in range(np.size(vars_diag,0)):
        vars_diag[i,:] = np.diag(u.ubm_vars[i])
    world.covars = vars_diag
    world.weights = np.reshape(u.ubm_weights, (np.size(u.ubm_weights,0),))

    return world



if __name__ == '__main__':
    
    pass
        
                      
                