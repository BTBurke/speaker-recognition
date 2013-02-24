#test_map_adapt.py
#
# Copyright 2011, Xemplar Biometrics, Inc

from spkrec.algorithm.map_adapt import map_adapt_speaker
import numpy as np
from spkrec.algorithm.train_ubm import train_gmm
    
params = {'num_mixtures': 2}
world = None

for i in range(2):
        
    NUM_SAMPLES = 10000
    RATIO = .5
    if i==0:
        GROUP1_X = 5.0
        GROUP1_Y = 5.0
        GROUP1_X_SIGMA = 2.0
        GROUP1_Y_SIGMA = 2.0
        GROUP2_X = 10.0
        GROUP2_Y = 10.0
        GROUP2_X_SIGMA = 1.0
        GROUP2_Y_SIGMA = 2.0
    else:
        GROUP1_X = 16.0
        GROUP1_Y = 32.0
        GROUP1_X_SIGMA = 2.0
        GROUP1_Y_SIGMA = 2.0
        GROUP2_X = 53.0
        GROUP2_Y = 3.0
        GROUP2_X_SIGMA = 1.0
        GROUP2_Y_SIGMA = 2.0
        
    num_group1 = int(np.floor(RATIO * NUM_SAMPLES))
    num_group2 = NUM_SAMPLES - num_group1
    
    group1_x_pts = np.random.randn(num_group1)*GROUP1_X_SIGMA + GROUP1_X
    group1_y_pts = np.random.randn(num_group1)*GROUP1_Y_SIGMA + GROUP1_Y
    group2_x_pts = np.random.randn(num_group2)*GROUP2_X_SIGMA + GROUP2_X
    group2_y_pts = np.random.randn(num_group2)*GROUP2_Y_SIGMA + GROUP2_Y
    group1_xy = [[x,y] for (x,y) in zip(group1_x_pts,group1_y_pts)]
    group2_xy = [[x,y] for (x,y) in zip(group2_x_pts,group2_y_pts)]
    
    ind = np.arange(NUM_SAMPLES)
    np.random.shuffle(ind)
    
    #Create test vector using shuffled indices
    obs = np.zeros((NUM_SAMPLES,2), dtype=np.float)
    obs[ind[0:num_group1],:] = group1_xy
    obs[ind[num_group1::]] = group2_xy
    
    if i ==0:
        world = train_gmm(obs, world, params)
        from pprint import pprint
        print '--Means--'
        pprint(world.means)
        print '--Covars--'
        pprint(world.covars)
        print '--Weights--'
        pprint(world.weights)
    else:
        w_hat, u_hat = map_adapt_speaker(obs, world)
        print '--Updated Means--'
        pprint(u_hat)
        print '--Updated Weights--'
        pprint(w_hat)

        # Test outputs compared to true values and measure MSE
        true_means = np.array([np.mean(group1_xy,0),np.mean(group2_xy,0)])
        true_means = np.sort(true_means,0)

        calc_means = np.sort(u_hat,0)

        MSE_means = np.sqrt(np.sum((calc_means-true_means)**2,1))
        
        assert np.max(MSE_means) < .5

        true_weights = np.sort([RATIO, 1.0-RATIO])
        calc_weights = np.sort(w_hat)
        MSE_weights = np.sqrt(np.sum((calc_weights-true_weights)**2))
        
        assert np.max(MSE_weights) < .5