#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pickle
from GBS_utils import gbs_simulation, save_program_and_results

def generate_random_squeezing_params(n_modes, scale=0.4, seed=None):
    if seed is not None:
        np.random.seed(seed)
    return 1 + scale * (np.random.rand(n_modes) - 0.5)  # random values in the range [0.8, 1.2]

def main():
    for n_modes in range(2, 11):
        for id in range(100):  
            squeezing_param = generate_random_squeezing_params(n_modes, seed=id)
            cutoff_dim = 4
            seed = 42

            state_vector, prog = gbs_simulation(n_modes, squeezing_param, cutoff_dim, seed)

            program_data = save_program_and_results(
                state_vector, prog, n_modes, squeezing_param, cutoff_dim
            )

            filename = f"./data/gbs_{n_modes}_id_{id}.pkl"

            with open(filename, 'wb') as f:
                pickle.dump(program_data, f)

            print(f"Saved {filename}")

if __name__ == "__main__":
    main()
