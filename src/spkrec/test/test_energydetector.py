from spkrec.algorithm.energydetector import classify_speech
import numpy as np

def test_energydetector():
    #Number of sample frames and percent speech
    NUM_SAMPLES = 500
    RATIO = .8
    SPEECH_MEAN = 10.0
    SPEECH_STD = 2.0
    
    num_energy = int(np.floor(RATIO * NUM_SAMPLES))
    num_silence = NUM_SAMPLES - num_energy
    
    energy_pts = np.random.randn(num_energy)*SPEECH_STD + SPEECH_MEAN
    silence_pts = np.random.randn(num_silence)
    
    ind = np.arange(NUM_SAMPLES)
    np.random.shuffle(ind)
    
    #Create test vector using shuffled indices
    energy_vec = np.zeros(NUM_SAMPLES, dtype=np.float)
    energy_vec[ind[0:num_energy]] = energy_pts
    energy_vec[ind[num_energy::]] = silence_pts
    energy_vec = np.reshape(energy_vec,(NUM_SAMPLES,1))
    
    #Ground truth
    truth_vec = np.zeros(np.shape(energy_vec), dtype=np.int)
    truth_vec[ind[0:num_energy]] = 1
    truth_vec[ind[num_energy::]] = 0
    
    #Test energy-based speech classifier
    detected_speech = classify_speech(energy_vec)  
    
    #Calculate prediction accuracy
    predict_pct = 1.0 - float(np.sum(np.abs(detected_speech-truth_vec)))/float(NUM_SAMPLES)
    
    #Prediction percentage should be nearly 100% for these settings
    assert predict_pct >= 0.95